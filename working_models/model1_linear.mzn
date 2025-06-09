
% Simple Linear Model
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: per_diem;
var 0.3..0.7: mile_rate;
var 0.5..0.9: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 20.0
);

solve satisfy;

output [
    "LINEAR MODEL SUCCESS\n",
    "Per diem: $", show_float(6, 2, per_diem), "\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\n"
];
