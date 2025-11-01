#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for APA Checker
Runs all test script files in the tests/ directory
"""
import sys
import os
import subprocess
import glob

def run_all_tests():
    """Run all test scripts"""
    # Find all test files
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = glob.glob(os.path.join(test_dir, 'test_*.py'))
    
    # Exclude this runner itself
    test_files = [f for f in test_files if not f.endswith('run_all_tests.py')]
    
    print("="*70)
    print(f"Found {len(test_files)} test files")
    print("="*70)
    
    passed = 0
    failed = 0
    
    # Run each test file
    for test_file in sorted(test_files):
        test_name = os.path.basename(test_file)
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print('='*70)
        
        try:
            # Run the test script - output goes directly to console
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=os.path.dirname(test_dir),
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode == 0:
                print(f"\n[PASS] {test_name}")
                passed += 1
            else:
                print(f"\n[FAIL] {test_name} (exit code: {result.returncode})")
                failed += 1
                
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {str(e)}")
            failed += 1
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*70)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
