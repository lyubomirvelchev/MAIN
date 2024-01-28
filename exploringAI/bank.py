# import numpy as np
#
#
# class Account:
#     """
#         This class represents a bank account. It has a name and a balance. Its methods are:
#         withdraw(amount) - withdraws money from the account
#         deposit(amount) - deposits money into the account
#         get_balance() - returns the current balance
#     """
#     def __init__(self, name, balance):
#         self.name = name
#         self.balance = balance
#
#     def withdraw(self, amount):
#         """
#         Withdraws money from the account. If there are not enough funds, it returns an error message. If the amount is
#         negative, it returns an error message.
#
#         :param amount: The ammount to withdraw
#         :type amount: float
#
#         :return: The new balance or an error message
#         :rtype: float or str
#         """
#         if amount < 0:
#             return 'Amount must be positive'
#         if amount > self.balance:
#             return 'Amount must be positive'
#         self.balance -= amount
#         return self.balance
#
#     def deposit(self, amount):
#         """
#         Deposits money into the account. If the amount is negative, it returns an error message.
#
#         :param amount: The ammount to deposit
#         :type amount: float
#         :return: The new balance or an error message
#         :rtype: float or str
#         """
#         if amount < 0:
#             return 'Amount must be positive'
#         self.balance += amount
#         return self.balance
#
#     def get_balance(self):
#         """
#         Returns the current balance of the account
#
#         :return: The current balance
#         :rtype: float
#         """
#         return round(self.balance, 2)
#
#
# class Bank:
#     """
#         This class represents a bank. It has a name, a transfer commission and a create account commission. Its methods are:
#         create_account(name, balance) - creates an account with the given name and balance
#         transfer(from_name, to_name, amount) - transfers money from one account to another
#         get_account_balance(name) - returns the balance of the account with the given name
#         get_bank_balance() - returns the bank balance
#
#         :param name: The name of the bank
#         :type name: str
#         :param transfer_commission: The commission for a transfer
#         :type transfer_commission: float
#         :param create_account_commission: The commission for creating an account
#         :type create_account_commission: float
#     """
#     def __init__(self, name, transfer_commission, create_account_commission):
#         self.name = name
#         self.transfer_commission = transfer_commission
#         self.create_account_commission = create_account_commission
#         self.accounts = {}
#         self.bank_balance = 0
#
#     def create_account(self, name, balance):
#         """
#         Creates an account with the given name and balance
#
#         :param name: The name of the account
#         :type name: str
#         :param balance: The balance of the account
#         :type balance: float
#
#         :return: The new bank balance or an error message
#         :rtype: float or str
#         """
#         name = str(name)
#         if name in self.accounts:
#             return 'Account already exists'
#         if balance < 0:
#             return 'Balance must be positive'
#         else:
#             self.accounts[name] = Account(name, balance)
#             self.bank_balance += self.create_account_commission
#
#     def transfer(self, from_name, to_name, amount):
#         """
#             Transfers money from one account to another. Checks if the accounts exist and if the sender has enough funds.
#             If the amount is negative, it returns an error message.
#
#         :param from_name: the name of the sender
#         :param to_name: the name of the receiver
#         :param to_name: the amount to transfer
#
#         :param amount: The ammount to transfer
#         :type amount: float
#         :return: The new bank balance or an error message
#         :rtype: float or str
#         """
#         from_name = str(from_name)
#         to_name = str(to_name)
#         if from_name not in self.accounts or to_name not in self.accounts:
#             return 'Account does not exist'
#         self.accounts[from_name].withdraw(amount)
#         commision = self.transfer_commission * amount
#         self.bank_balance += commision
#         self.accounts[to_name].deposit(amount - commision)
#
#     def get_account_balance(self, name):
#         """
#         Returns the balance of the account with the given name
#
#         :param name: The name of the account
#         :type name: str
#
#         :return: The balance of the account
#         :rtype: float
#         """
#         return self.accounts[name].get_balance()
#
#     def get_bank_balance(self):
#         """
#         Returns the bank balance
#
#         :return: The bank balance
#         :rtype: float
#         """
#         return round(self.bank_balance, 2)
#
#
# bank = Bank('My Bank', 0.02, 10)
#
# # generate 100000 accounts with random balance between 0 and 10000
#
# for i in range(100000):
#     amount = np.random.uniform(0, 10000)
#     if amount < 10:
#         amount = 10
#     bank.create_account(i, amount)
#
#
# def transefer_all_money_from_highest_account_to_lowest():
#     """
#     Transfers all money from the highest account to the lowest account
#
#     """
#     highest_account = max(bank.accounts, key=lambda x: bank.accounts[x].balance)
#     print("highest accound Id:", highest_account)
#     print("highest accound balance:", bank.accounts[highest_account].balance)
#     lowest_account = min(bank.accounts, key=lambda x: bank.accounts[x].balance)
#     print("lowest accound Id:", lowest_account)
#     print("lowest accound balance:", bank.accounts[lowest_account].balance)
#     balance = bank.accounts[highest_account].balance
#     bank.transfer(highest_account, lowest_account, bank.accounts[highest_account].balance)
#     print("highest accound balance after transfer:", bank.accounts[highest_account].balance)
#     print("lowest accound balance after transfer:", bank.accounts[lowest_account].balance)
#     print("bank balance after transfer:", bank.get_bank_balance())
#     print('Commision:', bank.transfer_commission * balance)
#
# def transefer_all_money_from_lowest_account_to_highest():
#     """
#     Transfers all money from the lowest account to the highest account
#
#     :return:
#     """
#     lowest_accont = min(bank.accounts, key=lambda x: bank.accounts[x].balance)
#     if bank.accounts[lowest_accont].balance < 10:
#         return 'Lowest account balance is less than 10'
#
#     highest_account = max(bank.accounts, key=lambda x: bank.accounts[x].balance)
#     balance = bank.accounts[lowest_accont].balance
#     bank.transfer(lowest_accont, highest_account, bank.accounts[lowest_accont].balance)
#     print("highest accound balance after transfer:", bank.accounts[highest_account].balance)
#     print("lowest accound balance after transfer:", bank.accounts[lowest_accont].balance)
#     print("bank balance after transfer:", bank.get_bank_balance())
#
#
# #  perform random transfers between accounts untill bank balance is increased by 20 %
#
# def transfer_at_random():
#     counter = 0
#     bank_balance_at_start = bank.get_bank_balance()
#     target = bank_balance_at_start + 0.2 * bank_balance_at_start
#     print("Bank balance at start:", bank_balance_at_start)
#     print("Target bank balance:", target)
#     while bank.get_bank_balance() < target:
#         from_account = str(np.random.randint(0, 100000))
#         to_account = str(np.random.randint(0, 100000))
#         if from_account == to_account:
#             continue
#         amount = np.random.uniform(0, 10000)
#         print('from acxcoumt id:', from_account)
#         print('to account Id:', to_account)
#         print('Amount:', amount)
#         bank.transfer(from_account, to_account, amount)
#         commision = bank.transfer_commission * amount
#         print('Commision:', commision)
#         print("Money until target:", target - bank.get_bank_balance())
#         counter += 1
#         print('Number of transfers:', counter)
#         print("----------------------------------")
#
#     print("Bank balance at the end:", bank.get_bank_balance())
#
#
# import unittest
#
# class TestBank(unittest.TestCase):
#     def setUp(self):
#         self.bank = Bank("Test Bank", 0.05, 1.0)
#         self.bank.create_account("Alice", 100.0)
#         self.bank.create_account("Bob", 50.0)
#
#     def test_create_account(self):
#         # Test creating an account with a positive balance
#         self.assertEqual(self.bank.create_account("Charlie", 200.0), None)
#         self.assertEqual(self.bank.get_bank_balance(), 201.0)
#         self.assertEqual(self.bank.get_account_balance("Charlie"), 200.0)
#
#         # Test creating an account with a negative balance
#         self.assertEqual(self.bank.create_account("David", -50.0), "Balance must be positive")
#         self.assertEqual(self.bank.get_bank_balance(), 201.0)
#         self.assertNotIn("David", self.bank.accounts)
#
#         # Test creating an account that already exists
#         self.assertEqual(self.bank.create_account("Alice", 500.0), "Account already exists")
#         self.assertEqual(self.bank.get_bank_balance(), 201.0)
#         self.assertEqual(self.bank.get_account_balance("Alice"), 100.0)
#
#     def test_transfer(self):
#         # Test transferring a positive amount between existing accounts
#         self.assertEqual(self.bank.transfer("Alice", "Bob", 50.0), None)
#         self.assertEqual(self.bank.get_bank_balance(), 103.0)
#         self.assertEqual(self.bank.get_account_balance("Alice"), 50.0)
#         self.assertEqual(self.bank.get_account_balance("Bob"), 100.0)
#
#         # Test transferring a negative amount
#         self.assertEqual(self.bank.transfer("Bob", "Alice", -50.0), "Amount must be positive")
#         self.assertEqual(self.bank.get_bank_balance(), 103.0)
#         self.assertEqual(self.bank.get_account_balance("Alice"), 50.0)
#         self.assertEqual(self.bank.get_account_balance("Bob"), 100.0)
#
#         # Test transferring from a non-existent account
#         self.assertEqual(self.bank.transfer("Charlie", "Alice", 50.0), "Account does not exist")
#         self.assertEqual(self.bank.get_bank_balance(), 103.0)
#         self.assertEqual(self.bank.get_account_balance("Alice"), 50.0)
#         self.assertEqual(self.bank.get_account_balance("Bob"), 100.0)
#
#         # Test transferring to a non-existent account
#         self.assertEqual(self.bank.transfer("Alice", "Charlie", 50.0), "Account does not exist")
#         self.assertEqual(self.bank.get_bank_balance(), 103.0)
#         self.assertEqual(self.bank.get_account_balance("Alice"), 50.0)
#         self.assertEqual(self.bank.get_account_balance("Bob"), 100.0)
#
#     def test_get_account_balance(self):
#         # Test getting the balance of an existing account
#         self.assertEqual(self.bank.get_account_balance("Alice"), 100.0)
#
#         # Test getting the balance of a non-existent account
#         self.assertRaises(KeyError, self.bank.get_account_balance, "Charlie")
#
#     def test_get_bank_balance(self):
#         # Test getting the bank balance
#         self.assertEqual(self.bank.get_bank_balance(), 101.0)
#
# if __name__ == '__main__':
#     unittest.main()
#
