from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

import httpx


class HttpClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/") + "/"
        self._headers = {
            "x-api-key": api_key,
        }

    def _build_url(
        self,
        path: str,
    ) -> str:
        return urljoin(self._base_url, path.lstrip("/"))

    async def _get(
        self,
        path: str,
    ) -> httpx.Response:
        return await self._client.get(
            self._build_url(path),
            headers=self._headers,
        )

    async def _post(
        self,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        return await self._client.post(
            self._build_url(path),
            headers=self._headers,
            json=payload,
        )
