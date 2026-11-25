"""Data update coordinator for DIVERA 24/7."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DiveraAuthError, DiveraClient, DiveraError
from .const import CONF_ACCESSKEY, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type DiveraConfigEntry = ConfigEntry[DiveraCoordinator]


class DiveraCoordinator(DataUpdateCoordinator[dict[str, Any] | None]):
    """Poll the last alarm from DIVERA 24/7."""

    config_entry: DiveraConfigEntry

    def __init__(self, hass: HomeAssistant, entry: DiveraConfigEntry) -> None:
        seconds = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=int(seconds)),
        )
        self.client = DiveraClient(
            async_get_clientsession(hass), entry.data[CONF_ACCESSKEY]
        )
        self.group_names: dict[str, str] = {}

    async def async_load_group_names(self) -> None:
        """Fetch group names once; failures only cost the nice names."""
        try:
            self.group_names = await self.client.async_get_groups()
        except DiveraError as err:
            _LOGGER.debug("Could not load DIVERA groups: %s", err)
            self.group_names = {}

    def names_for(self, group_ids: list[str]) -> list[str]:
        """Readable names for group ids (falls back to the id)."""
        return [self.group_names.get(gid, gid) for gid in group_ids]

    async def _async_update_data(self) -> dict[str, Any] | None:
        try:
            return await self.client.async_get_last_alarm()
        except DiveraAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except DiveraError as err:
            raise UpdateFailed(str(err)) from err
