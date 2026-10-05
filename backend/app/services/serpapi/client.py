from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx


class SerpApiError(RuntimeError):
    pass


class SerpApiClient:
    def __init__(self, api_key: str, timeout_seconds: float = 25.0) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://serpapi.com/search.json"
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> SerpApiClient:
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def search(self, *, engine: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise SerpApiError("SERPAPI_API_KEY is not configured")
        if self._client is None:
            raise SerpApiError("SerpApiClient must be used as an async context manager")

        request_params = {
            "engine": engine,
            "api_key": self.api_key,
            "no_cache": "false",
            **params,
        }

        try:
            response = await self._client.get(self.base_url, params=request_params)
        except httpx.TimeoutException as exc:
            raise SerpApiError(f"SerpApi timed out for engine {engine}") from exc
        except httpx.HTTPError as exc:
            raise SerpApiError(f"SerpApi request failed for engine {engine}") from exc

        if response.status_code != 200:
            raise SerpApiError(f"SerpApi returned HTTP {response.status_code} for engine {engine}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise SerpApiError(f"SerpApi returned invalid JSON for engine {engine}") from exc

        if not isinstance(payload, dict):
            raise SerpApiError(f"SerpApi returned an unexpected payload for engine {engine}")
        if error := payload.get("error"):
            raise SerpApiError(f"{engine}: {error}")

        return payload
