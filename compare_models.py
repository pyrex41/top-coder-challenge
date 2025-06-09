#!/usr/bin/env python3
"""
Model Comparison Script
Compare performance of different interview-informed models
"""

import json
import sys
from reimbursement_v2 import ReimbursementCalculatorV2
from reimbursement_v3_kevin_efficiency import ReimbursementCalculatorV3
from reimbursement_v4_marcus_hybrid import ReimbursementCalculatorV4

def load_test_data(limit=None):
    """Load test cases"""
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    if limit:
        data = data[:limit]
    
    return data

def calculate_score(predictions, actuals):
    """Calculate the scoring metric"""
    total_error = 0
    for pred, actual in zip(predictions, actuals):
        error = abs(pred - actual)
        total_error += error
    
    return total_error

def test_model(calculator_class, test_data, model_name):
    """Test a specific model"""
    calculator = calculator_class()
    predictions = []
    errors = []
    
    print(f"\n🧪 Testing {model_name}...")
    
    for i, case in enumerate(test_data):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(test_data)}")
            
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        try:
            predicted = calculator.calculate_reimbursement(days, miles, receipts)
            predictions.append(predicted)
            error = abs(predicted - expected)
            errors.append(error)
        except Exception as e:
            print(f"Error in case {i}: {e}")
            predictions.append(0)
            errors.append(expected)
    
    score = calculate_score(predictions, [case['expected_output'] for case in test_data])
    avg_error = sum(errors) / len(errors)
    max_error = max(errors)
    
    return {
        'score': score,
        'avg_error': avg_error,
        'max_error': max_error,
        'predictions': predictions,
        'errors': errors
    }

def analyze_high_errors(test_data, results, model_name, top_n=10):
    """Analyze the highest error cases"""
    print(f"\n🔍 Top {top_n} errors for {model_name}:")
    
    # Create list of (error, case_index, case_data)
    error_cases = []
    for i, (error, case) in enumerate(zip(results['errors'], test_data)):
        error_cases.append((error, i, case))
    
    # Sort by error and take top N
    error_cases.sort(reverse=True)
    top_errors = error_cases[:top_n]
    
    for error, idx, case in top_errors:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        predicted = results['predictions'][idx]
        
        print(f"Case {idx}: {days}d, {miles:.0f}mi, ${receipts:.2f} -> Expected: ${expected:.2f}, Got: ${predicted:.2f}, Error: ${error:.2f}")

def analyze_efficiency_patterns(test_data, results, model_name):
    """Analyze how model performs on Kevin's efficiency sweet spot"""
    print(f"\n⚡ Efficiency analysis for {model_name}:")
    
    # Group cases by miles per day
    efficiency_groups = {
        'low_efficiency': [],      # < 100 miles/day
        'medium_efficiency': [],   # 100-180 miles/day  
        'kevin_sweet_spot': [],    # 180-220 miles/day
        'high_efficiency': [],     # 220-300 miles/day
        'extreme_efficiency': []   # > 300 miles/day
    }
    
    for i, case in enumerate(test_data):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        
        if days == 0:
            continue
            
        miles_per_day = miles / days
        error = results['errors'][i]
        
        if miles_per_day < 100:
            efficiency_groups['low_efficiency'].append(error)
        elif miles_per_day < 180:
            efficiency_groups['medium_efficiency'].append(error)
        elif miles_per_day <= 220:
            efficiency_groups['kevin_sweet_spot'].append(error)
        elif miles_per_day <= 300:
            efficiency_groups['high_efficiency'].append(error)
        else:
            efficiency_groups['extreme_efficiency'].append(error)
    
    for group_name, errors in efficiency_groups.items():
        if errors:
            avg_error = sum(errors) / len(errors)
            print(f"{group_name}: {len(errors)} cases, avg error: ${avg_error:.2f}")

def analyze_receipt_patterns(test_data, results, model_name):
    """Analyze receipt processing performance"""
    print(f"\n💰 Receipt pattern analysis for {model_name}:")
    
    # Group by receipt amounts
    receipt_groups = {
        'very_low': [],      # < $50
        'low': [],           # $50-$200  
        'medium': [],        # $200-$600
        'lisa_sweet_spot': [], # $600-$800
        'high': [],          # $800-$1200
        'very_high': []      # > $1200
    }
    
    for i, case in enumerate(test_data):
        receipts = case['input']['total_receipts_amount']
        error = results['errors'][i]
        
        if receipts < 50:
            receipt_groups['very_low'].append(error)
        elif receipts < 200:
            receipt_groups['low'].append(error)
        elif receipts < 600:
            receipt_groups['medium'].append(error)
        elif receipts <= 800:
            receipt_groups['lisa_sweet_spot'].append(error)
        elif receipts <= 1200:
            receipt_groups['high'].append(error)
        else:
            receipt_groups['very_high'].append(error)
    
    for group_name, errors in receipt_groups.items():
        if errors:
            avg_error = sum(errors) / len(errors)
            print(f"{group_name}: {len(errors)} cases, avg error: ${avg_error:.2f}")

def main():
    """Main comparison function"""
    print("🔬 Interview-Informed Model Comparison")
    print("=" * 50)
    
    # Load test data
    test_data = load_test_data()
    print(f"Loaded {len(test_data)} test cases")
    
    # Test all models
    models = [
        (ReimbursementCalculatorV2, "V2 (Decision Tree)"),
        (ReimbursementCalculatorV3, "V3 (Kevin's Efficiency)"),
        (ReimbursementCalculatorV4, "V4 (Marcus's Effort)")
    ]
    
    all_results = {}
    
    for calculator_class, model_name in models:
        results = test_model(calculator_class, test_data, model_name)
        all_results[model_name] = results
        
        print(f"\n📊 {model_name} Results:")
        print(f"Score: {results['score']:.2f}")
        print(f"Average Error: ${results['avg_error']:.2f}")
        print(f"Max Error: ${results['max_error']:.2f}")
    
    # Find best model
    best_model = min(all_results.keys(), key=lambda x: all_results[x]['score'])
    best_score = all_results[best_model]['score']
    
    print(f"\n🏆 Best Model: {best_model}")
    print(f"🏆 Best Score: {best_score:.2f}")
    
    # Detailed analysis for each model
    for model_name, results in all_results.items():
        analyze_high_errors(test_data, results, model_name, 5)
        analyze_efficiency_patterns(test_data, results, model_name)
        analyze_receipt_patterns(test_data, results, model_name)
    
    # Compare improvements
    v2_score = all_results["V2 (Decision Tree)"]['score']
    print(f"\n📈 Improvement Analysis:")
    for model_name, results in all_results.items():
        if model_name != "V2 (Decision Tree)":
            improvement = ((v2_score - results['score']) / v2_score) * 100
            print(f"{model_name}: {improvement:+.1f}% vs V2")

if __name__ == "__main__":
    main()