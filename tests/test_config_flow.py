"""Tests for the DIVERA 24/7 config flow."""

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ha_divera247.api import DiveraAuthError, DiveraError
from custom_components.ha_divera247.const import (
    CONF_ACCESSKEY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

VALIDATE = "custom_components.ha_divera247.api.DiveraClient.async_get_last_alarm"
SETUP = "custom_components.ha_divera247.async_setup_entry"
USER_INPUT = {CONF_ACCESSKEY: " testkey ", "scan_interval": DEFAULT_SCAN_INTERVAL}


async def test_show_form(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_create_entry(hass):
    with patch(VALIDATE, return_value=None), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "DIVERA 24/7"
    assert result["data"][CONF_ACCESSKEY] == "testkey"


async def test_invalid_auth(hass):
    with patch(VALIDATE, side_effect=DiveraAuthError):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_cannot_connect(hass):
    with patch(VALIDATE, side_effect=DiveraError):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_aborts(hass):
    with patch(VALIDATE, return_value=None), patch(SETUP, return_value=True):
        await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=USER_INPUT
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
