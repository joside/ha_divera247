"""Binary sensor: is there an active DIVERA 24/7 alarm?"""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ACTIVE_ALARM_WINDOW, DOMAIN
from .coordinator import DiveraConfigEntry, DiveraCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DiveraConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensor from a config entry."""
    async_add_entities([DiveraActiveAlarmSensor(entry.runtime_data)])


class DiveraActiveAlarmSensor(CoordinatorEntity[DiveraCoordinator], BinarySensorEntity):
    """On while the last alarm is open and recent."""

    _attr_has_entity_name = True
    _attr_translation_key = "active_alarm"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: DiveraCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_active_alarm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Divera247",
            manufacturer="DIVERA GmbH",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://app.divera247.com",
        )

    @property
    def is_on(self) -> bool:
        alarm = self.coordinator.data
        if not alarm or alarm.get("closed"):
            return False
        date = alarm.get("date")
        if not isinstance(date, (int, float)) or date <= 0:
            return False
        age = dt_util.utcnow() - dt_util.utc_from_timestamp(date)
        return age <= timedelta(minutes=ACTIVE_ALARM_WINDOW)

    @property
    def icon(self) -> str:
        return "mdi:alarm-light" if self.is_on else "mdi:alarm-light-off-outline"

    @property
    def extra_state_attributes(self) -> dict:
        alarm = self.coordinator.data or {}
        return {"id": alarm.get("id"), "title": alarm.get("title")}
