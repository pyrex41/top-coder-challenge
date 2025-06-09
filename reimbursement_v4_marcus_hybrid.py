#!/usr/bin/env python3
"""
Reimbursement Calculator V4 - Marcus's Effort/Hustle Model
Based on Marcus's insights from interviews:
- System rewards "effort" and "hustle" 
- High-mileage days (300+ miles) get bonuses
- Combination of distance and receipt patterns
- Maintains decision tree structure but adds effort bonuses
"""

import sys
import math

class ReimbursementCalculatorV4:
    def __init__(self):
        # Marcus's "hustle" insights
        self.high_effort_miles_per_day = 300.0
        self.hustle_bonus_multiplier = 1.25
        
        # Moderate effort threshold
        self.moderate_effort_miles_per_day = 200.0
        self.moderate_bonus_multiplier = 1.1
        
        # Base components from v2 analysis
        self.receipt_major_threshold = 828.0
        self.base_per_diem = 100.0
        
        # Marcus's mileage insights - tiered with effort bonuses
        self.mileage_tiers = [
            (75, 0.45),    # Conservative start
            (200, 0.55),   # Building momentum  
            (400, 0.75),   # Good business pace
            (600, 0.85),   # High efficiency
            (800, 1.0),    # Marcus's "sweet spot" 
            (float('inf'), 1.2)  # Extreme hustle bonus
        ]
        
        # Receipt processing - Marcus's observations about caps
        self.receipt_rates = [
            (100, 0.4),    # Low receipts
            (300, 0.7),    # Building up
            (600, 0.85),   # Good range
            (1000, 0.9),   # Sweet spot
            (1500, 0.8),   # Diminishing returns
            (2000, 0.7),   # Marcus's "penalty zone"
            (float('inf'), 0.6)  # High penalty
        ]
    
    def calculate_effort_multiplier(self, days, miles):
        """Calculate Marcus's effort/hustle multiplier"""
        if days == 0:
            return 1.0
            
        miles_per_day = miles / days
        
        # High hustle bonus - Marcus's 300+ mile days
        if miles_per_day >= self.high_effort_miles_per_day:
            return self.hustle_bonus_multiplier
        
        # Moderate effort bonus - 200+ mile days  
        elif miles_per_day >= self.moderate_effort_miles_per_day:
            return self.moderate_bonus_multiplier
        
        # Linear scaling for effort between 100-200 miles/day
        elif 100 <= miles_per_day < 200:
            scale = (miles_per_day - 100) / 100
            return 1.0 + (scale * 0.1)
        
        # Low effort penalty for < 100 miles/day
        elif miles_per_day < 100:
            return 0.9
            
        return 1.0
    
    def calculate_mileage_component(self, miles):
        """Tiered mileage calculation"""
        total = 0
        remaining = miles
        prev_threshold = 0
        
        for threshold, rate in self.mileage_tiers:
            if remaining <= 0:
                break
                
            tier_miles = min(remaining, threshold - prev_threshold)
            if tier_miles > 0:
                total += tier_miles * rate
                remaining -= tier_miles
                prev_threshold = threshold
                
        return total
    
    def calculate_receipt_component(self, receipts):
        """Receipt calculation with Marcus's cap insights"""
        for threshold, rate in self.receipt_rates:
            if receipts <= threshold:
                return receipts * rate
        return receipts * 0.6  # High penalty fallback
    
    def apply_day_adjustments(self, amount, days):
        """Day-based adjustments - Marcus mentioned some patterns"""
        if days == 1:
            return amount * 1.3  # Single day premium
        elif days in [2, 3]:
            return amount * 1.15  # Short trip premium
        elif days in [4, 5, 6]:
            return amount * 1.05  # Slight bonus for "normal" trips
        elif days >= 8:
            # Marcus: longer trips can be great if high effort
            return amount * 0.95  # Slight penalty for very long trips
        
        return amount
    
    def apply_receipt_penalties(self, amount, receipts):
        """Marcus noticed some receipt amount penalties"""
        cents = int(round((receipts % 1) * 100))
        
        # Confirmed penalties from data analysis
        if cents == 49:
            return amount * 0.85
        elif cents == 99:
            return amount * 0.90
        
        # Marcus's theory about "round number" penalties
        if receipts == int(receipts):  # Perfectly round amounts
            return amount * 0.95
            
        return amount
    
    def calculate_reimbursement(self, days, miles, receipts):
        """Main calculation combining Marcus's insights with structure"""
        
        # Base per diem
        per_diem_base = self.base_per_diem * days
        
        # Mileage with tiers
        mileage_component = self.calculate_mileage_component(miles)
        
        # Receipt component
        receipt_component = self.calculate_receipt_component(receipts)
        
        # Combine base components
        base_amount = per_diem_base + mileage_component + receipt_component
        
        # Apply Marcus's effort multiplier (key insight!)
        base_amount *= self.calculate_effort_multiplier(days, miles)
        
        # Day adjustments
        base_amount = self.apply_day_adjustments(base_amount, days)
        
        # Receipt penalties
        final_amount = self.apply_receipt_penalties(base_amount, receipts)
        
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_v4_marcus_hybrid.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculatorV4()
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