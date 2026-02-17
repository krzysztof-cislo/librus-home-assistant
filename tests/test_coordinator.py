"""Tests for the Librus DataUpdateCoordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.librus.coordinator import LibrusDataUpdateCoordinator
from custom_components.librus.librus_client import (
    LibrusAuthError,
    LibrusConnectionError,
    LibrusTimeoutError,
)


@pytest.fixture
async def coordinator(hass: HomeAssistant, mock_config_entry):
    """Create a coordinator instance for testing."""
    return LibrusDataUpdateCoordinator(hass, mock_config_entry)


class TestLibrusDataUpdateCoordinator:
    """Tests for LibrusDataUpdateCoordinator."""

    async def test_successful_refresh(self, hass: HomeAssistant, coordinator, mock_homework_entries):
        """Test successful data fetch returns homework entries."""
        with patch(
            "custom_components.librus.coordinator.fetch_homework_data",
            return_value=mock_homework_entries,
        ):
            data = await coordinator._async_update_data()

        assert len(data) == 2
        assert data[0]["id"] == 6671271
        assert data[1]["id"] == 6674588

    async def test_auth_error_raises_config_entry_auth_failed(self, hass: HomeAssistant, coordinator):
        """Test that LibrusAuthError maps to ConfigEntryAuthFailed."""
        with patch(
            "custom_components.librus.coordinator.fetch_homework_data",
            side_effect=LibrusAuthError("Invalid credentials"),
        ), pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    async def test_timeout_error_raises_update_failed(self, hass: HomeAssistant, coordinator):
        """Test that LibrusTimeoutError maps to UpdateFailed (preserves previous data)."""
        with patch(
            "custom_components.librus.coordinator.fetch_homework_data",
            side_effect=LibrusTimeoutError("timed out"),
        ), pytest.raises(UpdateFailed, match="Timeout"):
            await coordinator._async_update_data()

    async def test_connection_error_raises_update_failed(self, hass: HomeAssistant, coordinator):
        """Test that LibrusConnectionError maps to UpdateFailed."""
        with patch(
            "custom_components.librus.coordinator.fetch_homework_data",
            side_effect=LibrusConnectionError("unreachable"),
        ), pytest.raises(UpdateFailed, match="connecting"):
            await coordinator._async_update_data()

    async def test_update_interval_is_one_hour(self, coordinator):
        """Verify the coordinator uses 1-hour update interval (FR-007)."""
        from datetime import timedelta

        assert coordinator.update_interval == timedelta(hours=1)

    async def test_coordinator_name(self, coordinator):
        """Verify the coordinator name includes domain."""
        assert "librus" in coordinator.name
