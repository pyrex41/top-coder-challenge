#!/usr/bin/env python3
"""
Advanced MiniZinc Models for Reimbursement System
Based on previous analysis showing decision tree structure and special rules
"""

from pathlib import Path

def create_decision_tree_model():
    """Create a decision tree based model matching our previous findings"""
    
    model_str = """
% Decision Tree Model - Based on previous analysis
% Primary split at receipts <= 828, then days and miles
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Key thresholds discovered in previous analysis
float: receipts_major_split = 828.0;
float: days_threshold = 4.5;
float: miles_threshold_1 = 583.0;
float: miles_threshold_2 = 624.0;
float: receipts_threshold_2 = 563.0;

% Discoverable leaf node values
var 50.0..200.0: low_receipt_low_day_value;
var 100.0..300.0: low_receipt_high_day_value;
var 200.0..500.0: high_receipt_low_miles_value;
var 300.0..600.0: high_receipt_high_miles_value;

% Fine-tuning parameters
var 0.0..1.0: receipt_factor;
var 0.0..0.5: mile_factor;
var 0.0..100.0: day_base;

% Calculate reimbursement using decision tree logic
function var float: calc_reimbursement(int: i) =
    if receipts[i] <= receipts_major_split then
        % Low receipt branch
        if days[i] <= days_threshold then
            low_receipt_low_day_value + receipts[i] * receipt_factor
        else
            low_receipt_high_day_value + receipts[i] * receipt_factor + 
            miles[i] * mile_factor
        endif
    else
        % High receipt branch
        if miles[i] <= miles_threshold_1 then
            high_receipt_low_miles_value + receipts[i] * receipt_factor
        else
            high_receipt_high_miles_value + receipts[i] * receipt_factor +
            days[i] * day_base
        endif
    endif;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 1.0
);

solve satisfy;

output [
    "=== DECISION TREE MODEL SUCCESS ===\\n",
    "Major split at receipts <= ", show(receipts_major_split), "\\n",
    "Low receipt, low days: $", show_float(6, 2, low_receipt_low_day_value), "\\n",
    "Low receipt, high days: $", show_float(6, 2, low_receipt_high_day_value), "\\n",
    "High receipt, low miles: $", show_float(6, 2, high_receipt_low_miles_value), "\\n",
    "High receipt, high miles: $", show_float(6, 2, high_receipt_high_miles_value), "\\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "\\n"
];
"""
    
    Path("models/combinations").mkdir(exist_ok=True)
    with open("models/combinations/decision_tree.mzn", "w") as f:
        f.write(model_str)
    
    return "models/combinations/decision_tree.mzn"

def create_penalty_bonus_model():
    """Create model with .49/.99 penalties and special bonuses"""
    
    model_str = """
% Model with Penalty/Bonus System
% Including .49/.99 cent penalties discovered in analysis
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Core parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.7: mile_rate;
var 0.5..0.9: receipt_rate;

% Penalty/bonus parameters
var bool: has_cent_penalties;
var 0.0..1.0: penalty_amount;
var bool: has_efficiency_bonus;
var 0.0..50.0: efficiency_bonus;

% Special case parameters
var 0.0..100.0: vacation_penalty_threshold_miles;
var 0.0..100.0: vacation_penalty_threshold_receipts;
var 0.0..200.0: vacation_penalty_amount;

% Calculate base reimbursement
function var float: calc_base(int: i) = 
    days[i] * base_per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate;

% Apply penalties and bonuses
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = calc_base(i);
        
        % Vacation penalty for 1-day trips with high miles + receipts
        var float: vacation_penalty = 
            if days[i] == 1 /\ miles[i] > vacation_penalty_threshold_miles /\ 
               receipts[i] > vacation_penalty_threshold_receipts then
                vacation_penalty_amount
            else 0.0 endif;
        
        % Efficiency bonus
        var float: eff_bonus = 
            if has_efficiency_bonus /\ miles[i]/days[i] >= 180 /\ 
               miles[i]/days[i] <= 220 then
                efficiency_bonus
            else 0.0 endif;
        
        var float: subtotal = base - vacation_penalty + eff_bonus;
        
        % .49/.99 cent penalties
        var float: final_amount = 
            if has_cent_penalties then
                let {
                    int: cents = int(subtotal * 100) mod 100;
                } in 
                if cents == 49 \/ cents == 99 then
                    subtotal + penalty_amount
                else subtotal endif
            else subtotal endif;
            
    } in final_amount;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.5
);

solve satisfy;

output [
    "=== PENALTY/BONUS MODEL SUCCESS ===\\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\\n",
    "Has cent penalties: ", show(has_cent_penalties), "\\n",
    "Vacation penalty threshold: ", show_float(6, 0, vacation_penalty_threshold_miles), " mi, $", show_float(6, 0, vacation_penalty_threshold_receipts), "\\n"
];
"""
    
    with open("models/combinations/penalty_bonus.mzn", "w") as f:
        f.write(model_str)
    
    return "models/combinations/penalty_bonus.mzn"

