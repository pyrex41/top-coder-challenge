
% Receipt-Driven Model with Thresholds
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: day_component;
var 0.1..1.0: mile_rate;

% Receipt processing with discovered threshold around 828
var 500.0..1000.0: receipt_threshold;
var 0.3..0.8: receipt_low_rate;
var 0.6..1.2: receipt_high_rate;

function var float: calc_receipts(float: r) =
    if r <= receipt_threshold then
        r * receipt_low_rate
    else
        receipt_threshold * receipt_low_rate + (r - receipt_threshold) * receipt_high_rate
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * day_component + miles[i] * mile_rate + calc_receipts(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 80.0
);

solve satisfy;

output [
    "=== RECEIPT-DRIVEN SUCCESS ===\n",
    "Day component: $", show_float(8, 4, day_component), "/day\n",
    "Mile rate: $", show_float(8, 5, mile_rate), "/mi\n",
    "Receipt threshold: $", show_float(8, 2, receipt_threshold), "\n",
    "Low receipt rate: ", show_float(8, 5, receipt_low_rate), "x\n",
    "High receipt rate: ", show_float(8, 5, receipt_high_rate), "x\n"
];
