#!/usr/bin/env python3
"""
Comprehensive MiniZinc Diagnostic Approach
Individual case tracking + systematic model testing based on interview analysis
"""

import json
import minizinc
from datetime import timedelta
from pathlib import Path
import pandas as pd
from collections import defaultdict
import asyncio

class DiagnosticMiniZincSearch:
    def __init__(self):
        self.cases = self.load_cases()
        self.setup_directories()
        self.results_matrix = {}  # Track which cases each model solves
        
    def load_cases(self):
        with open('public_cases.json', 'r') as f:
            cases = json.load(f)
        return cases
    
    def setup_directories(self):
        """Create comprehensive directory structure"""
        dirs = [
            "diagnostic_models",
            "diagnostic_models/mileage_structures", 
            "diagnostic_models/receipt_structures",
            "diagnostic_models/combinations",
            "diagnostic_models/edge_cases",
            "diagnostic_results"
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(exist_ok=True)
    
    def create_all_interview_models(self):
        """Create all 11 plausible models based on interview analysis"""
        
        models = []
        
        # === MILEAGE STRUCTURES (4 variants) ===
        
        # Model 1: Simple 3-Tier (Marcus: "first 100 miles or so")
        model1 = """
% Model 1: Simple 3-Tier Mileage (Marcus Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-100 miles
var 0.35..0.55: rate2;  % 100-500 miles  
var 0.15..0.35: rate3;  % 500+ miles
var 0.60..0.80: receipt_rate;

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 1 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Rates: $", show_float(6, 3, rate1), 
    "/$", show_float(6, 3, rate2), "/$", show_float(6, 3, rate3), ", Receipt: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        self.save_model("diagnostic_models/mileage_structures/model1_simple_3tier.mzn", model1)
        models.append(("Model 1: Simple 3-Tier", "diagnostic_models/mileage_structures/model1_simple_3tier.mzn"))
        
        # Model 2: 2-Tier Simple
        model2 = """
% Model 2: 2-Tier Simple (Maybe simpler than interviews suggest)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-100 miles
var 0.25..0.45: rate2;  % 100+ miles
var 0.60..0.80: receipt_rate;

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    else 100 * rate1 + (m - 100) * rate2 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 2 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Rates: $", show_float(6, 3, rate1), 
    "/$", show_float(6, 3, rate2), ", Receipt: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        self.save_model("diagnostic_models/mileage_structures/model2_simple_2tier.mzn", model2)
        models.append(("Model 2: 2-Tier Simple", "diagnostic_models/mileage_structures/model2_simple_2tier.mzn"))
        
        # === RECEIPT STRUCTURES (2 variants) ===
        
        # Model 6: 3-Tier Receipts (Lisa: "$600-800 get really good treatment")
        model6 = """
% Model 6: 3-Tier Receipts (Lisa Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.45..0.65: mile_rate;

var 0.20..0.40: receipt_low_rate;   % <$50 penalty
var 0.70..0.85: receipt_med_rate;   % $50-800 normal
var 0.15..0.35: receipt_high_rate;  % $800+ diminishing

function var float: calc_receipts(float: r) =
    if r < 50 then r * receipt_low_rate
    elseif r <= 800 then 50 * receipt_low_rate + (r - 50) * receipt_med_rate
    else 50 * receipt_low_rate + 750 * receipt_med_rate + (r - 800) * receipt_high_rate endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * base_per_diem + miles[i] * mile_rate + calc_receipts(receipts[i])
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 6 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Mile: $", show_float(6, 3, mile_rate), 
    ", Receipt rates: ", show_float(6, 3, receipt_low_rate), "/", show_float(6, 3, receipt_med_rate), 
    "/", show_float(6, 3, receipt_high_rate), "\\n"
];
"""
        self.save_model("diagnostic_models/receipt_structures/model6_3tier_receipts.mzn", model6)
        models.append(("Model 6: 3-Tier Receipts", "diagnostic_models/receipt_structures/model6_3tier_receipts.mzn"))
        
        # === COMBINATION MODELS WITH SPECIAL RULES (4 variants) ===
        
        # Model 11: Base + 5-Day Bonus Only (Marcus: "5-day trips almost always get a bonus")
        model11 = """
% Model 11: Base + 5-Day Bonus Only (Marcus Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-100 miles
var 0.35..0.55: rate2;  % 100-500 miles  
var 0.15..0.35: rate3;  % 500+ miles
var 0.60..0.80: receipt_rate;
var 0.05..0.15: five_day_bonus_rate;  % 5-day bonus

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var float: bonus = if days[i] == 5 then base * five_day_bonus_rate else 0.0 endif;
    } in base + bonus
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 11 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Base: $", show_float(6, 2, base_per_diem), ", 5-day bonus: ", show_float(6, 3, five_day_bonus_rate), "x\\n"
];
"""
        self.save_model("diagnostic_models/combinations/model11_5day_bonus.mzn", model11)
        models.append(("Model 11: 5-Day Bonus", "diagnostic_models/combinations/model11_5day_bonus.mzn"))
        
        # Model 12: Base + Efficiency Bonus Only (Kevin: "180-220 miles per day")
        model12 = """
% Model 12: Base + Efficiency Bonus Only (Kevin Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;
var 0.35..0.55: rate2;
var 0.15..0.35: rate3;
var 0.60..0.80: receipt_rate;
var 30.0..70.0: efficiency_bonus;  % Fixed efficiency bonus

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var float: miles_per_day = miles[i] / max(days[i], 1);
        var float: bonus = if miles_per_day >= 180.0 /\ miles_per_day <= 220.0 then efficiency_bonus else 0.0 endif;
    } in base + bonus
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 12 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Efficiency bonus: $", show_float(6, 2, efficiency_bonus), "\\n"
];
"""
        self.save_model("diagnostic_models/combinations/model12_efficiency_bonus.mzn", model12)
        models.append(("Model 12: Efficiency Bonus", "diagnostic_models/combinations/model12_efficiency_bonus.mzn"))
        
        # === EDGE CASES (1 variant) ===
        
        # Model 19: Ultra-Simple Linear (Test if everyone's overcomplicating)
        model19 = """
% Model 19: Ultra-Simple Linear
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: per_diem;
var 0.40..0.60: mile_rate;
var 0.65..0.75: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 19 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Per diem: $", show_float(6, 2, per_diem), ", Mile: $", show_float(6, 3, mile_rate), 
    ", Receipt: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        self.save_model("diagnostic_models/edge_cases/model19_ultra_simple.mzn", model19)
        models.append(("Model 19: Ultra-Simple", "diagnostic_models/edge_cases/model19_ultra_simple.mzn"))
        
        # Add the already created models from create_remaining_models.py
        models.extend([
            ("Model 3: Variant 3-Tier", "diagnostic_models/mileage_structures/model3_variant_3tier.mzn"),
            ("Model 7: Percentage Cap", "diagnostic_models/receipt_structures/model7_percentage_cap.mzn"),
            ("Model 13: Long Trip Penalty", "diagnostic_models/combinations/model13_long_trip_penalty.mzn"),
            ("Model 14: All Bonuses", "diagnostic_models/combinations/model14_all_bonuses.mzn"),
            ("Model 15: Rounding Bug", "diagnostic_models/combinations/model15_rounding_bug.mzn"),
            ("Model 20: Non-Linear", "diagnostic_models/edge_cases/model20_nonlinear.mzn")
        ])
        
        return models
    
    def save_model(self, path, content):
        """Save a model to file"""
        with open(path, "w") as f:
            f.write(content)
    
    def test_model_with_case_tracking(self, model_name, model_file, subset_size=50):
        """Test model and track individual case success/failure"""
        try:
            model = minizinc.Model(model_file)
            highs = minizinc.Solver.lookup("highs")
            instance = minizinc.Instance(highs, model)
            
            subset = self.cases[:subset_size]
            instance["n"] = len(subset)
            instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
            instance["miles"] = [int(float(c["input"]["miles_traveled"])) for c in subset]
            instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
            instance["expected"] = [c["expected_output"] for c in subset]
            
            result = instance.solve(timeout=timedelta(seconds=90))
            
            if result.status == minizinc.Status.SATISFIED:
                # Calculate which specific cases passed/failed
                perfect_cases = []
                failed_cases = []
                
                # Get model parameters for manual calculation
                solution = result.solution
                
                for i, case in enumerate(subset):
                    days = case["input"]["trip_duration_days"]
                    miles = int(float(case["input"]["miles_traveled"]))
                    receipts = case["input"]["total_receipts_amount"]
                    expected = case["expected_output"]
                    
                    # Calculate prediction based on model type
                    predicted = self.calculate_prediction(model_name, solution, days, miles, receipts)
                    error = abs(predicted - expected)
                    
                    if error < 0.5:
                        perfect_cases.append(i)
                    else:
                        failed_cases.append({
                            'case_id': i,
                            'days': days, 
                            'miles': miles,
                            'receipts': receipts,
                            'expected': expected,
                            'predicted': predicted,
                            'error': error
                        })
                
                return {
                    "status": "SUCCESS",
                    "perfect_count": len(perfect_cases),
                    "total_cases": len(subset),
                    "perfect_cases": perfect_cases,
                    "failed_cases": failed_cases,
                    "solution": solution,
                    "subset_size": subset_size
                }
            else:
                return {"status": "UNSATISFIABLE", "subset_size": subset_size}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "subset_size": subset_size}
    
    def calculate_prediction(self, model_name, solution, days, miles, receipts):
        """Calculate prediction based on model type and solution"""
        
        if "Ultra-Simple" in model_name:
            per_diem = solution.per_diem
            mile_rate = solution.mile_rate
            receipt_rate = solution.receipt_rate
            return days * per_diem + miles * mile_rate + receipts * receipt_rate
        
        elif "2-Tier" in model_name:
            base_per_diem = solution.base_per_diem
            rate1 = solution.rate1
            rate2 = solution.rate2
            receipt_rate = solution.receipt_rate
            
            if miles <= 100:
                mileage = miles * rate1
            else:
                mileage = 100 * rate1 + (miles - 100) * rate2
            
            return days * base_per_diem + mileage + receipts * receipt_rate
        
        elif "Variant 3-Tier" in model_name:
            # Model 3: 75-400 breakpoints
            base_per_diem = solution.base_per_diem
            rate1 = solution.rate1
            rate2 = solution.rate2
            rate3 = solution.rate3
            receipt_rate = solution.receipt_rate
            
            if miles <= 75:
                mileage = miles * rate1
            elif miles <= 400:
                mileage = 75 * rate1 + (miles - 75) * rate2
            else:
                mileage = 75 * rate1 + 325 * rate2 + (miles - 400) * rate3
            
            return days * base_per_diem + mileage + receipts * receipt_rate
        
        elif "3-Tier" in model_name and "Receipts" in model_name:
            # Model 6: 3-Tier Receipts
            base_per_diem = solution.base_per_diem
            mile_rate = solution.mile_rate
            receipt_low_rate = solution.receipt_low_rate
            receipt_med_rate = solution.receipt_med_rate
            receipt_high_rate = solution.receipt_high_rate
            
            if receipts < 50:
                receipt_component = receipts * receipt_low_rate
            elif receipts <= 800:
                receipt_component = 50 * receipt_low_rate + (receipts - 50) * receipt_med_rate
            else:
                receipt_component = 50 * receipt_low_rate + 750 * receipt_med_rate + (receipts - 800) * receipt_high_rate
            
            return days * base_per_diem + miles * mile_rate + receipt_component
        
        elif "Percentage Cap" in model_name:
            # Model 7: Percentage with Cap
            base_per_diem = solution.base_per_diem
            mile_rate = solution.mile_rate
            receipt_percentage = solution.receipt_percentage
            receipt_cap = solution.receipt_cap
            
            receipt_component = min(receipts * receipt_percentage, receipt_cap)
            return days * base_per_diem + miles * mile_rate + receipt_component
        
        elif "3-Tier" in model_name:
            # Models 1, 11, 12, 13, 14, 15 - Standard 3-tier mileage
            base_per_diem = solution.base_per_diem
            rate1 = solution.rate1
            rate2 = solution.rate2
            rate3 = solution.rate3
            receipt_rate = solution.receipt_rate
            
            if miles <= 100:
                mileage = miles * rate1
            elif miles <= 500:
                mileage = 100 * rate1 + (miles - 100) * rate2
            else:
                mileage = 100 * rate1 + 400 * rate2 + (miles - 500) * rate3
            
            base_calc = days * base_per_diem + mileage + receipts * receipt_rate
            
            # Add special bonuses/penalties
            if "5-Day" in model_name and days == 5:
                bonus = base_calc * solution.five_day_bonus_rate
                base_calc += bonus
            elif "Efficiency" in model_name:
                miles_per_day = miles / max(days, 1)
                if 180 <= miles_per_day <= 220:
                    base_calc += solution.efficiency_bonus
            elif "Long Trip Penalty" in model_name and days > 7:
                penalty = (days - 7) * solution.long_trip_penalty
                base_calc -= penalty
            elif "All Bonuses" in model_name:
                # Multiple bonuses/penalties
                if days == 5:
                    base_calc += base_calc * solution.five_day_bonus_rate
                miles_per_day = miles / max(days, 1)
                if 180 <= miles_per_day <= 220:
                    base_calc += solution.efficiency_bonus
                if days > 7:
                    base_calc -= (days - 7) * solution.long_trip_penalty
                if days == 1 and miles < 50:
                    base_calc -= solution.small_trip_penalty
            elif "Rounding Bug" in model_name:
                cents = int(base_calc * 100) % 100
                if cents == 49 or cents == 99:
                    base_calc += 0.01
            
            return base_calc
        
        elif "Non-Linear" in model_name:
            # Model 20: Logarithmic/Non-Linear
            import math
            day_base = solution.day_base
            mile_log_factor = solution.mile_log_factor
            receipt_sqrt_factor = solution.receipt_sqrt_factor
            
            return (days * day_base + 
                   mile_log_factor * math.log(miles + 1) + 
                   receipt_sqrt_factor * math.sqrt(receipts))
        
        # Default fallback
        return 300.0  # Average estimate
    
    def analyze_failure_patterns(self, all_results):
        """Analyze patterns in failed cases across models"""
        
        print("\n=== FAILURE PATTERN ANALYSIS ===")
        
        # Collect all failed cases across models
        all_failures = []
        for model_name, result in all_results.items():
            if result.get("status") == "SUCCESS":
                for failure in result["failed_cases"]:
                    failure['model'] = model_name
                    all_failures.append(failure)
        
        if not all_failures:
            print("🎉 No failures to analyze!")
            return
        
        # Group by characteristics
        failure_groups = {
            'by_days': defaultdict(list),
            'by_miles': defaultdict(list), 
            'by_receipts': defaultdict(list),
            'by_efficiency': defaultdict(list)
        }
        
        for failure in all_failures:
            days = failure['days']
            miles = failure['miles']
            receipts = failure['receipts']
            miles_per_day = miles / max(days, 1)
            
            # Group by trip length
            if days == 1:
                failure_groups['by_days']['1_day'].append(failure)
            elif days == 5:
                failure_groups['by_days']['5_day'].append(failure)
            elif days >= 7:
                failure_groups['by_days']['long_trip'].append(failure)
            
            # Group by efficiency
            if 180 <= miles_per_day <= 220:
                failure_groups['by_efficiency']['optimal'].append(failure)
            elif miles_per_day > 250:
                failure_groups['by_efficiency']['high'].append(failure)
            elif miles_per_day < 100:
                failure_groups['by_efficiency']['low'].append(failure)
            
            # Group by receipt amounts
            if receipts < 50:
                failure_groups['by_receipts']['very_low'].append(failure)
            elif receipts > 800:
                failure_groups['by_receipts']['very_high'].append(failure)
        
        # Report patterns
        for category, groups in failure_groups.items():
            if groups:
                print(f"\n{category.upper()} FAILURE PATTERNS:")
                for group_name, failures in groups.items():
                    if failures:
                        avg_error = sum(f['error'] for f in failures) / len(failures)
                        print(f"  {group_name}: {len(failures)} failures, avg error: ${avg_error:.2f}")
                        
                        # Show example
                        example = failures[0]
                        print(f"    Example: {example['days']}d, {example['miles']}mi, ${example['receipts']:.2f}")
                        print(f"             Expected: ${example['expected']:.2f}, Got: ${example['predicted']:.2f}")
    
    def create_coverage_matrix(self, all_results, subset_size=50):
        """Create coverage matrix showing which cases each model solves"""
        
        models = [name for name in all_results.keys() if all_results[name].get("status") == "SUCCESS"]
        
        if not models:
            print("No successful models for coverage matrix")
            return
        
        print(f"\n=== COVERAGE MATRIX (First {min(20, subset_size)} cases) ===")
        print(f"{'Model':<25} {'Cases (✓=perfect, ✗=failed)'}")
        print("-" * 70)
        
        for model_name in models:
            result = all_results[model_name]
            perfect_cases = set(result["perfect_cases"])
            
            coverage_str = ""
            for i in range(min(20, subset_size)):
                coverage_str += "✓" if i in perfect_cases else "✗"
                if (i + 1) % 5 == 0:
                    coverage_str += " "
            
            perfect_count = result["perfect_count"]
            total_count = result["total_cases"]
            percentage = (perfect_count / total_count) * 100 if total_count > 0 else 0
            
            print(f"{model_name:<25} {coverage_str} ({perfect_count}/{total_count} = {percentage:.1f}%)")
    
    def run_comprehensive_diagnostic(self):
        """Run comprehensive diagnostic testing"""
        
        print("=== COMPREHENSIVE MINIZINC DIAGNOSTIC SEARCH ===")
        print("Creating 11 plausible models based on interview analysis...")
        
        models = self.create_all_interview_models()
        
        print(f"Testing {len(models)} models with individual case tracking...")
        print("Using progressive subset sizes: 20 → 50 → 100 → full dataset")
        
        # Stage 1: Quick test on 20 cases
        print("\n🔍 STAGE 1: Quick test (20 cases)")
        print("=" * 50)
        
        stage1_results = {}
        promising_models = []
        
        for model_name, model_file in models:
            print(f"Testing {model_name}...", end=" ")
            result = self.test_model_with_case_tracking(model_name, model_file, subset_size=20)
            stage1_results[model_name] = result
            
            if result["status"] == "SUCCESS":
                perfect_count = result["perfect_count"]
                total_count = result["total_cases"]
                percentage = (perfect_count / total_count) * 100
                print(f"✅ {perfect_count}/{total_count} perfect ({percentage:.1f}%)")
                
                if perfect_count >= 15:  # 75% or better
                    promising_models.append((model_name, model_file))
            else:
                print(f"❌ {result['status']}")
        
        # Show coverage matrix for stage 1
        self.create_coverage_matrix(stage1_results, 20)
        
        # Analyze failure patterns
        self.analyze_failure_patterns(stage1_results)
        
        # Stage 2: Test promising models on larger set
        if promising_models:
            print(f"\n🎯 STAGE 2: Scaling promising models (50 cases)")
            print("=" * 50)
            
            stage2_results = {}
            for model_name, model_file in promising_models:
                print(f"Scaling {model_name}...", end=" ")
                result = self.test_model_with_case_tracking(model_name, model_file, subset_size=50)
                stage2_results[model_name] = result
                
                if result["status"] == "SUCCESS":
                    perfect_count = result["perfect_count"]
                    total_count = result["total_cases"]
                    percentage = (perfect_count / total_count) * 100
                    print(f"✅ {perfect_count}/{total_count} perfect ({percentage:.1f}%)")
                    
                    if perfect_count == total_count:
                        print(f"  🎉 PERFECT MATCH! Testing on full dataset...")
                        # Test on full dataset
                        full_result = self.test_model_with_case_tracking(model_name, model_file, subset_size=1000)
                        if full_result["status"] == "SUCCESS" and full_result["perfect_count"] == 1000:
                            print(f"  🏆 CHALLENGE SOLVED! {model_name} works on all 1000 cases!")
                            return model_name, full_result
                else:
                    print(f"❌ {result['status']}")
            
            # Show stage 2 coverage matrix
            self.create_coverage_matrix(stage2_results, 50)
            
        else:
            print("\n❌ No promising models found in stage 1")
            print("Recommendations:")
            print("- Relax error tolerance from 0.5 to 1.0 or 2.0")
            print("- Add more model variants")
            print("- Check for systematic calculation errors")
        
        return None, stage1_results

def main():
    """Main execution"""
    
    search = DiagnosticMiniZincSearch()
    winner, results = search.run_comprehensive_diagnostic()
    
    if winner:
        print(f"\n🏆 FINAL RESULT: {winner} solved the challenge!")
    else:
        print(f"\n🔍 ANALYSIS COMPLETE")
        print("Use failure patterns to guide next iteration of models")

if __name__ == "__main__":
    main()