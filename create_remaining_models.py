#!/usr/bin/env python3
"""
Create remaining interview-based models to complete the 20 plausible structures
"""

from pathlib import Path

def create_remaining_models():
    """Create the remaining models to complete the 20 structure analysis"""
    
    Path("diagnostic_models/mileage_structures").mkdir(exist_ok=True)
    Path("diagnostic_models/combinations").mkdir(exist_ok=True)
    Path("diagnostic_models/edge_cases").mkdir(exist_ok=True)
    
    models = []
    
    # Model 3: Variant 3-Tier Breakpoints (75-400)
    model3 = """
% Model 3: Variant 3-Tier (75-400 breakpoints)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-75 miles
var 0.35..0.55: rate2;  % 75-400 miles  
var 0.15..0.35: rate3;  % 400+ miles
var 0.60..0.80: receipt_rate;

function var float: calc_mileage(int: m) =
    if m <= 75 then m * rate1
    elseif m <= 400 then 75 * rate1 + (m - 75) * rate2
    else 75 * rate1 + 325 * rate2 + (m - 400) * rate3 endif;

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
    "MODEL 3 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Variant breakpoints: 0-75-400-∞ @ $", show_float(6, 3, rate1), "/$", show_float(6, 3, rate2), "/$", show_float(6, 3, rate3), "\\n"
];
"""
    
    with open("diagnostic_models/mileage_structures/model3_variant_3tier.mzn", "w") as f:
        f.write(model3)
    models.append("Model 3: Variant 3-Tier")
    
    # Model 7: Percentage with Cap (80% up to $1000)
    model7 = """
% Model 7: Percentage with Cap (80% up to $1000 max)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.45..0.65: mile_rate;
var 1000.0..1000.0: receipt_cap;  % Fixed at $1000
var 0.75..0.85: receipt_percentage;  % Around 80%

function var float: calc_receipts(float: r) =
    min(r * receipt_percentage, receipt_cap);

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
    "MODEL 7 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Receipt: ", show_float(6, 3, receipt_percentage), "x capped at $", show_float(6, 0, receipt_cap), "\\n"
];
"""
    
    with open("diagnostic_models/receipt_structures/model7_percentage_cap.mzn", "w") as f:
        f.write(model7)
    models.append("Model 7: Percentage with Cap")
    
    # Model 13: Base + Long Trip Penalty Only
    model13 = """
% Model 13: Base + Long Trip Penalty Only
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
var 20.0..40.0: long_trip_penalty;  % Per day penalty

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var float: penalty = if days[i] > 7 then (days[i] - 7) * long_trip_penalty else 0.0 endif;
    } in base - penalty
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 13 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Long trip penalty: $", show_float(6, 2, long_trip_penalty), "/day after 7 days\\n"
];
"""
    
    with open("diagnostic_models/combinations/model13_long_trip_penalty.mzn", "w") as f:
        f.write(model13)
    models.append("Model 13: Long Trip Penalty")
    
    # Model 14: All Interview Bonuses Combined
    model14 = """
% Model 14: All Interview Bonuses Combined (Kevin's Complex Model)
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

% All the special rules
var 0.05..0.15: five_day_bonus_rate;
var 30.0..70.0: efficiency_bonus;
var 20.0..40.0: long_trip_penalty;
var 10.0..30.0: small_trip_penalty;

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        
        % 5-day bonus
        var float: five_bonus = if days[i] == 5 then base * five_day_bonus_rate else 0.0 endif;
        
        % Efficiency bonus
        var float: miles_per_day = miles[i] / max(days[i], 1);
        var float: eff_bonus = if miles_per_day >= 180 /\ miles_per_day <= 220 then efficiency_bonus else 0.0 endif;
        
        % Long trip penalty
        var float: long_penalty = if days[i] > 7 then (days[i] - 7) * long_trip_penalty else 0.0 endif;
        
        % Small trip penalty
        var float: small_penalty = if days[i] == 1 /\ miles[i] < 50 then small_trip_penalty else 0.0 endif;
        
    } in base + five_bonus + eff_bonus - long_penalty - small_penalty
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 14 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "All bonuses: 5-day=", show_float(6, 3, five_day_bonus_rate), "x, eff=$", show_float(6, 2, efficiency_bonus), 
    ", penalties=$", show_float(6, 2, long_trip_penalty), "/$", show_float(6, 2, small_trip_penalty), "\\n"
];
"""
    
    with open("diagnostic_models/combinations/model14_all_bonuses.mzn", "w") as f:
        f.write(model14)
    models.append("Model 14: All Bonuses")
    
    # Model 15: Base + Rounding Bug
    model15 = """
% Model 15: Base + Rounding Bug (.49/.99 adjustment)
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

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var int: cents = int(base * 100) mod 100;
        var float: rounding_adj = if cents == 49 \/ cents == 99 then 0.01 else 0.0 endif;
    } in base + rounding_adj
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 15 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "With rounding bug: .49/.99 → +$0.01\\n"
];
"""
    
    with open("diagnostic_models/combinations/model15_rounding_bug.mzn", "w") as f:
        f.write(model15)
    models.append("Model 15: Rounding Bug")
    
    # Model 20: Logarithmic/Non-Linear
    model20 = """
% Model 20: Logarithmic/Non-Linear (for completeness)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_base;
var 40.0..60.0: mile_log_factor;
var 80.0..120.0: receipt_sqrt_factor;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * day_base + 
                   mile_log_factor * ln(miles[i] + 1) + 
                   receipt_sqrt_factor * sqrt(receipts[i])
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 2.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 20 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\\n",
    "Non-linear: ", show_float(6, 2, day_base), "*days + ", show_float(6, 2, mile_log_factor), 
    "*ln(miles+1) + ", show_float(6, 2, receipt_sqrt_factor), "*sqrt(receipts)\\n"
];
"""
    
    with open("diagnostic_models/edge_cases/model20_nonlinear.mzn", "w") as f:
        f.write(model20)
    models.append("Model 20: Non-Linear")
    
    return models

def main():
    """Create all remaining models"""
    models = create_remaining_models()
    print("Created additional models:")
    for model in models:
        print(f"  - {model}")
    print(f"\nTotal: {len(models)} additional models")
    print("Combined with diagnostic_minizinc_comprehensive.py = 11 total models")

if __name__ == "__main__":
    main()