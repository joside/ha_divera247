"""Small client for the DIVERA 24/7 API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import API_LAST_ALARM

REQUEST_TIMEOUT = 10


class DiveraError(Exception):
    """Generic error talking to DIVERA 24/7."""


class DiveraAuthError(DiveraError):
    """The access key was rejected."""


class DiveraClient:
    """Fetch data from DIVERA 24/7 with a personal or unit access key."""

    def __init__(self, session: aiohttp.ClientSession, accesskey: str) -> None:
        self._session = session
        self._accesskey = accesskey

    async def async_get_last_alarm(self) -> dict[str, Any] | None:
        """Return the last alarm, or None if there is none."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(
                    API_LAST_ALARM, params={"accesskey": self._accesskey}
                )
                if response.status in (401, 403):
                    raise DiveraAuthError("Access key rejected")
                if response.status == 404:
                    # No alarm available
                    return None
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except DiveraError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise DiveraError(f"Error communicating with DIVERA 24/7: {err}") from err

        if not isinstance(payload, dict):
            raise DiveraError("Unexpected response from DIVERA 24/7")
        if payload.get("success") is False:
            errors = str(payload.get("errors", ""))
            if "accesskey" in errors.lower() or "zugriff" in errors.lower():
                raise DiveraAuthError(errors)
            return None

        # The API wraps the alarm in "data"; fall back to the plain payload.
        alarm = payload.get("data", payload)
        if not isinstance(alarm, dict) or not alarm.get("id"):
            return None
        return alarm
