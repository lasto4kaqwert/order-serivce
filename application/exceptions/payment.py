class PaymentError(Exception):
    pass


class PaymentUnavailableError(PaymentError):
    pass


class PaymentRejectedError(PaymentError):
    pass


class InvalidPaymentResponseError(PaymentError):
    pass
