# Research: Config Flow with Librus Credentials

**Date**: 2026-02-16  
**Feature**: Config Flow with Librus Credentials (002-config-flow-librus-auth)  
**Purpose**: Resolve technical unknowns for credential collection, validation, secure storage, and reconfigure flow

## Research Tasks

### Task 1: Librus Authentication for Credential Validation

**Decision**: Use `py-librus-api` library for credential validation

**Rationale**:
- Mature Python library for Librus e-register API
- Simple synchronous `login(login, password)` returns `True` on success, `False` on failure
- Raises `ConnectionError` on network issues; `"User not logged in"` exception when operations attempted without auth
- Must wrap in `asyncio.to_thread()` or `run_in_executor` since Home Assistant config flows are async
- Aligns with spec: validate credentials against Librus before saving

**Alternatives considered**:
- `librusapi`: Uses `get_token()` for screen-scraping; different API style
- Custom HTTP requests: More work, fragile against Librus changes
- Defer validation: Rejected per spec clarification (must validate on submit)

**References**:
- https://github.com/lomber1/py-librus-api
- https://pypi.org/project/py-librus-api/

---

### Task 2: Secure Credential Storage in Home Assistant

**Decision**: Store credentials in config entry `data`; follow Home Assistant config entry storage conventions

**Rationale**:
- Home Assistant stores config entry data in `.storage/core.config_entries` (JSON, not YAML)
- Config entry data is the standard mechanism for integrations requiring username/password
- Storage directory has restricted filesystem permissions (owned by HA process)
- Password field in config flow UI is masked by default (voluptuous `str` type)
- Config entry data is not included in `configuration.yaml` or standard YAML exports
- OAuth2/Application Credentials exist but are for OAuth flows; Librus uses username/password
- Never log or print credentials; ensure reconfigure UI does not display password in plain text

**Alternatives considered**:
- Application Credentials (OAuth2): Librus does not support OAuth; spec assumes username/password
- `secrets.yaml`: For YAML config only; config flows use config entry storage
- External secrets manager: Overkill; not standard for HA custom integrations

**References**:
- Home Assistant Developer Docs: Config entries
- Home Assistant Developer Docs: Config flow handler

---

### Task 3: Config Flow with Reconfigure Support

**Decision**: Implement `async_step_user` for initial setup and `async_step_reconfigure` for credential updates

**Rationale**:
- `async_step_user`: Entry point when user adds integration; collect login/password, validate, save
- `async_step_reconfigure`: Called when user clicks "Configure" on existing integration; same form, validate, update via `async_update_reload_and_abort`
- Use `self._get_reconfigure_entry()` in reconfigure step to access existing entry
- Both steps validate against Librus before persisting (per spec clarification)
- Single schema can be reused for both user and reconfigure steps

**Alternatives considered**:
- Options flow: Meant for optional settings; credentials are core setup data—reconfigure is correct
- Reauth step: For expired/invalid credentials discovered at runtime; reconfigure handles proactive updates

**References**:
- Home Assistant Developer Docs: Config flow – Reconfigure
- Home Assistant Developer Docs: Config flow – Reauthentication

---

### Task 4: Inline Validation and Error Handling

**Decision**: Use `vol.Required()` for login and password; use `errors` dict in `async_show_form` for inline errors

**Rationale**:
- `vol.Required("login")` and `vol.Required("password")` prevent submit when empty; Voluptuous validation fails and re-shows form
- For Librus validation failure: `return self.async_show_form(..., errors={"base": "invalid_auth"})` to show error at top; can use field-specific keys for per-field errors
- For empty fields: Voluptuous raises; catch and map to `errors={"login": "required"}` or similar for inline display—or rely on vol.Required which blocks submit (no submit = no error needed; form stays visible)
- Spec says "inline error under empty field(s)"—HA's default vol.Required behavior shows validation error when submit attempted with empty; schema validation provides this
- For storage failure: Catch exception, return `async_show_form` with `errors={"base": "cannot_connect"}` or custom key; user remains on form to retry

**Alternatives considered**:
- Custom validation step: Unnecessary; validation in same step is simpler
- Summary error only: Spec requires inline for empty fields; vol.Required provides this

**References**:
- Home Assistant Developer Docs: Config flow – async_show_form
- Data entry flow – error parameter

---

### Task 5: Project Structure (Existing Architecture)

**Decision**: Extend existing `custom_components/librus/` structure; add dependency on `py-librus-api`

**Rationale**:
- User input: "use existing architecture which should match home assistant hacs integration"
- Structure already in place from 001-hacs-integration-skeleton: `config_flow.py`, `manifest.json`, `__init__.py`, `const.py`
- Add `py-librus-api` to `manifest.json` requirements
- No new top-level directories; only modify existing integration files
- Add `api.py` or `librus_client.py` to encapsulate Librus API calls for validation (testable, reusable for future features)

**Alternatives considered**:
- New integration domain: Rejected; extend existing librus integration
- Inline API calls in config_flow: Extract to helper for testability and reuse

---

## Technology Stack Decisions

### Language & Version
- **Python 3.11+**: Home Assistant requirement (unchanged from 001)

### Dependencies
- **homeassistant**: Core (required)
- **py-librus-api**: For credential validation (add to manifest `requirements`)

### Storage
- **Config entry data**: Credentials stored in `entry.data`; keys `username` (or `login`), `password`; consistent with const.py naming

### Testing
- **pytest**, **pytest-homeassistant-custom-component**, **pytest-asyncio**: Unchanged
- Mock Librus API in tests to avoid real network calls

---

## Summary

All technical unknowns resolved:
- ✅ Librus validation: py-librus-api `login()` in executor
- ✅ Credential storage: Config entry data (standard HA pattern)
- ✅ Reconfigure flow: `async_step_reconfigure` with validation
- ✅ Inline errors: vol.Required + errors dict in async_show_form
- ✅ Architecture: Extend existing custom_components/librus

Ready to proceed to Phase 1: Design & Contracts.
