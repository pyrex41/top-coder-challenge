#!/usr/bin/env python3
"""
Analyze failure cases to understand where our model is wrong
"""

import json
from reimbursement_calculator import ReimbursementCalculator

def analyze_failures():
    # Load the data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    calculator = ReimbursementCalculator()
    
    # Track errors
    errors = []
    for i, case in enumerate(data):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculator.calculate_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        
        errors.append({
            'case': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'ratio': predicted / expected if expected > 0 else 0
        })
    
    # Sort by error and analyze worst cases
    errors.sort(key=lambda x: x['error'], reverse=True)
    
    print("=== WORST 20 PREDICTIONS ===")
    for i, err in enumerate(errors[:20]):
        print(f"Case {err['case']:3d}: {err['days']}d, {err['miles']:6.1f}mi, ${err['receipts']:7.2f} → "
              f"Expected: ${err['expected']:7.2f}, Got: ${err['predicted']:7.2f}, "
              f"Error: ${err['error']:7.2f} ({err['ratio']:.2f}x)")
    
    # Analyze by trip length
    print("\n=== ERRORS BY TRIP LENGTH ===")
    by_days = {}
    for err in errors:
        days = err['days']
        if days not in by_days:
            by_days[days] = []
        by_days[days].append(err)
    
    for days in sorted(by_days.keys()):
        day_errors = by_days[days]
        avg_error = sum(e['error'] for e in day_errors) / len(day_errors)
        avg_ratio = sum(e['ratio'] for e in day_errors) / len(day_errors)
        print(f"{days:2d}-day trips: {len(day_errors):3d} cases, avg error: ${avg_error:6.2f}, avg ratio: {avg_ratio:.2f}x")
    
    # Focus on 1-day trips since they're the worst
    print("\n=== 1-DAY TRIP ANALYSIS ===")
    one_day_trips = [e for e in errors if e['days'] == 1]
    one_day_trips.sort(key=lambda x: x['miles'])
    
    print("Miles vs Expected output for 1-day trips:")
    for trip in one_day_trips[:15]:
        print(f"{trip['miles']:6.1f} miles, ${trip['receipts']:7.2f} receipts → ${trip['expected']:7.2f}")
    
    # Look for patterns in 1-day trips
    print("\n=== ANALYSIS: 1-DAY TRIP PATTERNS ===")
    
    # Check if there's a different formula for 1-day trips
    high_mile_1day = [t for t in one_day_trips if t['miles'] > 500]
    low_mile_1day = [t for t in one_day_trips if t['miles'] <= 500]
    
    print(f"High mileage 1-day (>500mi): {len(high_mile_1day)} cases")
    if high_mile_1day:
        avg_per_mile = sum(t['expected'] / t['miles'] for t in high_mile_1day) / len(high_mile_1day)
        print(f"  Average $/mile: {avg_per_mile:.2f}")
        
    print(f"Low mileage 1-day (<=500mi): {len(low_mile_1day)} cases")  
    if low_mile_1day:
        avg_per_mile = sum(t['expected'] / t['miles'] for t in low_mile_1day) / len(low_mile_1day)
        print(f"  Average $/mile: {avg_per_mile:.2f}")
        
    # Check if 1-day trips follow a simpler formula
    print("\n=== TRYING SIMPLE 1-DAY FORMULA ===")
    print("If 1-day trips are just: base + mileage + receipts (no multipliers)")
    
    base_estimate = 106.71
    mile_rate = 0.5  # rough estimate
    receipt_rate = 0.3  # rough estimate
    
    for trip in one_day_trips[:10]:
        simple_calc = base_estimate + trip['miles'] * mile_rate + trip['receipts'] * receipt_rate
        print(f"{trip['miles']:6.1f}mi, ${trip['receipts']:6.2f} → Expected: ${trip['expected']:6.2f}, "
              f"Simple: ${simple_calc:6.2f}, Error: ${abs(simple_calc - trip['expected']):6.2f}")

if __name__ == "__main__":
    analyze_failures()