# Tasks: Full Auth Flow During Integration Configuration

**Input**: Design documents from `/specs/003-auth-flow-postman/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec; omit test tasks.

**Organization**: Tasks grouped by user story. US1 and US2 share the same validation logic; foundational work blocks both.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Custom component**: `custom_components/librus/`
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and dependencies

- [X] T001 Verify custom_components/librus structure and that manifest.json has no new requirements (requests already used)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth client and error resources that BOTH user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add LibrusTimeoutError exception class (subclass of LibrusConnectionError) in custom_components/librus/librus_client.py
- [X] T003 [P] Add "timeout" error key with message "Connection to Librus timed out" to custom_components/librus/strings.json under config.error
- [X] T004 Rewrite validate_credentials in custom_components/librus/librus_client.py to implement the five-step auth flow per specs/003-auth-flow-postman/contracts/auth-flow-sequence.md: Step 1 OAuth Init, Step 2 OAuth Login, Step 3 OAuth Grant (not 2FA), Step 4 Get TokenInfo and extract UserIdentifier, Step 5 Activate API Access via UserInfo; use fresh requests.Session per call; raise LibrusTimeoutError on requests.Timeout, LibrusConnectionError on other network errors; return False on auth failure; no retries

**Checkpoint**: Foundation ready—librus_client exposes correct interface; user story implementation can begin

---

## Phase 3: User Story 1 - Initial Integration Setup with Full Auth Validation (Priority: P1) 🎯 MVP

**Goal**: User adds Librus integration with valid credentials; system validates via five-step flow; integration created only when all steps succeed

**Independent Test**: Add integration via HA UI with valid credentials → entry created. With invalid credentials → "Invalid login or password". With simulated timeout → "Connection to Librus timed out"

### Implementation for User Story 1

- [X] T005 [US1] Update custom_components/librus/config_flow.py: import LibrusTimeoutError from librus_client; in async_step_user and async_step_reconfigure add except LibrusTimeoutError before except LibrusConnectionError, mapping to errors["base"] = "timeout"
- [X] T006 [US1] Add step description or description_placeholders for "Validating credentials…" in async_step_user in custom_components/librus/config_flow.py (FR-008)

**Checkpoint**: User Story 1 complete—initial setup uses full five-step validation and shows correct errors

---

## Phase 4: User Story 2 - Reconfigure Integration with Full Auth Validation (Priority: P2)

**Goal**: User reconfigures existing integration; same five-step validation; config updated only when all steps succeed

**Independent Test**: Reconfigure integration via HA UI with valid credentials → config updated. With invalid credentials → error shown, config unchanged

### Implementation for User Story 2

- [X] T007 [US2] Add "Validating credentials…" description to async_step_reconfigure in custom_components/librus/config_flow.py (FR-008; reconfigure uses same validation so error mapping from T005 already applies)

**Checkpoint**: User Stories 1 and 2 both complete—setup and reconfigure share full auth validation

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and quality checks

- [X] T008 Verify no username or password logging in custom_components/librus/librus_client.py or custom_components/librus/config_flow.py
- [X] T009 Run quickstart verification per specs/003-auth-flow-postman/quickstart.md (add integration with valid/invalid credentials, verify error messages)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies—can start immediately
- **Foundational (Phase 2)**: Depends on Setup—BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational; config_flow updates from US1 (T005) apply to both steps, so T007 is additive
- **Polish (Phase 5)**: Depends on US1 and US2 complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2
- **US2 (P2)**: Starts after Phase 2; reuses error mapping from US1 (T005)

### Parallel Opportunities

- T002 and T003 can run in parallel (different files: librus_client vs strings.json)
- T002 must complete before T004 (T004 uses LibrusTimeoutError)

### Within Each Phase

- T004 depends on T002 (LibrusTimeoutError must exist)
- T005 and T006 can run in parallel after Phase 2 (both touch config_flow but different concerns—imports+except vs description)

---

## Parallel Example: Phase 2

```bash
# T002 and T003 can run in parallel:
Task T002: "Add LibrusTimeoutError to librus_client.py"
Task T003: "Add timeout key to strings.json"

# Then T004 (depends on T002)
Task T004: "Rewrite validate_credentials in librus_client.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (T002, T003, T004)
3. Complete Phase 3: User Story 1 (T005, T006)
4. **STOP and VALIDATE**: Add integration in HA with valid/invalid credentials
5. Verify timeout error shows when simulated

### Incremental Delivery

1. Setup + Foundational → librus_client ready
2. Add US1 (T005, T006) → Test initial setup → MVP
3. Add US2 (T007) → Test reconfigure
4. Polish (T008, T009) → Done

### Task Summary

| Phase   | Tasks | Count |
|---------|-------|-------|
| Setup   | T001 | 1 |
| Foundational | T002–T004 | 3 |
| US1     | T005–T006 | 2 |
| US2     | T007 | 1 |
| Polish  | T008–T009 | 2 |
| **Total** | | **9** |
