from models.account import Account
from storage.file_store import FileStore

class BankService:
    
    def __init__(self):
        self.store = FileStore()

    def create_account(self, name, email, acc_type):
        acc = Account(name, email, acc_type)
        accounts = self.store.load_accounts()
        accounts.append(acc.to_dict())
        self.store.save_accounts(accounts)
        return acc.acc_no

    def get_account(self, acc_no):
        accounts = self.store.load_accounts()
        for acc in accounts:
            if acc["acc_no"] == acc_no:
                return Account.from_dict(acc)
        return None

    def update_account(self, acc_no, name=None, email=None):
        accounts = self.store.load_accounts()
        for acc in accounts:
            if acc["acc_no"] == acc_no:
                if name:
                    acc["name"] = name
                if email:
                    acc["email"] = email
                self.store.save_accounts(accounts)
                return True
        return False

    def deposit(self, acc_no, amount):
        accounts = self.store.load_accounts()
        for acc in accounts:
            if acc["acc_no"] == acc_no:
                acc["balance"] += amount
                self.store.save_accounts(accounts)
                return True
        return False

    def withdraw(self, acc_no, amount):
        accounts = self.store.load_accounts()
        for acc in accounts:
            if acc["acc_no"] == acc_no and acc["balance"] >= amount:
                acc["balance"] -= amount
                self.store.save_accounts(accounts)
                return True
        return False

    def delete_account(self, acc_no):
        accounts = self.store.load_accounts()
        new_accounts = [acc for acc in accounts if acc["acc_no"] != acc_no]
        if len(accounts) == len(new_accounts):
            return False
        self.store.save_accounts(new_accounts)
        return True

    def list_accounts(self):
        return self.store.load_accounts()
