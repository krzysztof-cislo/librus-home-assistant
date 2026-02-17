# Quickstart: Full Auth Flow

**Feature**: 003-auth-flow-postman

## Goal

Replace the current four-step Librus auth flow with the full five-step sequence from the Postman collection. Credentials are valid only when all five steps succeed.

## Key Files

| File | Purpose |
|------|---------|
| `custom_components/librus/librus_client.py` | Implement five-step `validate_credentials` |
| `custom_components/librus/config_flow.py` | Map validation result/errors to HA error keys |
| `custom_components/librus/strings.json` | Add `timeout` error message |

## Implementation Sketch

### 1. Update librus_client.py

Replace `validate_credentials` to:

1. Create `session = requests.Session()` at start
2. **Step 1**: GET `api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata`
3. **Step 2**: POST credentials to same URL
4. **Step 3**: GET `api.librus.pl/OAuth/Authorization/Grant?client_id=46` (not `/2FA`)
5. **Step 4**: GET `synergia.librus.pl/gateway/api/2.0/Auth/TokenInfo` → parse JSON for `UserIdentifier`
6. **Step 5**: GET `synergia.librus.pl/gateway/api/2.0/Auth/UserInfo/{UserIdentifier}`

On any failure: return `False` or raise `LibrusConnectionError`; do not retry. Session is discarded when function returns.

See [contracts/auth-flow-sequence.md](./contracts/auth-flow-sequence.md) for full details.

### 2. Update config_flow.py

- Distinguish `LibrusConnectionError` subtypes if needed (timeout vs connection)
- Map to `invalid_auth`, `cannot_connect`, `timeout`, `unknown`
- Add `description` or `description_placeholders` for "Validating credentials…" if desired (HA may show loading state automatically)

### 3. Update strings.json

Add to `error` section:

```json
"timeout": "Connection to Librus timed out"
```

## Testing

```python
# Valid credentials
assert validate_credentials("valid_user", "valid_pass") is True

# Invalid credentials
assert validate_credentials("bad", "bad") is False

# Connection error
with patch("requests.Session.get", side_effect=requests.exceptions.Timeout()):
    with pytest.raises(LibrusConnectionError):
        validate_credentials("u", "p")
```

## Verification

1. Run all five Postman Auth steps manually with real credentials
2. Add integration in HA with valid credentials → entry created
3. Add with invalid credentials → "Invalid login or password"
4. Simulate timeout → "Connection to Librus timed out"
