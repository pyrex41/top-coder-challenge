#!/usr/bin/env python3
"""
Systematic exploration of the reimbursement system using all possible rules
"""

import json
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load and prepare the data"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame([
        {
            'days': int(case['input']['trip_duration_days']),
            'miles': float(case['input']['miles_traveled']), 
            'receipts': float(case['input']['total_receipts_amount']),
            'output': float(case['expected_output'])
        }
        for case in data
    ])
    
    return df

def phase1_isolate_components(df):
    """Phase 1: Isolate base components by analyzing extreme cases"""
    
    print("=" * 60)
    print("PHASE 1: COMPONENT ISOLATION")
    print("=" * 60)
    
    # Find pure per diem cases (very low miles and receipts)
    minimal_cases = df[(df['miles'] <= 50) & (df['receipts'] <= 50)].copy()
    if len(minimal_cases) > 0:
        minimal_cases['per_day'] = minimal_cases['output'] / minimal_cases['days']
        print(f"\nPURE PER DIEM ANALYSIS ({len(minimal_cases)} cases):")
        print("Days | Miles | Receipts | Output | Per Day")
        for _, row in minimal_cases.iterrows():
            print(f"{int(row['days']):4d} | {row['miles']:5.1f} | ${row['receipts']:7.2f} | ${row['output']:6.2f} | ${row['per_day']:6.2f}")
        
        print(f"\nPer diem statistics:")
        print(f"  Mean: ${minimal_cases['per_day'].mean():.2f}")
        print(f"  Median: ${minimal_cases['per_day'].median():.2f}")
        print(f"  Std: ${minimal_cases['per_day'].std():.2f}")
    
    # Find pure mileage cases (low receipts, vary miles)
    low_receipt_cases = df[df['receipts'] <= 50].copy()
    if len(low_receipt_cases) > 5:
        # Estimate base per diem and subtract to isolate mileage component
        base_per_diem = 100  # rough estimate
        low_receipt_cases['mileage_component'] = low_receipt_cases['output'] - (low_receipt_cases['days'] * base_per_diem)
        low_receipt_cases['rate_per_mile'] = low_receipt_cases['mileage_component'] / low_receipt_cases['miles']
        
        print(f"\nPURE MILEAGE ANALYSIS ({len(low_receipt_cases)} cases):")
        print("Days | Miles | Receipts | Component | Rate/Mile")
        for _, row in low_receipt_cases.head(15).iterrows():
            print(f"{int(row['days']):4d} | {row['miles']:5.1f} | ${row['receipts']:7.2f} | ${row['mileage_component']:8.2f} | ${row['rate_per_mile']:6.4f}")
    
    # Find pure receipt cases (low miles, vary receipts)  
    low_mile_cases = df[df['miles'] <= 50].copy()
    if len(low_mile_cases) > 5:
        base_per_diem = 100
        low_mile_cases['receipt_component'] = low_mile_cases['output'] - (low_mile_cases['days'] * base_per_diem) - (low_mile_cases['miles'] * 0.5)
        low_mile_cases['receipt_rate'] = low_mile_cases['receipt_component'] / low_mile_cases['receipts']
        
        print(f"\nPURE RECEIPT ANALYSIS ({len(low_mile_cases)} cases):")
        print("Days | Miles | Receipts | Component | Rate")
        for _, row in low_mile_cases.head(10).iterrows():
            if row['receipts'] > 0:
                print(f"{int(row['days']):4d} | {row['miles']:5.1f} | ${row['receipts']:7.2f} | ${row['receipt_component']:8.2f} | {row['receipt_rate']:6.3f}")

