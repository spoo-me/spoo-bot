"""Exception hierarchy.

SpooApiError tree mirrors API failure modes; cogs never branch on status
codes — they catch these types. NotLinkedError is bot-side only.
"""

from __future__ import annotations


class SpooBotError(Exception):
    """Base for all spoobot exceptions."""


class NotLinkedError(SpooBotError):
    """Raised when a linked-account command runs for an unlinked user."""


class SpooApiError(SpooBotError):
    def __init__(self, message: str, *, status: int = 0) -> None:
        super().__init__(message)
        self.status = status


class ApiValidationError(SpooApiError):
    """400/422 — bad input (invalid URL, taken alias, bad params)."""


class AuthRequiredError(SpooApiError):
    """401 — missing/expired/invalid token."""


class GrantRevokedError(SpooApiError):
    """401 with revoked-grant semantics on device refresh — relink needed."""


class ForbiddenError(SpooApiError):
    """403 — authenticated but not allowed (not the owner, scope missing)."""


class NotFoundError(SpooApiError):
    """404 — unknown short code / url id."""


class PasswordRequiredError(SpooApiError):
    """401/403 on stats for a password-protected URL without password."""


class RateLimitedError(SpooApiError):
    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        super().__init__(message, status=429)
        self.retry_after = retry_after


class ServerError(SpooApiError):
    """5xx from the API."""
