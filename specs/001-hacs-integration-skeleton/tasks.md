# Tasks: HACS Integration Skeleton

**Input**: Design documents from `/specs/001-hacs-integration-skeleton/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are not included. Tests can be added later if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Files in `custom_components/[domain]/` and `tests/` at repository root
- Paths follow Home Assistant custom integration structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create repository structure with custom_components/[domain]/ and tests/ directories
- [x] T002 [P] Create README.md in repository root with installation and configuration instructions
- [x] T003 [P] Create .gitignore file in repository root for Python and Home Assistant patterns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create custom_components/[domain]/const.py with DOMAIN constant
- [x] T005 Create custom_components/[domain]/manifest.json with required metadata (domain, name, version, config_flow, single_config_entry, documentation, issue_tracker, codeowners)
- [x] T006 Create hacs.json in repository root with HACS metadata (name, hacs version, domains, iot_class, homeassistant version)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Install Integration via HACS (Priority: P1) 🎯 MVP

**Goal**: Enable installation of the integration through HACS (Home Assistant Community Store) so users can discover and install it.

**Independent Test**: Can be fully tested by searching for the integration in HACS, installing it, and verifying it appears in the Home Assistant integrations list. This delivers the ability to distribute and install the integration.

### Implementation for User Story 1

- [x] T007 [US1] Create custom_components/[domain]/__init__.py with async_setup_entry and async_unload_entry functions
- [x] T008 [US1] Verify manifest.json includes all required fields for HACS discovery (domain, name, version, documentation, issue_tracker, codeowners)
- [x] T009 [US1] Verify hacs.json is properly formatted and includes correct domain reference
- [x] T010 [US1] Verify integration directory structure matches Home Assistant requirements (custom_components/[domain]/ with __init__.py and manifest.json)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Integration should be installable via HACS and appear in Home Assistant's available integrations list.

---

## Phase 4: User Story 2 - Configure Integration (Priority: P2)

**Goal**: Enable users to configure the integration through Home Assistant's standard configuration flow, establishing the configuration framework for future features.

**Independent Test**: Can be fully tested by adding the integration through Home Assistant's integration configuration flow and verifying it completes successfully. This delivers a configured integration ready for future functionality.

### Implementation for User Story 2

- [x] T011 [US2] Create custom_components/[domain]/config_flow.py with ConfigFlow class extending config_entries.ConfigFlow
- [x] T012 [US2] Implement async_step_user method in config_flow.py with single confirmation step (empty schema)
- [x] T013 [US2] Implement async_create_entry in config_flow.py to create configuration entry with empty data dictionary
- [x] T014 [US2] Verify manifest.json includes config_flow: true and single_config_entry: true
- [x] T015 [US2] Verify async_setup_entry in __init__.py handles configuration entry setup (returns True for skeleton)
- [x] T016 [US2] Verify async_unload_entry in __init__.py handles configuration entry cleanup (returns True for skeleton)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Integration should be installable via HACS, configurable through config flow, and appear in configured integrations list. Single instance enforcement should prevent duplicate configuration.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T017 [P] Update README.md with complete installation and configuration instructions based on quickstart.md
- [x] T018 [P] Verify all files follow Python type hints and Home Assistant coding standards
- [x] T019 [P] Verify manifest.json version follows SemVer or CalVer format
- [x] T020 [P] Verify integration can be uninstalled and reinstalled without errors
- [x] T021 [P] Verify single instance enforcement works (attempt to configure second instance should be prevented)
- [x] T022 Run quickstart.md validation steps to ensure integration works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for integration structure, but config flow can be developed independently

### Within Each User Story

- Core files before verification tasks
- Manifest configuration before implementation
- Implementation before integration testing
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks can run in parallel (T004, T005, T006) - different files
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- Polish phase tasks marked [P] can run in parallel (T017, T018, T019, T020, T021)

---

## Parallel Example: User Story 1

```bash
# All foundational tasks can run in parallel:
Task: "Create custom_components/[domain]/const.py with DOMAIN constant"
Task: "Create custom_components/[domain]/manifest.json with required metadata"
Task: "Create hacs.json in repository root with HACS metadata"
```

---

## Parallel Example: User Story 2

```bash
# Config flow implementation tasks can be done sequentially:
Task: "Create custom_components/[domain]/config_flow.py with ConfigFlow class"
Task: "Implement async_step_user method in config_flow.py"
Task: "Implement async_create_entry in config_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Verify integration installs via HACS
   - Verify integration appears in Home Assistant integrations list
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Integration installable via HACS
   - Integration appears in available integrations list
3. Add User Story 2 → Test independently → Deploy/Demo
   - Integration configurable through config flow
   - Integration appears in configured integrations list
   - Single instance enforcement works
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (integration structure and HACS setup)
   - Developer B: User Story 2 (config flow implementation)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Replace [domain] placeholder with actual integration domain name during implementation
- Replace [Display Name] placeholder with actual integration display name during implementation
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
