from dataclasses import dataclass
from typing import Optional

@dataclass
class Account:
    account_id: str
    name: str
    balance: float = 0.0

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0 or amount > self.balance:
            raise ValueError("Invalid withdrawal amount.")
        self.balance -= amount
