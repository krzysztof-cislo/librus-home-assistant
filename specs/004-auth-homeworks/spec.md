# Feature Specification: Auth Flow and Homework Integration

**Feature Branch**: `004-auth-homeworks`  
**Created**: 2025-02-17  
**Status**: Draft  
**Input**: User description: "Update auth flow during integration configuration using all auth steps from Postman collection (init, login, grant, get token info, activate API access); add getting homeworks and exposing in Home Assistant with details (date, lesson number with time, subject/lesson name, who created homework, category); refresh every hour or on demand"

## Clarifications

### Session 2025-02-17

- Q: Does the integration support multiple students, or is a single-student view sufficient for initial release? → A: Single-student view for initial release; multi-student can be added later
- Q: How should homework be exposed in Home Assistant? → A: Single sensor/entity with a structured list of all homework entries
- Q: Should the system fetch all homework or only future/upcoming? → A: Upcoming and recent only (e.g., past 7 days + next 14 days)
- Q: How to handle lesson number when the API may only provide TimeFrom/TimeTo? → A: Show time range when lesson number is missing; omit lesson number when not available
- Q: How to select the primary student when multiple children are linked to the account? → A: API returns data for a single student only; no selection needed

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Integration Setup with Full Auth Validation (Priority: P1)

A user adds or reconfigures the Librus integration and enters credentials. The system validates credentials by executing a complete five-step authentication sequence derived from the Postman collection. Credentials are considered valid only when all steps succeed.

**Why this priority**: Without full auth validation, users may save credentials that later fail when the integration fetches data. This ensures reliability from the start.

**Independent Test**: Add or reconfigure the integration with valid credentials; integration is created or updated only when all five steps succeed. Invalid credentials trigger an error with no storage.

**Acceptance Scenarios**:

1. **Given** a user on the integration setup form with valid Librus credentials, **When** the user submits the form, **Then** all five auth steps (init, login, grant, get token info, activate API access) complete successfully and the integration is created
2. **Given** a user with invalid credentials, **When** the user submits the form, **Then** the system rejects the credentials and displays an authentication error
3. **Given** any single auth step fails (e.g., network issue, API change), **When** validation runs, **Then** the system rejects the credentials and displays an appropriate error—credentials are never stored

---

### User Story 2 - View Homework in Home Assistant (Priority: P2)

A user (typically a parent or student) wants to see Librus homework directly in Home Assistant. Homework entries are retrieved with full details and displayed through Home Assistant entities or dashboards.

**Why this priority**: This is the core value of the homework feature—surfacing school assignments in a familiar smart home environment.

**Independent Test**: Configure integration, wait for initial or manual refresh; homework entries appear with date, lesson/time, subject, creator, and category.

**Acceptance Scenarios**:

1. **Given** the Librus integration is configured, **When** homework data is refreshed (scheduled or on demand), **Then** homework entries are retrieved and exposed in Home Assistant with: date, subject (lesson name), who created the homework, and category; lesson number and time range are included when available from the API
2. **Given** a user wants up-to-date homework, **When** the user triggers an on-demand refresh, **Then** homework data is refreshed and exposed entities are updated
3. **Given** no homework exists for the student, **When** data is refreshed, **Then** the system reflects an empty or minimal state without errors

---

### User Story 3 - Automatic and On-Demand Refresh (Priority: P3)

Homework data is kept reasonably current through periodic refresh and can also be refreshed manually when the user needs immediate updates.

**Why this priority**: Automatic refresh reduces manual effort; on-demand refresh gives control when needed (e.g., before a study session).

**Independent Test**: Verify that homework refreshes automatically on schedule (e.g., every hour) and that a manual refresh action updates data within a short time.

**Acceptance Scenarios**:

1. **Given** the integration is active, **When** the configured interval elapses (e.g., one hour), **Then** homework data is refreshed automatically
2. **Given** the user wants current data, **When** the user triggers an on-demand refresh, **Then** homework data is fetched and exposed entities are updated within a reasonable time

---

### Edge Cases

