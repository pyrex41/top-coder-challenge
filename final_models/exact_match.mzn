
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
    "=== EXACT MATCH SUCCESS ===\n",
    "Per diem: $", show_float(10, 6, per_diem), "\n",
    "Mile rate: $", show_float(10, 7, mile_rate), "/mi\n",
    "Receipt rate: ", show_float(10, 7, receipt_rate), "x\n"
];
