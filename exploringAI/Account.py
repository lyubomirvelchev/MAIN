# Define the Account class to represent individual accounts
class Account:
    def __init__(self, name, amount):
        """Initializes a new account with the given name and balance.

        Args:
            name (str): The name of the account holder.
            amount (float): The initial balance of the account.

        Returns:
            None.

        Raises:
            None.

        """
        self.name = name  # Name of the account holder
        self.balance = amount  # Balance in the account

    def withdraw(self, amount):
        """Withdraws a specified amount from the account balance.

        Args:
            amount (float): The amount to withdraw from the account balance.

        Returns:
            None.

        Raises:
            None.

        """
        if amount > self.balance:
            print("Insufficient funds")
        else:
            self.balance = self.balance - amount
            print("Withdrawal successful")

    def deposit(self, amount):
        """Deposits a specified amount into the account balance.

        Args:
            amount (float): The amount to deposit into the account balance.

        Returns:
            None.

        Raises:
            None.

        """
        if amount < 0:
            print("Invalid amount")
        else:
            self.balance = self.balance + amount
            print("Deposit successful")

    def check_balance(self):
        """Returns the current balance in the account.

        Args:
            None.

        Returns:
            balance (float): The current balance in the account.

        Raises:
            None.

        """
        return round(self.balance, 2)


# Define the Bank class to represent the bank as a whole
class Bank:
    def __init__(self, balance, create_account_tax, transfer_tax):
        """Initializes a new bank with the given initial balance and transaction fees.

        Args:
            balance (float): The initial balance of the bank.
            create_account_tax (float): The fee to charge for creating a new account.
            transfer_tax (float): The percentage fee to charge for each transfer.

        Returns:
            None.

        Raises:
            None.

        """
        self.balance = balance  # Total balance of the bank
        self.create_account_tax = create_account_tax  # Fee for creating a new account
        self.transfer_tax_percent = transfer_tax  # Percentage fee for each transfer
        self.accounts = {}  # Dictionary to hold all account objects

    def create_account(self, name, amount):
        """Creates a new account with the given name and initial balance.

        Args:
            name (str): The name of the account holder.
            amount (float): The initial balance of the account.

        Returns:
            None.

        Raises:
            None.

        """
        if amount < self.create_account_tax:
            print("Invalid amount")
        else:
            self.balance = self.balance + self.create_account_tax  # Add the account creation fee to the bank's balance
            self.accounts[name] = Account(name,
                                          amount - self.create_account_tax)  # Create a new Account object with the given name and initial balance minus the account creation fee

    def transfer(self, from_account, to_account, amount):
        """Transfers a specified amount from one account to another, with a fee applied to the transfer.

        Args:
            from_account (str): The name of the account to transfer funds from.
            to_account (str): The name of the account to transfer funds to.
            amount (float): The amount to transfer.

        Returns:
            None.

        Raises:
            None.

        """
        if from_account not in self.accounts or to_account not in self.accounts:
            print("Invalid account")
        elif amount > self.accounts[from_account].balance:
            print("Insufficient funds")
        else:
            commision = amount * self.transfer_tax_percent
            self.accounts[from_account].withdraw(amount)
            self.accounts[to_account].deposit(amount - commision)
            self.balance = self.balance + commision
            print("Transfer successful")

    def check_balance(self):
        """
        Returns the current balance of the bank.

        Args:
            None.


        Returns:
            balance (float): The current balance of the bank.

        Raises:
            None.

        """
        return round(self.balance, 2)


import random

bank = Bank(100000, 10, 0.02)
for i in range(10000):
    amount = random.randint(10, 10000)
    bank.create_account(i, amount)

bank_balance = bank.check_balance()
target = bank_balance * 1.2
count = 0

while bank.check_balance() < target:

    from_account = random.choice(list(bank.accounts.keys()))
    to_account = random.choice(list(bank.accounts.keys()))
    if from_account == to_account:
        continue

    amount = random.randint(100, 10000)
    bank.transfer(from_account, to_account, amount)
    count += 1
    print('From account: ', from_account, 'To account: ', to_account, 'Amount: ', amount)
    print("Money until target is met", round(target - bank.check_balance(), 2))
    print("Number of transfers: ", count)
    print("----------------------------------")

print("DONE")
print("Bank balance: ", bank.check_balance())
