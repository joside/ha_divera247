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


def _accesskey_selector(result):
    from homeassistant.helpers.selector import TextSelectorType

    for key, value in result["data_schema"].schema.items():
        if key == CONF_ACCESSKEY:
            return value.config["type"] == TextSelectorType.PASSWORD
    raise AssertionError("access key field missing")


async def test_user_form_masks_accesskey(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert _accesskey_selector(result)


async def test_reauth_form_masks_accesskey(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_ACCESSKEY: "oldkey"}, unique_id="x"
    )
    entry.add_to_hass(hass)
    result = await entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"
    assert _accesskey_selector(result)


# --- reconfigure: swap the access key without deleting the entry --------------

from custom_components.ha_divera247.config_flow import _key_id


def _entry(hass, key="oldkey"):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_ACCESSKEY: key}, unique_id=_key_id(key)
    )
    entry.add_to_hass(hass)
    return entry


async def test_reconfigure_changes_key(hass):
    entry = _entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    assert result["step_id"] == "reconfigure"
    assert _accesskey_selector(result)

    with patch(VALIDATE, return_value=None), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ACCESSKEY: " newkey "}
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_ACCESSKEY] == "newkey"
    assert entry.unique_id == _key_id("newkey")


async def test_reconfigure_rejected_key_keeps_old(hass):
    entry = _entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    with patch(VALIDATE, side_effect=DiveraAuthError):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ACCESSKEY: "badkey"}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert entry.data[CONF_ACCESSKEY] == "oldkey"


async def test_reconfigure_same_key_is_allowed(hass):
    entry = _entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    with patch(VALIDATE, return_value=None), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ACCESSKEY: "oldkey"}
        )
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_key_of_other_entry_aborts(hass):
    entry = _entry(hass, "firstkey")
    _entry(hass, "secondkey")
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_ACCESSKEY: "secondkey"}
    )
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_ACCESSKEY] == "firstkey"
