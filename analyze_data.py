#!/usr/bin/env python3
"""
Data analysis for the reimbursement system reverse engineering.
This will help us understand patterns before building the MiniZinc model.
"""

import json
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Load the public cases data"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame for easier analysis
    rows = []
    for case in data:
        row = case['input'].copy()
        row['output'] = case['expected_output']
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.columns = ['days', 'miles', 'receipts', 'output']
    return df

def basic_statistics(df):
    """Print basic statistics about the dataset"""
    print("=== BASIC STATISTICS ===")
    print(f"Total cases: {len(df)}")
    print(f"\nInput ranges:")
    print(f"Days: {df['days'].min()} to {df['days'].max()}")
    print(f"Miles: {df['miles'].min()} to {df['miles'].max()}")
    print(f"Receipts: ${df['receipts'].min():.2f} to ${df['receipts'].max():.2f}")
    print(f"Output: ${df['output'].min():.2f} to ${df['output'].max():.2f}")
    
    print(f"\nInput distributions:")
    print(df[['days', 'miles', 'receipts', 'output']].describe())

def analyze_per_diem_pattern(df):
    """Analyze the base per diem pattern"""
    print("\n=== PER DIEM ANALYSIS ===")
    
    # Look at minimal cases (very low miles and receipts)
    minimal_cases = df[(df['miles'] <= 50) & (df['receipts'] <= 20)]
    if len(minimal_cases) > 0:
        print(f"Minimal cases (miles<=50, receipts<=20): {len(minimal_cases)}")
        
        # Calculate implied per diem
        minimal_cases = minimal_cases.copy()
        minimal_cases['per_day'] = minimal_cases['output'] / minimal_cases['days']
        print(f"Per day amounts for minimal cases:")
        print(minimal_cases[['days', 'miles', 'receipts', 'output', 'per_day']].head(10))
        print(f"Average per day: ${minimal_cases['per_day'].mean():.2f}")
        print(f"Median per day: ${minimal_cases['per_day'].median():.2f}")

def analyze_mileage_patterns(df):
    """Analyze mileage reimbursement patterns"""
    print("\n=== MILEAGE ANALYSIS ===")
    
    # Try to isolate mileage effect by looking at low-receipt cases
    low_receipt_cases = df[df['receipts'] <= 25].copy()
    print(f"Low receipt cases (<=25): {len(low_receipt_cases)}")
    
    if len(low_receipt_cases) > 10:
        # Estimate base per diem and subtract to get mileage component
        estimated_per_diem = 100  # From interviews
        low_receipt_cases['mileage_component'] = low_receipt_cases['output'] - (low_receipt_cases['days'] * estimated_per_diem)
        low_receipt_cases['implied_rate'] = low_receipt_cases['mileage_component'] / low_receipt_cases['miles']
        
        # Sort by miles to see rate patterns
        sorted_cases = low_receipt_cases.sort_values('miles')
        print("Implied mileage rates (sorted by miles):")
        print(sorted_cases[['miles', 'mileage_component', 'implied_rate']].head(15))
        
        # Look for tier breakpoints
        rate_by_mile_range = []
        for start in range(0, 500, 50):
            end = start + 50
            range_cases = sorted_cases[(sorted_cases['miles'] >= start) & (sorted_cases['miles'] < end)]
            if len(range_cases) > 0:
                avg_rate = range_cases['implied_rate'].mean()
                rate_by_mile_range.append((start, end, len(range_cases), avg_rate))
        
        print("\nAverage implied rates by mile range:")
        for start, end, count, rate in rate_by_mile_range:
            if count > 0:
                print(f"{start}-{end} miles: ${rate:.4f}/mile ({count} cases)")

def analyze_receipt_patterns(df):
    """Analyze receipt reimbursement patterns"""
    print("\n=== RECEIPT ANALYSIS ===")
    
    # Group by receipt ranges
    receipt_bins = [0, 50, 100, 200, 500, 1000, 2000, 10000]
    df['receipt_bin'] = pd.cut(df['receipts'], bins=receipt_bins, include_lowest=True)
    
    receipt_analysis = df.groupby('receipt_bin').agg({
        'receipts': ['count', 'mean'],
        'output': 'mean',
        'days': 'mean',
        'miles': 'mean'
    }).round(2)
    
    print("Receipt patterns by bin:")
    print(receipt_analysis)
    
    # Look for the .49/.99 pattern mentioned in interviews
    df['receipt_cents'] = ((df['receipts'] % 1) * 100).round().astype(int)
    cents_pattern = df.groupby('receipt_cents').agg({
        'output': ['count', 'mean'],
        'receipts': 'mean'
    }).round(2)
    
    print(f"\nPatterns by receipt cents (showing counts > 5):")
    high_count_cents = cents_pattern[cents_pattern[('output', 'count')] > 5]
    print(high_count_cents)
    
    # Specifically check .49 and .99
    cents_49 = df[df['receipt_cents'] == 49]
    cents_99 = df[df['receipt_cents'] == 99]
    print(f"\nCases ending in .49 cents: {len(cents_49)}")
    print(f"Cases ending in .99 cents: {len(cents_99)}")

