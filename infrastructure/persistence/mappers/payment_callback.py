from application.dto.payment import ProcessedPaymentCallback
from domain.entities import PaymentStatus
from infrastructure.persistence.models.payment_callback import (
    PaymentCallbackModel,
)


def to_dto(
    model: PaymentCallbackModel
) -> ProcessedPaymentCallback | None:
    return ProcessedPaymentCallback(
        payment_id=model.payment_id,
        order_id=model.order_id,
        status=PaymentStatus(model.status),
        amount=model.amount,
        error_message=model.error_message,
        processed_at=model.processed_at,
    )
