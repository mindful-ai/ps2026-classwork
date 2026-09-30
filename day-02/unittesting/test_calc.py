import unittest
from calc import Calculator

c = Calculator() # DUT

class TestCasesForCalculator(unittest.TestCase): # Test Suite/ Test Bench

    # Write your test as simple python functions

    def test_add(self):
        self.assertEqual(c.add(10,3), 13, "Error in addition")

    def test_subtract(self):
        self.assertEqual(c.subtract(10, 3), 7, "Error in subtraction")

    def test_multiply(self):
        self.assertEqual(c.multiply(10, 3), 30, "Error in multiplication")

    # Normal Case
    def test_divide(self):
        self.assertEqual(c.divide(12, 4), 3, "Error in division")

    # Corner Case
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            c.divide(10, 0)

if __name__ == "__main__":
    unittest.main()