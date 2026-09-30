import unittest
from bankapp import BankAccount

class TestBankAccount(unittest.TestCase):

    # Ensures a clean, fresh start for every test you write, once before every test
    def setUp(self):
        self.account = BankAccount("Anil", 3000)

    def test_initial_balance(self):
        print(self.account.get_balance())
        self.assertEqual(self.account.get_balance(), 3000)

    def test_deposit_valid_amount(self):
        print(self.account.get_balance())
        self.account.deposit(500)
        self.assertEqual(self.account.get_balance(), 3500)

    def test_deposit_invalid_amount(self):
        print(self.account.get_balance())
        with self.assertRaises(ValueError):
            self.account.deposit(-100)
        self.assertEqual(self.account.get_balance(), 3000)

    def test_withdraw_valid_amount(self):
        print(self.account.get_balance())
        self.account.withdraw(200)
        self.assertEqual(self.account.get_balance(), 2800)

    def test_withdraw_exceeding_balance(self):
        print(self.account.get_balance())
        with self.assertRaises(ValueError):
            self.account.withdraw(100000)
        self.assertEqual(self.account.get_balance(), 3000)

    # Clean up after every test, onnce after each test
    def tearDown(self):
        del self.account

if __name__ == "__main__":
    unittest.main()