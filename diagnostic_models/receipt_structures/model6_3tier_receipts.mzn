
% Model 6: 3-Tier Receipts (Lisa Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.45..0.65: mile_rate;

var 0.20..0.40: receipt_low_rate;   % <$50 penalty
var 0.70..0.85: receipt_med_rate;   % $50-800 normal
var 0.15..0.35: receipt_high_rate;  % $800+ diminishing

function var float: calc_receipts(float: r) =
    if r < 50 then r * receipt_low_rate
    elseif r <= 800 then 50 * receipt_low_rate + (r - 50) * receipt_med_rate
    else 50 * receipt_low_rate + 750 * receipt_med_rate + (r - 800) * receipt_high_rate endif;

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
    "MODEL 6 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Mile: $", show_float(6, 3, mile_rate), 
    ", Receipt rates: ", show_float(6, 3, receipt_low_rate), "/", show_float(6, 3, receipt_med_rate), 
    "/", show_float(6, 3, receipt_high_rate), "\n"
];
