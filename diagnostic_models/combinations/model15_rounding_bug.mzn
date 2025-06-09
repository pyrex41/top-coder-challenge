
% Model 15: Base + Rounding Bug (.49/.99 adjustment)
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

function var float: calc_mileage(int: m) =
    if m <= 100 then m * rate1
    elseif m <= 500 then 100 * rate1 + (m - 100) * rate2
    else 100 * rate1 + 400 * rate2 + (m - 500) * rate3 endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = let {
        var float: base = days[i] * base_per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate;
        var int: cents = int(base * 100) mod 100;
        var float: rounding_adj = if cents == 49 \/ cents == 99 then 0.01 else 0.0 endif;
    } in base + rounding_adj
);

array[1..n] of var bool: is_perfect;
constraint forall(i in 1..n)(
    is_perfect[i] <-> (abs(calculated[i] - expected[i]) < 1.0)
);
var int: perfect_count = sum(is_perfect);

solve maximize perfect_count;

output [
    "MODEL 15 SUCCESS: ", show(perfect_count), "/", show(n), " cases perfect\n",
    "With rounding bug: .49/.99 → +$0.01\n"
];
