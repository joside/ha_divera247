import pytest
pytestmark = pytest.mark.asyncio

from homeassistant import data_entry_flow
from custom_components.ha_divera247.const import DOMAIN, CONF_ACCESSKEY, DEFAULT_SCAN_INTERVAL

async def test_show_set_form(hass):
    """Test that the config flow shows the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

async def test_create_entry(hass):
    """Test that the config flow creates an entry."""
    user_input = {
        CONF_ACCESSKEY: "testkey",
        "scan_interval": DEFAULT_SCAN_INTERVAL,
    }
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data=user_input
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "DIVERA 24/7"
    assert result["data"][CONF_ACCESSKEY] == "testkey"