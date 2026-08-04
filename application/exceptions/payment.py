class PaymentError(Exception):
    pass


class PaymentUnavailableError(PaymentError):
    pass


class PaymentRejectedError(PaymentError):
    pass


class InvalidPaymentResponseError(PaymentError):
    pass


class PaymentCallbackConflictError(Exception):
    def __init__(
        self,
        payment_id,
        order_id,
    ) -> None:
        self.payment_id = payment_id
        self.order_id = order_id

        super().__init__(
            f"Conflicting callback for payment "
            f"{payment_id} and order {order_id}"
        )
