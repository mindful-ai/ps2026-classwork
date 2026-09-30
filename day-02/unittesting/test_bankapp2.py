import unittest
from bank import BankAccount

class TestBankAccount(unittest.TestCase):

    # Run once before all tests, used to initialize shared/expensive resources
    @classmethod
    def setUpClass(cls):
        """Runs once before any test method."""
        cls.account = BankAccount("Alice", 1000)

    def test_initial_balance(self):
        self.assertEqual(self.account.get_balance(), 1000)

    def test_deposit_valid_amount(self):
        self.account.deposit(500)
        self.assertEqual(self.account.get_balance(), 1500)

    def test_withdraw_valid_amount(self):
        self.account.withdraw(200)
        self.assertEqual(self.account.get_balance(), 1300)

    def test_withdraw_exceeding_balance(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(2000)

    # Once after all tests, clean up shared state
    @classmethod
    def tearDownClass(cls):
        """Runs once after all tests."""
        print(f"Final balance for {cls.account.owner}: {cls.account.get_balance()}")


if __name__ == "__main__":
    unittest.main()