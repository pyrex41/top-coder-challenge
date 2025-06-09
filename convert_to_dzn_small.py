#!/usr/bin/env python3
"""
Convert first 100 public_cases.json to MiniZinc data format (.dzn) for testing
"""

import json

def convert_to_dzn_small():
    # Load the JSON data
    with open('public_cases.json', 'r') as f:
        data = json.load(f)
    
    # Take only first 100 cases for testing
    data = data[:100]
    n_cases = len(data)
    days_input = []
    miles_input = []
    receipts_input = []
    expected_output = []
    
    for case in data:
        days_input.append(case['input']['trip_duration_days'])
        miles_input.append(case['input']['miles_traveled'])
        receipts_input.append(case['input']['total_receipts_amount'])
        expected_output.append(case['expected_output'])
    
    # Write the .dzn file
    with open('reimbursement_data_small.dzn', 'w') as f:
        f.write(f"n_cases = {n_cases};\n\n")
        
        f.write("days_input = [\n")
        for i, val in enumerate(days_input):
            if i == len(days_input) - 1:
                f.write(f"  {val}\n")
            else:
                f.write(f"  {val},\n")
        f.write("];\n\n")
        
        f.write("miles_input = [\n")
        for i, val in enumerate(miles_input):
            if i == len(miles_input) - 1:
                f.write(f"  {val}\n")
            else:
                f.write(f"  {val},\n")
        f.write("];\n\n")
        
        f.write("receipts_input = [\n")
        for i, val in enumerate(receipts_input):
            if i == len(receipts_input) - 1:
                f.write(f"  {val}\n")
            else:
                f.write(f"  {val},\n")
        f.write("];\n\n")
        
        f.write("expected_output = [\n")
        for i, val in enumerate(expected_output):
            if i == len(expected_output) - 1:
                f.write(f"  {val}\n")
            else:
                f.write(f"  {val},\n")
        f.write("];\n")
    
    print(f"Converted {n_cases} cases to reimbursement_data_small.dzn")

if __name__ == "__main__":
    convert_to_dzn_small()