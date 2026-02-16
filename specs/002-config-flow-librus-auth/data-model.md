# Data Model: Config Flow with Librus Credentials

**Date**: 2026-02-16  
**Feature**: Config Flow with Librus Credentials

## Overview

This feature extends the configuration entry with credential data. Credentials are stored in the config entry `data` dictionary. The integration continues to enforce a single configuration entry per Home Assistant instance.

## Entities

### Credentials (Logical)

**Purpose**: Represents Librus authentication data—login and password. Used as provided (no format validation). Validated against Librus during config flow before persistence.

**Attributes**:
- `username` (string): Librus login/username, used as provided
- `password` (string): Librus password, used as provided

**Storage**: Stored in config entry `entry.data`:
```python
entry.data = {
    "username": "user@example.com",  # or plain username
    "password": "secret"
}
```

**Constraints**:
- Both fields required (non-empty) before submit
- Validated against Librus API before saving
- Password never logged or displayed in UI after setup
- No format validation (email, length, etc.)—values used as provided

**Lifecycle**:
1. **Collected**: User enters in config flow form
2. **Validated**: Integration calls Librus API to verify
3. **Stored**: On success, saved to config entry data
4. **Retrieved**: Integration reads from `entry.data` when authenticating
5. **Updated**: Via reconfigure flow; same validate-then-save sequence

### Configuration Entry (Extended)

**Purpose**: Represents the single configured instance of the Librus integration. Now includes credential data.

**Attributes** (extends 001 skeleton):
- `entry_id` (string): Unique identifier from Home Assistant
- `domain` (string): `"librus"`
- `title` (string): Display name, e.g. `"Librus"`
- `data` (dict): **Extended** to include:
  - `username`: Librus login
  - `password`: Librus password (sensitive; never expose)
- `options` (dict): Empty for this feature
- `version` (int): Config entry version (bump if schema changes)
- `source` (string): `"user"` for manual setup

**Constraints**:
- Single instance only (`single_config_entry: true` in manifest)
- Credentials required for integration to function (future use)

**State Transitions**:
```
Not Installed → Installed (via HACS)
Installed → Configured (via config flow with valid credentials)
Configured → Updated (via reconfigure flow)
Configured → Removed (via Home Assistant UI)
```

## Data Flow

### Initial Configuration Flow

```
User initiates config flow
  ↓
async_step_user() displays form (login, password)
  ↓
User submits → Validate non-empty (vol.Required)
  ↓
Validate against Librus (py-librus-api login)
  ↓
[Success] → async_create_entry(data={username, password})
  ↓
[Failure] → async_show_form(errors={...}), user can retry
  ↓
Entry stored in core.config_entries
  ↓
async_setup_entry() called (credentials in entry.data)
```

### Reconfigure Flow

```
User clicks Configure on existing entry
  ↓
async_step_reconfigure() invoked with entry context
  ↓
Display form (pre-fill username; password empty for security)
  ↓
User submits → Validate non-empty
  ↓
Validate against Librus
  ↓
[Success] → async_update_reload_and_abort(entry, data_updates={...})
  ↓
[Failure] → async_show_form(errors={...}), user can retry
```

### Credential Usage (Future)

```
Integration needs to authenticate with Librus
  ↓
Read entry.data["username"], entry.data["password"]
  ↓
Call Librus API (e.g. py-librus-api login)
  ↓
Use session/token for API calls
```

## Constants (const.py)

Proposed additions:

```python
# Existing
DOMAIN = "librus"

# New for credentials
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
```

## Validation Rules

| Rule | Implementation |
|------|----------------|
| Both fields required | `vol.Required()` in schema |
| Librus validation | `Librus().login(username, password)` before save |
| Storage failure handling | try/except around `async_create_entry` / `async_update_entry`; on failure, `async_show_form` with error |
| Empty field inline error | Voluptuous validation; HA displays schema errors inline |
