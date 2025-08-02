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

class Divera247OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for ha_divera247."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL,
                    self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ),
            ): int,
        })

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )

async def async_get_options_flow(config_entry):
    return Divera247OptionsFlowHandler(config_entry)