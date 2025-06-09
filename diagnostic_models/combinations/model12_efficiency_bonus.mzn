
% Model 12: Base + Efficiency Bonus Only (Kevin Interview)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 95.0..105.0: base_per_diem;
var 0.50..0.70: rate1;
var 0.35..0.55: rate2;
var 0.15..0.35: rate3;
var 0.60..0.80: receipt_rate;
var 30.0..70.0: efficiency_bonus;  % Fixed efficiency bonus

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var float: miles_per_day = miles[i] / max(days[i], 1);
        var float: bonus = if miles_per_day >= 180.0 /\ miles_per_day <= 220.0 then efficiency_bonus else 0.0 endif;
    } in base + bonus
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 12 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "Base: $", show_float(6, 2, base_per_diem), ", Efficiency bonus: $", show_float(6, 2, efficiency_bonus), "\n"
];
