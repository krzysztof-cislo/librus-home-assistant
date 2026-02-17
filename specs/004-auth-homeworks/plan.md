# Implementation Plan: Auth Flow and Homework Integration

**Branch**: `004-auth-homeworks` | **Date**: 2025-02-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-auth-homeworks/spec.md`

**User Guidance**: Use /HomeWorks API for data; /HomeWorks/Categories, /Subjects, /Users for lookups; prefer bulk fetch over per-ID calls; use Content field for homework body; reference `docs/postman/responses/` and `docs/postman/librus_api.json`.

## Summary

(1) **Auth flow**: Already implemented in `librus_client.validate_credentials` (five-step OAuth). Verify alignment with Postman Auth folder. (2) **Homework feature**: Add homework retrieval via GET /HomeWorks, resolve IDs from bulk endpoints (/HomeWorks/Categories, /Subjects, /Users), filter by date (past 7, next 14 days), expose as single sensor with structured list. Refresh hourly and on demand.

## Technical Context

**Language/Version**: Python 3.11+ (Home Assistant requirement)

**Primary Dependencies**:
- `homeassistant` (core)
- `requests` (HTTP client)

**Storage**: Home Assistant config entry; no persistent storage for homework (fetched on refresh)

**Testing**: `pytest`, `pytest-homeassistant-custom-component`, `pytest-asyncio`; mock API responses for homework flow

**Target Platform**: Home Assistant Core (Python 3.11+)

**Project Type**: Single project (Home Assistant custom integration)

**Performance Goals**:
- Config flow: <30s (SC-001)
- On-demand refresh: <60s (SC-005)
- 4 API calls per refresh (bulk strategy)

**Constraints**:
- Bulk fetch only (no per-ID lookups)
- Single sensor with list structure (FR-005)
- Date scope: past 7, next 14 days (FR-005a)

**Scale/Scope**: Single student; ~50–200 homework entries typical; hourly refresh

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution file found at `.specify/memory/constitution.md`

**Note**: Proceeding without constitution constraints.

## Project Structure

### Documentation (this feature)

```text
specs/004-auth-homeworks/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── librus-homeworks-api.md
│   └── homework-sensor-entity.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
custom_components/
└── librus/
    ├── __init__.py           # Register coordinator, sensor platform
    ├── manifest.json
    ├── config_flow.py        # Auth validation (existing)
    ├── const.py              # Add DOMAIN keys for homework
    ├── librus_client.py      # Extend: add session-based fetch for HomeWorks, Categories, Subjects, Users
    ├── coordinator.py         # NEW: LibrusDataUpdateCoordinator (hourly + on-demand)
    ├── sensor.py             # NEW: Homework sensor entity
    └── strings.json
```

**Structure Decision**: Extend `custom_components/librus/`. Add `coordinator.py` for data refresh and `sensor.py` for the homework entity. Extend `librus_client.py` with session-based API calls (reuse existing OAuth flow for session creation).

## Phase 0: Research (Complete)

See [research.md](./research.md). Key decisions: bulk fetch, Content field, client-side date filter, ID resolution from Categories/Subjects/Users.

## Phase 1: Design (Complete)

- [data-model.md](./data-model.md) — HomeworkEntry, lookup resolution
- [contracts/librus-homeworks-api.md](./contracts/librus-homeworks-api.md) — API endpoints
- [contracts/homework-sensor-entity.md](./contracts/homework-sensor-entity.md) — Entity contract

## Complexity Tracking

None. No constitution violations.
