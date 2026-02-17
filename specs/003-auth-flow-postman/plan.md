# Implementation Plan: Full Auth Flow During Integration Configuration

**Branch**: `003-auth-flow-postman` | **Date**: 2025-02-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-auth-flow-postman/spec.md`

## Summary

Replace the current four-step Librus credential validation with the full five-step OAuth sequence from the Postman collection (docs/postman/librus_api.json). Credentials are valid only when all five steps succeed: OAuth Init, OAuth Login, OAuth Grant, Get Token Info, Activate API Access. Key changes: (1) use OAuth/Grant instead of OAuth/2FA for Step 3; (2) add TokenInfo and UserInfo steps to activate the JSON API; (3) add timeout error key and LibrusTimeoutError; (4) ensure session discard on failure.

## Technical Context

**Language/Version**: Python 3.11+ (Home Assistant requirement)

**Primary Dependencies**:
- `homeassistant` (core package)
- `requests` (HTTP client—already used, no new deps)

**Storage**: Home Assistant config entry data; credentials stored only after successful validation

**Testing**: `pytest`, `pytest-homeassistant-custom-component`, `pytest-asyncio`; mock `requests.Session` for unit tests

**Target Platform**: Home Assistant Core (Python 3.11+)

**Project Type**: Single project (Home Assistant custom integration)

**Performance Goals**: Config flow completes in under 30 seconds (SC-001); validation typically <15s for five HTTP calls

**Constraints**:
- Must follow Postman Auth folder sequence exactly (FR-007)
- No retries (FR-009)
- Session discarded on failure (FR-010)
- Generic error categories only (FR-006)

**Scale/Scope**: One config entry; single set of credentials; config-time validation only (token refresh out of scope)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution file found at `.specify/memory/constitution.md`

**Note**: Proceeding without constitution constraints.

## Project Structure

### Documentation (this feature)

```text
specs/003-auth-flow-postman/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth-flow-sequence.md
│   └── validate-credentials-signature.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
custom_components/
└── librus/
    ├── __init__.py
    ├── manifest.json
    ├── config_flow.py       # Update: map timeout, LibrusTimeoutError
    ├── const.py
    ├── librus_client.py     # Rewrite validate_credentials (5 steps)
    └── strings.json         # Add timeout error message

tests/
├── test_config_flow.py      # Extend for new flow
└── test_librus_client.py   # Add/update for validate_credentials
```

**Structure Decision**: Extend existing `custom_components/librus/`. No new top-level directories. Primary changes: `librus_client.py` (full rewrite of auth logic), `config_flow.py` (error mapping), `strings.json` (timeout key).

## Complexity Tracking

No violations—standard extension of existing integration.
