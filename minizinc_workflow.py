#!/usr/bin/env python3
"""
MiniZinc Systematic Rule Discovery for Reimbursement System
Following the constraint satisfaction approach for exact rule matching
"""

import json
import minizinc
import asyncio
from pathlib import Path
import time

class MiniZincRuleDiscovery:
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
        Path("models").mkdir(exist_ok=True)
        Path("models/mileage_structures").mkdir(exist_ok=True)
        Path("models/receipt_structures").mkdir(exist_ok=True)
        Path("models/combinations").mkdir(exist_ok=True)
        Path("results").mkdir(exist_ok=True)
    
    def create_initial_exploration_model(self):
        """Step 1: Create initial simple exploration model"""
        
        model_str = """
% Initial exploration to understand the rule space
include "globals.mzn";

% Use first 20 cases for quick exploration
int: n = 20;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Start with simple linear model to establish bounds
var 90.0..110.0: base_per_diem;
var 0.3..0.8: simple_mile_rate;
var 0.0..1.0: receipt_factor;

% Calculate with simple formula
array[1..n] of var float: predicted;
constraint forall(i in 1..n)(
    predicted[i] = days[i] * base_per_diem + 
                   miles[i] * simple_mile_rate + 
                   receipts[i] * receipt_factor
);

% Track errors
array[1..n] of var float: errors;
constraint forall(i in 1..n)(
    errors[i] = abs(predicted[i] - expected[i])
);

var float: total_error = sum(i in 1..n)(errors[i]);
var float: max_error = max(i in 1..n)(errors[i]);

solve minimize total_error;

output [
    "=== INITIAL EXPLORATION RESULTS ===\\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\\n",
    "Mile rate: $", show_float(6, 4, simple_mile_rate), "/mile\\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "x\\n",
    "Total error: $", show_float(8, 2, total_error), "\\n",
    "Max error: $", show_float(6, 2, max_error), "\\n",
    "Average error: $", show_float(6, 2, total_error / n), "\\n"
];
"""
        
        with open("models/initial_exploration.mzn", "w") as f:
            f.write(model_str)
        
        return model_str
    
    def create_2tier_mileage_model(self, tier1_end=100, rate1=0.58, rate2=0.35):
        """Create 2-tier mileage model with specific parameters"""
        
        model_str = f"""
% 2-Tier Mileage Model: 0-{tier1_end} @ ${rate1}, {tier1_end}+ @ ${rate2}
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Fixed structure parameters
float: tier1_end = {tier1_end};
float: rate1 = {rate1};
float: rate2 = {rate2};

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.0..1.0: receipt_rate;
var 0.0..100.0: bonus_amount;

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {{
        var float: base = days[i] * base_per_diem;
        
        var float: mileage = 
            if miles[i] <= tier1_end then
                miles[i] * rate1
            else
                tier1_end * rate1 + (miles[i] - tier1_end) * rate2
            endif;
        
        var float: receipt_reimb = receipts[i] * receipt_rate;
        
        var float: bonus = 
            if days[i] == 5 then bonus_amount else 0.0 endif;
            
    }} in base + mileage + receipt_reimb + bonus;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

% Allow small tolerance
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.5
);

solve satisfy;

output [
    "=== 2-TIER MILEAGE MODEL SUCCESS ===\\n",
    "Tier structure: 0-{tier1_end} @ ${rate1}, {tier1_end}+ @ ${rate2}\\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n",
    "5-day bonus: $", show_float(6, 2, bonus_amount), "\\n"
];
"""
        
        filename = f"models/mileage_structures/2tier_{tier1_end}_{rate1:.2f}_{rate2:.2f}.mzn"
        with open(filename, "w") as f:
            f.write(model_str)
        
        return filename, model_str
    
    def create_3tier_mileage_model(self, tier1_end=100, tier2_end=500):
        """Create 3-tier mileage model"""
        
        model_str = f"""
% 3-Tier Mileage Model: 0-{tier1_end}, {tier1_end}-{tier2_end}, {tier2_end}+
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Structure parameters
int: tier1_end = {tier1_end};
int: tier2_end = {tier2_end};

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.8: rate1;  % Tier 1 rate
var 0.2..0.6: rate2;  % Tier 2 rate  
var 0.1..0.4: rate3;  % Tier 3 rate
var 0.0..1.0: receipt_rate;

% Logical constraints
constraint rate1 >= rate2;  % Higher rate for shorter distances
constraint rate2 >= rate3;  % Decreasing rates

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {{
        var float: base = days[i] * base_per_diem;
        
        var float: mileage = 
            if miles[i] <= tier1_end then
                miles[i] * rate1
            elseif miles[i] <= tier2_end then
                tier1_end * rate1 + (miles[i] - tier1_end) * rate2
            else
                tier1_end * rate1 + (tier2_end - tier1_end) * rate2 + 
                (miles[i] - tier2_end) * rate3
            endif;
        
        var float: receipt_reimb = receipts[i] * receipt_rate;
            
    }} in base + mileage + receipt_reimb;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.1
);

solve satisfy;

output [
    "=== 3-TIER MILEAGE MODEL SUCCESS ===\\n",
    "Tiers: 0-{tier1_end} @ $", show_float(6, 3, rate1), "/mi\\n",
    "       {tier1_end}-{tier2_end} @ $", show_float(6, 3, rate2), "/mi\\n", 
    "       {tier2_end}+ @ $", show_float(6, 3, rate3), "/mi\\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n"
];
"""
        
        filename = f"models/mileage_structures/3tier_{tier1_end}_{tier2_end}.mzn"
        with open(filename, "w") as f:
            f.write(model_str)
        
        return filename, model_str
    
    def create_tiered_receipt_model(self):
        """Create model with tiered receipt processing"""
        
        model_str = """
% Tiered Receipt Processing Model
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.7: simple_mile_rate;

% Receipt tier parameters
var 20.0..80.0: receipt_low_threshold;
var 500.0..1200.0: receipt_high_threshold;
var 0.0..0.5: receipt_low_rate;     % Penalty rate for low receipts
var 0.5..1.0: receipt_medium_rate;  % Normal rate for medium receipts
var 0.2..0.6: receipt_high_rate;    % Diminishing returns for high receipts

% Logical constraints
constraint receipt_low_threshold < receipt_high_threshold;
constraint receipt_medium_rate >= receipt_low_rate;

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = days[i] * base_per_diem;
        var float: mileage = miles[i] * simple_mile_rate;
        
        var float: receipt_reimb = 
            if receipts[i] <= receipt_low_threshold then
                receipts[i] * receipt_low_rate
            elseif receipts[i] <= receipt_high_threshold then
                receipt_low_threshold * receipt_low_rate +
                (receipts[i] - receipt_low_threshold) * receipt_medium_rate
            else
                receipt_low_threshold * receipt_low_rate +
                (receipt_high_threshold - receipt_low_threshold) * receipt_medium_rate +
                (receipts[i] - receipt_high_threshold) * receipt_high_rate
            endif;
            
    } in base + mileage + receipt_reimb;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.1
);

solve satisfy;

output [
    "=== TIERED RECEIPT MODEL SUCCESS ===\\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\\n",
    "Mile rate: $", show_float(6, 3, simple_mile_rate), "/mi\\n",
    "Receipt tiers:\\n",
    "  0-$", show_float(6, 0, receipt_low_threshold), ": ", show_float(6, 3, receipt_low_rate), "x\\n",
    "  $", show_float(6, 0, receipt_low_threshold), "-$", show_float(6, 0, receipt_high_threshold), ": ", show_float(6, 3, receipt_medium_rate), "x\\n",
    "  $", show_float(6, 0, receipt_high_threshold), "+: ", show_float(6, 3, receipt_high_rate), "x\\n"
];
"""
        
        with open("models/receipt_structures/tiered_receipts.mzn", "w") as f:
            f.write(model_str)
        
        return model_str
    
    async def test_model_async(self, model_file, data_subset_size=50):
        """Test a single model asynchronously"""
        try:
            # Load the model
            model = minizinc.Model(model_file)
            
            # Use Gecode solver
            gecode = minizinc.Solver.lookup("gecode")
            instance = minizinc.Instance(gecode, model)
            
            # Set data (use subset for speed)
            subset = self.cases[:data_subset_size]
            instance["n"] = len(subset)
            instance["days"] = [c["input"]["trip_duration_days"] for c in subset]
            instance["miles"] = [c["input"]["miles_traveled"] for c in subset]
            instance["receipts"] = [c["input"]["total_receipts_amount"] for c in subset]
            instance["expected"] = [c["expected_output"] for c in subset]
            
            # Solve with timeout
            result = await instance.solve_async(timeout=60)
            
            if result.status == minizinc.Status.SATISFIED:
                return {"model": model_file, "status": "SUCCESS", "result": result}
            else:
                return {"model": model_file, "status": "NO_SOLUTION", "result": None}
                
        except Exception as e:
            return {"model": model_file, "status": "ERROR", "error": str(e)}
    
    def create_all_model_variants(self):
        """Create all plausible model variants to test"""
        models = []
        
        print("Creating model variants...")
        
        # 1. Initial exploration
        self.create_initial_exploration_model()
        models.append("models/initial_exploration.mzn")
        
        # 2. 2-tier mileage variants
        tier1_values = [75, 100, 125, 150]
        rate_combinations = [(0.58, 0.35), (0.55, 0.40), (0.60, 0.30)]
        
        for tier1 in tier1_values:
            for rate1, rate2 in rate_combinations:
                filename, _ = self.create_2tier_mileage_model(tier1, rate1, rate2)
                models.append(filename)
        
        # 3. 3-tier mileage variants  
        tier_combinations = [(100, 500), (75, 400), (125, 600), (100, 300)]
        
        for tier1, tier2 in tier_combinations:
            filename, _ = self.create_3tier_mileage_model(tier1, tier2)
            models.append(filename)
        
        # 4. Receipt processing variants
        self.create_tiered_receipt_model()
        models.append("models/receipt_structures/tiered_receipts.mzn")
        
        print(f"Created {len(models)} model variants")
        return models
    
    async def run_comprehensive_search(self):
        """Run comprehensive parallel search across all models"""
        
        models = self.create_all_model_variants()
        
        print(f"\nTesting {len(models)} models in parallel...")
        print("This may take a few minutes...\n")
        
        # Test all models in parallel
        tasks = [self.test_model_async(model) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_models = []
        for result in results:
            if isinstance(result, dict):
                if result["status"] == "SUCCESS":
                    successful_models.append(result)
                    print(f"✓ SUCCESS: {result['model']}")
                elif result["status"] == "NO_SOLUTION":
                    print(f"✗ No solution: {result['model']}")
                else:
                    print(f"⚠ Error in {result['model']}: {result.get('error', 'Unknown')}")
        
        return successful_models
    
    def validate_on_full_dataset(self, successful_models):
        """Validate successful models on the full 1000-case dataset"""
        
        print(f"\nValidating {len(successful_models)} successful models on full dataset...")
        
        # For now, just report the successful models
        # In practice, you'd test each on all 1000 cases
        for model_info in successful_models:
            print(f"\nSuccessful model: {model_info['model']}")
            if model_info['result'] and hasattr(model_info['result'], 'solution'):
                print("Parameters found - ready for full validation")

def main():
    """Main execution function"""
    
    print("=== MiniZinc Systematic Rule Discovery ===")
    print("Finding exact reimbursement system rules through constraint satisfaction")
    print()
    
    discovery = MiniZincRuleDiscovery()
    
    # Run the comprehensive search
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        successful_models = loop.run_until_complete(discovery.run_comprehensive_search())
        
        if successful_models:
            print(f"\n🎉 Found {len(successful_models)} working model(s)!")
            discovery.validate_on_full_dataset(successful_models)
        else:
            print("\n❌ No exact matches found. Need to expand search space or adjust constraints.")
            print("Try:")
            print("- Loosening error tolerance")
            print("- Adding more rule types")
            print("- Testing with larger parameter ranges")
        
    finally:
        loop.close()
    
    print("\n=== Search Complete ===")

if __name__ == "__main__":
    main()