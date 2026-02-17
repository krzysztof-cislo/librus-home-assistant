"""DataUpdateCoordinator for Librus homework data."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .librus_client import (
    LibrusAuthError,
    LibrusConnectionError,
    LibrusTimeoutError,
    fetch_homework_data,
)

_LOGGER = logging.getLogger(__name__)


class LibrusDataUpdateCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Coordinator to fetch homework data from Librus API.

    Uses DataUpdateCoordinator for hourly auto-refresh (FR-007)
    and on-demand refresh support (FR-008).
    Preserves previous data on transient failures (FR-009).
    """

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_homework",
            update_interval=DEFAULT_UPDATE_INTERVAL,
            config_entry=entry,
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch homework data from Librus API in executor.

        Runs the blocking HTTP calls in the executor thread pool.
        Raises ConfigEntryAuthFailed on authentication failure.
        Raises UpdateFailed on transient errors (preserves previous data).
        """
        username = self.config_entry.data[CONF_USERNAME]
        password = self.config_entry.data[CONF_PASSWORD]

        try:
            data = await self.hass.async_add_executor_job(
                fetch_homework_data, username, password
            )
            _LOGGER.debug(
                "Librus homework refresh successful: %d entries", len(data)
            )
            return data

        except LibrusAuthError as err:
            raise ConfigEntryAuthFailed(
                "Invalid Librus credentials"
            ) from err
        except LibrusTimeoutError as err:
            raise UpdateFailed(
                f"Timeout fetching homework data: {err}"
            ) from err
        except LibrusConnectionError as err:
            raise UpdateFailed(
                f"Error connecting to Librus: {err}"
            ) from err
