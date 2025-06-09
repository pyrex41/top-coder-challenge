
% 2-Tier Mileage Model: 0-75 @ $0.58, 75+ @ $0.35
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Fixed structure parameters
float: tier1_end = 75;
float: rate1 = 0.58;
float: rate2 = 0.35;

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.0..1.0: receipt_rate;
var 0.0..100.0: bonus_amount;

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = days[i] * base_per_diem;
        
        var float: mileage = 
            if miles[i] <= tier1_end then
                miles[i] * rate1
            else
                tier1_end * rate1 + (miles[i] - tier1_end) * rate2
            endif;
        
        var float: receipt_reimb = receipts[i] * receipt_rate;
        
        var float: bonus = 
            if days[i] == 5 then bonus_amount else 0.0 endif;
            
    } in base + mileage + receipt_reimb + bonus;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

% Allow small tolerance
constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.5
);

solve satisfy;

output [
    "=== 2-TIER MILEAGE MODEL SUCCESS ===\n",
    "Tier structure: 0-75 @ $0.58, 75+ @ $0.35\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\n",
    "5-day bonus: $", show_float(6, 2, bonus_amount), "\n"
];
