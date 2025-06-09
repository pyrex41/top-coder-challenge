#!/usr/bin/env python3
"""
Wrapper script to run comprehensive MiniZinc diagnostic with proper environment setup
"""

import os
import sys

def setup_environment():
    """Set up MiniZinc environment"""
    minizinc_path = "/workspace/MiniZincIDE-2.9.3-bundle-linux-x86_64/bin"
    if minizinc_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{minizinc_path}:{os.environ.get('PATH', '')}"
    
    print(f"✅ MiniZinc PATH set: {minizinc_path}")

def main():
    """Main execution with environment setup"""
    
    print("=== COMPREHENSIVE MINIZINC DIAGNOSTIC (With Environment Setup) ===")
    
    # Set up environment
    setup_environment()
    
    # Test MiniZinc is working
    import subprocess
    try:
        result = subprocess.run(["minizinc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MiniZinc version: {result.stdout.strip()}")
        else:
            print(f"❌ MiniZinc test failed: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ MiniZinc not found: {e}")
        return
    
    # Now run the comprehensive diagnostic
    print("\n🚀 Starting comprehensive diagnostic search...")
    
    # Import and run the diagnostic class
    from comprehensive_minizinc_diagnostic import DiagnosticMiniZincSearch
    
    search = DiagnosticMiniZincSearch()
    winner, results = search.run_comprehensive_diagnostic()
    
    if winner:
        print(f"\n🏆 FINAL RESULT: {winner} solved the challenge!")
    else:
        print(f"\n🔍 ANALYSIS COMPLETE")
        print("Use failure patterns to guide next iteration of models")

if __name__ == "__main__":
    main()