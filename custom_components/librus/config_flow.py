"""Config flow for Librus."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .librus_client import LibrusConnectionError, LibrusTimeoutError

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class LibrusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Librus."""

    VERSION = 2

    async def _validate_librus_credentials(
        self, username: str, password: str
    ) -> bool:
        """Validate credentials against Librus in executor."""
        from .librus_client import validate_credentials

        return await self.hass.async_add_executor_job(
            validate_credentials,
            username,
            password,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            try:
                if not await self._validate_librus_credentials(username, password):
                    errors["base"] = "invalid_auth"
            except LibrusTimeoutError:
                errors["base"] = "timeout"
            except LibrusConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating Librus credentials")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="Librus",
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
                errors=errors,
                description_placeholders={"status": "Validating credentials…"},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of credentials."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            try:
                if not await self._validate_librus_credentials(username, password):
                    errors["base"] = "invalid_auth"
            except LibrusTimeoutError:
                errors["base"] = "timeout"
            except LibrusConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating Librus credentials")
                errors["base"] = "unknown"

            if not errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

            return self.async_show_form(
                step_id="reconfigure",
                data_schema=self._get_reconfigure_schema(entry),
                errors=errors,
                description_placeholders={"status": "Validating credentials…"},
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._get_reconfigure_schema(entry),
        )

    @staticmethod
    def _get_reconfigure_schema(entry) -> vol.Schema:
        """Build schema for reconfigure step with pre-filled username."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=entry.data.get(CONF_USERNAME, ""),
                ): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
