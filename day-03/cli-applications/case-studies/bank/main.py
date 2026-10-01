from services.bank_service import BankService

def menu():
    print("\n==== Bank Menu ====")
    print("1. Create Account")
    print("2. View Account")
    print("3. Update Account")
    print("4. Deposit")
    print("5. Withdraw")
    print("6. Delete Account")
    print("7. List All Accounts")
    print("0. Exit")

def main():
    service = BankService()

    while True:
        menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Name: ")
            email = input("Email: ")
            acc_type = input("Account Type (savings/current): ")
            acc_no = service.create_account(name, email, acc_type)
            print(f"Account created. Account No: {acc_no}")

        elif choice == "2":
            acc_no = input("Enter Account No: ")
            acc = service.get_account(acc_no)
            if acc:
                print(vars(acc))
            else:
                print("Account not found.")

        elif choice == "3":
            acc_no = input("Enter Account No: ")
            name = input("New Name (leave blank to skip): ")
            email = input("New Email (leave blank to skip): ")
            success = service.update_account(acc_no, name or None, email or None)
            print("Updated." if success else "Account not found.")

        elif choice == "4":
            acc_no = input("Enter Account No: ")
            amount = float(input("Amount to deposit: "))
            success = service.deposit(acc_no, amount)
            print("Deposited." if success else "Failed.")

        elif choice == "5":
            acc_no = input("Enter Account No: ")
            amount = float(input("Amount to withdraw: "))
            success = service.withdraw(acc_no, amount)
            print("Withdrawn." if success else "Insufficient balance or account not found.")

        elif choice == "6":
            acc_no = input("Enter Account No: ")
            success = service.delete_account(acc_no)
            print("Deleted." if success else "Account not found.")

        elif choice == "7":
            accounts = service.list_accounts()
            for acc in accounts:
                print(acc)

        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
