
% Very simple test model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Simple parameters
var 95.0..105.0: per_diem;
var 0.40..0.70: mile_rate;
var 0.60..0.90: receipt_rate;

% Calculate
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

% Allow large error for testing
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 50.0
);

solve satisfy;

output [
    "Per diem: ", show(per_diem), "\n",
    "Mile rate: ", show(mile_rate), "\n", 
    "Receipt rate: ", show(receipt_rate), "\n"
];
