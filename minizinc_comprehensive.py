#!/usr/bin/env python3
"""
Comprehensive MiniZinc Rule Discovery using HiGHS solver
Fixed version that works with the available solvers
"""

import json
import minizinc
from datetime import timedelta
from pathlib import Path
import asyncio

class WorkingMiniZincDiscovery:
    def __init__(self):
        self.cases = self.load_cases()
        self.setup_directories()
        
    def load_cases(self):
        """Load public cases for rule discovery"""
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        return cases
    
    def setup_directories(self):
        """Create directory structure for models"""
        Path("working_models").mkdir(exist_ok=True)
    
    def create_progressive_models(self):
        """Create increasingly sophisticated models to test"""
        
        models = []
        
        # Model 1: Simple linear
        model1 = """
% Simple Linear Model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: per_diem;
var 0.3..0.7: mile_rate;
var 0.5..0.9: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 20.0
);

solve satisfy;

output [
    "LINEAR MODEL SUCCESS\\n",
    "Per diem: $", show_float(6, 2, per_diem), "\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        
        with open("working_models/model1_linear.mzn", "w") as f:
            f.write(model1)
        models.append("working_models/model1_linear.mzn")
        
        # Model 2: 2-Tier Mileage
        model2 = """
% 2-Tier Mileage Model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: per_diem;
var 50.0..150.0: tier1_end;
var 0.4..0.8: rate1;
var 0.2..0.6: rate2;
var 0.5..0.9: receipt_rate;

constraint rate1 >= rate2;

function var float: calc_mileage(int: m) =
    if m <= tier1_end then
        m * rate1
    else
        tier1_end * rate1 + (m - tier1_end) * rate2
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 15.0
);

solve satisfy;

