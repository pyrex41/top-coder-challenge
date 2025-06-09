
% Receipt-Driven Model - Receipts are 67% of importance
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Primary receipt processing (most important)
var 10.0..50.0: receipt_threshold_1;
var 400.0..800.0: receipt_threshold_2;
var 1000.0..1500.0: receipt_threshold_3;

var 0.1..0.6: receipt_rate_1;  % Low receipts penalty
var 0.6..1.0: receipt_rate_2;  % Normal receipts
var 0.2..0.6: receipt_rate_3;  % High receipts diminishing

% Secondary factors (20% days, 12% miles)
var 80.0..120.0: day_base;
var 0.0..0.5: day_penalty_rate;  % Penalty for longer trips
var 0.2..0.6: mile_rate;

% Logical constraints
constraint receipt_threshold_1 < receipt_threshold_2;
constraint receipt_threshold_2 < receipt_threshold_3;
constraint receipt_rate_2 >= receipt_rate_1;

% Calculate reimbursement - receipt driven
function var float: calc_reimbursement(int: i) =
    let {
        % Primary: Receipt processing (67% importance)
        var float: receipt_component = 
            if receipts[i] <= receipt_threshold_1 then
                receipts[i] * receipt_rate_1
            elseif receipts[i] <= receipt_threshold_2 then
                receipt_threshold_1 * receipt_rate_1 +
                (receipts[i] - receipt_threshold_1) * receipt_rate_2
            else
                receipt_threshold_1 * receipt_rate_1 +
                (receipt_threshold_2 - receipt_threshold_1) * receipt_rate_2 +
                (receipts[i] - receipt_threshold_2) * receipt_rate_3
            endif;
        
        % Secondary: Day factor (20% importance) - penalty for long trips
        var float: day_component = day_base - (days[i] - 1) * day_penalty_rate;
        
        % Tertiary: Mile factor (12% importance) 
        var float: mile_component = miles[i] * mile_rate;
            
    } in receipt_component + day_component + mile_component;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.2
);

solve satisfy;

output [
    "=== RECEIPT-DRIVEN MODEL SUCCESS ===\n",
    "Receipt tiers: $0-", show_float(6, 0, receipt_threshold_1), " @ ", show_float(6, 3, receipt_rate_1), "x\n",
    "              $", show_float(6, 0, receipt_threshold_1), "-", show_float(6, 0, receipt_threshold_2), " @ ", show_float(6, 3, receipt_rate_2), "x\n",
    "              $", show_float(6, 0, receipt_threshold_2), "+ @ ", show_float(6, 3, receipt_rate_3), "x\n",
    "Day base: $", show_float(6, 2, day_base), " - $", show_float(6, 2, day_penalty_rate), "/extra day\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\n"
];
