#!/usr/bin/env python3
"""
Simple MiniZinc test to validate setup and identify exact issues
"""

import json
import minizinc
from datetime import timedelta

def test_simple_model():
    """Test a very simple MiniZinc model"""
    
    # Load first 10 cases
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    subset = cases[:10]
    
    # Create a simple model string
    model_str = """
% Very simple test model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Simple parameters
var 95.0..105.0: per_diem;
var 0.40..0.70: mile_rate;
var 0.60..0.90: receipt_rate;

% Calculate
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

% Allow large error for testing
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 50.0
);

solve satisfy;

output [
    "Per diem: ", show(per_diem), "\\n",
    "Mile rate: ", show(mile_rate), "\\n", 
    "Receipt rate: ", show(receipt_rate), "\\n"
];
"""
    
    # Save model to file
    with open("test_simple.mzn", "w") as f:
        f.write(model_str)
    
    try:
        # Load model
        model = minizinc.Model()
        model.add_string(model_str)
        
        # Get solver
        gecode = minizinc.Solver.lookup("gecode")
        instance = minizinc.Instance(gecode, model)
        
        # Set data
        instance["n"] = len(subset)
        instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
        instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
        instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
        instance["expected"] = [c["expected_output"] for c in subset]
        
        print("Solving simple model...")
        
        # Solve with proper timeout (timedelta object)
        result = instance.solve(timeout=timedelta(seconds=30))
        
        if result.status == minizinc.Status.SATISFIED:
            print("✓ SUCCESS! MiniZinc is working")
            print("Solution found:")
            print(result.solution)
            return True
        else:
            print(f"✗ No solution found. Status: {result.status}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_command_line_approach():
    """Test using command line MiniZinc directly"""
    
    # Create data file
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    subset = cases[:5]  # Very small subset
    
    # Create data file
    data_str = f"""
n = {len(subset)};
days = {[c["input"]["trip_duration_days"] for c in subset]};
miles = {[c["input"]["miles_traveled"] for c in subset]};
receipts = {[c["input"]["total_receipts_amount"] for c in subset]};
expected = {[c["expected_output"] for c in subset]};
"""
    
    with open("test_data.dzn", "w") as f:
        f.write(data_str)
    
    print("\nCreated test data file:")
    print(data_str)
    
    return True

def main():
    print("=== Simple MiniZinc Validation ===")
    
    # Test 1: Python API
    print("\n1. Testing Python API...")
    success = test_simple_model()
    
    # Test 2: Command line data
    print("\n2. Creating command line test files...")
    test_command_line_approach()
    
    if success:
        print("\n✓ MiniZinc setup validated! Ready for comprehensive search")
    else:
        print("\n❌ MiniZinc setup needs debugging")
        print("Recommendations:")
        print("- Check solver installation")
        print("- Try command line approach")
        print("- Verify model syntax")

if __name__ == "__main__":
    main()