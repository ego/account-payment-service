"""API tests."""

from decimal import Decimal
from unittest.mock import patch

from django.db import transaction
from django.test import Client, TestCase, TransactionTestCase

from payments import errors
from payments.models import Account, Payment
from payments.service import AccountPayment


class TestBase:
    """Base test class."""

    @classmethod
    def setUpTestData(cls):  # pylint: disable=C0103
        """Create some data for tests."""
        cls.account_usd1 = Account.objects.create(name="account_usd1", balance=Decimal("300"), currency=Account.USD)
        cls.account_usd2 = Account.objects.create(name="account_usd2", balance=Decimal("100"), currency=Account.USD)
        cls.account_uah1 = Account.objects.create(name="account_uah1", balance=Decimal("100"), currency=Account.UAH)

    def setUp(self):  # pylint: disable=C0103
        """Create request client."""
        self.client = Client()


class TestAccountAPI(TestBase, TestCase):
    """Test account API endpoints."""

    def test_api_get_account(self):
        """Test API endpoint GET `/api/v1/accounts/`."""
        response = self.client.get("/api/v1/accounts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)

    def test_api_get_account_neg(self):
        """Test API endpoint GET `/api/v1/accounts/`."""
        response = self.client.get("/api/v1/accounts/10/")
        self.assertEqual(response.status_code, 404)

    def test_api_post_account(self):
        """Test API endpoint POST `/api/v1/accounts/`."""
        response = self.client.post(
            "/api/v1/accounts/", dict(name="account_rub1", balance=Decimal("100"), currency=Account.RUB)
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["name"] == "account_rub1")

        # Test unique name
        response2 = self.client.post(
            "/api/v1/accounts/", dict(name="account_rub1", balance=Decimal("100"), currency=Account.RUB)
        )
        self.assertEqual(response2.status_code, 400)

    def test_api_post_account_neg(self):
        """Test API endpoint POST `/api/v1/accounts/`."""
        response = self.client.post(
            "/api/v1/accounts/", dict(name="account_rub1", balance=Decimal("100"), currency="TEST")
        )
        self.assertEqual(response.status_code, 400)

    def test_api_put_account(self):
        """Test API PUT."""
        response = self.client.put(f"/api/v1/accounts/{self.account_usd1.id}/", {"name": "test"})
        self.assertEqual(response.status_code, 405)


class TestPaymentAPI(TestBase, TestCase):
    """Test payment API endpoints."""

    def test_api_post_payment_outgoing(self):
        """Test API endpoint POST `/api/v1/payments/`.

        Initial state:
        account_usd1 = 300 USD
        account_usd2 = 100 USD

        Payment:
        account:    account_usd1
        direction:  outgoing
        amount:     100
        to_account: account_usd2

        Expected result:
        account_usd1 balance: 300 - 100 = 200
        account_usd2 balance: 100 + 100 = 200
        """
        response = self.client.post(
            "/api/v1/payments/",
            dict(
                account_id=self.account_usd1.id,
                direction=Payment.OUTGOING,
                amount="100",
                to_account_id=self.account_usd2.id,
            ),
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["id"])

        response2 = self.client.get("/api/v1/payments/")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.json()["results"]), 1)

        account_usd1 = self.client.get(f"/api/v1/accounts/{self.account_usd1.id}/").json()
        account_usd2 = self.client.get(f"/api/v1/accounts/{self.account_usd2.id}/").json()
        self.assertTrue(account_usd1["balance"] == Decimal("200"))
        self.assertTrue(account_usd2["balance"] == Decimal("200"))

    def test_api_post_payment_incoming(self):
        """Test API endpoint POST `/api/v1/payments/`.

        Initial state:
        account_usd1 = 300 USD
        account_usd2 = 100 USD

        Payment:
        account:    account_usd1
        direction:  incoming
        amount:     100
        to_account: account_usd2

        Expected result:
        account_usd1 balance: 300 + 100 = 400
        account_usd2 balance: 100 - 100 = 0
        """
        response = self.client.post(
            "/api/v1/payments/",
            dict(
                account_id=self.account_usd1.id,
                direction=Payment.INCOMING,
                amount="100",
                to_account_id=self.account_usd2.id,
            ),
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["id"])

        response2 = self.client.get("/api/v1/payments/")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.json()["results"]), 1)

        account_usd1 = self.client.get(f"/api/v1/accounts/{self.account_usd1.id}/").json()
        account_usd2 = self.client.get(f"/api/v1/accounts/{self.account_usd2.id}/").json()
        self.assertTrue(account_usd1["balance"] == Decimal("400"))
        self.assertTrue(account_usd2["balance"] == Decimal("0"))

    def test_api_post_payment_neg_currency(self):
        """Test API endpoint POST `/api/v1/payments/`.

        Case: payment with different accounts currency.
        Initial state:
        account_usd1 = 300 USD
        account_uah1 = 100 UAH

        Payment:
        account:    account_usd1
        direction:  outgoing
        amount:     100
        to_account: account_uah1

        Expected result:
        account_usd1 balance = 300 USD
        account_uah1 balance = 100 UAH
        """
        response = self.client.post(
            "/api/v1/payments/",
            dict(
                account_id=self.account_usd1.id,
                direction=Payment.OUTGOING,
                amount="100",
                to_account_id=self.account_uah1.id,
            ),
        )
        self.assertEqual(response.status_code, 400)

        account_usd1 = self.client.get(f"/api/v1/accounts/{self.account_usd1.id}/").json()
        account_usd2 = self.client.get(f"/api/v1/accounts/{self.account_usd2.id}/").json()
        self.assertTrue(account_usd1["balance"] == Decimal("300"))
        self.assertTrue(account_usd2["balance"] == Decimal("100"))

    def test_api_put_payment(self):
        """Test API endpoint PUT `/api/v1/payments/id/`."""
        response = self.client.post(
            "/api/v1/payments/",
            dict(
                account_id=self.account_usd1.id,
                direction=Payment.OUTGOING,
                amount="100",
                to_account_id=self.account_usd2.id,
            ),
        )
        self.assertEqual(response.status_code, 201)
        pid = response.json()["id"]
        self.assertTrue(pid)

        response2 = self.client.put(f"/api/v1/payments/{pid}/", {"amount": Decimal("1")})
        self.assertEqual(response2.status_code, 405)


class TestAccountPayment(TestBase, TransactionTestCase):
    """Test account payment transaction."""

    @classmethod
    def setUpClass(cls):
        """Create some data for tests."""
        super().setUpClass()
        cls.setUpTestData()

    def test_payment_concurrent(self):
        """Mock method check_balance and test transaction."""
        payment1 = dict(
            account_id=self.account_usd1.id,
            direction=Payment.OUTGOING,
            amount=Decimal("200"),
            to_account_id=self.account_usd2.id,
        )
        payment2 = dict(
            account_id=self.account_usd1.id,
            direction=Payment.OUTGOING,
            amount=Decimal("200"),
            to_account_id=self.account_usd2.id,
        )

        with self.assertRaises(errors.AccountPaymentTransactionError):
            with patch.object(AccountPayment, "check_balance", return_value=None):
                with transaction.atomic():
                    AccountPayment.transaction(**payment1)
                    AccountPayment.transaction(**payment2)
        # Account balance must not be changed
        self.assertEqual(self.account_usd1.balance, Account.objects.get(id=self.account_usd1.id).balance)