output [
    "2-TIER MILEAGE SUCCESS\\n",
    "Per diem: $", show_float(6, 2, per_diem), "\\n",
    "Tier 1 (0-", show_float(6, 0, tier1_end), " mi): $", show_float(6, 3, rate1), "/mi\\n",
    "Tier 2 (", show_float(6, 0, tier1_end), "+ mi): $", show_float(6, 3, rate2), "/mi\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        
        with open("working_models/model2_2tier.mzn", "w") as f:
            f.write(model2)
        models.append("working_models/model2_2tier.mzn")
        
        # Model 3: Receipt-driven (based on our 67% importance finding)
        model3 = """
% Receipt-Driven Model (67% importance)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_base;
var 0.0..0.5: mile_rate;
var 20.0..80.0: receipt_threshold;
var 0.2..0.6: receipt_low_rate;
var 0.6..1.0: receipt_high_rate;

function var float: calc_receipts(float: r) =
    if r <= receipt_threshold then
        r * receipt_low_rate
    else
        receipt_threshold * receipt_low_rate + (r - receipt_threshold) * receipt_high_rate
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = day_base + days[i] * 20.0 + miles[i] * mile_rate + calc_receipts(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 10.0
);

solve satisfy;

output [
    "RECEIPT-DRIVEN SUCCESS\\n",
    "Day base: $", show_float(6, 2, day_base), "\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\\n",
    "Receipt threshold: $", show_float(6, 0, receipt_threshold), "\\n",
    "Low receipt rate: ", show_float(6, 3, receipt_low_rate), "x\\n",
    "High receipt rate: ", show_float(6, 3, receipt_high_rate), "x\\n"
];
"""
        
        with open("working_models/model3_receipt_driven.mzn", "w") as f:
            f.write(model3)
        models.append("working_models/model3_receipt_driven.mzn")
        
        # Model 4: Decision tree model
        model4 = """
% Decision Tree Model (based on 828 split)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

float: major_split = 828.0;
float: day_split = 4.5;
float: mile_split = 583.0;

var 50.0..200.0: base_low_receipt_low_day;
var 100.0..300.0: base_low_receipt_high_day;
var 200.0..500.0: base_high_receipt_low_mile;
var 300.0..600.0: base_high_receipt_high_mile;

var 0.0..1.0: receipt_factor;
var 0.0..0.5: mile_factor;
var 0.0..50.0: day_factor;

function var float: calc_reimbursement(int: i) =
    if receipts[i] <= major_split then
        if days[i] <= day_split then
            base_low_receipt_low_day + receipts[i] * receipt_factor
        else
            base_low_receipt_high_day + receipts[i] * receipt_factor + miles[i] * mile_factor
        endif
    else
        if miles[i] <= mile_split then
            base_high_receipt_low_mile + receipts[i] * receipt_factor
        else
            base_high_receipt_high_mile + receipts[i] * receipt_factor + days[i] * day_factor
        endif
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 5.0
);

solve satisfy;

output [
    "DECISION TREE SUCCESS\\n",
    "Major split at receipts <= ", show(major_split), "\\n",
    "Low receipt, low days base: $", show_float(6, 2, base_low_receipt_low_day), "\\n",
    "Low receipt, high days base: $", show_float(6, 2, base_low_receipt_high_day), "\\n",
    "High receipt, low miles base: $", show_float(6, 2, base_high_receipt_low_mile), "\\n",
    "High receipt, high miles base: $", show_float(6, 2, base_high_receipt_high_mile), "\\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "\\n"
];
"""
        
        with open("working_models/model4_decision_tree.mzn", "w") as f:
            f.write(model4)
        models.append("working_models/model4_decision_tree.mzn")
        
        # Model 5: Exact match attempt
        model5 = """
% Exact Match Model - Tight constraints
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 99.0..101.0: per_diem;
var 0.55..0.65: mile_rate;
var 0.70..0.80: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 2.0
);

solve satisfy;

output [
    "EXACT MATCH SUCCESS\\n",
    "Per diem: $", show_float(8, 4, per_diem), "\\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\\n"
];
"""
        
        with open("working_models/model5_exact.mzn", "w") as f:
            f.write(model5)
        models.append("working_models/model5_exact.mzn")
        
        return models
    
    def test_model_sync(self, model_file, subset_size=30):
        """Test a single model synchronously using HiGHS"""
        try:
            # Load the model
            model = minizinc.Model(model_file)
            
            # Use HiGHS solver (which works)
            highs = minizinc.Solver.lookup("highs")
            instance = minizinc.Instance(highs, model)
            
            # Set data (use subset for speed)
            subset = self.cases[:subset_size]
            instance["n"] = len(subset)
            instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
            instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
            instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
            instance["expected"] = [c["expected_output"] for c in subset]
            
            # Solve with timeout
            result = instance.solve(timeout=timedelta(seconds=60))
            
            if result.status == minizinc.Status.SATISFIED:
                return {"model": model_file, "status": "SUCCESS", "result": result}
            elif result.status == minizinc.Status.UNSATISFIABLE:
                return {"model": model_file, "status": "UNSATISFIABLE", "result": None}
            else:
                return {"model": model_file, "status": "TIMEOUT", "result": None}
                
        except Exception as e:
            return {"model": model_file, "status": "ERROR", "error": str(e)}
    
    def run_progressive_search(self):
        """Run progressive search through increasingly sophisticated models"""
        
        models = self.create_progressive_models()
        
        print(f"\n=== Progressive MiniZinc Search ===")
        print(f"Testing {len(models)} models progressively...")
        print("Using HiGHS solver (which works in our environment)")
        print()
        
        successful_models = []
        
        for i, model in enumerate(models, 1):
            print(f"\n[{i}/{len(models)}] Testing {model}...")
            
            result = self.test_model_sync(model)
            
            if result["status"] == "SUCCESS":
                print(f"✅ SUCCESS: {model}")
                print("Solution:")
                print(result["result"].solution)
                successful_models.append(result)
                
                # Test on larger subset
                print("Testing on larger subset (100 cases)...")
                large_result = self.test_model_sync(model, subset_size=100)
                if large_result["status"] == "SUCCESS":
                    print("✅ Also works on 100 cases!")
                else:
                    print(f"❌ Failed on larger subset: {large_result['status']}")
                    
            elif result["status"] == "UNSATISFIABLE":
                print(f"❌ UNSATISFIABLE: {model}")
                print("  → No parameter values satisfy all constraints")
                
            elif result["status"] == "TIMEOUT":
                print(f"⏰ TIMEOUT: {model}")
                print("  → Model too complex or constraints too tight")
                
            else:
                print(f"❌ ERROR: {model}")
                print(f"  → {result.get('error', 'Unknown error')}")
        
        return successful_models
    
    def validate_best_model(self, successful_models):
        """Validate the best model on the full dataset"""
        
        if not successful_models:
            print("\n❌ No successful models to validate")
            return None
        
        print(f"\n=== Full Dataset Validation ===")
        print(f"Testing {len(successful_models)} successful models on all 1000 cases...")
        
        best_model = None
        
        for model_info in successful_models:
            model_file = model_info["model"]
            print(f"\nValidating {model_file} on full dataset...")
            
            # Test on all cases
            result = self.test_model_sync(model_file, subset_size=len(self.cases))
            
            if result["status"] == "SUCCESS":
                print(f"🎉 FULL SUCCESS: {model_file}")
                print("This model works on ALL 1000 cases!")
                best_model = result
                break
            else:
                print(f"❌ Failed on full dataset: {result['status']}")
        
        return best_model

def main():
    """Main execution function"""
    
    print("=== Comprehensive MiniZinc Rule Discovery ===")
    print("Using HiGHS solver for constraint satisfaction")
    print("Finding exact reimbursement system rules")
    print()
    
    discovery = WorkingMiniZincDiscovery()
    
    # Run progressive search
    successful_models = discovery.run_progressive_search()
    
    if successful_models:
        print(f"\n🎉 Found {len(successful_models)} working model(s)!")
        
        # Validate on full dataset
        best_model = discovery.validate_best_model(successful_models)
        
        if best_model:
            print("\n🏆 CHALLENGE SOLVED!")
            print("Found exact rules that work on all 1000 cases")
            print("Solution:")
            print(best_model['result'].solution)
        else:
            print("\n🔍 Partial success - need to refine models for full dataset")
            
    else:
        print("\n❌ No working models found")
        print("Recommendations:")
        print("- Relax constraint tolerances")
        print("- Add more model variations")
        print("- Check for calculation bugs")
    
    print("\n=== Search Complete ===")

if __name__ == "__main__":
    main()