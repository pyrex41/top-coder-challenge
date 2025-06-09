
% Model 19: Ultra-Simple Linear
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: per_diem;
var 0.40..0.60: mile_rate;
var 0.65..0.75: receipt_rate;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 19 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Per diem: $", show_float(6, 2, per_diem), ", Mile: $", show_float(6, 3, mile_rate), 
    ", Receipt: ", show_float(6, 3, receipt_rate), "x\n"
];
