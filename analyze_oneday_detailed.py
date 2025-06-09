#!/usr/bin/env python3
"""
Detailed analysis of 1-day trips to understand remaining patterns
"""

import json
from reimbursement_calculator import ReimbursementCalculator

def analyze_oneday():
    # Load the data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Get all 1-day trips
    oneday_trips = []
    for i, case in enumerate(data):
        if case['input']['trip_duration_days'] == 1:
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            calculator = ReimbursementCalculator()
            predicted = calculator.calculate_reimbursement(days, miles, receipts)
            error = abs(predicted - expected)
            
            oneday_trips.append({
                'case': i,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'predicted': predicted,
                'error': error,
                'expected_per_mile': expected / miles if miles > 0 else 0
            })
    
    # Sort by mileage to see patterns
    oneday_trips.sort(key=lambda x: x['miles'])
    
    print("=== 1-DAY TRIP DETAILED ANALYSIS ===")
    print(f"Total 1-day trips: {len(oneday_trips)}")
    
    # Look for mileage breakpoints
    print("\n=== EXPECTED OUTPUT PER MILE BY MILEAGE RANGE ===")
    
    mileage_ranges = [
        (0, 100, "Very Low"),
        (100, 300, "Low"), 
        (300, 500, "Medium"),
        (500, 700, "High"),
        (700, 900, "Very High"),
        (900, 1200, "Extreme")
    ]
    
    for min_miles, max_miles, label in mileage_ranges:
        range_trips = [t for t in oneday_trips if min_miles <= t['miles'] < max_miles]
        if range_trips:
            avg_per_mile = sum(t['expected_per_mile'] for t in range_trips) / len(range_trips)
            avg_expected = sum(t['expected'] for t in range_trips) / len(range_trips)
            print(f"{label:12s} ({min_miles:3d}-{max_miles:3d} mi): {len(range_trips):2d} cases, "
                  f"${avg_per_mile:.3f}/mile, avg output: ${avg_expected:.2f}")
    
    # Look for receipt impact
    print("\n=== HIGH MILEAGE 1-DAY TRIPS (800+ miles) ===")
    high_mile_trips = [t for t in oneday_trips if t['miles'] >= 800]
    high_mile_trips.sort(key=lambda x: x['expected'])
    
    for trip in high_mile_trips:
        print(f"Case {trip['case']:3d}: {trip['miles']:6.1f}mi, ${trip['receipts']:7.2f} → "
              f"${trip['expected']:7.2f} (${trip['expected_per_mile']:.3f}/mi), "
              f"Error: ${trip['error']:6.2f}")
    
    # Check if there's a formula for very high mileage
    print("\n=== TRYING TO FIND EXTREME MILEAGE PENALTY ===")
    extreme_trips = [t for t in oneday_trips if t['miles'] >= 1000]
    
    if extreme_trips:
        print(f"Extreme mileage trips (1000+ miles): {len(extreme_trips)}")
        for trip in extreme_trips:
            # Try different penalty formulas
            base_calc = 50 + trip['miles'] * 1.2  # our current formula (simplified)
            penalty_factor = trip['expected'] / base_calc if base_calc > 0 else 0
            print(f"  {trip['miles']:6.1f}mi: Expected ${trip['expected']:6.2f}, "
                  f"Base calc: ${base_calc:6.2f}, Penalty factor: {penalty_factor:.3f}")
    
    # Look at the worst remaining errors
    oneday_trips.sort(key=lambda x: x['error'], reverse=True)
    print(f"\n=== WORST 10 REMAINING 1-DAY ERRORS ===")
    for trip in oneday_trips[:10]:
        print(f"Case {trip['case']:3d}: {trip['miles']:6.1f}mi, ${trip['receipts']:7.2f} → "
              f"Expected: ${trip['expected']:7.2f}, Got: ${trip['predicted']:7.2f}, "
              f"Error: ${trip['error']:6.2f}")

if __name__ == "__main__":
    analyze_oneday()