def create_receipt_driven_model():
    """Create receipt-driven model (67% importance from analysis)"""
    
    model_str = """
% Receipt-Driven Model - Receipts are 67% of importance
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Primary receipt processing (most important)
var 10.0..50.0: receipt_threshold_1;
var 400.0..800.0: receipt_threshold_2;
var 1000.0..1500.0: receipt_threshold_3;

var 0.1..0.6: receipt_rate_1;  % Low receipts penalty
var 0.6..1.0: receipt_rate_2;  % Normal receipts
var 0.2..0.6: receipt_rate_3;  % High receipts diminishing

% Secondary factors (20% days, 12% miles)
var 80.0..120.0: day_base;
var 0.0..0.5: day_penalty_rate;  % Penalty for longer trips
var 0.2..0.6: mile_rate;

% Logical constraints
constraint receipt_threshold_1 < receipt_threshold_2;
constraint receipt_threshold_2 < receipt_threshold_3;
constraint receipt_rate_2 >= receipt_rate_1;

% Calculate reimbursement - receipt driven
function var float: calc_reimbursement(int: i) =
    let {
        % Primary: Receipt processing (67% importance)
        var float: receipt_component = 
            if receipts[i] <= receipt_threshold_1 then
                receipts[i] * receipt_rate_1
            elseif receipts[i] <= receipt_threshold_2 then
                receipt_threshold_1 * receipt_rate_1 +
                (receipts[i] - receipt_threshold_1) * receipt_rate_2
            else
                receipt_threshold_1 * receipt_rate_1 +
                (receipt_threshold_2 - receipt_threshold_1) * receipt_rate_2 +
                (receipts[i] - receipt_threshold_2) * receipt_rate_3
            endif;
        
        % Secondary: Day factor (20% importance) - penalty for long trips
        var float: day_component = day_base - (days[i] - 1) * day_penalty_rate;
        
        % Tertiary: Mile factor (12% importance) 
        var float: mile_component = miles[i] * mile_rate;
            
    } in receipt_component + day_component + mile_component;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.2
);

solve satisfy;

output [
    "=== RECEIPT-DRIVEN MODEL SUCCESS ===\\n",
    "Receipt tiers: $0-", show_float(6, 0, receipt_threshold_1), " @ ", show_float(6, 3, receipt_rate_1), "x\\n",
    "              $", show_float(6, 0, receipt_threshold_1), "-", show_float(6, 0, receipt_threshold_2), " @ ", show_float(6, 3, receipt_rate_2), "x\\n",
    "              $", show_float(6, 0, receipt_threshold_2), "+ @ ", show_float(6, 3, receipt_rate_3), "x\\n",
    "Day base: $", show_float(6, 2, day_base), " - $", show_float(6, 2, day_penalty_rate), "/extra day\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\\n"
];
"""
    
    with open("models/combinations/receipt_driven.mzn", "w") as f:
        f.write(model_str)
    
    return "models/combinations/receipt_driven.mzn"

