from __future__ import annotations

from spoobot.cogs.getcode import LANGUAGES, TEMPLATE_DIR, render_snippet


def test_every_language_has_a_template():
    missing = [
        n
        for n, (stem, _) in LANGUAGES.items()
        if not (TEMPLATE_DIR / f"{stem}.tmpl").exists()
    ]
    assert missing == []


def test_render_substitutes_url():
    code, tag = render_snippet(
        "Python", url="https://example.com", alias=None, password=None, max_clicks=None
    )
    assert "https://example.com" in code
    assert "api/v1/shorten" in code
    assert tag == "py"
