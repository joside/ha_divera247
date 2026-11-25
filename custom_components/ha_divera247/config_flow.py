"""Config flow for the DIVERA 24/7 integration."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DiveraAuthError, DiveraClient, DiveraError
from .const import (
    CONF_ACCESSKEY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .coordinator import DiveraConfigEntry

INTERVAL = vol.All(
    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
)


def _key_id(accesskey: str) -> str:
    """Stable unique id without storing the key itself in the registry."""
    return hashlib.sha256(accesskey.encode()).hexdigest()[:16]


class Divera247ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DIVERA 24/7."""

    VERSION = 1
    MINOR_VERSION = 2

    async def _async_validate(self, accesskey: str) -> str | None:
        """Return an error key, or None if the access key works."""
        client = DiveraClient(async_get_clientsession(self.hass), accesskey)
        try:
            await client.async_get_last_alarm()
        except DiveraAuthError:
            return "invalid_auth"
        except DiveraError:
            return "cannot_connect"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            accesskey = user_input[CONF_ACCESSKEY].strip()
            await self.async_set_unique_id(_key_id(accesskey))
            self._abort_if_unique_id_configured()
            if not (error := await self._async_validate(accesskey)):
                return self.async_create_entry(
                    title="DIVERA 24/7",
                    data={**user_input, CONF_ACCESSKEY: accesskey},
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCESSKEY): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): INTERVAL,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            accesskey = user_input[CONF_ACCESSKEY].strip()
            if not (error := await self._async_validate(accesskey)):
                entry = self._get_reauth_entry()
                return self.async_update_reload_and_abort(
                    entry,
                    unique_id=_key_id(accesskey),
                    data_updates={CONF_ACCESSKEY: accesskey},
                )
            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_ACCESSKEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: DiveraConfigEntry) -> OptionsFlow:
        return Divera247OptionsFlow()


class Divera247OptionsFlow(OptionsFlow):
    """Change the polling interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Optional(CONF_SCAN_INTERVAL, default=current): INTERVAL}
            ),
        )
