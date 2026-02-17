# Contract: validate_credentials Function

**Module**: `custom_components.librus.librus_client`  
**Feature**: 003-auth-flow-postman

## Signature

```python
def validate_credentials(username: str, password: str) -> bool
```

## Behavior

- Executes the five-step auth flow (see [auth-flow-sequence.md](./auth-flow-sequence.md))
- Returns `True` if and only if all five steps succeed
- Raises `LibrusConnectionError` on timeout or connection failure (caller maps to `timeout` or `cannot_connect`)
- Returns `False` on auth failure (invalid credentials)
- Does NOT retry on failure (FR-009)
- Creates a new session per call; does not reuse sessions (FR-010)

## Exceptions

| Exception | Raised when | Caller maps to |
|-----------|-------------|----------------|
| `LibrusTimeoutError` (subclass of LibrusConnectionError) | `requests.exceptions.Timeout` | `timeout` |
| `LibrusConnectionError` | ConnectionError, other RequestException | `cannot_connect` |
| (none for auth failure) | Steps 2–5 indicate invalid auth | `invalid_auth` (return `False`) |

**Recommendation**: Introduce `LibrusTimeoutError` as a subclass of `LibrusConnectionError` so config_flow can distinguish with `isinstance(exc, LibrusTimeoutError)`.

## Caller Responsibility

Config flow (`config_flow.py`) must:
1. Call `validate_credentials` in executor (`async_add_executor_job`)
2. Map `False` → `errors["base"] = "invalid_auth"`
3. Map `LibrusTimeoutError` → `errors["base"] = "timeout"`
4. Map `LibrusConnectionError` → `errors["base"] = "cannot_connect"`
5. Map unexpected `Exception` → `errors["base"] = "unknown"`
