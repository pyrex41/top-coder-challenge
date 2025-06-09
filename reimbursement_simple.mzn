% Simplified MiniZinc Model for Reimbursement System
% Linear solver friendly version

include "globals.mzn";

% Input data
int: n_cases;
array[1..n_cases] of int: days_input;
array[1..n_cases] of float: miles_input;
array[1..n_cases] of float: receipts_input;
array[1..n_cases] of float: expected_output;

% Decision variables with explicit bounds
var 80.0..150.0: base_per_diem;

% Simplified mileage model - just two tiers
var 0.1..1.0: mile_rate_low;    % 0-threshold miles
var 0.1..1.0: mile_rate_high;   % threshold+ miles  
var 50..200: mile_threshold;    % Threshold between tiers

% Simplified receipt model - three rates
var 0.0..1.5: receipt_rate_low;    % Low receipts
var 0.0..1.5: receipt_rate_medium; % Medium receipts
var 0.0..1.5: receipt_rate_high;   % High receipts
var 20.0..100.0: receipt_threshold_low;   % Low->medium threshold
var 500.0..1500.0: receipt_threshold_high; % Medium->high threshold

% Day adjustment factors (bounded)
var 0.5..3.0: factor_short;  % 1-3 days
var 0.5..2.0: factor_medium; % 4-7 days  
var 0.3..1.5: factor_long;   % 8+ days

% Simple bonuses
var 0.0..200.0: bonus_single_day;
var 0.0..100.0: bonus_five_day;

% Calculate reimbursement for each case
array[1..n_cases] of var 0.0..5000.0: calculated;
array[1..n_cases] of var 0.0..3000.0: errors;

% Constraints for each case
constraint forall(i in 1..n_cases)(
    let {
        int: days = days_input[i];
        float: miles = miles_input[i];
        float: receipts = receipts_input[i];
        
        % Base per diem
        var 0.0..2000.0: base_amount = days * base_per_diem;
        
        % Mileage calculation (simplified to linear)
        var 0.0..2000.0: mileage_amount = 
            if miles <= mile_threshold then
                miles * mile_rate_low
            else
                mile_threshold * mile_rate_low + (miles - mile_threshold) * mile_rate_high
            endif;
        
        % Receipt calculation (simplified)
        var 0.0..3000.0: receipt_amount = 
            if receipts <= receipt_threshold_low then
                receipts * receipt_rate_low
            elseif receipts <= receipt_threshold_high then
                receipt_threshold_low * receipt_rate_low + 
                (receipts - receipt_threshold_low) * receipt_rate_medium
            else
                receipt_threshold_low * receipt_rate_low +
                (receipt_threshold_high - receipt_threshold_low) * receipt_rate_medium +
                (receipts - receipt_threshold_high) * receipt_rate_high
            endif;
            
        % Subtotal
        var 0.0..4000.0: subtotal = base_amount + mileage_amount + receipt_amount;
        
        % Day factor adjustment
        var 0.0..5000.0: day_adjusted = 
            if days <= 3 then subtotal * factor_short
            elseif days <= 7 then subtotal * factor_medium
            else subtotal * factor_long
            endif;
            
        % Add bonuses
        var 0.0..5000.0: with_bonuses = day_adjusted +
            (if days == 1 then bonus_single_day else 0.0 endif) +
            (if days == 5 then bonus_five_day else 0.0 endif);
            
    } in calculated[i] = with_bonuses
);

% Error calculation
constraint forall(i in 1..n_cases)(
    errors[i] = abs(calculated[i] - expected_output[i])
);

% Objective
var 0.0..1000000.0: total_error = sum(i in 1..n_cases)(errors[i]);

% Logical constraints
constraint mile_rate_high >= mile_rate_low;  % Higher rates for longer distances
constraint receipt_rate_medium >= receipt_rate_low;  % Better rates for medium receipts
constraint factor_short >= factor_medium;    % Shorter trips get higher factors
constraint factor_medium >= factor_long;     % Medium trips better than long

solve minimize total_error;

output [
    "=== SIMPLIFIED MODEL RESULTS ===\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Mileage rates:\n",
    "  0-", show(mile_threshold), " miles: $", show_float(6, 4, mile_rate_low), "/mile\n",
    "  ", show(mile_threshold), "+ miles: $", show_float(6, 4, mile_rate_high), "/mile\n",
    "Receipt rates:\n",
    "  0-$", show_float(6, 0, receipt_threshold_low), ": ", show_float(6, 3, receipt_rate_low), "x\n",
    "  $", show_float(6, 0, receipt_threshold_low), "-$", show_float(6, 0, receipt_threshold_high), ": ", show_float(6, 3, receipt_rate_medium), "x\n",
    "  $", show_float(6, 0, receipt_threshold_high), "+: ", show_float(6, 3, receipt_rate_high), "x\n",
    "Day factors:\n",
    "  1-3 days: ", show_float(6, 3, factor_short), "x\n",
    "  4-7 days: ", show_float(6, 3, factor_medium), "x\n",
    "  8+ days: ", show_float(6, 3, factor_long), "x\n",
    "Bonuses:\n",
    "  Single day: $", show_float(6, 2, bonus_single_day), "\n",
    "  Five day: $", show_float(6, 2, bonus_five_day), "\n",
    "Total error: $", show_float(8, 2, total_error), "\n",
    "Average error: $", show_float(6, 2, total_error / n_cases), "\n"
];