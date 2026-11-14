"""
ASTRA Test Suite Runner
Executes automated tests using pytest (or standard unittest fallback).
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication

# Ensure QApp exists for any QObject signals during testing
app = QApplication.instance() or QApplication(sys.argv)

try:
    import pytest
    print("Running test suite via pytest...")
    ret = pytest.main(["-v", "astra/tests"])
    sys.exit(ret)
except ImportError:
    print("Pytest not installed; running standard unittest suite...")
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover("astra/tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