def create_piecewise_function_model():
    """Create model with multiple breakpoints and piecewise functions"""
    
    model_str = """
% Piecewise Function Model - Multiple breakpoints
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Multiple breakpoints for days (from analysis: 1.5, 2.5, 4.5, 8.5, 10.5)
array[1..5] of float: day_breaks = [1.5, 2.5, 4.5, 8.5, 10.5];
array[1..6] of var 50.0..150.0: day_values;

% Multiple breakpoints for miles (from analysis: 263, 583, 621, 624, 833)
array[1..5] of float: mile_breaks = [263, 583, 621, 624, 833];
array[1..6] of var 0.1..0.8: mile_rates;

% Multiple breakpoints for receipts (from analysis: 491, 562, 563, 567, 828, 1236)
array[1..6] of float: receipt_breaks = [491, 562, 563, 567, 828, 1236];
array[1..7] of var 0.1..1.0: receipt_rates;

% Piecewise function for days
function var float: day_component(int: d) =
    if d <= day_breaks[1] then day_values[1]
    elseif d <= day_breaks[2] then day_values[2]
    elseif d <= day_breaks[3] then day_values[3]
    elseif d <= day_breaks[4] then day_values[4]
    elseif d <= day_breaks[5] then day_values[5]
    else day_values[6] endif;

% Piecewise function for miles
function var float: mile_component(int: m) =
    if m <= mile_breaks[1] then m * mile_rates[1]
    elseif m <= mile_breaks[2] then 
        mile_breaks[1] * mile_rates[1] + (m - mile_breaks[1]) * mile_rates[2]
    elseif m <= mile_breaks[3] then
        mile_breaks[1] * mile_rates[1] + (mile_breaks[2] - mile_breaks[1]) * mile_rates[2] +
        (m - mile_breaks[2]) * mile_rates[3]
    % ... continue pattern
    else
        mile_breaks[1] * mile_rates[1] + (mile_breaks[2] - mile_breaks[1]) * mile_rates[2] +
        (mile_breaks[3] - mile_breaks[2]) * mile_rates[3] + (mile_breaks[4] - mile_breaks[3]) * mile_rates[4] +
        (mile_breaks[5] - mile_breaks[4]) * mile_rates[5] + (m - mile_breaks[5]) * mile_rates[6]
    endif;

% Piecewise function for receipts
function var float: receipt_component(float: r) =
    if r <= receipt_breaks[1] then r * receipt_rates[1]
    elseif r <= receipt_breaks[2] then 
        receipt_breaks[1] * receipt_rates[1] + (r - receipt_breaks[1]) * receipt_rates[2]
    elseif r <= receipt_breaks[3] then
        receipt_breaks[1] * receipt_rates[1] + (receipt_breaks[2] - receipt_breaks[1]) * receipt_rates[2] +
        (r - receipt_breaks[2]) * receipt_rates[3]
    % ... continue for all breakpoints
    else
        receipt_breaks[1] * receipt_rates[1] + (receipt_breaks[2] - receipt_breaks[1]) * receipt_rates[2] +
        (receipt_breaks[3] - receipt_breaks[2]) * receipt_rates[3] + (receipt_breaks[4] - receipt_breaks[3]) * receipt_rates[4] +
        (receipt_breaks[5] - receipt_breaks[4]) * receipt_rates[5] + (receipt_breaks[6] - receipt_breaks[5]) * receipt_rates[6] +
        (r - receipt_breaks[6]) * receipt_rates[7]
    endif;

% Calculate total reimbursement
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = day_component(days[i]) + mile_component(miles[i]) + receipt_component(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.1
);

solve satisfy;

output [
    "=== PIECEWISE FUNCTION MODEL SUCCESS ===\\n",
    "Day values: ", show(day_values), "\\n",
    "Mile rates: ", show(mile_rates), "\\n", 
    "Receipt rates: ", show(receipt_rates), "\\n"
];
"""
    
    with open("models/combinations/piecewise_function.mzn", "w") as f:
        f.write(model_str)
    
    return "models/combinations/piecewise_function.mzn"

def create_simple_exact_model():
    """Create a very simple model for exact parameter discovery"""
    
    model_str = """
% Simple Exact Model - Minimal parameters for exact matching
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Minimal parameter set
var 99.0..101.0: per_diem;
var 0.55..0.65: mile_rate;
var 0.70..0.80: receipt_rate;

% Simple calculation
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

% Very tight constraint for exact match
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 5.0
);

solve satisfy;

output [
    "Per diem: $", show_float(6, 2, per_diem), "\\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "\\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "\\n"
];
"""
    
    with open("models/simple_exact.mzn", "w") as f:
        f.write(model_str)
    
    return "models/simple_exact.mzn"

def main():
    """Create all advanced models"""
    
    Path("models").mkdir(exist_ok=True)
    Path("models/combinations").mkdir(exist_ok=True)
    
    models = [
        create_simple_exact_model(),
        create_decision_tree_model(),
        create_penalty_bonus_model(), 
        create_receipt_driven_model(),
        create_piecewise_function_model()
    ]
    
    print("Created advanced MiniZinc models:")
    for model in models:
        print(f"  - {model}")
    
    return models

if __name__ == "__main__":
    main()