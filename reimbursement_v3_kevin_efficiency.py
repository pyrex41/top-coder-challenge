#!/usr/bin/env python3
"""
Reimbursement Calculator V3 - Kevin's Efficiency Model
Based on Kevin's systematic analysis from interviews:
- 180-220 miles/day efficiency sweet spot
- Receipt processing with .49/.99 penalties
- High-mileage bonuses for business efficiency
"""

import sys
import math

class ReimbursementCalculatorV3:
    def __init__(self):
        # Kevin's efficiency insights
        self.efficiency_sweet_spot_min = 180.0
        self.efficiency_sweet_spot_max = 220.0
        self.efficiency_bonus_multiplier = 1.15
        
        # Base per diem from data analysis
        self.base_per_diem = 107.0
        
        # Mileage tiers from analysis
        self.mileage_rates = [
            (100, 0.48),   # 0-100 miles
            (300, 0.71),   # 100-300 miles  
            (600, 0.85),   # 300-600 miles
            (1000, 0.95),  # 600-1000 miles
            (float('inf'), 1.1)  # 1000+ miles (efficiency bonus)
        ]
        
        # Receipt processing - Lisa's insights about $600-800 sweet spot
        self.receipt_tiers = [
            (50, 0.3),     # Low receipts penalty
            (200, 0.6),    # Building up
            (600, 0.8),    # Good treatment starts
            (800, 0.9),    # Sweet spot  
            (1200, 0.85),  # Diminishing returns
            (2000, 0.75),  # High penalty
            (float('inf'), 0.65)  # Very high penalty
        ]
        
        # Day bonuses - corrected based on data (no 5-day bonus!)
        self.day_multipliers = {
            1: 1.4,   # Single day premium
            2: 1.2,   # Short trip premium
            3: 1.15,  # Short trip premium
            4: 1.1,   # Slight premium
            # 5-7 days: base rate (no special bonus)
            8: 0.95,  # Long trip slight penalty
            9: 0.95,
            10: 0.93,
            11: 0.93,
            12: 0.91,
            13: 0.90,
            14: 0.90
        }
    
    def calculate_mileage_component(self, miles):
        """Calculate mileage reimbursement with tiered rates"""
        total = 0
        remaining_miles = miles
        
        for threshold, rate in self.mileage_rates:
            if remaining_miles <= 0:
                break
                
            miles_in_tier = min(remaining_miles, threshold - sum(t for t, r in self.mileage_rates[:self.mileage_rates.index((threshold, rate))]))
            if miles_in_tier > 0:
                total += miles_in_tier * rate
                remaining_miles -= miles_in_tier
        
        return total
    
    def calculate_receipt_component(self, receipts, days):
        """Calculate receipt reimbursement with tiers"""
        for threshold, rate in self.receipt_tiers:
            if receipts <= threshold:
                return receipts * rate
        return receipts * 0.65  # Fallback
    
    def apply_efficiency_bonus(self, base_amount, days, miles):
        """Apply Kevin's efficiency bonus for optimal miles/day"""
        if days == 0:
            return base_amount
            
        miles_per_day = miles / days
        
        # Kevin's sweet spot: 180-220 miles/day
        if self.efficiency_sweet_spot_min <= miles_per_day <= self.efficiency_sweet_spot_max:
            return base_amount * self.efficiency_bonus_multiplier
        
        # Gradual falloff outside sweet spot
        if 150 <= miles_per_day < 180:
            bonus = 1.0 + (miles_per_day - 150) / 150 * 0.15
            return base_amount * bonus
        elif 220 < miles_per_day <= 300:
            bonus = 1.15 - (miles_per_day - 220) / 160 * 0.15
            return base_amount * max(bonus, 1.0)
        
        return base_amount
    
    def apply_receipt_penalties(self, amount, receipts):
        """Apply the confirmed .49/.99 penalties"""
        cents = int(round((receipts % 1) * 100))
        
        if cents == 49:
            return amount * 0.85  # Penalty
        elif cents == 99:
            return amount * 0.90  # Penalty
        
        return amount
    
    def calculate_reimbursement(self, days, miles, receipts):
        """Main calculation using Kevin's efficiency model"""
        
        # Base per diem component
        per_diem_component = self.base_per_diem * days
        
        # Mileage component with tiers
        mileage_component = self.calculate_mileage_component(miles)
        
        # Receipt component with sweet spot processing
        receipt_component = self.calculate_receipt_component(receipts, days)
        
        # Combine components
        base_amount = per_diem_component + mileage_component + receipt_component
        
        # Apply day-based multipliers
        day_multiplier = self.day_multipliers.get(days, 1.0)
        base_amount *= day_multiplier
        
        # Apply Kevin's efficiency bonus
        base_amount = self.apply_efficiency_bonus(base_amount, days, miles)
        
        # Apply receipt cent penalties
        final_amount = self.apply_receipt_penalties(base_amount, receipts)
        
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_v3_kevin_efficiency.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculatorV3()
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