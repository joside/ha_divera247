from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
import voluptuous as vol
from homeassistant.const import CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

DOMAIN = "ha_divera247"
CONF_ACCESSKEY = "accesskey"

DEFAULT_SCAN_INTERVAL = 60

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ACCESSKEY): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ha_divera247 component."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ha_divera247 from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, entry)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload(entry.entry_id)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok