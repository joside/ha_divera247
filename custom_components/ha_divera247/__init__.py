"""The DIVERA 24/7 integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import DiveraConfigEntry, DiveraCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: DiveraConfigEntry) -> bool:
    """Set up DIVERA 24/7 from a config entry."""
    coordinator = DiveraCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load_group_names()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_on_update))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DiveraConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_on_update(hass: HomeAssistant, entry: DiveraConfigEntry) -> None:
    """Reload when the options (scan interval) change."""
    await hass.config_entries.async_reload(entry.entry_id)
