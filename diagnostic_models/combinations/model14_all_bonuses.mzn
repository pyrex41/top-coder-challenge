
% Model 14: All Interview Bonuses Combined (Kevin's Complex Model)
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

% All the special rules
var 0.05..0.15: five_day_bonus_rate;
var 30.0..70.0: efficiency_bonus;
var 20.0..40.0: long_trip_penalty;
var 10.0..30.0: small_trip_penalty;

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        
        % 5-day bonus
        var float: five_bonus = if days[i] == 5 then base * five_day_bonus_rate else 0.0 endif;
        
        % Efficiency bonus
        var float: miles_per_day = miles[i] / max(days[i], 1);
        var float: eff_bonus = if miles_per_day >= 180 /\ miles_per_day <= 220 then efficiency_bonus else 0.0 endif;
        
        % Long trip penalty
        var float: long_penalty = if days[i] > 7 then (days[i] - 7) * long_trip_penalty else 0.0 endif;
        
        % Small trip penalty
        var float: small_penalty = if days[i] == 1 /\ miles[i] < 50 then small_trip_penalty else 0.0 endif;
        
    } in base + five_bonus + eff_bonus - long_penalty - small_penalty
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 14 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "All bonuses: 5-day=", show_float(6, 3, five_day_bonus_rate), "x, eff=$", show_float(6, 2, efficiency_bonus), 
    ", penalties=$", show_float(6, 2, long_trip_penalty), "/$", show_float(6, 2, small_trip_penalty), "\n"
];
