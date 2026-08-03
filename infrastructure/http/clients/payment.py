import httpx
from pydantic import ValidationError
from typing_extensions import override

from application.dto.payment import (
    CreatePaymentCommand,
    PaymentItem,
)
from application.exceptions.payment import (
    InvalidPaymentResponseError,
    PaymentRejectedError,
    PaymentUnavailableError,
)
from application.ports.clients import ABCPaymentClient
from infrastructure.http.http_client import HttpClient
from infrastructure.http.schemas.payment import (
    PaymentCreateRequest,
    PaymentCreateResponse,
)


class HttpPaymentClient(HttpClient, ABCPaymentClient):
    @override
    async def create_payment(
        self,
        payment: CreatePaymentCommand,
    ) -> PaymentItem:
        request_model = PaymentCreateRequest(
            order_id=payment.order_id,
            amount=payment.amount,
            callback_url=payment.callback_url,
            idempotency_key=payment.idempotency_key,
        )

        try:
            response = await self._post(
                "/api/payments",
                payload=request_model.model_dump(mode="json"),
            )
        except httpx.TimeoutException as error:
            raise PaymentUnavailableError(
                "Payments Service timed out"
            ) from error
        except httpx.RequestError as error:
            raise PaymentUnavailableError(
                "Payments Service is unavailable"
            ) from error

        if response.is_server_error:
            raise PaymentUnavailableError(
                "Payments Service returned a server error"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise PaymentRejectedError(
                f"Payments Service rejected the request: "
                f"HTTP {response.status_code}"
            ) from error

        try:
            response_model = PaymentCreateResponse.model_validate_json(
                response.content,
            )
        except ValidationError as error:
            raise InvalidPaymentResponseError(
                "Payments Service returned an invalid response"
            ) from error

        if response_model.order_id != payment.order_id:
            raise InvalidPaymentResponseError(
                "Payments Service returned an unexpected order_id"
            )
        if response_model.amount != payment.amount:
            raise InvalidPaymentResponseError(
                "Payments Service returned an unexpected amount"
            )
        if response_model.idempotency_key != payment.idempotency_key:
            raise InvalidPaymentResponseError(
                "Payments Service returned an unexpected idempotency_key"
            )

        return PaymentItem(
            id=response_model.id,
            user_id=response_model.user_id,
            order_id=response_model.order_id,
            amount=response_model.amount,
            status=response_model.status,
            idempotency_key=response_model.idempotency_key,
            created_at=response_model.created_at,
        )
