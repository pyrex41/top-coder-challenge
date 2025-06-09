
% Decision Tree Model (based on 828 split)
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

float: major_split = 828.0;
float: day_split = 4.5;
float: mile_split = 583.0;

var 50.0..200.0: base_low_receipt_low_day;
var 100.0..300.0: base_low_receipt_high_day;
var 200.0..500.0: base_high_receipt_low_mile;
var 300.0..600.0: base_high_receipt_high_mile;

var 0.0..1.0: receipt_factor;
var 0.0..0.5: mile_factor;
var 0.0..50.0: day_factor;

function var float: calc_reimbursement(int: i) =
    if receipts[i] <= major_split then
        if days[i] <= day_split then
            base_low_receipt_low_day + receipts[i] * receipt_factor
        else
            base_low_receipt_high_day + receipts[i] * receipt_factor + miles[i] * mile_factor
        endif
    else
        if miles[i] <= mile_split then
            base_high_receipt_low_mile + receipts[i] * receipt_factor
        else
            base_high_receipt_high_mile + receipts[i] * receipt_factor + days[i] * day_factor
        endif
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 5.0
);

solve satisfy;

output [
    "DECISION TREE SUCCESS\n",
    "Major split at receipts <= ", show(major_split), "\n",
    "Low receipt, low days base: $", show_float(6, 2, base_low_receipt_low_day), "\n",
    "Low receipt, high days base: $", show_float(6, 2, base_low_receipt_high_day), "\n",
    "High receipt, low miles base: $", show_float(6, 2, base_high_receipt_low_mile), "\n",
    "High receipt, high miles base: $", show_float(6, 2, base_high_receipt_high_mile), "\n",
    "Receipt factor: ", show_float(6, 3, receipt_factor), "\n"
];
