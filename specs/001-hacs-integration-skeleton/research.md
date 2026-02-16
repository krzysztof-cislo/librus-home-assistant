# Research: HACS Integration Skeleton

**Date**: 2026-02-16  
**Feature**: HACS Integration Skeleton  
**Purpose**: Resolve technical unknowns for Home Assistant custom integration structure and HACS requirements

## Research Tasks

### Task 1: Home Assistant Integration Structure

**Decision**: Use standard Home Assistant custom integration structure with Python

**Rationale**: 
- Home Assistant integrations are Python-based and follow a standardized structure
- Must be placed in `custom_components/[domain]/` directory
- Minimum required files: `__init__.py`, `manifest.json`
- For config flow: add `config_flow.py`

**Alternatives considered**:
- None - this is the standard pattern required by Home Assistant

**References**:
- Home Assistant Developer Docs: Integration file structure
- Home Assistant Developer Docs: Integration manifest

---

### Task 2: HACS Repository Requirements

**Decision**: Follow HACS standard repository structure with required metadata files

**Rationale**:
- HACS requires files in `ROOT_OF_THE_REPO/custom_components/INTEGRATION_NAME/`
- Only one integration per repository allowed
- `hacs.json` file recommended in repository root
- Integration must be registered in home-assistant/brands repository
- GitHub releases preferred but optional

**Alternatives considered**:
- None - HACS has strict requirements for discovery and installation

**References**:
- HACS Documentation: Publishing integrations
- HACS Documentation: Include default repositories

---

### Task 3: Single Instance Configuration Pattern

**Decision**: Use `single_config_entry: true` manifest option for single instance enforcement

**Rationale**:
- Home Assistant 2024.3+ provides built-in `single_config_entry` manifest option
- Automatically prevents multiple config entries without manual code checks
- Simplifies implementation and follows best practices
- Aligns with spec requirement for single instance only

**Alternatives considered**:
- Manual check in config flow: More code, error-prone, not recommended
- Using `unique_id` pattern: More complex, unnecessary for skeleton

**References**:
- Home Assistant Developer Docs: Single instance only manifest option
- Home Assistant Developer Docs: Config flow handler

---

### Task 4: Config Flow Implementation Pattern

**Decision**: Implement minimal config flow with single confirmation step using `async_step_user`

**Rationale**:
- Config flow must extend `homeassistant.config_entries.ConfigFlow` with domain parameter
- Use `async_step_user` as entry point (standard pattern)
- Single confirmation step aligns with spec requirement
- Must set `VERSION` and optionally `MINOR_VERSION` in ConfigFlow class
- Update manifest.json with `config_flow: true`

**Alternatives considered**:
- Zero-step flow: Not standard Home Assistant pattern, may confuse users
- Multi-step flow: Unnecessary complexity for skeleton

**References**:
- Home Assistant Developer Docs: Config flow
- Home Assistant Developer Docs: Config entries

---

### Task 5: Error Handling Pattern

**Decision**: Use Home Assistant's built-in error handling with `async_show_form` error parameter

**Rationale**:
- Home Assistant provides `errors` dictionary parameter in `async_show_form`
- Can display user-friendly error messages in config flow UI
- For duplicate configuration, `single_config_entry` handles prevention automatically
- Simple error messages sufficient for skeleton (per spec clarification)

**Alternatives considered**:
- Custom error handling: Unnecessary complexity for skeleton
- Silent prevention: Doesn't meet spec requirement for user-friendly messages

**References**:
- Home Assistant Developer Docs: Config flow error handling

---

## Technology Stack Decisions

### Language & Version
- **Python 3.11+**: Home Assistant requires Python 3.11 or higher
- **Type hints**: Recommended for Home Assistant integrations

### Dependencies
- **homeassistant**: Core Home Assistant package (required)
- **No external dependencies**: Skeleton has no functionality requiring additional packages

### Testing
- **pytest**: Standard Python testing framework
- **pytest-homeassistant-custom-component**: Home Assistant testing utilities
- **pytest-asyncio**: For async test support

### Target Platform
- **Home Assistant Core**: Runs on Home Assistant instance
- **Python 3.11+**: Required Python version
- **Linux/Unix/Windows**: Home Assistant supported platforms

---

## Integration Domain & Naming

**Decision**: Domain name and display name will be determined during implementation

**Rationale**: 
- Spec assumption states "Integration domain name and display name will be determined during implementation"
- Domain must be unique and follow Home Assistant naming conventions
- Display name should be user-friendly

**Note**: This is a placeholder decision - actual domain/name will be set when creating the integration files.

---

## Summary

All technical unknowns resolved:
- ✅ Integration structure: `custom_components/[domain]/` with standard files
- ✅ HACS requirements: Repository structure and metadata files
- ✅ Single instance: Use `single_config_entry: true` manifest option
- ✅ Config flow: Minimal single-step confirmation flow
- ✅ Error handling: Built-in Home Assistant error display
- ✅ Technology stack: Python 3.11+, Home Assistant core dependencies

Ready to proceed to Phase 1: Design & Contracts.
