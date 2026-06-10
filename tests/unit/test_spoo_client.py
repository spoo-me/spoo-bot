from __future__ import annotations

import json

import httpx
import pytest

from spoobot.errors import ApiValidationError, AuthRequiredError
from spoobot.infrastructure.http import create_client
from spoobot.services.spoo_client import SpooClient

BASE = "https://spoo.test"


class FakeApi:
    """Route table + request recorder for MockTransport."""

    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], httpx.Response] = {}
        self.requests: list[httpx.Request] = []

    def on(
        self, method: str, path: str, *, status: int = 200, body: dict | None = None
    ) -> None:
        self.routes[(method, path)] = httpx.Response(status, json=body or {})

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        key = (request.method, request.url.path)
        if key not in self.routes:
            return httpx.Response(404, json={"message": f"no fake route {key}"})
        return self.routes[key]


@pytest.fixture
def api() -> FakeApi:
    return FakeApi()


@pytest.fixture
async def client(api):
    http = create_client(base_url=BASE, transport=httpx.MockTransport(api.handler))
    yield SpooClient(http)
    await http.aclose()


async def test_shorten_anon(client, api):
    api.on(
        "POST",
        "/api/v1/shorten",
        status=201,
        body={
            "alias": "abc",
            "short_url": f"{BASE}/abc",
            "long_url": "https://example.com",
            "created_at": 1704067200,
            "status": "ACTIVE",
        },
    )
    result = await client.shorten("https://example.com")
    assert result.alias == "abc"
    assert result.short_url.endswith("/abc")
    sent = json.loads(api.requests[0].content)
    assert sent == {"long_url": "https://example.com"}  # no None fields leaked


async def test_shorten_sends_bearer_when_token_given(client, api):
    api.on(
        "POST",
        "/api/v1/shorten",
        status=201,
        body={
            "alias": "x",
            "short_url": f"{BASE}/x",
            "long_url": "https://e.com",
        },
    )
    await client.shorten("https://e.com", token="tok-1")
    assert api.requests[0].headers["Authorization"] == "Bearer tok-1"


async def test_shorten_anon_sends_no_auth_header(client, api):
    api.on(
        "POST",
        "/api/v1/shorten",
        status=201,
        body={
            "alias": "x",
            "short_url": f"{BASE}/x",
            "long_url": "https://e.com",
        },
    )
    await client.shorten("https://e.com")
    assert "Authorization" not in api.requests[0].headers


async def test_taken_alias_maps_to_validation_error(client, api):
    api.on("POST", "/api/v1/shorten", status=400, body={"message": "alias taken"})
    with pytest.raises(ApiValidationError, match="alias taken"):
        await client.shorten("https://e.com", alias="taken")


async def test_list_urls_parses_camel_case(client, api):
    api.on(
        "GET",
        "/api/v1/urls",
        body={
            "items": [{"id": "a" * 24, "alias": "x", "long_url": "https://e.com"}],
            "page": 1,
            "pageSize": 10,
            "total": 1,
            "hasNext": False,
        },
    )
    page = await client.list_urls("tok", page=1, page_size=10)
    assert page.has_next is False and page.items[0].alias == "x"
    q = dict(api.requests[0].url.params)
    assert q["pageSize"] == "10" and q["sortBy"] == "created_at"


async def test_list_urls_requires_token(client):
    with pytest.raises(AuthRequiredError):
        await client.list_urls(None)  # type: ignore[arg-type]


async def test_stats_series_helper(client, api):
    api.on(
        "GET",
        "/api/v1/stats",
        body={
            "scope": "anon",
            "group_by": ["browser"],
            "timezone": "UTC",
            "summary": {
                "total_clicks": 5,
                "unique_clicks": 3,
                "avg_redirection_time": 1.0,
            },
            "metrics": {
                "clicks_by_browser": [
                    {"browser": "Chrome", "clicks": 5, "clicks_percentage": 100.0}
                ]
            },
            "short_code": "abc",
        },
    )
    res = await client.stats(
        scope="anon", short_code="abc", group_by=["browser"], metrics=["clicks"]
    )
    assert res.series("clicks", "browser") == [("Chrome", 5)]


async def test_emojify_uses_legacy_route(client, api):
    api.on("POST", "/emoji", body={"short_url": f"{BASE}/😀😀"})
    result = await client.emojify("https://e.com")
    assert "😀" in result.short_url
