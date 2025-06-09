
% Model 11: Base + 5-Day Bonus Only (Marcus Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;  % 0-100 miles
var 0.35..0.55: rate2;  % 100-500 miles  
var 0.15..0.35: rate3;  % 500+ miles
var 0.60..0.80: receipt_rate;
var 0.05..0.15: five_day_bonus_rate;  % 5-day bonus

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var float: bonus = if days[i] == 5 then base * five_day_bonus_rate else 0.0 endif;
    } in base + bonus
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 11 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Base: $", show_float(6, 2, base_per_diem), ", 5-day bonus: ", show_float(6, 3, five_day_bonus_rate), "x\n"
];
