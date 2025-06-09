
% 3-Tier Mileage Model: 0-75, 75-400, 400+
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Structure parameters
int: tier1_end = 75;
int: tier2_end = 400;

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.8: rate1;  % Tier 1 rate
var 0.2..0.6: rate2;  % Tier 2 rate  
var 0.1..0.4: rate3;  % Tier 3 rate
var 0.0..1.0: receipt_rate;

% Logical constraints
constraint rate1 >= rate2;  % Higher rate for shorter distances
constraint rate2 >= rate3;  % Decreasing rates

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = days[i] * base_per_diem;
        
        var float: mileage = 
            if miles[i] <= tier1_end then
                miles[i] * rate1
            elseif miles[i] <= tier2_end then
                tier1_end * rate1 + (miles[i] - tier1_end) * rate2
            else
                tier1_end * rate1 + (tier2_end - tier1_end) * rate2 + 
                (miles[i] - tier2_end) * rate3
            endif;
        
        var float: receipt_reimb = receipts[i] * receipt_rate;
            
    } in base + mileage + receipt_reimb;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.1
);

solve satisfy;

output [
    "=== 3-TIER MILEAGE MODEL SUCCESS ===\n",
    "Tiers: 0-75 @ $", show_float(6, 3, rate1), "/mi\n",
    "       75-400 @ $", show_float(6, 3, rate2), "/mi\n", 
    "       400+ @ $", show_float(6, 3, rate3), "/mi\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\n"
];
