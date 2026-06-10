from __future__ import annotations

import httpx

from spoobot.errors import (
    ApiValidationError,
    AuthRequiredError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
    ServerError,
    SpooApiError,
)

USER_AGENT = "spoo-bot/2.0 (+https://github.com/spoo-me/spoo-bot)"


def create_client(
    *,
    base_url: str = "",
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.AsyncClient:
    """One factory for every outbound client — UA, timeouts, HTTP/2 in one place."""
    return httpx.AsyncClient(
        base_url=base_url,
        transport=transport,
        timeout=httpx.Timeout(30.0, connect=10.0),
        headers={"User-Agent": USER_AGENT},
        follow_redirects=False,
    )


def _error_message(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        for key in ("message", "detail", "error"):
            if isinstance(data, dict) and isinstance(data.get(key), str):
                return data[key]
    except Exception:
        pass
    return f"API request failed with HTTP {resp.status_code}"


def raise_for_status_mapped(resp: httpx.Response) -> None:
    """Map non-2xx responses to the spoobot exception hierarchy.

    Sync on purpose: httpx non-streaming responses are fully read.
    """
    status = resp.status_code
    if status < 400:
        return
    message = _error_message(resp)
    if status in (400, 422):
        raise ApiValidationError(message, status=status)
    if status == 401:
        raise AuthRequiredError(message, status=401)
    if status == 403:
        raise ForbiddenError(message, status=403)
    if status == 404:
        raise NotFoundError(message, status=404)
    if status == 429:
        retry_raw = resp.headers.get("Retry-After")
        retry_after = (
            float(retry_raw)
            if retry_raw and retry_raw.replace(".", "", 1).isdigit()
            else None
        )
        raise RateLimitedError(message, retry_after=retry_after)
    if status >= 500:
        raise ServerError(message, status=status)
    raise SpooApiError(message, status=status)
