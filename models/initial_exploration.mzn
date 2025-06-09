
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
    "=== INITIAL EXPLORATION RESULTS ===\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Mile rate: $", show_float(6, 4, simple_mile_rate), "/mile\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "x\n",
    "Total error: $", show_float(8, 2, total_error), "\n",
    "Max error: $", show_float(6, 2, max_error), "\n",
    "Average error: $", show_float(6, 2, total_error / n), "\n"
];
