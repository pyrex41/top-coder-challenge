#!/usr/bin/env python3
"""
Test V6 conservative improvements vs V2
"""

import json
from reimbursement_v2 import ReimbursementCalculatorV2
from reimbursement_v6_conservative import ReimbursementCalculatorV6

def test_models(num_cases=200):
    """Test V2 vs V6 on first N cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    test_data = data[:num_cases]
    
    v2_calc = ReimbursementCalculatorV2()
    v6_calc = ReimbursementCalculatorV6()
    
    v2_errors = []
    v6_errors = []
    
    print(f"🧪 Testing V2 vs V6 on {num_cases} cases...")
    
    for i, case in enumerate(test_data):
        if i % 50 == 0:
            print(f"Progress: {i}/{num_cases}")
            
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        v2_pred = v2_calc.calculate_reimbursement(days, miles, receipts)
        v6_pred = v6_calc.calculate_reimbursement(days, miles, receipts)
        
        v2_error = abs(v2_pred - expected)
        v6_error = abs(v6_pred - expected)
        
        v2_errors.append(v2_error)
        v6_errors.append(v6_error)
    
    v2_score = sum(v2_errors)
    v6_score = sum(v6_errors)
    
    v2_avg = sum(v2_errors) / len(v2_errors)
    v6_avg = sum(v6_errors) / len(v6_errors)
    
    improvement = ((v2_score - v6_score) / v2_score) * 100
    
    print(f"\n📊 Results on {num_cases} cases:")
    print(f"V2 total score: {v2_score:.2f}")
    print(f"V6 total score: {v6_score:.2f}")
    print(f"V2 average error: ${v2_avg:.2f}")
    print(f"V6 average error: ${v6_avg:.2f}")
    print(f"Improvement: {improvement:+.2f}%")
    
    # Test specific case types
    print(f"\n🔍 Testing specific patterns:")
    
    # Test .99 cases specifically  
    test_99_cases(test_data, v2_calc, v6_calc)
    
    # Test extreme efficiency cases
    test_extreme_efficiency(test_data, v2_calc, v6_calc)

def test_99_cases(test_data, v2_calc, v6_calc):
    """Test cases ending in .99 cents"""
    cases_99 = []
    for case in test_data:
        receipts = case['input']['total_receipts_amount']
        cents = int(round((receipts % 1) * 100))
        if cents == 99:
            cases_99.append(case)
    
    if len(cases_99) == 0:
        print("No .99 cases in test set")
        return
    
    v2_errors_99 = []
    v6_errors_99 = []
    
    for case in cases_99:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        v2_pred = v2_calc.calculate_reimbursement(days, miles, receipts)
        v6_pred = v6_calc.calculate_reimbursement(days, miles, receipts)
        
        v2_errors_99.append(abs(v2_pred - expected))
        v6_errors_99.append(abs(v6_pred - expected))
    
    v2_avg_99 = sum(v2_errors_99) / len(v2_errors_99)
    v6_avg_99 = sum(v6_errors_99) / len(v6_errors_99)
    
    improvement_99 = ((v2_avg_99 - v6_avg_99) / v2_avg_99) * 100 if v2_avg_99 > 0 else 0
    
    print(f"💰 .99 cases ({len(cases_99)} cases):")
    print(f"  V2 avg error: ${v2_avg_99:.2f}")
    print(f"  V6 avg error: ${v6_avg_99:.2f}")
    print(f"  Improvement: {improvement_99:+.1f}%")

def test_extreme_efficiency(test_data, v2_calc, v6_calc):
    """Test extreme efficiency cases (300+ miles/day)"""
    extreme_cases = []
    for case in test_data:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        if days > 0 and (miles / days) >= 300:
            extreme_cases.append(case)
    
    if len(extreme_cases) == 0:
        print("No extreme efficiency cases in test set")
        return
    
    v2_errors_extreme = []
    v6_errors_extreme = []
    
    for case in extreme_cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        v2_pred = v2_calc.calculate_reimbursement(days, miles, receipts)
        v6_pred = v6_calc.calculate_reimbursement(days, miles, receipts)
        
        v2_errors_extreme.append(abs(v2_pred - expected))
        v6_errors_extreme.append(abs(v6_pred - expected))
    
    v2_avg_extreme = sum(v2_errors_extreme) / len(v2_errors_extreme)
    v6_avg_extreme = sum(v6_errors_extreme) / len(v6_errors_extreme)
    
    improvement_extreme = ((v2_avg_extreme - v6_avg_extreme) / v2_avg_extreme) * 100 if v2_avg_extreme > 0 else 0
    
    print(f"⚡ Extreme efficiency cases ({len(extreme_cases)} cases, 300+ miles/day):")
    print(f"  V2 avg error: ${v2_avg_extreme:.2f}")
    print(f"  V6 avg error: ${v6_avg_extreme:.2f}")
    print(f"  Improvement: {improvement_extreme:+.1f}%")

if __name__ == "__main__":
    test_models(200)