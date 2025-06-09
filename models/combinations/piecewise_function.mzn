
% Piecewise Function Model - Multiple breakpoints
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Multiple breakpoints for days (from analysis: 1.5, 2.5, 4.5, 8.5, 10.5)
array[1..5] of float: day_breaks = [1.5, 2.5, 4.5, 8.5, 10.5];
array[1..6] of var 50.0..150.0: day_values;

% Multiple breakpoints for miles (from analysis: 263, 583, 621, 624, 833)
array[1..5] of float: mile_breaks = [263, 583, 621, 624, 833];
array[1..6] of var 0.1..0.8: mile_rates;

% Multiple breakpoints for receipts (from analysis: 491, 562, 563, 567, 828, 1236)
array[1..6] of float: receipt_breaks = [491, 562, 563, 567, 828, 1236];
array[1..7] of var 0.1..1.0: receipt_rates;

% Piecewise function for days
function var float: day_component(int: d) =
    if d <= day_breaks[1] then day_values[1]
    elseif d <= day_breaks[2] then day_values[2]
    elseif d <= day_breaks[3] then day_values[3]
    elseif d <= day_breaks[4] then day_values[4]
    elseif d <= day_breaks[5] then day_values[5]
    else day_values[6] endif;

% Piecewise function for miles
function var float: mile_component(int: m) =
    if m <= mile_breaks[1] then m * mile_rates[1]
    elseif m <= mile_breaks[2] then 
        mile_breaks[1] * mile_rates[1] + (m - mile_breaks[1]) * mile_rates[2]
    elseif m <= mile_breaks[3] then
        mile_breaks[1] * mile_rates[1] + (mile_breaks[2] - mile_breaks[1]) * mile_rates[2] +
        (m - mile_breaks[2]) * mile_rates[3]
    % ... continue pattern
    else
        mile_breaks[1] * mile_rates[1] + (mile_breaks[2] - mile_breaks[1]) * mile_rates[2] +
        (mile_breaks[3] - mile_breaks[2]) * mile_rates[3] + (mile_breaks[4] - mile_breaks[3]) * mile_rates[4] +
        (mile_breaks[5] - mile_breaks[4]) * mile_rates[5] + (m - mile_breaks[5]) * mile_rates[6]
    endif;

% Piecewise function for receipts
function var float: receipt_component(float: r) =
    if r <= receipt_breaks[1] then r * receipt_rates[1]
    elseif r <= receipt_breaks[2] then 
        receipt_breaks[1] * receipt_rates[1] + (r - receipt_breaks[1]) * receipt_rates[2]
    elseif r <= receipt_breaks[3] then
        receipt_breaks[1] * receipt_rates[1] + (receipt_breaks[2] - receipt_breaks[1]) * receipt_rates[2] +
        (r - receipt_breaks[2]) * receipt_rates[3]
    % ... continue for all breakpoints
    else
        receipt_breaks[1] * receipt_rates[1] + (receipt_breaks[2] - receipt_breaks[1]) * receipt_rates[2] +
        (receipt_breaks[3] - receipt_breaks[2]) * receipt_rates[3] + (receipt_breaks[4] - receipt_breaks[3]) * receipt_rates[4] +
        (receipt_breaks[5] - receipt_breaks[4]) * receipt_rates[5] + (receipt_breaks[6] - receipt_breaks[5]) * receipt_rates[6] +
        (r - receipt_breaks[6]) * receipt_rates[7]
    endif;

% Calculate total reimbursement
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = day_component(days[i]) + mile_component(miles[i]) + receipt_component(receipts[i])
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.1
);

solve satisfy;

output [
    "=== PIECEWISE FUNCTION MODEL SUCCESS ===\n",
    "Day values: ", show(day_values), "\n",
    "Mile rates: ", show(mile_rates), "\n", 
    "Receipt rates: ", show(receipt_rates), "\n"
];
