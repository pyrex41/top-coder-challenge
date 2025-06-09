
% Tiered Receipt Processing Model
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Discoverable parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.7: simple_mile_rate;

% Receipt tier parameters
var 20.0..80.0: receipt_low_threshold;
var 500.0..1200.0: receipt_high_threshold;
var 0.0..0.5: receipt_low_rate;     % Penalty rate for low receipts
var 0.5..1.0: receipt_medium_rate;  % Normal rate for medium receipts
var 0.2..0.6: receipt_high_rate;    % Diminishing returns for high receipts

% Logical constraints
constraint receipt_low_threshold < receipt_high_threshold;
constraint receipt_medium_rate >= receipt_low_rate;

% Calculate reimbursement
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = days[i] * base_per_diem;
        var float: mileage = miles[i] * simple_mile_rate;
        
        var float: receipt_reimb = 
            if receipts[i] <= receipt_low_threshold then
                receipts[i] * receipt_low_rate
            elseif receipts[i] <= receipt_high_threshold then
                receipt_low_threshold * receipt_low_rate +
                (receipts[i] - receipt_low_threshold) * receipt_medium_rate
            else
                receipt_low_threshold * receipt_low_rate +
                (receipt_high_threshold - receipt_low_threshold) * receipt_medium_rate +
                (receipts[i] - receipt_high_threshold) * receipt_high_rate
            endif;
            
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
    "=== TIERED RECEIPT MODEL SUCCESS ===\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Mile rate: $", show_float(6, 3, simple_mile_rate), "/mi\n",
    "Receipt tiers:\n",
    "  0-$", show_float(6, 0, receipt_low_threshold), ": ", show_float(6, 3, receipt_low_rate), "x\n",
    "  $", show_float(6, 0, receipt_low_threshold), "-$", show_float(6, 0, receipt_high_threshold), ": ", show_float(6, 3, receipt_medium_rate), "x\n",
    "  $", show_float(6, 0, receipt_high_threshold), "+: ", show_float(6, 3, receipt_high_rate), "x\n"
];