def phase2_find_breakpoints(df):
    """Phase 2: Use regression trees to find natural breakpoints"""
    
    print("\n" + "=" * 60)
    print("PHASE 2: BREAKPOINT DETECTION")
    print("=" * 60)
    
    # Create comprehensive feature set
    df_features = df.copy()
    df_features['miles_per_day'] = df_features['miles'] / df_features['days']
    df_features['receipts_per_day'] = df_features['receipts'] / df_features['days']
    df_features['output_per_day'] = df_features['output'] / df_features['days']
    
    # Simple decision tree to find major splits
    X = df_features[['days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day']]
    y = df_features['output']
    
    # Shallow tree to find major breakpoints
    tree = DecisionTreeRegressor(max_depth=5, min_samples_split=20, min_samples_leaf=10, random_state=42)
    tree.fit(X, y)
    
    print("\nMAJOR DECISION TREE STRUCTURE:")
    tree_rules = export_text(tree, feature_names=['days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day'])
    print(tree_rules[:2000] + "\n..." if len(tree_rules) > 2000 else tree_rules)
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': X.columns,
        'importance': tree.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFEATURE IMPORTANCE:")
    for _, row in importance.iterrows():
        print(f"  {row['feature']:15s}: {row['importance']:.3f}")
    
    # Find specific breakpoints for each variable
    print("\nSPECIFIC BREAKPOINTS:")
    
    for var in ['days', 'miles', 'receipts']:
        print(f"\n{var.upper()} breakpoints:")
        sorted_df = df_features.sort_values(var)
        
        # Look for jumps in output per unit
        if var == 'days':
            sorted_df['rate'] = sorted_df['output'] / sorted_df['days']
        elif var == 'miles': 
            sorted_df['rate'] = (sorted_df['output'] - sorted_df['days'] * 100) / sorted_df['miles']  # rough per diem subtraction
        else:  # receipts
            sorted_df['rate'] = (sorted_df['output'] - sorted_df['days'] * 100 - sorted_df['miles'] * 0.5) / sorted_df['receipts']
        
        # Find natural breakpoints where rate changes significantly
        percentiles = [10, 25, 50, 75, 90, 95]
        for p in percentiles:
            val = np.percentile(sorted_df[var], p)
            subset = sorted_df[sorted_df[var] <= val]
            if len(subset) > 10:
                avg_rate = subset['rate'].mean()
                print(f"  {p:2d}th percentile ({val:6.1f}): avg rate = {avg_rate:.3f}")

def phase3_model_interactions(df):
    """Phase 3: Model interactions between variables"""
    
    print("\n" + "=" * 60)
    print("PHASE 3: INTERACTION MODELING")
    print("=" * 60)
    
    # Create interaction features
    df_int = df.copy()
    df_int['miles_per_day'] = df_int['miles'] / df_int['days']
    df_int['receipts_per_day'] = df_int['receipts'] / df_int['days']
    
    # Test different day categories
    print("\nOUTPUT BY DAY CATEGORY:")
    day_categories = [
        (1, 1, "1-day"),
        (2, 3, "2-3 day"),
        (4, 5, "4-5 day"), 
        (6, 7, "6-7 day"),
        (8, 14, "8+ day")
    ]
    
    for min_day, max_day, label in day_categories:
        subset = df_int[(df_int['days'] >= min_day) & (df_int['days'] <= max_day)]
        if len(subset) > 0:
            print(f"  {label:10s}: {len(subset):3d} cases, avg output: ${subset['output'].mean():6.2f}, avg per day: ${(subset['output']/subset['days']).mean():6.2f}")
    
    # Test mileage categories
    print("\nOUTPUT BY MILEAGE CATEGORY:")
    mile_categories = [
        (0, 100, "Local"),
        (100, 300, "Regional"),
        (300, 600, "Long"), 
        (600, 1000, "Very Long"),
        (1000, 2000, "Extreme")
    ]
    
    for min_mile, max_mile, label in mile_categories:
        subset = df_int[(df_int['miles'] >= min_mile) & (df_int['miles'] < max_mile)]
        if len(subset) > 0:
            avg_rate = ((subset['output'] - subset['days'] * 100) / subset['miles']).mean()
            print(f"  {label:10s}: {len(subset):3d} cases, avg output: ${subset['output'].mean():6.2f}, avg $/mile: ${avg_rate:.3f}")
    
    # Test receipt categories
    print("\nOUTPUT BY RECEIPT CATEGORY:")
    receipt_categories = [
        (0, 100, "Low"),
        (100, 500, "Medium"),
        (500, 1000, "High"),
        (1000, 2000, "Very High"),
        (2000, 3000, "Extreme")
    ]
    
    for min_receipt, max_receipt, label in receipt_categories:
        subset = df_int[(df_int['receipts'] >= min_receipt) & (df_int['receipts'] < max_receipt)]
        if len(subset) > 0:
            # Estimate receipt component by subtracting estimated per diem and mileage
            est_receipt_comp = subset['output'] - subset['days'] * 100 - subset['miles'] * 0.5
            avg_rate = (est_receipt_comp / subset['receipts']).mean()
            print(f"  {label:10s}: {len(subset):3d} cases, avg output: ${subset['output'].mean():6.2f}, avg rate: {avg_rate:.3f}")

