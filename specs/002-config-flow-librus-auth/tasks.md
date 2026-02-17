# Tasks: Config Flow with Librus Credentials

**Input**: Design documents from `/specs/002-config-flow-librus-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec; test tasks omitted. Add manually if TDD preferred.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Integration: `custom_components/librus/`
- Tests: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependency and constants required by all user stories

- [X] T001 Add `py-librus-api>=0.3.1` to `requirements` in `custom_components/librus/manifest.json`
- [X] T002 [P] Add `CONF_USERNAME` and `CONF_PASSWORD` constants in `custom_components/librus/const.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create Librus validation helper and shared config flow schema used by user and reconfigure steps

**Checkpoint**: Foundation ready—user story implementation can begin

- [X] T003 Implement `_validate_librus_credentials_sync` and `_validate_librus_credentials` helpers in `custom_components/librus/config_flow.py` (runs Librus.login in executor; see contracts/config-flow-schema.md)
- [X] T004 Define `DATA_SCHEMA` with `vol.Required(CONF_USERNAME)` and `vol.Required(CONF_PASSWORD)` in `custom_components/librus/config_flow.py`

---

## Phase 3: User Story 1 - Configure Integration with Librus Credentials (Priority: P1) 🎯 MVP

**Goal**: User can add the integration, enter login and password, have credentials validated against Librus, and on success have the integration configured with credentials stored.

**Independent Test**: Add Integration → Enter valid Librus credentials → Submit → Integration configures; invalid credentials show error and allow retry.

### Implementation for User Story 1

- [X] T005 [US1] Replace empty schema in `async_step_user` with credential form (login, password) in `custom_components/librus/config_flow.py`
- [X] T006 [US1] Add Librus validation before `async_create_entry` in `async_step_user`; on failure return `async_show_form` with `errors={"base": "invalid_auth"}` in `custom_components/librus/config_flow.py`
- [X] T007 [US1] Add exception handling around Librus validation; on connection/network error return `async_show_form` with `errors={"base": "cannot_connect"}` in `custom_components/librus/config_flow.py`
- [X] T008 [US1] Update `async_create_entry` to pass `data={CONF_USERNAME, CONF_PASSWORD}` in `custom_components/librus/config_flow.py`
- [X] T009 [US1] Add try/except around `async_create_entry`; on storage failure return `async_show_form` with `errors={"base": "unknown"}` in `custom_components/librus/config_flow.py`

**Checkpoint**: User Story 1 complete—initial config flow with credential collection and Librus validation works

---

## Phase 4: User Story 2 - Credentials Stored Securely (Priority: P2)

**Goal**: Credentials are stored in config entry data; never logged; password never displayed in plain text in UI.

**Independent Test**: Configure integration → Verify credentials not in logs; password masked in form; no plain-text exposure in config export.

### Implementation for User Story 2

- [X] T010 [US2] Audit `custom_components/librus/config_flow.py` and `custom_components/librus/__init__.py`; ensure no `_LOGGER` or print of username/password
- [X] T011 [US2] Verify password field uses default masking (vol str in schema; HA masks password inputs by default) in `custom_components/librus/config_flow.py`
- [X] T012 [US2] Create `custom_components/librus/strings.json` with config step titles and error keys (`invalid_auth`, `cannot_connect`, `unknown`) so errors display user-friendly messages

**Checkpoint**: User Story 2 complete—credentials handled securely; no exposure in logs or UI

---

## Phase 5: User Story 3 - Reconfigure or Update Credentials (Priority: P3)

**Goal**: User can update Librus credentials via integration Configure flow; validation against Librus before saving.

**Independent Test**: With integration configured → Click Configure → Update login/password → Submit → Credentials updated; invalid credentials show error and allow retry.

### Implementation for User Story 3

- [X] T013 [US3] Implement `async_step_reconfigure` in `custom_components/librus/config_flow.py` with same schema and flow as `async_step_user`
- [X] T014 [US3] Pre-fill username from `entry.data` in reconfigure form; leave password empty in `custom_components/librus/config_flow.py`
- [X] T015 [US3] Add Librus validation in `async_step_reconfigure`; on success call `async_update_reload_and_abort(entry, data_updates={username, password})` in `custom_components/librus/config_flow.py`
- [X] T016 [US3] Add error handling (invalid_auth, cannot_connect) and storage failure handling in `async_step_reconfigure` in `custom_components/librus/config_flow.py`
- [X] T017 [US3] Add reconfigure step translations to `custom_components/librus/strings.json`

**Checkpoint**: User Story 3 complete—reconfigure flow works; credentials can be updated

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Migration for existing entries, README update, validation

- [X] T018 Implement `async_migrate_entry` in `custom_components/librus/__init__.py` if needed (migrate empty `entry.data` to include username/password placeholders for users who must reconfigure)
- [X] T019 [P] Update `README.md` with configuration instructions (enter Librus login and password; reconfigure via Configure button)
- [X] T020 Run manual validation per `quickstart.md` (initial config, invalid credentials, empty fields, reconfigure, single instance)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies—start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1—blocks all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 3 (audits config_flow from US1)
- **Phase 5 (US3)**: Depends on Phase 3 (reconfigure extends config_flow)
- **Phase 6 (Polish)**: Depends on Phases 3–5

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational—no other story dependencies
- **User Story 2 (P2)**: Builds on US1; audits and strings
- **User Story 3 (P3)**: Builds on US1; adds reconfigure step

### Within Each User Story

- US1: Schema → validation → create entry → error handling
- US2: Audit → verify → translations
- US3: reconfigure step → pre-fill → validation → update → errors → translations

### Parallel Opportunities

- T001 and T002 can run in parallel (Phase 1)
- T010, T011 can run in parallel (Phase 4)
- T018 and T019 can run in parallel (Phase 6)

---

## Parallel Example: Phase 1

```bash
# Launch Setup tasks together:
Task T001: "Add py-librus-api to manifest.json"
Task T002: "Add CONF_USERNAME, CONF_PASSWORD to const.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Add Integration with valid/invalid credentials
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test initial config flow → MVP
3. Add User Story 2 → Verify secure handling
4. Add User Story 3 → Test reconfigure flow
5. Polish → Migration, docs, manual validation

### Sequential Execution (Single Developer)

1. T001 → T002 → T003 → T004 (Setup + Foundational)
2. T005 → T006 → T007 → T008 → T009 (US1)
3. T010 → T011 → T012 (US2)
4. T013 → T014 → T015 → T016 → T017 (US3)
5. T018 → T019 → T020 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to user story for traceability
- Each user story independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
