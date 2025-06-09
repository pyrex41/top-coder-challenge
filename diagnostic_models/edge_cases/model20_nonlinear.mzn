
% Model 20: Logarithmic/Non-Linear (for completeness)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_base;
var 40.0..60.0: mile_log_factor;
var 80.0..120.0: receipt_sqrt_factor;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * day_base + 
                   mile_log_factor * ln(miles[i] + 1) + 
                   receipt_sqrt_factor * sqrt(receipts[i])
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 2.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 20 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Non-linear: ", show_float(6, 2, day_base), "*days + ", show_float(6, 2, mile_log_factor), 
    "*ln(miles+1) + ", show_float(6, 2, receipt_sqrt_factor), "*sqrt(receipts)\n"
];
