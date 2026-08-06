import httpx
from pydantic import ValidationError
from typing_extensions import override

from application.dto.notification import (
    NotificationItem,
    SendNotificationCommand,
)
from application.exceptions.notification import (
    InvalidNotificationResponseError,
    NotificationRejectedError,
    NotificationUnavailableError,
)
from application.ports.clients.notification_client import (
    ABCNotificationClient,
)
from infrastructure.http.http_client import HttpClient
from infrastructure.http.schemas.notification import (
    NotificationCreateRequest,
    NotificationCreateResponse,
)


class HttpNotificationClient(HttpClient, ABCNotificationClient):
    @override
    async def send_notification(
        self,
        notification: SendNotificationCommand,
    ) -> NotificationItem:
        request_model = NotificationCreateRequest(
            message=notification.message,
            reference_id=notification.reference_id,
            idempotency_key=notification.idempotency_key,
        )

        try:
            response = await self._post(
                "/api/notifications",
                payload=request_model.model_dump(mode="json"),
            )
        except httpx.TimeoutException as error:
            raise NotificationUnavailableError(
                "Notification Service timed out"
            ) from error
        except httpx.RequestError as error:
            raise NotificationUnavailableError(
                "Notification Service is unavailable"
            ) from error

        if response.is_server_error:
            raise NotificationUnavailableError(
                "Notification Service returned a server error"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise NotificationRejectedError(
                "Notification Service rejected the request: "
                f"HTTP {response.status_code}"
            ) from error

        try:
            response_model = (
                NotificationCreateResponse.model_validate_json(
                    response.content
                )
            )
        except ValidationError as error:
            raise InvalidNotificationResponseError(
                "Notification Service returned an invalid response"
            ) from error

        if response_model.reference_id != notification.reference_id:
            raise InvalidNotificationResponseError(
                "Notification Service returned "
                "an unexpected reference_id"
            )

        return NotificationItem(
            id=response_model.id,
            user_id=response_model.user_id,
            message=response_model.message,
            reference_id=response_model.reference_id,
            created_at=response_model.created_at,
        )
