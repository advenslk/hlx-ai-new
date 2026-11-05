"""
HELZERX AI Support - Automated Test Suite Runner
Discovers and executes all unit, security, AI, and ticket tests.
"""
import unittest
import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import individual test suites
from tests.test_security import TestSecurityControls
from tests.test_ai_engine import TestAIEngine
from tests.test_knowledge import TestKnowledgeBase
from tests.test_tickets import TestTicketSystem


def run_all_tests() -> bool:
    print("\n" + "=" * 65)
    print("  HELZERX AI SUPPORT - AUTOMATED TEST SUITE")
    print("=" * 65)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSecurityControls))
    suite.addTests(loader.loadTestsFromTestCase(TestAIEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBase))
    suite.addTests(loader.loadTestsFromTestCase(TestTicketSystem))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 65)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed:          {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:        {len(result.failures)}")
    print(f"Errors:          {len(result.errors)}")
    print("=" * 65 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
