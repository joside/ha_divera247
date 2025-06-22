import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)
API_URL = "https://app.divera247.com/api/last-alarm"

CONF_ACCESSKEY = "accesskey"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    pass  # Wird nicht benötigt, da async_setup_entry verwendet wird

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensor from a config entry."""
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    accesskey = entry.data.get(CONF_ACCESSKEY)
    coordinator = Divera247Coordinator(hass, scan_interval, accesskey)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([Divera247Sensor(coordinator)], True)

class Divera247Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, scan_interval, accesskey):
        super().__init__(
            hass,
            _LOGGER,
            name="divera247",
            update_interval=scan_interval,
        )
        self.accesskey = accesskey

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                params = {"accesskey": self.accesskey}
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL, params=params) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Fehler beim Abrufen der Daten: {response.status}")
                        return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Update: {err}")

class Divera247Sensor(SensorEntity):
    def __init__(self, coordinator: Divera247Coordinator):
        self.coordinator = coordinator
        self._attr_name = "Divera247 Letzter Einsatz"
        self._attr_unique_id = "divera247_last_alarm"

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        data = self.coordinator.data
        if data and "id" in data:
            return data.get("title", "Unbekannter Einsatz")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        return {
            "id": data.get("id"),
            "details": data.get("details"),
            "timestamp": data.get("timestamp"),
        }

    async def async_update(self):
        await self.coordinator.async_request_refresh()