"""Small client for the DIVERA 24/7 API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_LAST_ALARM, API_PULL_ALL

REQUEST_TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class DiveraError(Exception):
    """Generic error talking to DIVERA 24/7."""


class DiveraAuthError(DiveraError):
    """The access key was rejected."""


def _collection_names(raw: Any) -> dict[str, str]:
    """{id: name} from an id-keyed object or a list of objects."""
    if isinstance(raw, dict):
        items = [
            {**value, "id": value.get("id", key)} if isinstance(value, dict) else {"id": key, "name": value}
            for key, value in raw.items()
        ]
    elif isinstance(raw, list):
        items = [item for item in raw if isinstance(item, dict)]
    else:
        return {}
    names: dict[str, str] = {}
    for item in items:
        item_id = str(item.get("id", "")).strip()
        name = item.get("name") or item.get("title")
        if item_id.isdigit() and isinstance(name, str) and name.strip():
            names[item_id] = name.strip()
    return names


def parse_all_names(payload: Any) -> dict[str, str]:
    """{id: name} for every named collection under data.cluster."""
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data", payload)
    cluster = data.get("cluster") if isinstance(data, dict) else None
    if not isinstance(cluster, dict):
        return {}
    names: dict[str, str] = {}
    for key, value in cluster.items():
        if key != "group":
            names.update(_collection_names(value))
    names.update(parse_groups(payload))  # real groups win
    return names


def parse_groups(payload: Any) -> dict[str, str]:
    """Extract {group_id: name} from a /v2/pull/all response.

    DIVERA puts the groups under data.cluster.group, either as an object keyed
    by id or as a list. Both shapes are accepted.
    """
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data", payload)
    cluster = data.get("cluster") if isinstance(data, dict) else None
    raw = cluster.get("group") if isinstance(cluster, dict) else None

    if isinstance(raw, dict):
        items = [
            {**value, "id": value.get("id", key)} if isinstance(value, dict) else {"id": key, "name": value}
            for key, value in raw.items()
        ]
    elif isinstance(raw, list):
        items = [item for item in raw if isinstance(item, dict)]
    else:
        return {}

    groups: dict[str, str] = {}
    for item in items:
        group_id = str(item.get("id", "")).strip()
        if not group_id or not group_id.isdigit():
            continue
        name = str(item.get("name") or item.get("title") or "").strip()
        groups[group_id] = name or f"Gruppe {group_id}"
    return dict(sorted(groups.items(), key=lambda kv: kv[1].lower()))


class DiveraClient:
    """Fetch data from DIVERA 24/7 with a personal or unit access key."""

    def __init__(self, session: aiohttp.ClientSession, accesskey: str) -> None:
        self._session = session
        self._accesskey = accesskey

    def _hide_key(self, text: str) -> str:
        return text.replace(self._accesskey, "***") if self._accesskey else text

    async def _async_get_json(self, url: str) -> tuple[int, Any]:
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(
                    url, params={"accesskey": self._accesskey}
                )
                if response.status in (401, 403):
                    raise DiveraAuthError("Access key rejected")
                if response.status == 404:
                    return 404, None
                response.raise_for_status()
                return response.status, await response.json(content_type=None)
        except DiveraError:
            raise
        except aiohttp.ClientResponseError as err:
            # str(err) contains the request URL including ?accesskey=..., so
            # build the message from the status only.
            raise DiveraError(f"DIVERA 24/7 returned HTTP {err.status}") from None
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            message = self._hide_key(str(err))
            raise DiveraError(
                f"Error communicating with DIVERA 24/7: {message}"
            ) from None

    async def async_get_last_alarm(self) -> dict[str, Any] | None:
        """Return the last alarm, or None if there is none."""
        status, payload = await self._async_get_json(API_LAST_ALARM)
        if status == 404 or payload is None:
            return None
        if not isinstance(payload, dict):
            raise DiveraError("Unexpected response from DIVERA 24/7")
        if payload.get("success") is False:
            # DIVERA uses "error" (string) or "errors" (list/object).
            errors = str(payload.get("errors") or payload.get("error") or "")
            if "accesskey" in errors.lower() or "zugriff" in errors.lower():
                raise DiveraAuthError(self._hide_key(errors))
            # Normal answer while there is no alarm for this key.
            _LOGGER.debug("DIVERA 24/7: no alarm (%s)", self._hide_key(errors)[:200])
            return None

        # The API wraps the alarm in "data"; fall back to the plain payload.
        alarm = payload.get("data", payload)
        if not isinstance(alarm, dict) or not alarm.get("id"):
            _LOGGER.debug("DIVERA 24/7 answered without an alarm")
            return None
        return alarm

    async def async_get_groups_and_names(self) -> tuple[dict[str, str], dict[str, str]]:
        """One request: (groups for the picker, all known id->name labels)."""
        status, payload = await self._async_get_json(API_PULL_ALL)
        if status == 404 or not isinstance(payload, dict) or payload.get("success") is False:
            return {}, {}
        return parse_groups(payload), parse_all_names(payload)

    async def async_get_names(self) -> dict[str, str]:
        """Every id->name DIVERA exposes for the unit (groups, RICs, ...)."""
        status, payload = await self._async_get_json(API_PULL_ALL)
        if status == 404 or not isinstance(payload, dict) or payload.get("success") is False:
            return {}
        return parse_all_names(payload)

    async def async_get_groups(self) -> dict[str, str]:
        """Return the unit's groups as {id: name}; empty if not visible."""
        status, payload = await self._async_get_json(API_PULL_ALL)
        if status == 404 or not isinstance(payload, dict):
            return {}
        if payload.get("success") is False:
            return {}
        return parse_groups(payload)
