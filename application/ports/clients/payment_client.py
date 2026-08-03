from abc import ABC, abstractmethod

from application.dto.payment import (
    CreatePaymentCommand,
    PaymentItem,
)


class ABCPaymentClient(ABC):
    @abstractmethod
    async def create_payment(
        self,
        payment: CreatePaymentCommand
    ) -> PaymentItem:
        raise NotImplementedError
