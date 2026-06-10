from __future__ import annotations

import httpx

from spoobot.infrastructure.http import create_client
from spoobot.services.qr_client import QrClient

BASE = "https://qr.spoo.test"


def _qr_with_recorder(captured: list[httpx.Request]) -> QrClient:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, content=b"\x89PNG fake", headers={"Content-Type": "image/png"})

    return QrClient(create_client(base_url=BASE, transport=httpx.MockTransport(handler)))


async def test_gradient_png():
    captured: list[httpx.Request] = []
    qr = _qr_with_recorder(captured)
    png = await qr.gradient("https://spoo.me/abc", start="#497dff", end="#7289da")
    assert png.startswith(b"\x89PNG")
    assert captured[0].url.path == "/api/v1/gradient"
    assert dict(captured[0].url.params)["start"] == "#497dff"


async def test_classic_png():
    captured: list[httpx.Request] = []
    qr = _qr_with_recorder(captured)
    png = await qr.classic("https://spoo.me/abc", color="black", style="rounded")
    assert png.startswith(b"\x89PNG")
    assert captured[0].url.path == "/api/v1/classic"