- What happens when the external homework API is temporarily unavailable during a scheduled refresh? → Refresh fails gracefully; previously exposed data remains; next scheduled or manual refresh retries
- What happens when auth fails during a scheduled homework refresh? → Refresh fails; user receives appropriate feedback (e.g., via entity unavailable state or integration status)
- What happens when homework has missing optional fields (e.g., category not set)? → System exposes available data; missing fields are represented as empty or "unknown" rather than causing errors
- What happens when lesson time or lesson number is not available? → System exposes date and time range (TimeFrom/TimeTo) when available; lesson number is shown only when derivable, otherwise omitted
- What happens when multiple students (children) are linked to the account? → The Librus API returns data for a single student only; no student selection is required

## Requirements *(mandatory)*

### Functional Requirements

**Auth Flow**

- **FR-001**: The integration configuration flow MUST validate credentials using the five-step auth sequence from the Postman collection: (1) OAuth init, (2) OAuth login, (3) OAuth grant, (4) Get token info, (5) Activate API access
- **FR-002**: Credentials MUST be considered valid ONLY when all five steps complete successfully in sequence
- **FR-003**: If any step fails, the system MUST reject the credentials and MUST NOT store them
- **FR-004**: The auth sequence MUST match the reference in `docs/postman/librus_api.json` (Auth folder)

**Homework Retrieval and Exposure**

- **FR-005**: The system MUST retrieve homework from the Librus API and expose it in Home Assistant as a single sensor or entity containing a structured list of homework entries
- **FR-005a**: Homework retrieval MUST be scoped to upcoming and recent assignments (e.g., past 7 days and next 14 days from today); historical homework outside this window may be excluded
- **FR-006**: Each homework entry MUST include: date, subject (lesson name), who created the homework, and category. Lesson number and time range (TimeFrom/TimeTo) MUST be included when available; when lesson number is not available, the time range MUST be shown and lesson number MAY be omitted. The homework description (content) MUST be included when available from the API
- **FR-007**: The system MUST refresh homework data at least every hour when the integration is active
- **FR-008**: The system MUST support on-demand refresh of homework data (e.g., via service call or entity button)
- **FR-009**: The system MUST handle API errors and missing data gracefully without crashing or leaving entities in an inconsistent state
- **FR-010**: Subject names and creator names MUST be resolved from related API data (Subjects, Users) so users see human-readable labels, not raw identifiers

### Key Entities

- **Credentials**: Username and password. Valid only when all five auth steps succeed.
- **Homework Entry**: A single homework assignment with date, subject (lesson name), creator, category, and optionally lesson number and/or time range (TimeFrom/TimeTo). Lesson number and time are included when available from the API.
- **Homework Sensor**: A single Home Assistant entity exposing a structured list of all homework entries (not one entity per entry).
- **Refresh**: Scheduled (e.g., hourly) or on-demand fetch of homework data from the external API. Data scope: past 7 days and next 14 days from today.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with valid credentials complete integration setup in under 30 seconds; invalid credentials receive feedback within 15 seconds
- **SC-002**: Zero false positives: credentials that fail any auth step are never stored
- **SC-003**: Homework entries display with required details (date, subject, creator, category) and optional details (lesson number, time range) when the API provides them
- **SC-004**: Homework data refreshes automatically at least every hour when the integration is active
- **SC-005**: On-demand refresh completes and updates entities within 60 seconds under normal network conditions
- **SC-006**: Users can distinguish between "no homework" and "refresh failed" states

## Out of Scope

- Multi-student support (multiple children per account); the API provides single-student data only

## Assumptions

- The Postman collection (`docs/postman/librus_api.json`) accurately reflects the Librus API auth flow
- The HomeWorks and related endpoints (Subjects, Users, HomeWorks/Categories) are available to the integration after successful auth
- The Librus API returns homework for a single student per account; no student selection logic is required
- The default refresh interval of one hour balances freshness with API load; this can be made configurable in a future iteration
- Home Assistant provides suitable primitives for exposing entities and triggering on-demand refresh (e.g., service calls, sensor/entity attributes)
