
% 2-Tier Mileage Model - Realistic
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

var 80.0..120.0: per_diem;
var 50.0..200.0: tier1_end;
var 0.3..1.0: rate1;
var 0.1..0.8: rate2;
var 0.5..1.5: receipt_rate;

constraint rate1 >= rate2;

function var float: calc_mileage(int: m) =
    if m <= tier1_end then
        m * rate1
    else
        tier1_end * rate1 + (m - tier1_end) * rate2
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = days[i] * per_diem + calc_mileage(miles[i]) + receipts[i] * receipt_rate
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 100.0
);

solve satisfy;

output [
    "=== 2-TIER MILEAGE SUCCESS ===\n",
    "Per diem: $", show_float(8, 4, per_diem), "\n",
    "Tier 1 (0-", show_float(6, 0, tier1_end), " mi): $", show_float(8, 5, rate1), "/mi\n",
    "Tier 2 (", show_float(6, 0, tier1_end), "+ mi): $", show_float(8, 5, rate2), "/mi\n",
    "Receipt rate: ", show_float(8, 5, receipt_rate), "x\n"
];