def phase4_special_cases(df):
    """Phase 4: Identify special cases and edge conditions"""
    
    print("\n" + "=" * 60)
    print("PHASE 4: SPECIAL CASES")
    print("=" * 60)
    
    # Test specific day counts
    print("\nSPECIFIC DAY COUNT ANALYSIS:")
    for day in sorted(df['days'].unique()):
        subset = df[df['days'] == day]
        avg_output = subset['output'].mean()
        avg_per_day = avg_output / day
        print(f"  {int(day):2d} days: {len(subset):3d} cases, avg output: ${avg_output:6.2f}, per day: ${avg_per_day:6.2f}")
    
    # Test receipt cents endings
    print("\nRECEIPT CENTS ANALYSIS:")
    df['receipt_cents'] = ((df['receipts'] % 1) * 100).round().astype(int)
    cents_analysis = df.groupby('receipt_cents').agg({
        'output': ['count', 'mean']
    }).round(2)
    
    # Show most common cent endings
    cents_counts = df['receipt_cents'].value_counts()
    print("Most common receipt cent endings:")
    for cent in cents_counts.head(10).index:
        count = cents_counts[cent]
        avg_output = df[df['receipt_cents'] == cent]['output'].mean()
        print(f"  .{cent:02d}: {count:2d} cases, avg output: ${avg_output:.2f}")
    
    # Test extreme combinations
    print("\nEXTREME COMBINATIONS:")
    
    # High everything
    extreme_high = df[(df['days'] >= 10) & (df['miles'] >= 800) & (df['receipts'] >= 1500)]
    if len(extreme_high) > 0:
        print(f"  High everything (10+ days, 800+ miles, $1500+ receipts): {len(extreme_high)} cases")
        print(f"    Avg output: ${extreme_high['output'].mean():.2f}")
        print(f"    Output per day: ${(extreme_high['output']/extreme_high['days']).mean():.2f}")
    
    # High miles + low receipts
    high_miles_low_receipts = df[(df['miles'] >= 800) & (df['receipts'] <= 100)]
    if len(high_miles_low_receipts) > 0:
        print(f"  High miles + low receipts (800+ miles, <$100 receipts): {len(high_miles_low_receipts)} cases")
        print(f"    Avg output: ${high_miles_low_receipts['output'].mean():.2f}")

def main():
    """Run systematic exploration"""
    
    print("SYSTEMATIC REIMBURSEMENT SYSTEM EXPLORATION")
    print("=" * 80)
    
    df = load_data()
    print(f"Loaded {len(df)} cases")
    print(f"Input ranges: Days {df['days'].min()}-{df['days'].max()}, Miles {df['miles'].min():.1f}-{df['miles'].max():.1f}, Receipts ${df['receipts'].min():.2f}-${df['receipts'].max():.2f}")
    print(f"Output range: ${df['output'].min():.2f}-${df['output'].max():.2f}")
    
    phase1_isolate_components(df)
    phase2_find_breakpoints(df) 
    phase3_model_interactions(df)
    phase4_special_cases(df)
    
    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE - Ready for parameter optimization!")
    print("=" * 80)

if __name__ == "__main__":
    main()