"""Homework sensor for the Librus integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_HOMEWORK_KEY
from .coordinator import LibrusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Librus homework sensor from a config entry."""
    coordinator: LibrusDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HomeworkSensor(coordinator, entry)])


class HomeworkSensor(CoordinatorEntity[LibrusDataUpdateCoordinator], SensorEntity):
    """Sensor showing homework entries from Librus.

    State: count of homework entries (int).
    Attributes: homework_entries list of dicts per data-model.md.
    Distinguishes 'no homework' (state=0, empty list) from
    'unavailable' (refresh failed, coordinator has no data).
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:book-open-variant"

    def __init__(
        self,
        coordinator: LibrusDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the homework sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{SENSOR_HOMEWORK_KEY}"
        self._attr_translation_key = SENSOR_HOMEWORK_KEY

    @property
    def native_value(self) -> int | None:
        """Return the count of homework entries, or None if unavailable."""
        if self.coordinator.data is None:
            return None
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return homework entries as a structured attribute."""
        data = self.coordinator.data
        if data is None:
            return {"homework_entries": []}
        return {"homework_entries": data}
