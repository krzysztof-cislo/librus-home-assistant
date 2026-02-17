# Research: Full Auth Flow for Librus Integration

**Feature**: 003-auth-flow-postman  
**Date**: 2025-02-17

## 1. Librus OAuth Flow: Grant vs 2FA

**Decision**: Use `OAuth/Authorization/Grant` (not `/2FA`) for Step 3.

**Rationale**: The Postman collection and librusik reference library explicitly state Step 3 is `/Grant`. The current implementation uses `/2FA`, which is deprecated or incorrect for standard Librus accounts. The Postman description: "UWAGA: To jest /Grant (NIE /2FA). Potwierdzone w działającej bibliotece librusik."

**Alternatives considered**:
- Keep `/2FA`: Rejected—Postman and librusik document `/Grant` as correct
- Support both: Rejected—adds complexity; spec requires single reference flow

---

## 2. Five-Step Sequence vs Current Four-Step

**Decision**: Replace current four-step flow with the full five-step sequence from Postman.

**Rationale**: Current flow: (1) Init, (2) Login, (3) 2FA, (4) GET synergia.librus.pl. This does not activate the JSON API—TokenInfo and UserInfo are required to enable access to `gateway/api/2.0` endpoints. Credentials may pass current validation but fail when integration tries to fetch grades/timetable. Spec FR-007 requires full Postman Auth folder sequence.

**Five steps**:
1. OAuth Init: GET `api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata`
2. OAuth Login: POST credentials to same URL
3. OAuth Grant: GET `api.librus.pl/OAuth/Authorization/Grant?client_id=46`
4. Get Token Info: GET `synergia.librus.pl/gateway/api/2.0/Auth/TokenInfo` → extract `UserIdentifier`
5. Activate API Access: GET `synergia.librus.pl/gateway/api/2.0/Auth/UserInfo/{UserIdentifier}`

**Alternatives considered**:
- Keep current flow: Rejected—does not activate JSON API
- Add TokenInfo only: Rejected—UserInfo activation step required per Postman

---

## 3. Error Category Mapping

**Decision**: Map failures to three generic categories—`invalid_auth`, `cannot_connect`, `timeout`—with distinct user-facing messages. Map HTTP/response semantics to these; do not expose per-step details.

**Rationale**: Spec FR-006 and SC-005 require generic categories only; connection/timeout must be distinguishable from invalid credentials. Home Assistant config flow uses `errors["base"] = "<key>"`; keys map to `strings.json`.

**Mapping**:
- Steps 1–2 body contains "error"/"Nieprawidłowy" or login returns auth failure → `invalid_auth`
- Timeout on any request → `timeout` (new key)
- Connection error, HTTP 5xx, other network errors → `cannot_connect`

**Alternatives considered**:
- Single "validation_failed" key: Rejected—violates SC-005
- Per-step keys: Rejected—violates FR-006

---

## 4. Session Cleanup on Failure

**Decision**: Use a new `requests.Session` per validation attempt; do not reuse. Discard session (let it go out of scope) immediately on any step failure. Do not persist cookies across attempts.

**Rationale**: Spec FR-010 requires discarding session state on failure. `requests.Session()` holds cookies in memory; creating a fresh session per call and not reusing it satisfies the requirement. Python GC will clean up when the function returns.

**Alternatives considered**:
- Explicit `session.close()`: Acceptable—redundant but clearer
- Reuse session for retries: Rejected—spec FR-009 forbids retries; FR-010 forbids reuse

---

## 5. Loading Message (FR-008)

**Decision**: Use Home Assistant's built-in progress indicator. Config flow automatically shows a loading state while `async_step_user` / `async_step_reconfigure` awaits `_validate_librus_credentials`. Add `description_placeholders` or ensure step title hints "Validating…" if needed. HA does not require custom progress UI for async validation.

**Rationale**: Home Assistant config flow blocks the form and shows a loading state during async operations. No custom step is needed. If the default is insufficient, a minor strings.json or step description update can add "Validating credentials…" context.

**Alternatives considered**:
- Custom progress step: Rejected—adds unnecessary complexity for config flow
- Disable form only: May be default—verify HA behavior; description_placeholders can reinforce message

---

## 6. Cookie Domain and Redirect Handling

**Decision**: Follow Postman: use `follow_redirects=True` for Steps 1–3 so the Grant redirect chain sets `synergia.librus.pl` cookies. Use same `User-Agent` and `Referer` as Postman. Session cookies are automatically stored by `requests.Session` when following redirects.

**Rationale**: Postman Auth steps use `followRedirects: true`. Grant step redirects to set session cookies on synergia.librus.pl. `requests` follows redirects by default. Ensure session is created fresh per validation to satisfy FR-010.

---

## Summary

| Topic | Decision |
|-------|----------|
| Step 3 URL | `/OAuth/Authorization/Grant` (not 2FA) |
| Full sequence | All 5 steps (Init, Login, Grant, TokenInfo, UserInfo) |
| Error keys | `invalid_auth`, `cannot_connect`, `timeout` |
| Session handling | New session per attempt; discard on failure |
| Loading UX | Rely on HA config flow async loading state |
