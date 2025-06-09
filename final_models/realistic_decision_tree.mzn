
% Decision Tree Model with Known Thresholds
int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Fixed thresholds from previous analysis
float: receipt_split = 828.0;
float: day_split = 4.5;
float: mile_split = 583.0;

% Discoverable base values for each leaf
var 50.0..250.0: leaf1_base;  % Low receipt, low days
var 100.0..350.0: leaf2_base; % Low receipt, high days
var 200.0..600.0: leaf3_base; % High receipt, low miles
var 300.0..700.0: leaf4_base; % High receipt, high miles

% Adjustable factors
var 0.0..1.5: receipt_factor;
var 0.0..1.0: mile_factor;
var 0.0..50.0: day_factor;

function var float: calc_reimbursement(int: i) =
    if receipts[i] <= receipt_split then
        if days[i] <= day_split then
            leaf1_base + receipts[i] * receipt_factor
        else
            leaf2_base + receipts[i] * receipt_factor + miles[i] * mile_factor
        endif
    else
        if miles[i] <= mile_split then
            leaf3_base + receipts[i] * receipt_factor
        else
            leaf4_base + receipts[i] * receipt_factor + days[i] * day_factor
        endif
    endif;

array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 50.0
);

solve satisfy;

output [
    "=== DECISION TREE SUCCESS ===\n",
    "Split thresholds: receipts <= ", show(receipt_split), ", days <= ", show(day_split), ", miles <= ", show(mile_split), "\n",
    "Leaf bases: ", show_float(6, 2, leaf1_base), " | ", show_float(6, 2, leaf2_base), " | ", show_float(6, 2, leaf3_base), " | ", show_float(6, 2, leaf4_base), "\n",
    "Factors: receipt=", show_float(6, 3, receipt_factor), ", mile=", show_float(6, 3, mile_factor), ", day=", show_float(6, 2, day_factor), "\n"
];
