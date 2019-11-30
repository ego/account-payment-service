"""Models data layer."""

from django.db import models


class Account(models.Model):
    """Account table representations."""

    USD = "USD"
    UAH = "UAH"
    RUB = "RUB"
    CURRENCY_TYPE_CHOICES = ((USD, f"USA {USD}"), (UAH, f"Ukraine {UAH}"), (RUB, f"Russia {RUB}"))

    name = models.CharField(unique=True, max_length=512)
    balance = models.DecimalField(max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=50, choices=CURRENCY_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # pylint: disable=C0111
        managed = False
        db_table = "account"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} (id{self.id})"


class Payment(models.Model):
    """Payment table representations."""

    OUTGOING = "outgoing"
    INCOMING = "incoming"
    DIRECTION_TYPE_CHOICES = ((OUTGOING, f"{OUTGOING} (-)"), (INCOMING, f"{INCOMING} (+)"))

    account = models.ForeignKey(Account, models.DO_NOTHING, related_name="payments")
    to_account = models.ForeignKey(Account, models.DO_NOTHING, related_name="payments_to")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    direction = models.CharField(max_length=8, choices=DIRECTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # pylint: disable=C0111
        managed = False
        db_table = "payment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.account_id} -> {self.to_account_id}"
