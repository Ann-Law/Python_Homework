"""
Unit tests for Problem 2: BankAccount

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the BankAccount object
(e.g., balance, status, transaction_history, summary) to verify state consistency.

Running tests:
    python -m unittest test_problem2.py -v
"""
import unittest
from problem2 import BankAccount


class TestBankAccount(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.account_empty = BankAccount("ACC001", "Alice", initial_balance=0.0, overdraft_limit=100.0)
        self.account_funded = BankAccount("ACC002", "Bob", initial_balance=200.0, overdraft_limit=50.0)

    def test_initial_state_multi_attributes(self):
        """
        Verify that a newly created account initializes all attributes correctly.
        Check balance, owner, status, overdraft_limit, transaction_history, and summary.
        """
        # Test empty account
        # TODO: implement it
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.owner, "Alice")
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.overdraft_limit, 100.0)
        self.assertEqual(len(self.account_empty.transaction_history), 0)

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 0.0)
        self.assertEqual(summary["status"], "ACTIVE")
        self.assertEqual(summary["transaction_count"], 0)

        # Test funded account
        # TODO: implement it
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.owner, "Bob")
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(self.account_funded.overdraft_limit, 50.0)
        self.assertEqual(len(self.account_funded.transaction_history), 1)
        self.assertEqual(self.account_funded.transaction_history[0]["type"], "INITIAL_DEPOSIT")
        self.assertEqual(self.account_funded.transaction_history[0]["amount"], 200.0)

        summary2 = self.account_funded.get_summary()
        self.assertEqual(summary2["balance"], 200.0)
        self.assertEqual(summary2["transaction_count"], 1)
        

    def test_deposit_updates_multiple_attributes(self):
        """
        Test that deposit correctly updates balance, transaction_history, and summary.
        """
        # TODO: Implement test: deposit $150 into self.account_empty
        result = self.account_empty.deposit(150.0)

        self.assertTrue(result)
        self.assertEqual(self.account_empty.balance, 150.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "DEPOSIT")
        self.assertEqual(self.account_empty.transaction_history[0]["amount"], 150.0)
        self.assertEqual(self.account_empty.transaction_history[0]["balance_after"], 150.0)

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 150.0)
        self.assertEqual(summary["transaction_count"], 1)

    def test_withdrawal_within_balance_multi_attributes(self):
        """
        Test withdrawal when sufficient positive balance exists.
        """
        # TODO: Implement test: withdraw $50 with a $2.50 fee from self.account_funded
        result = self.account_funded.withdraw(50.0, fee=2.50)

        self.assertTrue(result)
        # balance = 200 - 50 - 2.50 = 147.50
        self.assertEqual(self.account_funded.balance, 147.50)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        # 1 initial deposit + 1 withdrawal = 2 transactions
        self.assertEqual(len(self.account_funded.transaction_history), 2)
        withdrawal = self.account_funded.transaction_history[-1]
        self.assertEqual(withdrawal["type"], "WITHDRAWAL")
        self.assertEqual(withdrawal["amount"], 50.0)
        self.assertEqual(withdrawal["fee"], 2.50)
        self.assertEqual(withdrawal["balance_after"], 147.50)

        summary = self.account_funded.get_summary()
        self.assertEqual(summary["balance"], 147.5)
        self.assertEqual(summary["transaction_count"], 2)

    def test_overdraft_withdrawal_and_status_transition(self):
        """
        Test withdrawal that uses overdraft protection (balance becomes negative but >= -overdraft_limit).
        """
        # TODO: Implement test: withdraw $50 from self.account_empty (which has 0 balance, limit 100)
        result = self.account_empty.withdraw(50.0)

        self.assertTrue(result)
        # balance = 0 - 50 = -50.0
        self.assertEqual(self.account_empty.balance, -50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "WITHDRAWAL")

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], -50.0)
        self.assertEqual(summary["status"], "OVERDRAWN")

    def test_deposit_recovering_from_overdrawn_status(self):
        """
        Test that depositing enough money to bring balance >= 0 transitions status from OVERDRAWN to ACTIVE.
        """
        # TODO: Implement test
        self.account_empty.withdraw(80.0)
        self.assertEqual(self.account_empty.balance, -80.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")

        # Now deposit $100 → balance = 20, should go back to ACTIVE
        self.account_empty.deposit(100.0)
        self.assertEqual(self.account_empty.balance, 20.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        # withdrawal + deposit = 2 transactions
        self.assertEqual(len(self.account_empty.transaction_history), 2)

        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 20.0)
        self.assertEqual(summary["status"], "ACTIVE")
    def test_transfer_between_accounts_multi_attributes(self):
        """
        Test fund transfer between two accounts.
        """
        # TODO: Implement test: transfer $50 from account_funded to account_empty with $5 fee
        result = self.account_funded.transfer_to(self.account_empty, 50.0, transfer_fee=5.0)

        self.assertTrue(result)
        # Sender: 200 - 50 - 5 = 145
        self.assertEqual(self.account_funded.balance, 145.0)
        self.assertEqual(self.account_funded.status, "ACTIVE")
        # Receiver: 0 + 50 = 50
        self.assertEqual(self.account_empty.balance, 50.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")
        # Sender: 1 initial + 1 withdrawal = 2
        self.assertEqual(len(self.account_funded.transaction_history), 2)
        # Receiver: 0 + 1 deposit = 1
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "DEPOSIT")

    def test_frozen_account_restrictions(self):
        """
        Test that a FROZEN account rejects deposits, withdrawals, and transfers with RuntimeError.
        """
        # TODO: Implement test: freeze account and verify exceptions with self.assertRaises(RuntimeError)
        self.account_empty.freeze()
        self.assertEqual(self.account_empty.status, "FROZEN")

        # Deposit should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.deposit(100.0)

        # Withdraw should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.withdraw(10.0)

        # Transfer from frozen account should raise RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.transfer_to(self.account_funded, 10.0)

        # Balance should be unchanged after failed operations
        self.assertEqual(self.account_empty.balance, 0.0)

        # Unfreeze and verify status restored correctly (balance=0 → ACTIVE)
        self.account_empty.unfreeze()
        self.assertEqual(self.account_empty.status, "ACTIVE")

    def test_invalid_operations_raise_exceptions(self):
        """
        Test exception handling
        """
        # TODO: Implement exception tests using self.assertRaises()
        with self.assertRaises(ValueError):
            self.account_funded.deposit(-10.0)
        with self.assertRaises(ValueError):
            self.account_funded.deposit(0)

        # Withdraw amount <= 0
        with self.assertRaises(ValueError):
            self.account_funded.withdraw(-10.0)

        # Negative fee
        with self.assertRaises(ValueError):
            self.account_funded.withdraw(10.0, fee=-5.0)

        # Withdraw exceeding overdraft limit (empty account has limit=100)
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(150.0)  # would go to -150, exceeds -100 limit

        # Transfer to non-BankAccount
        with self.assertRaises(TypeError):
            self.account_funded.transfer_to("not_an_account", 50.0)

        # Transfer amount <= 0
        with self.assertRaises(ValueError):
            self.account_funded.transfer_to(self.account_empty, 0)

        # Transfer to a frozen account
        self.account_empty.freeze()
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(self.account_empty, 50.0)

        # Constructor: negative initial balance
        with self.assertRaises(ValueError):
            BankAccount("ACC999", "Charlie", initial_balance=-10.0)

        # Constructor: negative overdraft limit
        with self.assertRaises(ValueError):
            BankAccount("ACC999", "Charlie", overdraft_limit=-10.0)


if __name__ == "__main__":
    unittest.main()
