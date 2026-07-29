import uuid

import httpx
from pydantic import ValidationError
from typing_extensions import override

from application.dto.catalog import CatalogItem
from application.exceptions.catalog import (
    CatalogItemNotFoundError,
    CatalogUnavailableError,
    InvalidCatalogResponseError,
)
from application.ports import ApplicationCatalogClient
from infrastructure.http.http_client import HttpClient
from infrastructure.http.schemas.catalog import CatalogItemResponse


class HttpCatalogClient(HttpClient, ApplicationCatalogClient):
    @override
    async def get_item(
        self,
        item_id: uuid.UUID
    ) -> CatalogItem:
        try:
            response = await self._get(
                f"/api/catalog/items/{item_id}"
            )
        except httpx.TimeoutException as error:
            raise CatalogUnavailableError(
                "Catalog serivce is timeout"
            ) from error
        except httpx.RequestError as error:
            raise CatalogUnavailableError(
                "Catalog service is unavailable"
            ) from error

        if response.status_code == 404:
            raise CatalogItemNotFoundError(
                f"Item {item_id} not found"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise CatalogUnavailableError(
                "Catalog service returned an error"
            ) from error

        try:
            payload = CatalogItemResponse.model_validate_json(
                response.content
            )
        except ValidationError as error:
            raise InvalidCatalogResponseError(
                "Catalog service returned as invalid response"
            ) from error

        if payload.id != item_id:
            raise InvalidCatalogResponseError(
                "Catalog service returned an uxpected item"
            )

        return CatalogItem(
            id=payload.id,
            name=payload.name,
            price=payload.price,
            available_qty=payload.available_qty,
        )
