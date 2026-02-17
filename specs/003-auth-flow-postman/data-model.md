# Data Model: Full Auth Flow

**Feature**: 003-auth-flow-postman  
**Date**: 2025-02-17

## Entities

### Credentials

User-provided login and password. Stored only after successful validation.

| Field | Type | Validation | Notes |
|-------|------|------------|-------|
| username | string | Non-empty | Librus login |
| password | string | Non-empty | Librus password |

**Lifecycle**: Provided in config flow form → validated by five-step flow → stored in `ConfigEntry.data` on success; never stored on failure (FR-005).

---

### Auth Session (Transient)

Temporary HTTP session established during validation. Not persisted.

| Attribute | Type | Notes |
|----------|------|-------|
| cookies | dict | Set by api.librus.pl and synergia.librus.pl redirects |
| headers | dict | User-Agent, Referer |
| domain | — | Cookies scoped to synergia.librus.pl, api.librus.pl |

**Lifecycle**: Created at start of `validate_credentials` → used for Steps 1–5 → discarded when function returns (success or failure). On failure, must not be reused (FR-010).

---

### Integration Configuration (ConfigEntry.data)

Stored configuration after successful validation.

| Field | Type | Source |
|-------|------|--------|
| CONF_USERNAME | string | From form |
| CONF_PASSWORD | string | From form |

**State transitions**: None during this feature. Entry created/updated only when all five auth steps succeed.

---

### TokenInfo Response (External API)

Response from `GET /gateway/api/2.0/Auth/TokenInfo` used internally during validation.

| Field | Type | Notes |
|-------|------|-------|
| UserIdentifier | string | Required for Step 5 (UserInfo URL path) |

**Validation**: If missing or non-200, validation fails → `cannot_connect` or `invalid_auth` per response semantics.

---

## State Transitions

```
[User submits form]
       ↓
[Create new Session]
       ↓
[Step 1: Init] ──fail──→ [Discard session] → [Show error]
       ↓ ok
[Step 2: Login] ──fail──→ [Discard session] → [Show error]
       ↓ ok
[Step 3: Grant] ──fail──→ [Discard session] → [Show error]
       ↓ ok
[Step 4a: TokenInfo] ──fail──→ [Discard session] → [Show error]
       ↓ ok (extract UserIdentifier)
[Step 5: UserInfo] ──fail──→ [Discard session] → [Show error]
       ↓ ok
[Store credentials in ConfigEntry]
```

---

## Error Keys (strings.json)

| Key | User message | When used |
|-----|--------------|-----------|
| invalid_auth | Invalid login or password | Login failure, auth error in response |
| cannot_connect | Could not connect to Librus | Connection error, HTTP 5xx, other network |
| timeout | Connection timed out | requests.Timeout |
| unknown | An unexpected error occurred | Unexpected exception |
