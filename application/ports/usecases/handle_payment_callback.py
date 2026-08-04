from abc import ABC, abstractmethod

from application.dto.payment import (
    PaymentCallbackCommand,
)


class ABCHandlePaymentCallbackUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        command: PaymentCallbackCommand,
    ) -> None:
        raise NotImplementedError
