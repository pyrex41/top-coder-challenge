
% Model with Penalty/Bonus System
% Including .49/.99 cent penalties discovered in analysis
include "globals.mzn";

int: n;
array[1..n] of int: days;
array[1..n] of int: miles;
array[1..n] of float: receipts;
array[1..n] of float: expected;

% Core parameters
var 95.0..105.0: base_per_diem;
var 0.4..0.7: mile_rate;
var 0.5..0.9: receipt_rate;

% Penalty/bonus parameters
var bool: has_cent_penalties;
var 0.0..1.0: penalty_amount;
var bool: has_efficiency_bonus;
var 0.0..50.0: efficiency_bonus;

% Special case parameters
var 0.0..100.0: vacation_penalty_threshold_miles;
var 0.0..100.0: vacation_penalty_threshold_receipts;
var 0.0..200.0: vacation_penalty_amount;

% Calculate base reimbursement
function var float: calc_base(int: i) = 
    days[i] * base_per_diem + miles[i] * mile_rate + receipts[i] * receipt_rate;

% Apply penalties and bonuses
function var float: calc_reimbursement(int: i) =
    let {
        var float: base = calc_base(i);
        
        % Vacation penalty for 1-day trips with high miles + receipts
        var float: vacation_penalty = 
            if days[i] == 1 /\ miles[i] > vacation_penalty_threshold_miles /\ 
               receipts[i] > vacation_penalty_threshold_receipts then
                vacation_penalty_amount
            else 0.0 endif;
        
        % Efficiency bonus
        var float: eff_bonus = 
            if has_efficiency_bonus /\ miles[i]/days[i] >= 180 /\ 
               miles[i]/days[i] <= 220 then
                efficiency_bonus
            else 0.0 endif;
        
        var float: subtotal = base - vacation_penalty + eff_bonus;
        
        % .49/.99 cent penalties
        var float: final_amount = 
            if has_cent_penalties then
                let {
                    int: cents = int(subtotal * 100) mod 100;
                } in 
                if cents == 49 \/ cents == 99 then
                    subtotal + penalty_amount
                else subtotal endif
            else subtotal endif;
            
    } in final_amount;

% Exact match constraint
array[1..n] of var float: calculated;
constraint forall(i in 1..n)(
    calculated[i] = calc_reimbursement(i)
);

constraint forall(i in 1..n)(
    abs(calculated[i] - expected[i]) <= 0.5
);

solve satisfy;

output [
    "=== PENALTY/BONUS MODEL SUCCESS ===\n",
    "Base per diem: $", show_float(6, 2, base_per_diem), "\n",
    "Mile rate: $", show_float(6, 3, mile_rate), "/mi\n",
    "Receipt rate: ", show_float(6, 3, receipt_rate), "x\n",
    "Has cent penalties: ", show(has_cent_penalties), "\n",
    "Vacation penalty threshold: ", show_float(6, 0, vacation_penalty_threshold_miles), " mi, $", show_float(6, 0, vacation_penalty_threshold_receipts), "\n"
];
