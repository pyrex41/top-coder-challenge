
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
    "=== SIMPLE LINEAR SUCCESS ===\n",
    "Per diem: $", show_float(8, 4, per_diem), "\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\n"
];
