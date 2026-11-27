"""Tests for parsing DIVERA API responses."""

from custom_components.ha_divera247.api import parse_groups


def test_groups_as_object():
    payload = {
        "success": True,
        "data": {
            "cluster": {
                "group": {
                    "177769": {"id": 177769, "name": "Maschinisten"},
                    "177768": {"id": 177768, "name": "Löschzug"},
                }
            }
        },
    }
    assert parse_groups(payload) == {"177768": "Löschzug", "177769": "Maschinisten"}


def test_groups_as_list_and_missing_names():
    payload = {"data": {"cluster": {"group": [{"id": 1, "name": "A"}, {"id": 2}]}}}
    assert parse_groups(payload) == {"1": "A", "2": "Gruppe 2"}


def test_groups_missing():
    assert parse_groups({"data": {}}) == {}
    assert parse_groups(None) == {}


def test_all_names_include_other_collections():
    from custom_components.ha_divera247.api import parse_all_names

    payload = {
        "data": {
            "cluster": {
                "group": {"67806": {"id": 67806, "name": "Niederbühl Vollalarm"}},
                "ric": {"177768": {"id": 177768, "name": "Vollalarm RIC"}},
            }
        }
    }
    assert parse_all_names(payload) == {
        "177768": "Vollalarm RIC",
        "67806": "Niederbühl Vollalarm",
    }


# --- errors must never contain the access key ---------------------------------

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from yarl import URL

from custom_components.ha_divera247.api import DiveraClient, DiveraError

SECRET = "supersecretkey123"


def _client_with_response(status: int) -> DiveraClient:
    url = URL(f"https://app.divera247.com/api/last-alarm?accesskey={SECRET}")
    request_info = aiohttp.RequestInfo(url, "GET", {}, url)
    response = MagicMock(status=status)
    response.raise_for_status.side_effect = aiohttp.ClientResponseError(
        request_info, (), status=status, message="Server Error"
    )
    session = MagicMock()
    session.get = AsyncMock(return_value=response)
    return DiveraClient(session, SECRET)


@pytest.mark.parametrize("status", [400, 429, 500, 503])
async def test_http_error_hides_accesskey(status):
    client = _client_with_response(status)
    with pytest.raises(DiveraError) as exc_info:
        await client.async_get_last_alarm()
    assert str(exc_info.value) == f"DIVERA 24/7 returned HTTP {status}"
    assert SECRET not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


async def test_other_client_error_redacts_accesskey():
    session = MagicMock()
    session.get = AsyncMock(
        side_effect=aiohttp.ClientError(f"boom ?accesskey={SECRET}")
    )
    client = DiveraClient(session, SECRET)
    with pytest.raises(DiveraError) as exc_info:
        await client.async_get_last_alarm()
    assert SECRET not in str(exc_info.value)
    assert "Error communicating with DIVERA 24/7" in str(exc_info.value)
