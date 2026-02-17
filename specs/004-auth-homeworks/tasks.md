# Tasks: Auth Flow and Homework Integration

**Input**: Design documents from `/specs/004-auth-homeworks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

**Tests**: Not explicitly requested in spec; no test tasks included.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Home Assistant custom integration**: `custom_components/librus/` at repository root
- **API reference**: `docs/postman/librus_api.json`, `docs/postman/responses/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add constants and ensure manifest supports new components

- [x] T001 Add homework-related constants to custom_components/librus/const.py (e.g., CONF_UPDATE_INTERVAL, sensor entity ID key)
- [x] T002 [P] Ensure custom_components/librus/manifest.json includes any new dependencies if needed (requests already present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Session-based API client that authenticates and fetches HomeWorks, Categories, Subjects, Users. BLOCKS US2 and US3.

**⚠️ CRITICAL**: No homework feature work can begin until this phase is complete

- [x] T003 Extend custom_components/librus/librus_client.py with a class or functions that: (1) perform full 5-step OAuth to obtain authenticated session, (2) fetch GET /HomeWorks, GET /HomeWorks/Categories, GET /Subjects, GET /Users using that session (bulk fetch per research.md)
- [x] T004 Add fetch_homework_data(username, password) (or equivalent) in custom_components/librus/librus_client.py that returns structured homework entries: list of dicts with id, date, subject, creator, category, lesson_no, time_from, time_to, content, add_date per data-model.md
- [x] T005 Implement client-side date filtering in custom_components/librus/librus_client.py: include only entries where Date is within [today - 7 days, today + 14 days] (FR-005a)
- [x] T006 Implement ID resolution in custom_components/librus/librus_client.py: map Category.Id → Name, CreatedBy.Id → "FirstName LastName", Subject.Id → Name; use "Unknown" when absent or unresolved (FR-010, data-model validation rules)
- [x] T007 Add error handling in custom_components/librus/librus_client.py for fetch_homework_data: raise LibrusConnectionError, LibrusTimeoutError, or return empty list / signal failure per FR-009

**Checkpoint**: Librus client can fetch and return homework data; US2 and US3 can proceed

---

## Phase 3: User Story 1 - Integration Setup with Full Auth Validation (Priority: P1) 🎯 MVP

**Goal**: Credentials validated via five-step OAuth; integration created only when all steps succeed.

**Independent Test**: Add or reconfigure integration with valid credentials; integration created. With invalid credentials, error shown and nothing stored.

### Implementation for User Story 1

- [x] T008 [P] [US1] Verify custom_components/librus/librus_client.py validate_credentials implements all five steps per docs/postman/librus_api.json Auth folder: OAuth Init, Login, Grant, TokenInfo, Activate API Access
- [x] T009 [P] [US1] Verify custom_components/librus/config_flow.py correctly maps LibrusTimeoutError → "timeout", LibrusConnectionError → "cannot_connect", invalid credentials → "invalid_auth"
- [x] T010 [P] [US1] Verify custom_components/librus/strings.json (or translations) has user-facing messages for invalid_auth, timeout, cannot_connect, unknown

**Checkpoint**: Auth flow verified; integration setup works as specified

---

## Phase 4: User Story 2 - View Homework in Home Assistant (Priority: P2)

**Goal**: Homework entries displayed in Home Assistant via single sensor with structured list (date, subject, creator, category, lesson_no, time, content).

**Independent Test**: Configure integration, wait for initial refresh; sensor shows homework entries with required fields.

### Implementation for User Story 2

- [x] T011 [US2] Create custom_components/librus/coordinator.py with LibrusDataUpdateCoordinator that uses DataUpdateCoordinator, calls librus_client fetch logic in executor, stores homework list in coordinator.data
- [x] T012 [US2] Implement coordinator async_update_data in custom_components/librus/coordinator.py to call fetch_homework_data with config entry credentials and handle errors (preserve previous data on failure per FR-009)
- [x] T013 [US2] Create custom_components/librus/sensor.py with HomeworkSensor entity that reads from coordinator.data, exposes homework_entries as attribute (list of dicts per data-model.md HomeworkEntry)
- [x] T014 [US2] Set sensor state to count of homework entries (or similar); ensure entity distinguishes "no homework" (empty list) from "unavailable" (refresh failed) per SC-006
- [x] T015 [US2] Register coordinator and sensor platform in custom_components/librus/__init__.py: create coordinator on async_setup_entry, forward entry to sensor platform, clean up on unload

**Checkpoint**: Homework sensor visible in Home Assistant; shows entries after first successful refresh

---

## Phase 5: User Story 3 - Automatic and On-Demand Refresh (Priority: P3)

**Goal**: Homework refreshes automatically every hour; user can trigger on-demand refresh.

**Independent Test**: Verify hourly refresh runs; trigger on-demand refresh and see updated data within 60 seconds.

### Implementation for User Story 3

- [x] T016 [US3] Set coordinator update_interval to 1 hour (datetime.timedelta(hours=1)) in custom_components/librus/coordinator.py per FR-007
- [x] T017 [US3] Expose on-demand refresh via service call `librus.refresh_homework` that invokes coordinator.async_request_refresh(); register service in custom_components/librus/__init__.py and wire to coordinator per FR-008

**Checkpoint**: Hourly auto-refresh and on-demand refresh both work

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, logging, UX polish

- [x] T018 [P] Add logging in custom_components/librus/coordinator.py and custom_components/librus/sensor.py for refresh success/failure, API errors
- [x] T019 Ensure custom_components/librus/strings.json has any new translation keys for homework sensor (name, state messages if needed)
- [x] T020 Run quickstart.md validation: verify integration setup (<30s), homework sensor appears, refresh works; verify on-demand refresh via librus.refresh_homework completes within 60s (SC-001, SC-005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS US2, US3
- **Phase 3 (US1)**: Can run in parallel with Phase 2 (verification only; auth already exists)
- **Phase 4 (US2)**: Depends on Phase 2 — needs librus_client fetch
- **Phase 5 (US3)**: Depends on Phase 4 — extends coordinator and sensor
- **Phase 6 (Polish)**: Depends on Phase 5

### User Story Dependencies

- **US1**: Independent; verification of existing auth (can run anytime)
- **US2**: Depends on Foundational (T003–T007)
- **US3**: Depends on US2 (coordinator must exist for interval and on-demand)

### Parallel Opportunities

- T001 and T002 can run in parallel (Phase 1)
- T008, T009, T010 (US1) can run in parallel
- T018 can run in parallel with T019 (Phase 6)

---

## Parallel Example: Phase 1 + US1

```bash
# Phase 1
T001: Add constants to const.py
T002: Check manifest.json

# US1 (verification)
T008: Verify librus_client auth steps
T009: Verify config_flow error mapping
T010: Verify strings.json
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1: Setup
2. Phase 2: Foundational (librus_client homework fetch)
3. Phase 3: US1 verification (quick)
4. Phase 4: US2 (coordinator + sensor)
5. **STOP and VALIDATE**: Configure integration, see homework in HA
6. Phase 5: US3 (refresh interval + on-demand)
7. Phase 6: Polish

### Incremental Delivery

- After Phase 4: Homework visible in HA (manual/initial refresh only)
- After Phase 5: Full refresh behavior (hourly + on-demand)
- After Phase 6: Production-ready with logging and validation

---

## Notes

- [P] tasks = different files or no dependencies
- [Story] label maps task to user story for traceability
- Librus API base: https://synergia.librus.pl/gateway/api/2.0
- Reference responses: docs/postman/responses/Homeworks.json, Homeworks_Categories.json, Subjects.json, Users.json
