#!/usr/bin/env python3
"""
Debug MiniZinc constraints - find realistic error ranges
"""

import json
import minizinc
from datetime import timedelta

def analyze_error_ranges():
    """Analyze what error ranges are realistic for simple models"""
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Take first 10 cases to analyze
    subset = cases[:10]
    
    print("=== Analyzing Error Ranges ===")
    print("Testing simple linear model with different parameters")
    
    # Test a few parameter combinations manually
    test_params = [
        (100.0, 0.5, 0.7),  # per_diem, mile_rate, receipt_rate
        (105.0, 0.4, 0.8),
        (95.0, 0.6, 0.6),
    ]
    
    for per_diem, mile_rate, receipt_rate in test_params:
        print(f"\nTesting: per_diem=${per_diem}, mile_rate=${mile_rate}, receipt_rate={receipt_rate}")
        
        errors = []
        for case in subset:
            days = case["input"]["trip_duration_days"]
            miles = case["input"]["miles_traveled"]
            receipts = case["input"]["total_receipts_amount"]
            expected = case["expected_output"]
            
            calculated = days * per_diem + miles * mile_rate + receipts * receipt_rate
            error = abs(calculated - expected)
            errors.append(error)
            
            print(f"  Case: {days}d, {miles}mi, ${receipts:.2f} → calc=${calculated:.2f}, exp=${expected:.2f}, err=${error:.2f}")
        
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        min_error = min(errors)
        
        print(f"  → Avg error: ${avg_error:.2f}, Max: ${max_error:.2f}, Min: ${min_error:.2f}")

def create_relaxed_model():
    """Create a very relaxed model that should work"""
    
    model_str = """
% Very Relaxed Linear Model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 90.0..110.0: per_diem;
var 0.2..0.8: mile_rate;
var 0.4..1.0: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

% Very relaxed constraint - 100 dollar error tolerance
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 100.0
);

solve satisfy;

output [
    "RELAXED SUCCESS\\n",
    "Per diem: $", show_float(6, 2, per_diem), "\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
    
    return model_str

def test_relaxed_model():
    """Test the relaxed model"""
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    subset = cases[:10]
    
    model_str = create_relaxed_model()
    
    try:
        # Load model
        model = minizinc.Model()
        model.add_string(model_str)
        
        # Use HiGHS solver
        highs = minizinc.Solver.lookup("highs")
        instance = minizinc.Instance(highs, model)
        
        # Set data
        instance["n"] = len(subset)
        instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
        instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
        instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
        instance["expected"] = [c["expected_output"] for c in subset]
        
        print("\n=== Testing Relaxed Model ===")
        print("Solving with 100 dollar error tolerance...")
        
        # Solve
        result = instance.solve(timeout=timedelta(seconds=30))
        
        if result.status == minizinc.Status.SATISFIED:
            print("✅ SUCCESS! Relaxed model works")
            print("Solution:")
            print(result.solution)
            
            # Calculate actual errors
            per_diem = result.solution.per_diem
            mile_rate = result.solution.mile_rate
            receipt_rate = result.solution.receipt_rate
            
            print("\nActual errors with this solution:")
            errors = []
            for case in subset:
                days = case["input"]["trip_duration_days"]
                miles = case["input"]["miles_traveled"]
                receipts = case["input"]["total_receipts_amount"]
                expected = case["expected_output"]
                
                calculated = days * per_diem + miles * mile_rate + receipts * receipt_rate
                error = abs(calculated - expected)
                errors.append(error)
                
                print(f"  {days}d, {miles}mi, ${receipts:.2f} → err=${error:.2f}")
            
            avg_error = sum(errors) / len(errors)
            max_error = max(errors)
            print(f"\nAverage error: ${avg_error:.2f}")
            print(f"Maximum error: ${max_error:.2f}")
            
            return True
        else:
            print(f"❌ Failed: {result.status}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_optimization_model():
    """Create a model that minimizes error instead of exact matching"""
    
    model_str = """
% Optimization Model - Minimize Total Error
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 90.0..110.0: per_diem;
var 0.2..0.8: mile_rate;
var 0.4..1.0: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

array[1..n] of var float: errors;
constraint forall(i in 1..n)(
    errors[i] = abs(calculated[i] - expected[i])
);

var float: total_error = sum(i in 1..n)(errors[i]);
var float: max_error = max(i in 1..n)(errors[i]);

solve minimize total_error;

output [
    "OPTIMIZATION SUCCESS\\n",
    "Per diem: $", show_float(8, 4, per_diem), "\\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\\n",
    "Total error: $", show_float(8, 2, total_error), "\\n",
    "Max error: $", show_float(8, 2, max_error), "\\n",
    "Avg error: $", show_float(8, 2, total_error / n), "\\n"
];
"""
    
    return model_str

def test_optimization_model():
    """Test the optimization model that minimizes error"""
    
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    subset = cases[:20]  # Use more cases for optimization
    
    model_str = create_optimization_model()
    
    try:
        # Load model
        model = minizinc.Model()
        model.add_string(model_str)
        
        # Use HiGHS solver
        highs = minizinc.Solver.lookup("highs")
        instance = minizinc.Instance(highs, model)
        
        # Set data
        instance["n"] = len(subset)
        instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
        instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
        instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
        instance["expected"] = [c["expected_output"] for c in subset]
        
        print("\n=== Testing Optimization Model ===")
        print("Finding parameters that minimize total error...")
        
        # Solve
        result = instance.solve(timeout=timedelta(seconds=60))
        
        if result.status == minizinc.Status.SATISFIED:
            print("✅ SUCCESS! Found optimal parameters")
            print("Solution:")
            print(result.solution)
            return True
        else:
            print(f"❌ Failed: {result.status}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run debugging analysis"""
    
    print("=== MiniZinc Debugging Analysis ===")
    
    # Step 1: Analyze realistic error ranges
    analyze_error_ranges()
    
    # Step 2: Test relaxed model
    test_relaxed_model()
    
    # Step 3: Test optimization model
    test_optimization_model()

if __name__ == "__main__":
    main()