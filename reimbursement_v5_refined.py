#!/usr/bin/env python3
"""
Reimbursement Calculator V5 - Refined Hybrid
Keeps V2's proven decision tree but fixes specific weaknesses:
- Better handling of high-mileage, high-receipt cases (the main error source)
- Incorporates only validated insights from interview analysis
- Addresses the extreme efficiency bonus that data confirms
"""

import sys
import math

class ReimbursementCalculatorV5:
    def __init__(self):
        # Keep V2's proven foundation
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
        
        # V2's base values but with refinements
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
        
        # NEW: High-mileage, high-receipt bonuses (addresses main error cases)
        self.ultra_high_performance_bonus = 1.85  # For extreme combinations
        self.high_performance_bonus = 1.45        # For high combinations
        
        # Confirmed from data: extreme efficiency does get bonuses
        self.extreme_efficiency_threshold = 300.0  # miles per day
        self.extreme_efficiency_bonus = 1.25
        
    def classify_case(self, days, miles, receipts):
        """Enhanced classification with high-performance detection"""
        receipts_per_day = receipts / days if days > 0 else 0
        miles_per_day = miles / days if days > 0 else 0
        
        # NEW: Detect ultra-high performance cases (main V2 error source)
        is_ultra_high_performance = (
            miles >= 1000 and receipts >= 1000 and 
            days >= 7 and miles_per_day >= 140
        )
        
        is_high_performance = (
            miles >= 800 and receipts >= 800 and 
            days >= 5 and miles_per_day >= 120
        )
        
        # Use V2's classification logic
        if receipts <= self.receipt_major_threshold:
            # Low receipt branch (keep V2 logic)
            if days <= self.days_short_threshold:
                if miles <= self.miles_threshold_1:
                    if receipts <= self.receipt_threshold_1:
                        if days <= 1.5:
                            category = 'short_low_miles_low_receipts'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'short_low_miles_med_receipts'
                            base = self.low_receipt_base[category]
                    else:
                        category = 'short_low_miles_high_receipts'
                        base = self.low_receipt_base[category]
                else:
                    if receipts <= self.receipt_threshold_2:
                        if days <= 2.5:
                            category = 'short_high_miles_low_receipts_1day'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'short_high_miles_low_receipts_multiday'
                            base = self.low_receipt_base[category]
                    else:
                        category = 'short_high_miles_high_receipts'
                        base = self.low_receipt_base[category]
            else:
                # Long trips - apply performance bonuses
                if miles <= self.miles_threshold_2:
                    if days <= 8.5:
                        if miles <= 263:
                            category = 'long_low_miles_short'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'long_low_miles_med'
                            base = self.low_receipt_base[category]
                    else:
                        if receipts <= 567:
                            category = 'long_low_miles_very_long_low_receipts'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'long_low_miles_very_long_high_receipts'
                            base = self.low_receipt_base[category]
                else:
                    # High miles - key improvement area
                    if receipts <= 491:
                        if days <= 10.5:
                            category = 'long_high_miles_low_receipts_short'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'long_high_miles_low_receipts_long'
                            base = self.low_receipt_base[category]
                    else:
                        if miles <= self.miles_threshold_3:
                            category = 'long_high_miles_med_receipts'
                            base = self.low_receipt_base[category]
                        else:
                            category = 'long_high_miles_high_receipts'
                            base = self.low_receipt_base[category]
                        
                        # Apply performance bonuses to high miles cases
                        if is_ultra_high_performance:
                            base *= self.ultra_high_performance_bonus
                        elif is_high_performance:
                            base *= self.high_performance_bonus
        else:
            # High receipt branch - enhanced
            if days <= 5.5:
                if miles <= 621:
                    if receipts <= self.receipt_threshold_3:
                        if receipts_per_day <= self.receipts_per_day_1:
                            category = 'short_low_miles_low_receipts_per_day'
                            base = self.high_receipt_base[category]
                        else:
                            category = 'short_low_miles_med_receipts_per_day'
                            base = self.high_receipt_base[category]
                    else:
                        if receipts_per_day <= self.receipts_per_day_2:
                            category = 'short_low_miles_high_receipts_low_rpd'
                            base = self.high_receipt_base[category]
                        else:
                            category = 'short_low_miles_high_receipts_high_rpd'
                            base = self.high_receipt_base[category]
                else:
                    # High miles, high receipts - major improvement area
                    category = 'high_miles_high_receipts'
                    base = receipts * 0.85 + miles * 0.95 + days * 45
                    
                    if is_ultra_high_performance:
                        base *= self.ultra_high_performance_bonus
                    elif is_high_performance:
                        base *= self.high_performance_bonus
            else:
                # Long high-receipt trips - another key area
                category = 'long_high_receipts'
                base = receipts * 0.75 + miles * 1.1 + days * 60
                
                if is_ultra_high_performance:
                    base *= self.ultra_high_performance_bonus
                elif is_high_performance:
                    base *= self.high_performance_bonus
                    
        # Fallback with better handling
        if 'base' not in locals():
            base = receipts * 0.7 + days * 35 + miles * 0.35
            category = 'fallback'
        
        return category, base
    
    def apply_adjustments(self, base_amount, days, miles, receipts, category):
        """Enhanced adjustments with validated insights"""
        
        # Keep confirmed .49/.99 penalties
        cents = int(round((receipts % 1) * 100))
        if cents == 49:
            base_amount *= 0.85
        elif cents == 99:
            base_amount *= 0.90
        
        # Apply confirmed extreme efficiency bonus
        if days > 0:
            miles_per_day = miles / days
            if miles_per_day >= self.extreme_efficiency_threshold:
                base_amount *= self.extreme_efficiency_bonus
        
        return base_amount
    
    def calculate_reimbursement(self, days, miles, receipts):
        """Enhanced calculation with targeted improvements"""
        category, base_amount = self.classify_case(days, miles, receipts)
        final_amount = self.apply_adjustments(base_amount, days, miles, receipts, category)
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_v5_refined.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculatorV5()
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