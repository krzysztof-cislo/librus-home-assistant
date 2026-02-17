"""The Librus integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    SERVICE_REFRESH_HOMEWORK,
)
from .coordinator import LibrusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Librus from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = LibrusDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH_HOMEWORK)

    return unload_ok


def _register_services(hass: HomeAssistant) -> None:
    """Register Librus services (idempotent)."""
    if hass.services.has_service(DOMAIN, SERVICE_REFRESH_HOMEWORK):
        return

    async def handle_refresh_homework(call: ServiceCall) -> None:
        """Handle the refresh_homework service call."""
        _LOGGER.debug("On-demand homework refresh triggered via service call")
        for coordinator in hass.data.get(DOMAIN, {}).values():
            if isinstance(coordinator, LibrusDataUpdateCoordinator):
                await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_HOMEWORK,
        handle_refresh_homework,
        schema=vol.Schema({}),
    )


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries to new version."""
    if entry.version < 2:
        _LOGGER.debug("Migrating Librus config entry from version %s to 2", entry.version)
        new_data = {**entry.data}
        if CONF_USERNAME not in new_data:
            new_data[CONF_USERNAME] = ""
        if CONF_PASSWORD not in new_data:
            new_data[CONF_PASSWORD] = ""
        hass.config_entries.async_update_entry(entry, data=new_data, version=2)
        _LOGGER.debug("Migration to version 2 successful")
    return True
