import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import DOMAIN, CONF_ACCESSKEY, DEFAULT_SCAN_INTERVAL

class Divera247ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ha_divera247."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="DIVERA 24/7", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_ACCESSKEY): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )