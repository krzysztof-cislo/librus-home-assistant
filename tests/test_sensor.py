"""Tests for the Librus homework sensor."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.librus.const import DOMAIN
from custom_components.librus.coordinator import LibrusDataUpdateCoordinator
from custom_components.librus.sensor import HomeworkSensor


@pytest.fixture
async def mock_coordinator(hass: HomeAssistant, mock_config_entry):
    """Create a mock coordinator."""
    coordinator = LibrusDataUpdateCoordinator(hass, mock_config_entry)
    return coordinator


class TestHomeworkSensor:
    """Tests for the HomeworkSensor entity."""

    async def test_state_returns_entry_count(self, mock_coordinator, mock_config_entry, mock_homework_entries):
        """State should be the count of homework entries."""
        mock_coordinator.data = mock_homework_entries
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 2

    async def test_state_returns_zero_for_empty_list(self, mock_coordinator, mock_config_entry):
        """State should be 0 when there are no homework entries."""
        mock_coordinator.data = []
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value == 0

    async def test_state_returns_none_when_unavailable(self, mock_coordinator, mock_config_entry):
        """State should be None when coordinator has no data (unavailable)."""
        mock_coordinator.data = None
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.native_value is None

    async def test_attributes_contain_homework_entries(self, mock_coordinator, mock_config_entry, mock_homework_entries):
        """Extra attributes should contain the full homework_entries list."""
        mock_coordinator.data = mock_homework_entries
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        attrs = sensor.extra_state_attributes
        assert "homework_entries" in attrs
        assert len(attrs["homework_entries"]) == 2
        assert attrs["homework_entries"][0]["subject"] == "Historia"

    async def test_attributes_empty_list_when_no_data(self, mock_coordinator, mock_config_entry):
        """Attributes should return empty list when coordinator data is None."""
        mock_coordinator.data = None
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        attrs = sensor.extra_state_attributes
        assert attrs["homework_entries"] == []

    async def test_unique_id_format(self, mock_coordinator, mock_config_entry):
        """Unique ID should combine entry_id and sensor key."""
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.unique_id == "test_entry_id_homework"

    async def test_has_entity_name(self, mock_coordinator, mock_config_entry):
        """Sensor should use entity name translation."""
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.has_entity_name is True

    async def test_translation_key(self, mock_coordinator, mock_config_entry):
        """Sensor should use homework translation key."""
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.translation_key == "homework"

    async def test_icon(self, mock_coordinator, mock_config_entry):
        """Sensor should have a book icon."""
        sensor = HomeworkSensor(mock_coordinator, mock_config_entry)
        assert sensor.icon == "mdi:book-open-variant"
