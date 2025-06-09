#!/usr/bin/env python3
"""
Test V5 improvements on specific high-error cases from V2
"""

import json
from reimbursement_v2 import ReimbursementCalculatorV2
from reimbursement_v5_refined import ReimbursementCalculatorV5

def test_high_error_cases():
    """Test the specific cases that had highest errors in V2"""
    
    # High error cases from V2 analysis
    high_error_cases = [
        # Case 512: 8d, 1025mi, $1031.33 -> Expected: $2214.64, V2 Got: $1269.43, Error: $945.21
        {"days": 8, "miles": 1025, "receipts": 1031.33, "expected": 2214.64, "case_id": "512"},
        # Case 148: 7d, 1006mi, $1181.33 -> Expected: $2279.82, V2 Got: $1338.73, Error: $941.09  
        {"days": 7, "miles": 1006, "receipts": 1181.33, "expected": 2279.82, "case_id": "148"},
        # Case 995: 1d, 1082mi, $1809.49 -> Expected: $446.94, V2 Got: $1378.06, Error: $931.12
        {"days": 1, "miles": 1082, "receipts": 1809.49, "expected": 446.94, "case_id": "995"},
        # Case 668: 7d, 1033mi, $1013.03 -> Expected: $2119.83, V2 Got: $1229.02, Error: $890.81
        {"days": 7, "miles": 1033, "receipts": 1013.03, "expected": 2119.83, "case_id": "668"},
        # Case 326: 7d, 1089mi, $1026.25 -> Expected: $2132.85, V2 Got: $1255.08, Error: $877.77  
        {"days": 7, "miles": 1089, "receipts": 1026.25, "expected": 2132.85, "case_id": "326"},
    ]
    
    v2_calc = ReimbursementCalculatorV2()
    v5_calc = ReimbursementCalculatorV5()
    
    print("🎯 Testing V5 improvements on V2's highest error cases:")
    print("=" * 80)
    
    total_v2_error = 0
    total_v5_error = 0
    
    for case in high_error_cases:
        days = case["days"]
        miles = case["miles"]
        receipts = case["receipts"]
        expected = case["expected"]
        case_id = case["case_id"]
        
        v2_pred = v2_calc.calculate_reimbursement(days, miles, receipts)
        v5_pred = v5_calc.calculate_reimbursement(days, miles, receipts)
        
        v2_error = abs(v2_pred - expected)
        v5_error = abs(v5_pred - expected)
        
        total_v2_error += v2_error
        total_v5_error += v5_error
        
        improvement = ((v2_error - v5_error) / v2_error) * 100 if v2_error > 0 else 0
        
        print(f"Case {case_id}: {days}d, {miles:.0f}mi, ${receipts:.2f}")
        print(f"  Expected: ${expected:.2f}")
        print(f"  V2: ${v2_pred:.2f} (error: ${v2_error:.2f})")
        print(f"  V5: ${v5_pred:.2f} (error: ${v5_error:.2f})")
        print(f"  Improvement: {improvement:+.1f}%")
        print()
    
    overall_improvement = ((total_v2_error - total_v5_error) / total_v2_error) * 100
    print(f"📊 Overall improvement on high-error cases: {overall_improvement:+.1f}%")
    print(f"📊 Total V2 error: ${total_v2_error:.2f}")
    print(f"📊 Total V5 error: ${total_v5_error:.2f}")

def quick_full_test():
    """Quick test on first 100 cases to see overall impact"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    test_data = data[:100]  # Quick test on first 100
    
    v2_calc = ReimbursementCalculatorV2()
    v5_calc = ReimbursementCalculatorV5()
    
    v2_errors = []
    v5_errors = []
    
    for case in test_data:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        v2_pred = v2_calc.calculate_reimbursement(days, miles, receipts)
        v5_pred = v5_calc.calculate_reimbursement(days, miles, receipts)
        
        v2_errors.append(abs(v2_pred - expected))
        v5_errors.append(abs(v5_pred - expected))
    
    v2_score = sum(v2_errors)
    v5_score = sum(v5_errors)
    
    improvement = ((v2_score - v5_score) / v2_score) * 100
    
    print(f"\n🧪 Quick test on 100 cases:")
    print(f"V2 score: {v2_score:.2f}")
    print(f"V5 score: {v5_score:.2f}")
    print(f"Improvement: {improvement:+.1f}%")

if __name__ == "__main__":
    test_high_error_cases()
    quick_full_test()