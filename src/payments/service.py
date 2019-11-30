"""Business logic for account payments transaction.

Separate application logic out models and view representations.
"""

from decimal import Decimal
from typing import Tuple, Union

from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F
from django.db.transaction import TransactionManagementError

from payments import errors
from payments.models import Account, Payment

DirectionType = Union[Payment.OUTGOING, Payment.OUTGOING]


class AccountPayment:
    """Base class for making payments.

    Making transaction from one account to the another.
    """

    @classmethod
    def transaction(cls, *, account_id: int, direction: DirectionType, amount: Decimal, to_account_id: int) -> Payment:
        """Public transaction interface.

        This method make two things:
          * Payment.OUTGOING - take the amount from the account A (withdraw)
          * Payment.INCOMING - put this amount into the account B (deposit)

        Before call this method make simple check:
          * amount > 0
          * account != to_account

        This method validate:
          * account balance - amount <= 0
          * same currency for account A and account B
          * account A/account B has enough balance
        """
        # Start transaction
        try:
            with transaction.atomic():
                # Lock two rows
                account1 = cls.select_for_update(account_id)
                account2 = cls.select_for_update(to_account_id)
                # Determine payment direction
                credit_account, deposit_account = cls.determine_direction(direction, account1, account2)
                # Check balance and currency
                cls.check_balance(credit_account, amount)
                cls.check_currency(credit_account, deposit_account)
                # Change money
                credit_account.balance = F("balance") - amount
                deposit_account.balance = F("balance") + amount
                credit_account.save(update_fields=["balance"])
                deposit_account.save(update_fields=["balance"])
                # Create payment
                payment = Payment.objects.create(
                    account_id=account_id, direction=direction, amount=amount, to_account_id=to_account_id
                )
                return payment
        # On exception transaction already have been rolled back safely
        except (IntegrityError, TransactionManagementError, DatabaseError):
            raise errors.AccountPaymentTransactionError

    @classmethod
    def select_for_update(cls, account_id: int) -> Account:
        """Read and write lock row in table account."""
        return Account.objects.select_for_update().get(id=account_id)

    @classmethod
    def determine_direction(cls, direction: DirectionType, account1: int, account2: int) -> Tuple[Account, Account]:
        """Determine payment direction."""
        if Payment.OUTGOING == direction:
            return account1, account2
        return account2, account1

    @classmethod
    def check_balance(cls, credit_account: Account, amount: Decimal) -> None:
        """Check account balance."""
        if credit_account.balance - amount < 0:
            raise errors.AccountBalanceError

    @classmethod
    def check_currency(cls, credit_account: Account, deposit_account: Account) -> None:
        """Check currency of two accounts."""
        if credit_account.currency != deposit_account.currency:
            raise errors.AccountCurrencyError
