import json
import uuid
import os
from typing import Dict
from .models import Account
from .security import hash_pin, verify_pin

DATA_FILE = "accounts.json"
PIN_MAP_FILE = "pin_hashes.json"

accounts: Dict[str, Account] = {}
pin_map: Dict[str, str] = {}

def load_data():
    global accounts, pin_map
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            accounts = {k: Account(**v) for k, v in data.items()}
    else:
        accounts = {}

    if os.path.exists(PIN_MAP_FILE):
        with open(PIN_MAP_FILE, "r") as f:
            pin_map = json.load(f)
    else:
        pin_map = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({k: vars(v) for k, v in accounts.items()}, f, indent=2)
    with open(PIN_MAP_FILE, "w") as f:
        json.dump(pin_map, f, indent=2)

def create_account(name: str, pin: str) -> Account:
    load_data()
    account_id = str(uuid.uuid4())[:8]
    pin_hash = hash_pin(pin)
    acc = Account(account_id, name)
    accounts[account_id] = acc
    pin_map[account_id] = pin_hash
    save_data()
    return acc

def authenticate(account_id: str, pin: str) -> Account:
    load_data()
    if account_id not in accounts:
        raise ValueError("Account not found.")
    if not verify_pin(pin, pin_map[account_id]):
        raise ValueError("Invalid PIN.")
    return accounts[account_id]

def deposit(account_id: str, pin: str, amount: float) -> Account:
    acc = authenticate(account_id, pin)
    acc.deposit(amount)
    accounts[account_id] = acc
    save_data()
    return acc

def withdraw(account_id: str, pin: str, amount: float) -> Account:
    acc = authenticate(account_id, pin)
    acc.withdraw(amount)
    accounts[account_id] = acc
    save_data()
    return acc

def update_name(account_id: str, pin: str, new_name: str) -> Account:
    acc = authenticate(account_id, pin)
    acc.name = new_name
    accounts[account_id] = acc
    save_data()
    return acc

def list_accounts():
    load_data()
    return list(accounts.values())
