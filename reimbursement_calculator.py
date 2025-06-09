#!/usr/bin/env python3
"""
Reimbursement Calculator Implementation
Based on analysis of 1000 public cases and employee interviews
Updated based on failure analysis
"""

import sys
import math

class ReimbursementCalculator:
    def __init__(self):
        # Parameters discovered from data analysis
        
        # Base per diem (from analysis: ~$107)
        self.base_per_diem = 106.71
        
        # Mileage rates (tiered system)
        self.mile_rate_tier1 = 0.48  # 0-100 miles
        self.mile_rate_tier2 = 0.60  # 100+ miles
        self.mile_threshold1 = 100
        
        # Receipt processing (complex tiers)
        self.receipt_rate_low = 0.2     # Penalty for very low receipts
        self.receipt_rate_medium = 0.4  # Medium receipts
        self.receipt_rate_high = 0.3    # High receipts (diminishing returns)
        self.receipt_low_threshold = 50.0
        self.receipt_high_threshold = 1000.0
        
        # Day-length factors (ONLY for multi-day trips, NOT 1-day!)
        self.day_factors = {
            2: 1.10,   # 2-day trips get slight bonus
            3: 1.00,   # 3-day trips (baseline)
            4: 0.95,   # 4-day trips
            5: 0.90,   # 5-day trips  
            6: 0.85,   # 6-day trips
            7: 0.80,   # 7-day trips
            8: 0.75,   # 8+ day trips (penalty)
        }
        
        # Special parameters for 1-day trips (completely different formula)
        self.oneday_base = 50.0        # Lower base for 1-day trips
        self.oneday_mile_rate = 1.2    # Higher mileage rate for 1-day
        self.oneday_receipt_rate = 0.5 # Different receipt handling
        
        # Special bonuses
        self.five_day_bonus = 15.0      # 5-day "sweet spot" bonus
        
        # Quirk bonuses (from interviews) 
        self.cents_49_bonus = 0.51
        self.cents_99_bonus = 0.01
        
    def calculate_mileage(self, miles):
        """Calculate mileage reimbursement using tiered rates"""
        if miles <= self.mile_threshold1:
            return miles * self.mile_rate_tier1
        else:
            return (self.mile_threshold1 * self.mile_rate_tier1 + 
                   (miles - self.mile_threshold1) * self.mile_rate_tier2)
    
    def calculate_receipts(self, receipts):
        """Calculate receipt reimbursement with penalty/bonus tiers"""
        if receipts < self.receipt_low_threshold:
            # Penalty for very low receipts
            return receipts * self.receipt_rate_low
        elif receipts <= self.receipt_high_threshold:
            # Medium treatment
            return (self.receipt_low_threshold * self.receipt_rate_low +
                   (receipts - self.receipt_low_threshold) * self.receipt_rate_medium)
        else:
            # Diminishing returns for high receipts
            return (self.receipt_low_threshold * self.receipt_rate_low +
                   (self.receipt_high_threshold - self.receipt_low_threshold) * self.receipt_rate_medium +
                   (receipts - self.receipt_high_threshold) * self.receipt_rate_high)
    
    def get_day_factor(self, days):
        """Get the day-length multiplier factor"""
        if days <= 8:
            return self.day_factors.get(days, self.day_factors[8])
        else:
            # Very long trips get even lower factors
            return max(0.6, self.day_factors[8] - (days - 8) * 0.02)
    
    def calculate_quirks(self, receipts):
        """Calculate quirk bonuses based on receipt cents"""
        cents = int(round((receipts - int(receipts)) * 100))
        if cents == 49:
            return self.cents_49_bonus
        elif cents == 99:
            return self.cents_99_bonus
        else:
            return 0.0
    
    def calculate_oneday_trip(self, miles, receipts):
        """
        Special calculation for 1-day trips (completely different formula)
        Based on analysis showing 1-day trips don't use day factors
        """
        # Different base calculation for 1-day trips
        base = self.oneday_base
        
        # Different mileage calculation
        mileage = miles * self.oneday_mile_rate
        
        # Different receipt handling (seems to cap at certain level)
        if receipts <= 100:
            receipt_reimb = receipts * 0.8  # Good rate for low receipts
        else:
            # High receipts get capped/penalized more heavily
            receipt_reimb = 100 * 0.8 + (receipts - 100) * self.oneday_receipt_rate
        
        total = base + mileage + receipt_reimb
        
        # VACATION PENALTY: High mileage + high receipts gets severely penalized
        # This is the key insight from the data analysis!
        if miles >= 1000 and receipts >= 1500:
            # Severe penalty for "vacation-like" 1-day trips
            total *= 0.4  # Reduce by 60%
        elif miles >= 1000 and receipts >= 500:
            # Moderate penalty for high mileage + moderate receipts
            total *= 0.75  # Reduce by 25%
        elif miles >= 1000:
            # Small penalty for just high mileage
            total *= 0.9   # Reduce by 10%
        
        # Add quirks
        total += self.calculate_quirks(receipts)
        
        return total
    
    def calculate_reimbursement(self, days, miles, receipts):
        """
        Main calculation function
        
        Args:
            days (int): Trip duration in days
            miles (float): Miles traveled
            receipts (float): Total receipt amount
            
        Returns:
            float: Calculated reimbursement amount
        """
        # 1-day trips use completely different formula
        if days == 1:
            return round(self.calculate_oneday_trip(miles, receipts), 2)
        
        # Multi-day trips use the original approach
        base = days * self.base_per_diem
        mileage = self.calculate_mileage(miles)
        receipt_reimb = self.calculate_receipts(receipts)
        
        subtotal = base + mileage + receipt_reimb
        
        # Apply day-length factor
        day_factor = self.get_day_factor(days)
        day_adjusted = subtotal * day_factor
        
        # Add special bonuses
        bonuses = 0.0
        if days == 5:
            bonuses += self.five_day_bonus
            
        # Add quirk bonuses
        bonuses += self.calculate_quirks(receipts)
        
        final_amount = day_adjusted + bonuses
        
        return round(final_amount, 2)

def main():
    """Main function for command line interface"""
    if len(sys.argv) != 4:
        print("Usage: python reimbursement_calculator.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        calculator = ReimbursementCalculator()
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