def analyze_day_patterns(df):
    """Analyze patterns by trip duration"""
    print("\n=== DAY PATTERNS ANALYSIS ===")
    
    day_analysis = df.groupby('days').agg({
        'output': ['count', 'mean', 'std'],
        'miles': 'mean',
        'receipts': 'mean'
    }).round(2)
    
    print("Patterns by trip days:")
    print(day_analysis)
    
    # Look specifically at 5-day trips mentioned in interviews
    five_day_trips = df[df['days'] == 5]
    print(f"\n5-day trip analysis ({len(five_day_trips)} cases):")
    print(f"Average output: ${five_day_trips['output'].mean():.2f}")
    print(f"Output per day: ${five_day_trips['output'].mean() / 5:.2f}")
    
    # Compare to other durations
    for days in [3, 4, 6, 7]:
        day_trips = df[df['days'] == days]
        if len(day_trips) > 0:
            avg_per_day = day_trips['output'].mean() / days
            print(f"{days}-day trips output per day: ${avg_per_day:.2f}")

def analyze_efficiency_patterns(df):
    """Analyze the efficiency bonus patterns mentioned in interviews"""
    print("\n=== EFFICIENCY ANALYSIS ===")
    
    df['miles_per_day'] = df['miles'] / df['days']
    df['receipts_per_day'] = df['receipts'] / df['days']
    
    # Kevin mentioned 180-220 miles per day sweet spot
    efficiency_bins = [0, 100, 150, 180, 220, 300, 500, 1000]
    df['efficiency_bin'] = pd.cut(df['miles_per_day'], bins=efficiency_bins, include_lowest=True)
    
    efficiency_analysis = df.groupby('efficiency_bin').agg({
        'output': ['count', 'mean'],
        'miles_per_day': 'mean',
        'receipts_per_day': 'mean',
        'days': 'mean'
    }).round(2)
    
    print("Efficiency patterns (miles per day):")
    print(efficiency_analysis)

def find_extreme_cases(df):
    """Find outliers and extreme cases that might reveal special rules"""
    print("\n=== EXTREME CASES ANALYSIS ===")
    
    # High output cases
    top_outputs = df.nlargest(10, 'output')
    print("Top 10 highest outputs:")
    print(top_outputs[['days', 'miles', 'receipts', 'output']])
    
    # Cases with very high output per day
    df['output_per_day'] = df['output'] / df['days']
    top_per_day = df.nlargest(10, 'output_per_day')
    print("\nTop 10 highest output per day:")
    print(top_per_day[['days', 'miles', 'receipts', 'output', 'output_per_day']])
    
    # Cases with surprisingly low outputs
    bottom_outputs = df.nsmallest(10, 'output_per_day')
    print("\nBottom 10 lowest output per day:")
    print(bottom_outputs[['days', 'miles', 'receipts', 'output', 'output_per_day']])

def extract_potential_parameters(df):
    """Extract potential parameter values for MiniZinc model"""
    print("\n=== PARAMETER EXTRACTION FOR MINIZINC ===")
    
    # Base per diem estimate
    minimal_cases = df[(df['miles'] <= 50) & (df['receipts'] <= 20)]
    if len(minimal_cases) > 0:
        base_per_diem = (minimal_cases['output'] / minimal_cases['days']).median()
        print(f"Estimated base per diem: ${base_per_diem:.2f}")
    
    # Mileage tier estimates
    low_receipt_cases = df[df['receipts'] <= 25].copy()
    if len(low_receipt_cases) > 10:
        estimated_per_diem = 100
        low_receipt_cases['mileage_component'] = low_receipt_cases['output'] - (low_receipt_cases['days'] * estimated_per_diem)
        low_receipt_cases['implied_rate'] = low_receipt_cases['mileage_component'] / low_receipt_cases['miles']
        
        # Tier 1 (0-100 miles)
        tier1_cases = low_receipt_cases[low_receipt_cases['miles'] <= 100]
        if len(tier1_cases) > 0:
            tier1_rate = tier1_cases['implied_rate'].median()
            print(f"Estimated tier 1 mileage rate (0-100): ${tier1_rate:.4f}")
        
        # Tier 2 (100-300 miles)
        tier2_cases = low_receipt_cases[(low_receipt_cases['miles'] > 100) & (low_receipt_cases['miles'] <= 300)]
        if len(tier2_cases) > 0:
            tier2_rate = tier2_cases['implied_rate'].median()
            print(f"Estimated tier 2 mileage rate (100-300): ${tier2_rate:.4f}")
    
    # Receipt processing insights
    print(f"Receipt amount ranges:")
    print(f"  Low penalty threshold: likely around $50")
    print(f"  Medium good treatment: $200-$800")
    print(f"  High diminishing returns: >$1000")
    
    # Day-specific bonuses
    five_day_avg = df[df['days'] == 5]['output'].mean() / 5 if len(df[df['days'] == 5]) > 0 else 0
    four_day_avg = df[df['days'] == 4]['output'].mean() / 4 if len(df[df['days'] == 4]) > 0 else 0
    if five_day_avg > four_day_avg * 1.05:  # 5% threshold
        bonus = five_day_avg - four_day_avg
        print(f"Estimated 5-day bonus: ${bonus:.2f} per day")

def main():
    print("Loading data...")
    df = load_data()
    
    basic_statistics(df)
    analyze_per_diem_pattern(df)
    analyze_mileage_patterns(df)
    analyze_receipt_patterns(df)
    analyze_day_patterns(df)
    analyze_efficiency_patterns(df)
    find_extreme_cases(df)
    extract_potential_parameters(df)
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("Use these insights to build the MiniZinc constraint model!")

if __name__ == "__main__":
    main()