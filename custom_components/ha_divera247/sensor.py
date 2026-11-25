"""Sensor for the last DIVERA 24/7 alarm."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, alarm_group_ids
from .coordinator import DiveraConfigEntry, DiveraCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DiveraConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor from a config entry."""
    async_add_entities([DiveraLastAlarmSensor(entry.runtime_data)])


def _as_datetime(value: Any):
    """DIVERA sends unix timestamps; convert them for the attributes."""
    if isinstance(value, (int, float)) and value > 0:
        return dt_util.as_local(dt_util.utc_from_timestamp(value))
    return value


class DiveraLastAlarmSensor(CoordinatorEntity[DiveraCoordinator], SensorEntity):
    """Title of the last alarm, details as attributes."""

    _attr_has_entity_name = True
    _attr_translation_key = "last_alarm"
    _attr_icon = "mdi:fire-truck"

    def __init__(self, coordinator: DiveraCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_last_alarm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Divera247",
            manufacturer="DIVERA GmbH",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://app.divera247.com",
        )

    @property
    def native_value(self) -> str | None:
        alarm = self.coordinator.data
        if not alarm:
            return None
        return alarm.get("title") or "Unbekannter Einsatz"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        alarm = self.coordinator.data
        if not alarm:
            return {}
        return {
            "id": alarm.get("id"),
            "text": alarm.get("text"),
            "address": alarm.get("address"),
            "latitude": alarm.get("lat"),
            "longitude": alarm.get("lng"),
            "priority": alarm.get("priority"),
            "closed": alarm.get("closed"),
            "groups": alarm_group_ids(alarm),
            "group_names": self.coordinator.names_for(alarm_group_ids(alarm)),
            "date": _as_datetime(alarm.get("date")),
            "ts_update": _as_datetime(alarm.get("ts_update")),
        }
