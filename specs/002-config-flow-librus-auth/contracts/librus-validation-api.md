# Librus Validation API Contract

**Date**: 2026-02-16  
**Feature**: Config Flow with Librus Credentials

## Overview

This contract defines how the integration validates Librus credentials using the `py-librus-api` library. The library is synchronous; Home Assistant config flows are async—validation must run in an executor.

## API: py-librus-api

**Package**: `py-librus-api`  
**Import**: `from py_librus_api import Librus`

### Method: login

```python
def login(login: str, password: str) -> bool
```

- **Returns**: `True` if login successful, `False` if credentials invalid
- **Raises**: `ConnectionError` or similar on network failure

### Usage Pattern

```python
librus = Librus()
success = librus.login(username, password)
if success:
    # Valid
else:
    # Invalid credentials
```

## Integration Wrapper

The config flow must not block the event loop. Use `hass.async_add_executor_job`:

```python
def _validate_sync(username: str, password: str) -> bool:
    from py_librus_api import Librus
    librus = Librus()
    return librus.login(username, password)

async def _validate_librus_credentials(hass, username: str, password: str) -> bool:
    return await hass.async_add_executor_job(_validate_sync, username, password)
```

## Error Handling

| Condition | Result | Integration Response |
|-----------|--------|------------------------|
| Valid credentials | `login()` returns True | Proceed to save |
| Invalid credentials | `login()` returns False | Show "invalid_auth" error |
| Network error | Exception raised | Show "cannot_connect" error |
| Timeout | May raise or hang | Consider adding timeout; show "cannot_connect" |

## Out of Scope (This Feature)

- Session persistence: We only validate; no need to keep Librus session
- API data fetching: Credentials stored for future use
- Token refresh: Librus uses username/password per request (no OAuth tokens)
