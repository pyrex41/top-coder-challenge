% MiniZinc Model for Reimbursement System Reverse Engineering
% Based on analysis of 1000 public cases and employee interviews

include "globals.mzn";

% Input: We'll read from a data file
int: n_cases;
array[1..n_cases] of int: days_input;
array[1..n_cases] of float: miles_input;
array[1..n_cases] of float: receipts_input;
array[1..n_cases] of float: expected_output;

% Decision variables - the parameters we want to find

% Base per diem (from analysis: ~$107)
var 90.0..130.0: base_per_diem;

% Mileage rates and thresholds (analysis shows counter-intuitive pattern)
var 0.2..0.8: mile_rate_tier1;  % 0-100 miles: ~0.48
var 0.2..1.2: mile_rate_tier2;  % 100-300 miles: ~0.71 (higher!)
var 0.1..0.6: mile_rate_tier3;  % 300+ miles: likely lower again
var 80..120: mile_threshold1;   % Around 100 miles
var 250..350: mile_threshold2;  % Around 300 miles

% Receipt processing parameters
var 0.0..1.0: receipt_rate_low;     % For receipts < low_threshold
var 0.6..1.2: receipt_rate_medium;  % For medium receipts  
var 0.3..0.8: receipt_rate_high;    % For high receipts (diminishing returns)
var 30.0..80.0: receipt_low_threshold;    % Around $50
var 800.0..1200.0: receipt_high_threshold; % Around $1000

% Day-length adjustments (analysis shows inverse relationship)
var 0.8..2.0: day_factor_1;    % 1-day trips: very high multiplier
var 0.9..1.3: day_factor_2;    % 2-day trips 
var 0.8..1.2: day_factor_3;    % 3-day trips
var 0.7..1.1: day_factor_4_5;  % 4-5 day trips
var 0.5..0.9: day_factor_6_7;  % 6-7 day trips
var 0.4..0.7: day_factor_8plus; % 8+ day trips

% Special bonuses and penalties
var 0.0..100.0: single_day_bonus;     % Special bonus for 1-day trips
var 0.0..50.0: five_day_bonus;        % 5-day "sweet spot" bonus
var 0.0..0.3: efficiency_bonus_rate;  % Efficiency bonus rate
var 150.0..250.0: efficiency_min;     % Min miles/day for bonus
var 200.0..300.0: efficiency_max;     % Max miles/day for bonus

% Quirk parameters
var 0.0..5.0: cents_49_bonus;  % .49 cent bonus from interviews
var 0.0..5.0: cents_99_bonus;  % .99 cent bonus from interviews

% Function to calculate mileage reimbursement
function var float: calc_mileage(var float: miles) =
    if miles <= mile_threshold1 then
        miles * mile_rate_tier1
    elseif miles <= mile_threshold2 then
        mile_threshold1 * mile_rate_tier1 + 
        (miles - mile_threshold1) * mile_rate_tier2
    else
        mile_threshold1 * mile_rate_tier1 + 
        (mile_threshold2 - mile_threshold1) * mile_rate_tier2 +
        (miles - mile_threshold2) * mile_rate_tier3
    endif;

% Function to calculate receipt reimbursement
function var float: calc_receipts(var float: receipts) =
    if receipts < receipt_low_threshold then
        receipts * receipt_rate_low  % Penalty for very low receipts
    elseif receipts <= receipt_high_threshold then
        receipt_low_threshold * receipt_rate_low +
        (receipts - receipt_low_threshold) * receipt_rate_medium
    else
        receipt_low_threshold * receipt_rate_low +
        (receipt_high_threshold - receipt_low_threshold) * receipt_rate_medium +
        (receipts - receipt_high_threshold) * receipt_rate_high
    endif;

% Function to get day factor based on trip length
function var float: get_day_factor(var int: days) =
    if days == 1 then day_factor_1
    elseif days == 2 then day_factor_2  
    elseif days == 3 then day_factor_3
    elseif days <= 5 then day_factor_4_5
    elseif days <= 7 then day_factor_6_7
    else day_factor_8plus
    endif;

% Function to calculate efficiency bonus
function var float: calc_efficiency_bonus(var int: days, var float: miles, var float: base_amount) =
    let {
        var float: miles_per_day = miles / days;
    } in
    if miles_per_day >= efficiency_min /\ miles_per_day <= efficiency_max then
        base_amount * efficiency_bonus_rate
    else
        0.0
    endif;

% Function to calculate quirk bonuses
function var float: calc_quirks(var float: receipts) =
    let {
        var int: cents = round((receipts - floor(receipts)) * 100);
    } in
    if cents == 49 then cents_49_bonus
    elseif cents == 99 then cents_99_bonus
    else 0.0
    endif;

