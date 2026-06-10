from __future__ import annotations

import pytest
from aiohttp.test_utils import TestClient, TestServer

from spoobot.services.auth import LinkError, LinkResult
from spoobot.web.server import make_app


class FakeAuth:
    def __init__(self):
        self.completed = []
        self.raises: Exception | None = None

    async def complete_link(self, *, code: str, state: str) -> LinkResult:
        if self.raises:
            raise self.raises
        self.completed.append((code, state))
        return LinkResult(discord_user_id=1, spoo_email="z@example.com", interaction_token="itok")


class FakeNotifier:
    def __init__(self):
        self.calls = []

    async def __call__(self, result: LinkResult) -> None:
        self.calls.append(result)


@pytest.fixture
async def client():
    auth, notifier = FakeAuth(), FakeNotifier()
    app = make_app(auth, on_linked=notifier)
    c = TestClient(TestServer(app))
    await c.start_server()
    yield c, auth, notifier
    await c.close()


async def test_callback_success(client):
    c, auth, notifier = client
    resp = await c.get("/callback", params={"code": "abc", "state": "n.1.9999999999.sig"})
    assert resp.status == 200
    assert "linked" in (await resp.text()).lower()
    assert auth.completed == [("abc", "n.1.9999999999.sig")]
    assert len(notifier.calls) == 1


async def test_callback_missing_params(client):
    c, _, _ = client
    resp = await c.get("/callback")
    assert resp.status == 400


async def test_callback_link_error_renders_failure(client):
    c, auth, notifier = client
    auth.raises = LinkError("expired")
    resp = await c.get("/callback", params={"code": "x", "state": "y"})
    assert resp.status == 400
    assert "expired" in (await resp.text()).lower()
    assert notifier.calls == []


async def test_health(client):
    c, _, _ = client
    resp = await c.get("/health")
    assert resp.status == 200
    assert await resp.json() == {"status": "ok"}
