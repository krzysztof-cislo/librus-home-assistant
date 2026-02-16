# Quick Start Guide: Config Flow with Librus Credentials

**Date**: 2026-02-16  
**Feature**: Config Flow with Librus Credentials

## Overview

This guide covers the implementation steps to add Librus credential collection, validation, and reconfigure flow to the existing Librus integration. Assumes the skeleton from 001-hacs-integration-skeleton is in place.

## Prerequisites

- Integration skeleton installed (`custom_components/librus/`)
- Home Assistant 2024.1.0+
- Valid Librus account for testing

## Implementation Steps

### 1. Update Manifest

Add `py-librus-api` to requirements:

**`custom_components/librus/manifest.json`**:

```json
{
  "domain": "librus",
  "name": "Librus",
  "integration_type": "hub",
  "version": "1.0.0",
  "config_flow": true,
  "single_config_entry": true,
  "documentation": "https://github.com/krzysztof-cislo/librus-home-assistant",
  "issue_tracker": "https://github.com/krzysztof-cislo/librus-home-assistant/issues",
  "codeowners": ["@krzysztof-cislo"],
  "requirements": ["py-librus-api>=0.3.1"],
  "dependencies": []
}
```

### 2. Update Constants

**`custom_components/librus/const.py`**:

```python
"""Constants for the Librus integration."""

DOMAIN = "librus"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
```

### 3. Update Config Flow

**`custom_components/librus/config_flow.py`**:

- Add `vol.Required` schema for username and password
- Implement Librus validation via `py-librus-api` in executor
- Add `async_step_reconfigure` for credential updates
- Handle errors: invalid_auth, cannot_connect, storage failure
- See `contracts/config-flow-schema.md` for full implementation contract

### 4. Add Translations

Create **`custom_components/librus/strings.json`**:

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
    }
  }
}
```

### 5. Bump Config Flow Version (if schema changes)

If existing entries have empty `data`, implement `async_migrate_entry` in `__init__.py` to migrate to new schema, or bump `VERSION` in ConfigFlow and ensure migration handles old entries.

## Manual Testing

### Initial Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Librus"
3. Enter valid Librus login and password
4. Submit — should configure successfully
5. Verify integration appears in configured list

### Invalid Credentials

1. Add Integration → Enter invalid credentials
2. Submit — should show "Invalid login or password"
3. Correct credentials and retry — should succeed

### Empty Fields

1. Add Integration → Leave login or password empty
2. Submit — form should not proceed; inline validation error
3. Fill both fields — should proceed

### Reconfigure

1. With integration configured, click the "Configure" button on the Librus integration card
2. Update login/password
3. Submit — should update and reload
4. Invalid credentials — should show error, allow retry

### Single Instance

1. Try to add Librus integration again when already configured
2. Should be prevented (single_config_entry)

## Automated Testing

Mock `py_librus_api.Librus.login` in tests to avoid real API calls:

```python
@patch("custom_components.librus.config_flow.Librus")
async def test_user_step_valid_credentials(mock_librus, hass):
    """Test successful configuration with valid credentials."""
    mock_instance = AsyncMock()
    mock_instance.login.return_value = True
    mock_librus.return_value = mock_instance

    flow = init_config_flow(hass)
    result = await flow.async_step_user({"username": "test", "password": "pass"})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["username"] == "test"
```

## Credential Storage

- Credentials stored in `entry.data` (username, password)
- Never log or print credentials
- Password field is masked in config flow UI
- Reconfigure flow: do not pre-fill password

## Next Steps

After this feature:
- Use credentials in `async_setup_entry` or platform setup to authenticate with Librus
- Implement sensors, switches, or other entities that fetch data from Librus