% Main calculation function
function var float: calculate_reimbursement(var int: days, var float: miles, var float: receipts) =
    let {
        % Base calculation
        var float: base = days * base_per_diem;
        var float: mileage = calc_mileage(miles);
        var float: receipt_reimb = calc_receipts(receipts);
        var float: subtotal = base + mileage + receipt_reimb;
        
        % Apply day-length factor
        var float: day_adjusted = subtotal * get_day_factor(days);
        
        % Add special bonuses
        var float: with_single_bonus = 
            if days == 1 then day_adjusted + single_day_bonus
            else day_adjusted endif;
            
        var float: with_five_bonus =
            if days == 5 then with_single_bonus + five_day_bonus
            else with_single_bonus endif;
            
        % Add efficiency bonus
        var float: with_efficiency = with_five_bonus + 
            calc_efficiency_bonus(days, miles, subtotal);
            
        % Add quirks
        var float: final_amount = with_efficiency + calc_quirks(receipts);
        
    } in final_amount;

% Constraints: minimize total error across all cases
array[1..n_cases] of var float: calculated_outputs;
array[1..n_cases] of var float: errors;

constraint forall(i in 1..n_cases)(
    calculated_outputs[i] = calculate_reimbursement(days_input[i], miles_input[i], receipts_input[i])
);

constraint forall(i in 1..n_cases)(
    errors[i] = abs(calculated_outputs[i] - expected_output[i])
);

% Objective: minimize total absolute error
var float: total_error = sum(i in 1..n_cases)(errors[i]);
var float: avg_error = total_error / n_cases;
var float: max_error = max(i in 1..n_cases)(errors[i]);

% Add some logical constraints based on analysis
constraint mile_rate_tier2 >= mile_rate_tier1;  % Tier 2 rate is higher (from data)
constraint mile_rate_tier3 <= mile_rate_tier2;  % Tier 3 drops back down
constraint receipt_rate_medium >= receipt_rate_low;   % Medium receipts treated better
constraint receipt_rate_high <= receipt_rate_medium;  % High receipts diminishing returns
constraint day_factor_1 >= day_factor_2;       % 1-day trips get highest factor
constraint day_factor_2 >= day_factor_3;       % Decreasing with length
constraint day_factor_8plus <= day_factor_6_7; % Long trips penalized

solve minimize total_error;

% Output the found parameters
output [
    "=== FOUND PARAMETERS ===\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "\nMileage rates:\n",
    "  Tier 1 (0-", show(mile_threshold1), " miles): $", show_float(8, 4, mile_rate_tier1), "/mile\n",
    "  Tier 2 (", show(mile_threshold1), "-", show(mile_threshold2), " miles): $", show_float(8, 4, mile_rate_tier2), "/mile\n", 
    "  Tier 3 (", show(mile_threshold2), "+ miles): $", show_float(8, 4, mile_rate_tier3), "/mile\n",
    "\nReceipt processing:\n",
    "  Low rate (<$", show_float(6, 0, receipt_low_threshold), "): ", show_float(6, 3, receipt_rate_low), "x\n",
    "  Medium rate ($", show_float(6, 0, receipt_low_threshold), "-$", show_float(6, 0, receipt_high_threshold), "): ", show_float(6, 3, receipt_rate_medium), "x\n",
    "  High rate (>$", show_float(6, 0, receipt_high_threshold), "): ", show_float(6, 3, receipt_rate_high), "x\n",
    "\nDay length factors:\n",
    "  1-day: ", show_float(6, 3, day_factor_1), "x\n",
    "  2-day: ", show_float(6, 3, day_factor_2), "x\n", 
    "  3-day: ", show_float(6, 3, day_factor_3), "x\n",
    "  4-5 day: ", show_float(6, 3, day_factor_4_5), "x\n",
    "  6-7 day: ", show_float(6, 3, day_factor_6_7), "x\n",
    "  8+ day: ", show_float(6, 3, day_factor_8plus), "x\n",
    "\nSpecial bonuses:\n",
    "  Single day bonus: $", show_float(6, 2, single_day_bonus), "\n",
    "  Five day bonus: $", show_float(6, 2, five_day_bonus), "\n",
    "  Efficiency bonus rate: ", show_float(6, 3, efficiency_bonus_rate), "x\n",
    "  Efficiency range: ", show_float(6, 0, efficiency_min), "-", show_float(6, 0, efficiency_max), " miles/day\n",
    "\nQuirks:\n",
    "  .49 cent bonus: $", show_float(6, 2, cents_49_bonus), "\n",
    "  .99 cent bonus: $", show_float(6, 2, cents_99_bonus), "\n",
    "\n=== ERROR METRICS ===\n",
    "Total error: $", show_float(8, 2, total_error), "\n",
    "Average error: $", show_float(6, 2, avg_error), "\n",
    "Max error: $", show_float(6, 2, max_error), "\n"
];