"""
Test Runner for Naruto Jutsu Recognition System
Runs all unit tests and generates a test report.
"""

import unittest
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_tests(verbosity=2):
    """
    Run all unit tests for the Naruto Jutsu Recognition System.
    
    Args:
        verbosity: Test output verbosity level (0=quiet, 1=normal, 2=verbose)
        
    Returns:
        TestResult object
    """
    print("=" * 70)
    print("Naruto Jutsu Recognition System - Unit Test Suite")
    print("=" * 70)
    print()
    
    # Discover and load all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    print(f"Running tests from: {start_dir}")
    print()
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Time: {end_time - start_time:.2f}s")
    print("=" * 70)
    
    if result.wasSuccessful():
        print()
        print("✅ All tests passed!")
        print()
    else:
        print()
        print("❌ Some tests failed. Review the output above for details.")
        print()
    
    return result


if __name__ == '__main__':
    # Run with verbose output
    result = run_tests(verbosity=2)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
