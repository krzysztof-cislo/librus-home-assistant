# Config Flow Schema Contract: Librus Credentials

**Date**: 2026-02-16  
**Feature**: Config Flow with Librus Credentials

## Overview

The configuration flow collects Librus login and password, validates them against Librus before saving, and stores credentials in the config entry. Supports initial setup (`user` step) and credential updates (`reconfigure` step).

## Config Flow Steps

### Step: `user`

**Purpose**: Initial setup—collect and validate credentials

**Schema**:
```python
vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
})
```

**Flow**:
1. User initiates config flow from Home Assistant integrations UI
2. Config flow displays form with login and password fields (password masked)
3. User submits
4. Validate: both fields non-empty (vol.Required)
5. Validate: call Librus API `login(username, password)`
6. On success: `async_create_entry(title="Librus", data={username, password})`
7. On failure: `async_show_form(step_id="user", data_schema=..., errors={"base": "invalid_auth"})` — user can correct and retry

**Error Keys** (strings.json):
- `invalid_auth`: Invalid Librus credentials
- `cannot_connect`: Network/connection error or Librus unreachable
- `unknown`: Unexpected error (e.g. storage failure)

---

### Step: `reconfigure`

**Purpose**: Update credentials for existing config entry

**Schema**: Same as `user` step

**Flow**:
1. User clicks Configure on existing Librus integration
2. `async_step_reconfigure` invoked
3. Form displayed; username may be pre-filled from `entry.data`; password left empty (user must re-enter)
4. User submits
5. Validate non-empty
6. Validate against Librus
7. On success: `async_update_reload_and_abort(self._get_reconfigure_entry(), data_updates={username, password})`
8. On failure: `async_show_form` with errors; user can retry

**Pre-fill**:
- `username`: From `entry.data.get(CONF_USERNAME, "")`
- `password`: Empty (never pre-fill password)

## Implementation Contract

### Python Code Structure (User Step)

```python
async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
    if user_input is not None:
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]
        # Validate against Librus
        try:
            if not await self._validate_librus_credentials(username, password):
                return self.async_show_form(
                    step_id="user",
                    data_schema=DATA_SCHEMA,
                    errors={"base": "invalid_auth"},
                )
        except Exception as err:
            _LOGGER.exception("Librus validation error")
            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
                errors={"base": "cannot_connect"},
            )
        return self.async_create_entry(
            title="Librus",
            data={CONF_USERNAME: username, CONF_PASSWORD: password},
        )
    return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
```

### Python Code Structure (Reconfigure Step)

```python
async def async_step_reconfigure(self, user_input: dict | None = None) -> ConfigFlowResult:
    entry = self._get_reconfigure_entry()
    if user_input is not None:
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]
        # Same validation as user step
        ...
        return self.async_update_reload_and_abort(
            entry,
            data_updates={CONF_USERNAME: username, CONF_PASSWORD: password},
        )
    return self.async_show_form(
        step_id="reconfigure",
        data_schema=DATA_SCHEMA,
        description_placeholders={"username": entry.data.get(CONF_USERNAME, "")},
    )
```

### Librus Validation Helper

```python
async def _validate_librus_credentials(self, username: str, password: str) -> bool:
    """Validate credentials against Librus API. Run in executor (sync lib)."""
    return await self.hass.async_add_executor_job(
        self._validate_librus_credentials_sync,
        username,
        password,
    )

def _validate_librus_credentials_sync(self, username: str, password: str) -> bool:
    from py_librus_api import Librus
    librus = Librus()
    return librus.login(username, password)
```

## Validation

- **Empty fields**: Handled by `vol.Required()`; form not submitted until both filled
- **Librus validation**: Must succeed before `async_create_entry` or `async_update_reload_and_abort`
- **Storage failure**: Catch around create/update; return `async_show_form` with error
- **Single instance**: Enforced by `single_config_entry: true` in manifest

## Translations (strings.json)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Librus credentials",
        "data": {
          "username": "Login",
          "password": "Password"
        }
      },
      "reconfigure": {
        "title": "Update Librus credentials",
        "data": {
          "username": "Login",
          "password": "Password"
        }
      }
    },
    "error": {
      "invalid_auth": "Invalid login or password",
      "cannot_connect": "Could not connect to Librus",
      "unknown": "An unexpected error occurred"
    },
    "abort": {
      "already_configured": "Integration is already configured"
    }
  }
}
```
