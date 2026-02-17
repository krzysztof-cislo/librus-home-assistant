"""The Librus integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Librus from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.pop(DOMAIN, None)
    return True


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
