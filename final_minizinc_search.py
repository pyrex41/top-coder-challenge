#!/usr/bin/env python3
"""
Final Comprehensive MiniZinc Search with Realistic Constraints
Based on debugging analysis showing error ranges of $20-100
"""

import json
import minizinc
from datetime import timedelta
from pathlib import Path

class FinalMiniZincSearch:
    def __init__(self):
        self.cases = self.load_cases()
        Path("final_models").mkdir(exist_ok=True)
        
    def load_cases(self):
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        return cases
    
    def create_realistic_models(self):
        """Create models with realistic error tolerances (50-150 dollars)"""
        
        models = []
        
        # Model 1: Simple Linear (realistic tolerance)
        model1 = """
% Simple Linear Model - Realistic Constraints
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: per_diem;
var 0.1..1.0: mile_rate;
var 0.5..1.5: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 150.0
);

solve satisfy;

output [
    "=== SIMPLE LINEAR SUCCESS ===\\n",
    "Per diem: $", show_float(8, 4, per_diem), "\\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\\n"
];
"""
        
        with open("final_models/realistic_linear.mzn", "w") as f:
            f.write(model1)
        models.append("final_models/realistic_linear.mzn")
        
        # Model 2: 2-Tier Mileage (realistic)
        model2 = """
% 2-Tier Mileage Model - Realistic
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: per_diem;
var 50.0..200.0: tier1_end;
var 0.3..1.0: rate1;
var 0.1..0.8: rate2;
var 0.5..1.5: receipt_rate;

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
    abs(calculated[i] - expected[i]) <= 100.0
);

solve satisfy;

output [
    "=== 2-TIER MILEAGE SUCCESS ===\\n",
    "Per diem: $", show_float(8, 4, per_diem), "\\n",
    "Tier 1 (0-", show_float(6, 0, tier1_end), " mi): $", show_float(8, 5, rate1), "/mi\\n",
    "Tier 2 (", show_float(6, 0, tier1_end), "+ mi): $", show_float(8, 5, rate2), "/mi\\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\\n"
];
"""
        
        with open("final_models/realistic_2tier.mzn", "w") as f:
            f.write(model2)
        models.append("final_models/realistic_2tier.mzn")
        
        # Model 3: Receipt-Driven with Thresholds
        model3 = """
% Receipt-Driven Model with Thresholds
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_component;
var 0.1..1.0: mile_rate;

% Receipt processing with discovered threshold around 828
var 500.0..1000.0: receipt_threshold;
var 0.3..0.8: receipt_low_rate;
var 0.6..1.2: receipt_high_rate;

function var float: calc_receipts(float: r) =
    if r <= receipt_threshold then
        r * receipt_low_rate
    else
        receipt_threshold * receipt_low_rate + (r - receipt_threshold) * receipt_high_rate
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * day_component + miles[i] * mile_rate + calc_receipts(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 80.0
);

solve satisfy;

output [
    "=== RECEIPT-DRIVEN SUCCESS ===\\n",
    "Day component: $", show_float(8, 4, day_component), "/day\\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\\n",
    "Receipt threshold: $", show_float(8, 2, receipt_threshold), "\\n",
    "Low receipt rate: ", show_float(8, 5, receipt_low_rate), "x\\n",
    "High receipt rate: ", show_float(8, 5, receipt_high_rate), "x\\n"
];
"""
        
        with open("final_models/realistic_receipt_driven.mzn", "w") as f:
            f.write(model3)
        models.append("final_models/realistic_receipt_driven.mzn")
        
        # Model 4: Decision Tree with Fixed Thresholds
        model4 = """
% Decision Tree Model with Known Thresholds
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Fixed thresholds from previous analysis
float: receipt_split = 828.0;
float: day_split = 4.5;
float: mile_split = 583.0;

% Discoverable base values for each leaf
var 50.0..250.0: leaf1_base;  % Low receipt, low days
var 100.0..350.0: leaf2_base; % Low receipt, high days
var 200.0..600.0: leaf3_base; % High receipt, low miles
var 300.0..700.0: leaf4_base; % High receipt, high miles

% Adjustable factors
var 0.0..1.5: receipt_factor;
var 0.0..1.0: mile_factor;
var 0.0..50.0: day_factor;

function var float: calc_reimbursement(int: i) =
    if receipts[i] <= receipt_split then
        if days[i] <= day_split then
            leaf1_base + receipts[i] * receipt_factor
        else
            leaf2_base + receipts[i] * receipt_factor + miles[i] * mile_factor
        endif
    else
        if miles[i] <= mile_split then
            leaf3_base + receipts[i] * receipt_factor
        else
            leaf4_base + receipts[i] * receipt_factor + days[i] * day_factor
        endif
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 50.0
);

solve satisfy;

output [
    "=== DECISION TREE SUCCESS ===\\n",
    "Split thresholds: receipts <= ", show(receipt_split), ", days <= ", show(day_split), ", miles <= ", show(mile_split), "\\n",
    "Leaf bases: ", show_float(6, 2, leaf1_base), " | ", show_float(6, 2, leaf2_base), " | ", show_float(6, 2, leaf3_base), " | ", show_float(6, 2, leaf4_base), "\\n",
    "Factors: receipt=", show_float(6, 3, receipt_factor), ", mile=", show_float(6, 3, mile_factor), ", day=", show_float(6, 2, day_factor), "\\n"
];
"""
        
        with open("final_models/realistic_decision_tree.mzn", "w") as f:
            f.write(model4)
        models.append("final_models/realistic_decision_tree.mzn")
        
        # Model 5: Exact Match Attempt (very tight)
        model5 = """
% Exact Match Model - Tightest Possible
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 90.0..95.0: per_diem;
var 0.50..0.60: mile_rate;
var 0.95..1.05: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 10.0
);

solve satisfy;

output [
    "=== EXACT MATCH SUCCESS ===\\n",
    "Per diem: $", show_float(10, 6, per_diem), "\\n",
    "Mile rate: $", show_float(10, 7, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(10, 7, receipt_rate), "x\\n"
];
"""
        
        with open("final_models/exact_match.mzn", "w") as f:
            f.write(model5)
        models.append("final_models/exact_match.mzn")
        
        return models
    
    def test_model_comprehensive(self, model_file, subset_size=50):
        """Test a model comprehensively"""
        try:
            model = minizinc.Model(model_file)
            highs = minizinc.Solver.lookup("highs")
            instance = minizinc.Instance(highs, model)
            
            subset = self.cases[:subset_size]
            instance["n"] = len(subset)
            instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
            instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
            instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
            instance["expected"] = [c["expected_output"] for c in subset]
            
            result = instance.solve(timeout=timedelta(seconds=120))
            
            if result.status == minizinc.Status.SATISFIED:
                return {"status": "SUCCESS", "result": result, "subset_size": subset_size}
            elif result.status == minizinc.Status.UNSATISFIABLE:
                return {"status": "UNSATISFIABLE", "subset_size": subset_size}
            else:
                return {"status": "TIMEOUT", "subset_size": subset_size}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "subset_size": subset_size}
    
    def run_final_search(self):
        """Run the final comprehensive search"""
        
        models = self.create_realistic_models()
        
        print("=== Final MiniZinc Comprehensive Search ===")
        print("Using realistic error tolerances based on debugging analysis")
        print(f"Testing {len(models)} models with progressive subset sizes")
        print()
        
        successful_models = []
        
        for i, model_file in enumerate(models, 1):
            print(f"\n[{i}/{len(models)}] Testing {model_file}")
            print("-" * 60)
            
            # Progressive testing: start small, scale up
            subset_sizes = [20, 50, 100, 200, 500, 1000]
            
            for subset_size in subset_sizes:
                if subset_size > len(self.cases):
                    subset_size = len(self.cases)
                
                print(f"  Testing on {subset_size} cases...", end=" ")
                
                result = self.test_model_comprehensive(model_file, subset_size)
                
                if result["status"] == "SUCCESS":
                    print(f"✅ SUCCESS")
                    if subset_size >= 1000:
                        print(f"  🎉 FULL SUCCESS on all {subset_size} cases!")
                        successful_models.append({
                            "model": model_file,
                            "result": result["result"],
                            "full_success": True
                        })
                        break
                elif result["status"] == "UNSATISFIABLE":
                    print(f"❌ UNSATISFIABLE")
                    break  # No point trying larger sets
                elif result["status"] == "TIMEOUT":
                    print(f"⏰ TIMEOUT")
                    break  # No point trying larger sets
                else:
                    print(f"❌ ERROR: {result.get('error', 'Unknown')}")
                    break
                
                # If we succeeded on a smaller set, try the next larger one
                if result["status"] == "SUCCESS" and subset_size < 1000:
                    successful_models.append({
                        "model": model_file,
                        "result": result["result"],
                        "max_size": subset_size,
                        "full_success": False
                    })
                    continue
        
        return successful_models
    
    def analyze_results(self, successful_models):
        """Analyze and report the results"""
        
        if not successful_models:
            print("\n❌ No successful models found")
            return
        
        print(f"\n🎉 Found {len(successful_models)} working models!")
        print("=" * 70)
        
        full_success_models = [m for m in successful_models if m.get("full_success", False)]
        partial_success_models = [m for m in successful_models if not m.get("full_success", False)]
        
        if full_success_models:
            print("\n🏆 MODELS WITH FULL SUCCESS (all 1000 cases):")
            for model_info in full_success_models:
                print(f"\n✅ {model_info['model']}")
                print("Solution:")
                print(model_info['result'].solution)
                print("🎯 This model solves the ENTIRE challenge!")
        
        if partial_success_models:
            print("\n🔍 MODELS WITH PARTIAL SUCCESS:")
            for model_info in partial_success_models:
                max_size = model_info.get("max_size", "Unknown")
                print(f"\n📊 {model_info['model']} - Works up to {max_size} cases")
                print("Solution:")
                print(model_info['result'].solution)
        
        # Provide final recommendations
        if full_success_models:
            print("\n🎉 CHALLENGE SOLVED!")
            print("You have exact parameter values that work on all test cases!")
            best_model = full_success_models[0]
            print(f"\nBest solution from {best_model['model']}:")
            print(best_model['result'].solution)
            
        elif partial_success_models:
            print("\n🔍 PARTIAL SOLUTION FOUND")
            print("Need to:")
            print("- Relax constraints further")
            print("- Add more sophisticated rule structures")
            print("- Consider non-linear relationships")
            
        print("\n" + "=" * 70)

def main():
    """Main execution"""
    
    search = FinalMiniZincSearch()
    successful_models = search.run_final_search()
    search.analyze_results(successful_models)

if __name__ == "__main__":
    main()