import uuid

class Account:
    
    def __init__(self, name, email, acc_type, balance=0.0, acc_no=None):
        self.name = name
        self.email = email
        self.acc_type = acc_type
        self.balance = balance
        self.acc_no = acc_no or str(uuid.uuid4())[:8]

    def to_dict(self):
        return {
            "acc_no": self.acc_no,
            "name": self.name,
            "email": self.email,
            "acc_type": self.acc_type,
            "balance": self.balance
        }

    @staticmethod
    def from_dict(data):
        return Account(
            name=data["name"],
            email=data["email"],
            acc_type=data["acc_type"],
            balance=data["balance"],
            acc_no=data["acc_no"]
        )
