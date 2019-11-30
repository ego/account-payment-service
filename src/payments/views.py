"""DRF views layer."""

from rest_framework import mixins, viewsets
from rest_framework.response import Response

from payments.models import Account, Payment
from payments.serializers import AccountSerializer, PaymentSerializer
from payments.service import AccountPayment


class CreateListRetrieveViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """A viewset that provides `retrieve`, `create`, and `list` actions."""


class AccountViewSet(CreateListRetrieveViewSet):
    """API endpoint that allows create and view `Accounts`.

    Provide only **create** and view operation.
    You can not modify accounts.
    """

    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class PaymentViewSet(CreateListRetrieveViewSet):
    """API endpoint that allows **create** and view `Payments`.

    You can transfer money from one account to the another.
    If all condition will pass the payment will be created.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):
        """Create payment transaction."""
        serializer = self.serializer_class(data=request.data)
        # Validate data
        serializer.is_valid(raise_exception=True)
        # Make payment
        payment = AccountPayment.transaction(**serializer.validated_data)
        serializer = self.serializer_class(payment)
        return Response(serializer.data, status=201)
