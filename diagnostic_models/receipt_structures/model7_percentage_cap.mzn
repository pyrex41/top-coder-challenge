
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
    "MODEL 7 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Receipt: ", show_float(6, 3, receipt_percentage), "x capped at $", show_float(6, 0, receipt_cap), "\n"
];
