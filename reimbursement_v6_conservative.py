#!/usr/bin/env python3
"""
Reimbursement Calculator V6 - Conservative Data-Driven Improvements
Minimal changes to V2 based only on strongest data signals:
- Keeps all of V2's proven structure
- Only adds small, validated adjustments 
- Conservative approach to avoid over-fitting
"""

import sys
import math

class ReimbursementCalculatorV6:
    def __init__(self):
        # Keep ALL of V2's proven parameters unchanged
        self.receipt_major_threshold = 828.0
        self.days_short_threshold = 4.5
        self.miles_threshold_1 = 583.0
        self.miles_threshold_2 = 624.5  
        self.miles_threshold_3 = 833.5
        self.receipt_threshold_1 = 562.0
        self.receipt_threshold_2 = 563.0
        self.receipt_threshold_3 = 1236.0
        self.receipts_per_day_1 = 240.0
        self.receipts_per_day_2 = 568.0
        
        # Keep ALL of V2's base values exactly
        self.low_receipt_base = {
            'short_low_miles_low_receipts': 232.0,
            'short_low_miles_med_receipts': 448.0,
            'short_low_miles_high_receipts': 684.0,
            'short_high_miles_low_receipts_1day': 625.0,
            'short_high_miles_low_receipts_multiday': 772.0,
            'short_high_miles_high_receipts': 1012.0,
            'long_low_miles_short': 638.0,
            'long_low_miles_med': 878.0,
            'long_low_miles_very_long_low_receipts': 904.0,
            'long_low_miles_very_long_high_receipts': 1179.0,
            'long_high_miles_low_receipts_short': 1049.0,
            'long_high_miles_low_receipts_long': 1307.0,
            'long_high_miles_med_receipts': 1234.0,
            'long_high_miles_high_receipts': 1468.0,
        }
        
        self.high_receipt_base = {
            'short_low_miles_low_receipts_per_day': 1276.0,
            'short_low_miles_med_receipts_per_day': 1005.0,
            'short_low_miles_high_receipts_low_rpd': 1453.0,
            'short_low_miles_high_receipts_high_rpd': 1282.0,
        }
        
        # ONLY data-confirmed adjustments (very small)
        # From analysis: extreme efficiency (300+ miles/day) had lower avg error ($149 vs $224)
        self.extreme_efficiency_threshold = 300.0
        self.extreme_efficiency_adjustment = 1.05  # Very small 5% boost
        
        # From analysis: confirmed .99 penalty pattern 
        # (.99 cases averaged $688 vs $1349 overall - strong signal)
        self.cents_99_penalty = 0.92  # Small 8% penalty
        self.cents_49_penalty = 0.94  # Smaller 6% penalty
    
    def classify_case(self, days, miles, receipts):
        """Use V2's exact classification logic - no changes"""
        receipts_per_day = receipts / days if days > 0 else 0
        
        if receipts <= self.receipt_major_threshold:
            # Low receipt branch - EXACT V2 logic
            if days <= self.days_short_threshold:
                if miles <= self.miles_threshold_1:
                    if receipts <= self.receipt_threshold_1:
                        if days <= 1.5:
                            return 'short_low_miles_low_receipts', self.low_receipt_base['short_low_miles_low_receipts']
                        else:
                            return 'short_low_miles_med_receipts', self.low_receipt_base['short_low_miles_med_receipts']
                    else:
                        return 'short_low_miles_high_receipts', self.low_receipt_base['short_low_miles_high_receipts']
                else:
                    if receipts <= self.receipt_threshold_2:
                        if days <= 2.5:
                            return 'short_high_miles_low_receipts_1day', self.low_receipt_base['short_high_miles_low_receipts_1day']
                        else:
                            return 'short_high_miles_low_receipts_multiday', self.low_receipt_base['short_high_miles_low_receipts_multiday']
                    else:
                        return 'short_high_miles_high_receipts', self.low_receipt_base['short_high_miles_high_receipts']
            else:
                # Long trips - EXACT V2 logic
                if miles <= self.miles_threshold_2:
                    if days <= 8.5:
                        if miles <= 263:
                            return 'long_low_miles_short', self.low_receipt_base['long_low_miles_short']
                        else:
                            return 'long_low_miles_med', self.low_receipt_base['long_low_miles_med']
                    else:
                        if receipts <= 567:
                            return 'long_low_miles_very_long_low_receipts', self.low_receipt_base['long_low_miles_very_long_low_receipts']
                        else:
                            return 'long_low_miles_very_long_high_receipts', self.low_receipt_base['long_low_miles_very_long_high_receipts']
                else:
                    # High miles - EXACT V2 logic
                    if receipts <= 491:
                        if days <= 10.5:
                            return 'long_high_miles_low_receipts_short', self.low_receipt_base['long_high_miles_low_receipts_short']
                        else:
                            return 'long_high_miles_low_receipts_long', self.low_receipt_base['long_high_miles_low_receipts_long']
                    else:
                        if miles <= self.miles_threshold_3:
                            return 'long_high_miles_med_receipts', self.low_receipt_base['long_high_miles_med_receipts']
                        else:
                            return 'long_high_miles_high_receipts', self.low_receipt_base['long_high_miles_high_receipts']
        else:
            # High receipt branch - EXACT V2 logic
            if days <= 5.5:
                if miles <= 621:
                    if receipts <= self.receipt_threshold_3:
                        if receipts_per_day <= self.receipts_per_day_1:
                            return 'short_low_miles_low_receipts_per_day', self.high_receipt_base['short_low_miles_low_receipts_per_day']
                        else:
                            return 'short_low_miles_med_receipts_per_day', self.high_receipt_base['short_low_miles_med_receipts_per_day']
                    else:
                        if receipts_per_day <= self.receipts_per_day_2:
                            return 'short_low_miles_high_receipts_low_rpd', self.high_receipt_base['short_low_miles_high_receipts_low_rpd']
                        else:
                            return 'short_low_miles_high_receipts_high_rpd', self.high_receipt_base['short_low_miles_high_receipts_high_rpd']
                            
        # Fallback - EXACT V2 logic
        base = receipts * 0.7 + days * 30 + miles * 0.3
        return 'fallback', base
    
    def apply_adjustments(self, base_amount, days, miles, receipts, category):
        """Minimal, data-confirmed adjustments only"""
        
        # Keep V2's cent penalties but refine based on data
        cents = int(round((receipts % 1) * 100))
        if cents == 49:
            base_amount *= self.cents_49_penalty
        elif cents == 99:
            base_amount *= self.cents_99_penalty
        
        # Only add confirmed extreme efficiency adjustment (very small)
        if days > 0:
            miles_per_day = miles / days
            if miles_per_day >= self.extreme_efficiency_threshold:
                base_amount *= self.extreme_efficiency_adjustment
        
        return base_amount
    
    def calculate_reimbursement(self, days, miles, receipts):
        """Main calculation - minimal changes to V2"""
        category, base_amount = self.classify_case(days, miles, receipts)
        final_amount = self.apply_adjustments(base_amount, days, miles, receipts, category)
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_v6_conservative.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculatorV6()
        reimbursement = calculator.calculate_reimbursement(days, miles, receipts)
        
        print(f"{reimbursement:.2f}")
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()