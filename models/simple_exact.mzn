
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
    "Per diem: $", show_float(6, 2, per_diem), "\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "\n"
];
