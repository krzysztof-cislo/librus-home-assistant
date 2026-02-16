# Implementation Plan: Config Flow with Librus Credentials

**Branch**: `002-config-flow-librus-auth` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-config-flow-librus-auth/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the Librus HACS integration with a credential-collecting config flow. Users enter Librus login and password; credentials are validated against Librus before saving and stored in the config entry. Support reconfigure flow for credential updates. Use existing architecture matching Home Assistant HACS integration structure. Dependencies: `py-librus-api` for validation; config entry data for storage.

## Technical Context

**Language/Version**: Python 3.11+ (Home Assistant requirement)

**Primary Dependencies**:
- `homeassistant` (core package, required)
- `py-librus-api` (Librus credential validation)

**Storage**: Home Assistant config entry data (`entry.data`); credentials stored as `username` and `password` keys

**Testing**:
- `pytest`
- `pytest-homeassistant-custom-component`
- `pytest-asyncio`
- Mock `py-librus-api` in tests

**Target Platform**: Home Assistant Core (Python 3.11+)

**Project Type**: Single project (Home Assistant custom integration)

**Performance Goals**: Config flow completes in under 2 minutes (per spec SC-001); Librus validation typically &lt;5s

**Constraints**:
- Must follow Home Assistant integration structure
- Single instance only (`single_config_entry: true`)
- Credentials never logged or displayed in plain text
- No format validation on login/password (use as provided)

**Scale/Scope**:
- One configuration entry per Home Assistant instance
- One set of credentials per integration
- No runtime entities in this feature (credentials for future use)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution file found at `.specify/memory/constitution.md`

**Note**: Proceeding without constitution constraints. If constitution is added later, re-evaluate this plan.

## Project Structure

### Documentation (this feature)

```text
specs/002-config-flow-librus-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── config-flow-schema.md
│   └── librus-validation-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
custom_components/
└── librus/
    ├── __init__.py          # Component initialization (existing)
    ├── manifest.json        # Integration metadata (update: add py-librus-api)
    ├── config_flow.py       # Config flow handler (extend: user + reconfigure steps)
    ├── const.py             # Constants (add CONF_USERNAME, CONF_PASSWORD)
    └── strings.json         # Config flow translations (new)

tests/
├── __init__.py
├── test_config_flow.py      # Config flow tests (extend)
└── conftest.py

hacs.json
README.md
```

**Structure Decision**: Extend existing `custom_components/librus/` structure from 001-hacs-integration-skeleton. No new top-level directories. Add `strings.json` for translations; update `config_flow.py`, `manifest.json`, `const.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations—standard Home Assistant integration extension.
