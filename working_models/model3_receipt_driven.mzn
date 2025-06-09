
% Receipt-Driven Model (67% importance)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_base;
var 0.0..0.5: mile_rate;
var 20.0..80.0: receipt_threshold;
var 0.2..0.6: receipt_low_rate;
var 0.6..1.0: receipt_high_rate;

function var float: calc_receipts(float: r) =
    if r <= receipt_threshold then
        r * receipt_low_rate
    else
        receipt_threshold * receipt_low_rate + (r - receipt_threshold) * receipt_high_rate
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = day_base + days[i] * 20.0 + miles[i] * mile_rate + calc_receipts(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 10.0
);

solve satisfy;

output [
    "RECEIPT-DRIVEN SUCCESS\n",
    "Day base: $", show_float(6, 2, day_base), "\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\n",
    "Receipt threshold: $", show_float(6, 0, receipt_threshold), "\n",
    "Low receipt rate: ", show_float(6, 3, receipt_low_rate), "x\n",
    "High receipt rate: ", show_float(6, 3, receipt_high_rate), "x\n"
];
