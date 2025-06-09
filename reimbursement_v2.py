#!/usr/bin/env python3
"""
Reimbursement Calculator V2 - Based on Systematic Exploration
Key insight: This is a RECEIPT-DRIVEN system with day penalties, not per-diem driven!
"""

import sys
import math

class ReimbursementCalculatorV2:
    def __init__(self):
        # MAJOR INSIGHT: Receipts are 67% of importance, days 20%, miles 12%
        
        # Base calculation uses regression tree insights
        # Primary split: receipts <= $828.10
        self.receipt_major_threshold = 828.0
        
        # Secondary splits found by tree
        self.days_short_threshold = 4.5      # days <= 4.5
        self.miles_threshold_1 = 583.0       # miles <= 583
        self.miles_threshold_2 = 624.5       # miles <= 624.5  
        self.miles_threshold_3 = 833.5       # miles <= 833.5
        
        # Receipt sub-thresholds
        self.receipt_threshold_1 = 562.0     # receipts <= 562.04
        self.receipt_threshold_2 = 563.0     # receipts <= 563.10
        self.receipt_threshold_3 = 1236.0    # receipts <= 1235.90
        
        # Receipts per day thresholds  
        self.receipts_per_day_1 = 240.0      # receipts_per_day <= 240.23
        self.receipts_per_day_2 = 568.0      # receipts_per_day <= 567.87
        
        # Values from decision tree leaf nodes (approximate)
        # These are the actual outputs the tree predicts for different combinations
        
        # Low receipt formulas (receipts <= 828)
        self.low_receipt_base = {
            # Short trips (days <= 4.5)
            'short_low_miles_low_receipts': 232.0,   # days<=1.5, miles<=583, receipts<=562
            'short_low_miles_med_receipts': 448.0,   # days>1.5, miles<=583, receipts<=562
            'short_low_miles_high_receipts': 684.0,  # miles<=583, receipts>562
            'short_high_miles_low_receipts_1day': 625.0,  # days<=2.5, miles>583, receipts<=563
            'short_high_miles_low_receipts_multiday': 772.0,  # days>2.5, miles>583, receipts<=563
            'short_high_miles_high_receipts': 1012.0,  # miles>583, receipts>563
            
            # Long trips (days > 4.5)
            'long_low_miles_short': 638.0,    # days<=8.5, miles<=262.97
            'long_low_miles_med': 878.0,      # days<=8.5, miles>262.97
            'long_low_miles_very_long_low_receipts': 904.0,  # days>8.5, receipts<=567
            'long_low_miles_very_long_high_receipts': 1179.0, # days>8.5, receipts>567
            'long_high_miles_low_receipts_short': 1049.0,  # days<=10.5, receipts<=491
            'long_high_miles_low_receipts_long': 1307.0,   # days>10.5, receipts<=491
            'long_high_miles_med_receipts': 1234.0,        # receipts>491, miles<=833.5
            'long_high_miles_high_receipts': 1468.0,       # receipts>491, miles>833.5
        }
        
        # High receipt formulas (receipts > 828)
        self.high_receipt_base = {
            'short_low_miles_low_receipts_per_day': 1276.0,   # days<=5.5, miles<=621, receipts<=1236, rpd<=240
            'short_low_miles_med_receipts_per_day': 1005.0,   # days<=5.5, miles<=621, receipts<=1236, rpd>240  
            'short_low_miles_high_receipts_low_rpd': 1453.0,  # days<=5.5, miles<=621, receipts>1236, rpd<=568
            'short_low_miles_high_receipts_high_rpd': 1282.0, # days<=5.5, miles<=621, receipts>1236, rpd>568
            # Add more combinations as needed...
        }
        
    def classify_case(self, days, miles, receipts):
        """Classify the case based on decision tree logic"""
        receipts_per_day = receipts / days if days > 0 else 0
        
        if receipts <= self.receipt_major_threshold:
            # Low receipt branch
            if days <= self.days_short_threshold:
                # Short trips
                if miles <= self.miles_threshold_1:
                    if receipts <= self.receipt_threshold_1:
                        if days <= 1.5:
                            return 'short_low_miles_low_receipts', self.low_receipt_base['short_low_miles_low_receipts']
                        else:
                            return 'short_low_miles_med_receipts', self.low_receipt_base['short_low_miles_med_receipts']
                    else:
                        return 'short_low_miles_high_receipts', self.low_receipt_base['short_low_miles_high_receipts']
                else:
                    # High miles
                    if receipts <= self.receipt_threshold_2:
                        if days <= 2.5:
                            return 'short_high_miles_low_receipts_1day', self.low_receipt_base['short_high_miles_low_receipts_1day']
                        else:
                            return 'short_high_miles_low_receipts_multiday', self.low_receipt_base['short_high_miles_low_receipts_multiday']
                    else:
                        return 'short_high_miles_high_receipts', self.low_receipt_base['short_high_miles_high_receipts']
            else:
                # Long trips  
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
                    # High miles
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
            # High receipt branch - simplified for now
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
                            
        # Default fallback - use a simple linear model based on discovery
        # receipts are 67% important, so weight heavily
        base = receipts * 0.7 + days * 30 + miles * 0.3
        return 'fallback', base
    
    def apply_adjustments(self, base_amount, days, miles, receipts, category):
        """Apply fine-tuning adjustments based on analysis"""
        
        # The .49/.99 "penalties" discovered in analysis
        cents = int(round((receipts % 1) * 100))
        if cents == 49:
            base_amount *= 0.85  # Penalty, not bonus!
        elif cents == 99:
            base_amount *= 0.90  # Penalty, not bonus!
        
        # Additional minor adjustments could go here
        
        return base_amount
    
    def calculate_reimbursement(self, days, miles, receipts):
        """
        Main calculation using decision tree logic
        """
        category, base_amount = self.classify_case(days, miles, receipts)
        
        # Apply any fine-tuning adjustments
        final_amount = self.apply_adjustments(base_amount, days, miles, receipts, category)
        
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_v2.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculatorV2()
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