"""DRF serializers."""

from decimal import Decimal

from rest_framework import serializers

from payments import errors
from payments.models import Account, Payment


class AccountSerializer(serializers.ModelSerializer):
    """DRF Account serializer."""

    class Meta:  # pylint: disable=C0111
        model = Account
        fields = ["id", "name", "balance", "currency", "created_at"]
        read_only_fields = ["created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    """DRF Payment serializer."""

    account_id = serializers.IntegerField()
    to_account_id = serializers.IntegerField()

    class Meta:  # pylint: disable=C0111
        model = Payment
        fields = ["id", "account_id", "direction", "amount", "to_account_id", "created_at"]
        read_only_fields = ["created_at"]

    def validate_amount(self, value):  # pylint: disable=R0201
        """Check that amount > 0."""
        if value <= Decimal(0):
            raise errors.AccountAmountError
        return value

    def validate(self, data):
        """Validate payment directions."""
        data = super().validate(data)
        if data["account_id"] == data["to_account_id"]:
            raise errors.AccountSelfError
        return data
