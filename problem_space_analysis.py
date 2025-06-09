#!/usr/bin/env python3
"""
Complete Problem Space Analysis for Reimbursement System
Mapping all possible rules and variable ranges
"""

import json
import numpy as np

def analyze_problem_space():
    """
    Comprehensive analysis of the 3-input reimbursement system problem space
    """
    
    # Load data to understand ranges
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    days_list = [case['input']['trip_duration_days'] for case in data]
    miles_list = [case['input']['miles_traveled'] for case in data]
    receipts_list = [case['input']['total_receipts_amount'] for case in data]
    outputs_list = [case['expected_output'] for case in data]
    
    print("=" * 80)
    print("COMPLETE PROBLEM SPACE ANALYSIS")
    print("=" * 80)
    
    print("\n1. INPUT VARIABLE RANGES AND DISTRIBUTIONS")
    print("-" * 50)
    
    print(f"DAYS (integer):")
    print(f"  Range: {min(days_list)} to {max(days_list)}")
    print(f"  Unique values: {sorted(set(days_list))}")
    print(f"  Distribution: {dict(zip(*np.unique(days_list, return_counts=True)))}")
    
    print(f"\nMILES (float):")
    print(f"  Range: {min(miles_list):.2f} to {max(miles_list):.2f}")
    print(f"  Mean: {np.mean(miles_list):.2f}, Std: {np.std(miles_list):.2f}")
    print(f"  Percentiles: 25%={np.percentile(miles_list, 25):.1f}, 50%={np.percentile(miles_list, 50):.1f}, 75%={np.percentile(miles_list, 75):.1f}, 95%={np.percentile(miles_list, 95):.1f}")
    
    print(f"\nRECEIPTS (float):")
    print(f"  Range: ${min(receipts_list):.2f} to ${max(receipts_list):.2f}")
    print(f"  Mean: ${np.mean(receipts_list):.2f}, Std: ${np.std(receipts_list):.2f}")
    print(f"  Percentiles: 25%=${np.percentile(receipts_list, 25):.1f}, 50%=${np.percentile(receipts_list, 50):.1f}, 75%=${np.percentile(receipts_list, 75):.1f}, 95%=${np.percentile(receipts_list, 95):.1f}")
    
    print(f"\nOUTPUT (float):")
    print(f"  Range: ${min(outputs_list):.2f} to ${max(outputs_list):.2f}")
    print(f"  Mean: ${np.mean(outputs_list):.2f}, Std: ${np.std(outputs_list):.2f}")
    
    print("\n2. POSSIBLE RULE CATEGORIES")
    print("-" * 50)
    
    print("""
A. BASE COMPONENT RULES:
   1. Per Diem: days * base_rate
      - Constant rate vs variable rate by day count
      - Range: $50-150/day based on data analysis
      
   2. Mileage Reimbursement: f(miles)
      - Linear: miles * rate
      - Tiered: different rates for mile ranges
      - Progressive: rate changes continuously with distance
      - Capped: maximum reimbursement regardless of miles
      - Range: $0.10-1.50/mile based on analysis
      
   3. Receipt Reimbursement: f(receipts)
      - Percentage: receipts * rate
      - Tiered percentage: different rates for receipt ranges
      - Capped: maximum reimbursement
      - Minimum threshold: penalty for very low receipts
      - Range: 0%-100% reimbursement rates

B. INTERACTION RULES (between inputs):
   1. Days affecting Mileage rates
      - Longer trips get better/worse mileage rates
      - Efficiency bonuses: miles/day in optimal range
      
   2. Days affecting Receipt rates  
      - Longer trips get different receipt treatment
      - Per-day spending limits: receipts/day thresholds
      
   3. Miles affecting Receipt rates
      - High mileage trips get different receipt treatment
      - Travel distance justifies higher spending
      
   4. Combined thresholds
      - Rules that trigger only when multiple conditions met
      - E.g., high miles AND high receipts = penalty

C. THRESHOLD/DISCRETE RULES:
   1. Day-specific rules
      - Special handling for 1-day, 5-day, weekend trips
      - Different formulas for short vs long trips
      - Business day vs total day calculations
      
   2. Mileage breakpoints
      - Local (0-50mi), Regional (50-200mi), Long-distance (200+mi)
      - Round number thresholds: 100mi, 500mi, 1000mi
      
   3. Receipt breakpoints  
      - Low ($0-50), Medium ($50-500), High ($500-1500), Extreme ($1500+)
      - IRS limits, company policy limits
      
   4. Output caps and floors
      - Minimum reimbursement regardless of inputs
      - Maximum reimbursement per day/trip

D. SPECIAL CASE RULES:
   1. Rounding and precision
      - Receipt cents ending in specific digits (.49, .99)
      - Output rounding to nearest cent/dollar
      
   2. Edge case handling
      - Zero miles, zero receipts, zero days
      - Extreme values (vacation detection)
      - Suspicious patterns (fraud detection)
      
   3. Legacy quirks and bugs
      - Historical artifacts from system evolution
      - Unintended behavior that became policy
      - Version-specific calculation differences

E. MATHEMATICAL OPERATIONS:
   1. Linear combinations: a*days + b*miles + c*receipts
   2. Multiplicative factors: base * day_factor * efficiency_factor
   3. Piecewise functions: different formulas for different ranges
   4. Non-linear relationships: sqrt, log, exponential
   5. Conditional logic: if-then-else trees
   6. Min/max operations: caps and floors
   7. Modular arithmetic: cycle-based rules
""")

    print("\n3. POSSIBLE PARAMETER RANGES")
    print("-" * 50)
    
    print("""
Based on data analysis and business logic:

RATES:
- Base per diem: $50-200/day
- Mileage rates: $0.10-2.00/mile  
- Receipt rates: 0%-150% reimbursement
- Efficiency bonus rates: 0%-50% additional
- Penalty factors: 0.1-1.0 multipliers

THRESHOLDS:
- Day breakpoints: 1, 2, 3, 5, 7, 10, 14+ days
- Mile breakpoints: 50, 100, 200, 500, 1000+ miles
- Receipt breakpoints: $25, $50, $100, $500, $1000, $2000+
- Efficiency ranges: 50-500 miles/day
- Spending ranges: $50-300/day

CAPS AND FLOORS:
- Minimum reimbursement: $50-200
- Maximum daily reimbursement: $200-500
- Maximum total reimbursement: $1000-5000
- Receipt caps: 100%-300% of per diem
""")

    print("\n4. SYSTEMATIC EXPLORATION STRATEGY")
    print("-" * 50)
    
    print("""
To find the exact rules, we should explore:

PHASE 1: Isolate base components
- Find pure per diem by analyzing minimal cases (low miles, low receipts)
- Find pure mileage rates by analyzing low-receipt cases  
- Find pure receipt rates by analyzing low-mileage cases

PHASE 2: Identify breakpoints
- Sort data by each input variable
- Look for discontinuities in output/input ratios
- Use regression trees to find natural split points

PHASE 3: Model interactions
- Analyze residuals after accounting for base components
- Look for patterns in 2D and 3D input space
- Test efficiency metrics (miles/day, receipts/day)

PHASE 4: Handle special cases
- Identify outliers and edge cases
- Test specific day counts (1, 5, etc.)
- Check rounding and precision effects

PHASE 5: Optimize parameters
- Use the 1000 cases as optimization target
- Gradient descent, genetic algorithms, or constraint solving
- Cross-validation to avoid overfitting
""")

    print("\n5. NEXT STEPS FOR IMPROVEMENT")
    print("-" * 50)
    
    print("""
1. Regression tree analysis to find natural breakpoints
2. Isolation of pure components (per diem, mileage, receipts)
3. Residual analysis to find interaction patterns
4. Grid search over parameter combinations
5. Statistical significance testing of rules
6. Cross-validation on held-out data
""")

if __name__ == "__main__":
    analyze_problem_space()