"""Tests for the Librus integration setup (__init__.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.librus import async_setup_entry, async_unload_entry
from custom_components.librus.const import DOMAIN, SERVICE_REFRESH_HOMEWORK
from custom_components.librus.coordinator import LibrusDataUpdateCoordinator


async def _setup_integration(hass, mock_config_entry):
    """Helper to set up the integration with mocked I/O."""
    with patch(
        "custom_components.librus.coordinator.LibrusDataUpdateCoordinator._async_update_data",
        return_value=[],
    ), patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        new_callable=AsyncMock,
    ):
        result = await async_setup_entry(hass, mock_config_entry)
    return result


class TestAsyncSetupEntry:
    """Tests for integration setup."""

    async def test_setup_creates_coordinator(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Setup should create coordinator and store it in hass.data."""
        result = await _setup_integration(hass, mock_config_entry)

        assert result is True
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        assert isinstance(
            hass.data[DOMAIN][mock_config_entry.entry_id],
            LibrusDataUpdateCoordinator,
        )

    async def test_setup_registers_refresh_service(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Setup should register the librus.refresh_homework service."""
        await _setup_integration(hass, mock_config_entry)
        assert hass.services.has_service(DOMAIN, SERVICE_REFRESH_HOMEWORK)


class TestAsyncUnloadEntry:
    """Tests for integration unload."""

    async def test_unload_removes_coordinator(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Unload should remove coordinator from hass.data."""
        await _setup_integration(hass, mock_config_entry)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            new_callable=AsyncMock,
            return_value=True,
        ):
            result = await async_unload_entry(hass, mock_config_entry)

        assert result is True
        assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})

    async def test_unload_removes_service_when_last_entry(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Service should be removed when the last config entry is unloaded."""
        await _setup_integration(hass, mock_config_entry)
        assert hass.services.has_service(DOMAIN, SERVICE_REFRESH_HOMEWORK)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            new_callable=AsyncMock,
            return_value=True,
        ):
            await async_unload_entry(hass, mock_config_entry)

        assert not hass.services.has_service(DOMAIN, SERVICE_REFRESH_HOMEWORK)
