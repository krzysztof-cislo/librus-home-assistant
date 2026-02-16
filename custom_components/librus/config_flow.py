"""Config flow for Librus."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

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

    @staticmethod
    def _validate_librus_credentials_sync(username: str, password: str) -> bool:
        """Validate credentials against Librus API (synchronous)."""
        import requests as req

        host = "https://api.librus.pl/"
        headers = {
            "Authorization": "Basic Mjg6ODRmZGQzYTg3YjAzZDNlYTZmZmU3NzdiNThiMzMyYjE="
        }

        response = req.post(
            f"{host}OAuth/Token",
            data={
                "username": username,
                "password": password,
                "librus_long_term_token": "1",
                "grant_type": "password",
            },
            headers=headers,
            timeout=30,
        )

        if response.ok:
            return True

        _LOGGER.debug(
            "Librus login failed: HTTP %s - %s",
            response.status_code,
            response.text,
        )
        return False

    async def _validate_librus_credentials(
        self, username: str, password: str
    ) -> bool:
        """Validate credentials against Librus API in executor."""
        return await self.hass.async_add_executor_job(
            self._validate_librus_credentials_sync,
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
            except Exception:
                _LOGGER.exception("Unexpected error validating Librus credentials")
                errors["base"] = "cannot_connect"

            if not errors:
                try:
                    return self.async_create_entry(
                        title="Librus",
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                        },
                    )
                except Exception:
                    _LOGGER.exception("Unexpected error creating config entry")
                    errors["base"] = "unknown"

            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
                errors=errors,
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
            except Exception:
                _LOGGER.exception("Unexpected error validating Librus credentials")
                errors["base"] = "cannot_connect"

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
