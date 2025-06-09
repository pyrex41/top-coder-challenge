
% Model 3: Variant 3-Tier (75-400 breakpoints)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-75 miles
var 0.35..0.55: rate2;  % 75-400 miles  
var 0.15..0.35: rate3;  % 400+ miles
var 0.60..0.80: receipt_rate;

function var float: calc_mileage(int: m) =
    if m <= 75 then m * rate1
    elseif m <= 400 then 75 * rate1 + (m - 75) * rate2
    else 75 * rate1 + 325 * rate2 + (m - 400) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 3 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Variant breakpoints: 0-75-400-∞ @ $", show_float(6, 3, rate1), "/$", show_float(6, 3, rate2), "/$", show_float(6, 3, rate3), "\n"
];
