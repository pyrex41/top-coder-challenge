
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
    "=== DECISION TREE MODEL SUCCESS ===\n",
    "Major split at receipts <= ", show(receipts_major_split), "\n",
    "Low receipt, low days: $", show_float(6, 2, low_receipt_low_day_value), "\n",
    "Low receipt, high days: $", show_float(6, 2, low_receipt_high_day_value), "\n",
    "High receipt, low miles: $", show_float(6, 2, high_receipt_low_miles_value), "\n",
    "High receipt, high miles: $", show_float(6, 2, high_receipt_high_miles_value), "\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "\n"
];
