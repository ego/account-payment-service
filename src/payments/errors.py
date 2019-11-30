"""Base API errors."""

from rest_framework.exceptions import APIException, ValidationError


class AccountBalanceError(APIException):
    """Account balance error."""

    status_code = 400
    default_detail = "Error, not enough balance!"
    default_code = "bad_request"


class AccountCurrencyError(APIException):
    """Account currency error."""

    status_code = 400
    default_detail = "Error, accounts must be the same currency!"
    default_code = "bad_request"


class AccountAmountError(ValidationError):
    """Account amount error."""

    status_code = 400
    default_detail = "Error, the amount must be greater than 0!"
    default_code = "bad_request"


class AccountSelfError(ValidationError):
    """Account directions error."""

    status_code = 400
    default_detail = "The account value must be different from the to_account value."
    default_code = "bad_request"


class AccountPaymentTransactionError(APIException):
    """Account payment transaction error."""

    status_code = 409
    default_detail = "Error, account payment transaction conflict!"
    default_code = "conflict"
