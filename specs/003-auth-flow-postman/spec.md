# Feature Specification: Full Auth Flow During Integration Configuration

**Feature Branch**: `003-auth-flow-postman`  
**Created**: 2025-02-17  
**Status**: Draft  
**Input**: User description: "Update auth flow during integration configuration, the auth flow should use all auth steps from postman collection (init, login, grant, get token info and activate api access), only if all these requests will succeed we should consider the credentials as valid"

## Clarifications

### Session 2025-02-17

- Q: What loading/progress feedback should users see during the 5-step validation? → A: Generic "Validating credentials…" (or similar) message with loading indicator
- Q: Should validation retry on transient network failure before showing error? → A: No retries - first failure immediately surfaces an error
- Q: Per-step error messages or generic categories? → A: Generic categories only (invalid credentials, connection error, timeout)
- Q: What is explicitly out of scope? → A: Token refresh / session renewal and multi-account support are out of scope
- Q: Discard session state on validation failure? → A: Yes — explicitly discard session state on failure; do not reuse on retry

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initial Integration Setup with Full Auth Validation (Priority: P1)

A user adds the Librus integration for the first time and enters their Librus credentials (username and password). The system validates credentials by executing a complete five-step authentication sequence. The integration is created only when all steps succeed.

**Why this priority**: This is the primary entry point for new users. Without full auth validation, users may save credentials that appear valid but later fail when the integration tries to fetch data.

**Independent Test**: Can be fully tested by adding the integration via Home Assistant UI with valid credentials and verifying the integration is created and functional. With invalid credentials, the form shows an error and no integration is created.

**Acceptance Scenarios**:

1. **Given** a user on the integration setup form with valid Librus credentials, **When** the user submits the form, **Then** all five auth steps complete successfully and the integration is created
2. **Given** a user on the integration setup form with invalid credentials, **When** the user submits the form, **Then** the system rejects the credentials and displays an authentication error
3. **Given** a user on the integration setup form with valid credentials, **When** any single auth step fails (e.g., network issue, API change), **Then** the system rejects the credentials and displays an appropriate error

---

### User Story 2 - Reconfigure Integration with Full Auth Validation (Priority: P2)

A user reconfigures an existing Librus integration (e.g., to update password). The system validates the new credentials using the same complete five-step sequence. The configuration is updated only when all steps succeed.

**Why this priority**: Reconfigure follows the same validation logic as initial setup. Users expect consistent behavior.

**Independent Test**: Can be fully tested by reconfiguring an existing integration entry and submitting new credentials. Valid credentials update the config; invalid credentials show an error.

**Acceptance Scenarios**:

1. **Given** a user reconfiguring the integration with valid credentials, **When** the user submits the form, **Then** all five auth steps complete successfully and the integration configuration is updated
2. **Given** a user reconfiguring with invalid credentials, **When** the user submits the form, **Then** the system rejects the credentials and displays an error without updating the configuration

---

### Edge Cases

- What happens when the OAuth init step succeeds but the login step fails (wrong password)? → Credentials rejected, user sees authentication error
- What happens when login succeeds but the grant step fails (e.g., service temporarily unavailable)? → Credentials rejected, user sees connection error
- What happens when the grant step succeeds but TokenInfo returns an error or missing data? → Credentials rejected
- What happens when TokenInfo succeeds but Activate API Access fails? → Credentials rejected
- How does the system handle network timeouts or connection errors during any step? → Appropriate error message (connection or timeout), no partial credential storage
- How does the system handle rate limiting or temporary blocking from the external service? → User sees an error indicating the service is temporarily unavailable

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The integration configuration flow MUST validate credentials using a five-step authentication sequence: (1) OAuth init, (2) OAuth login, (3) OAuth grant, (4) Get token info, (5) Activate API access
- **FR-002**: Credentials MUST be considered valid ONLY when all five steps complete successfully in sequence
- **FR-003**: If any step fails, the system MUST reject the credentials and display an appropriate error to the user
- **FR-004**: The same validation flow MUST apply to both initial integration setup and integration reconfiguration
- **FR-005**: The system MUST NOT store or persist credentials when validation fails
- **FR-006**: The system MUST surface clear, user-friendly error messages using generic categories only (e.g., invalid credentials, connection error, timeout)—no per-step error details
- **FR-007**: The auth flow sequence MUST match the reference specification (Postman collection `docs/postman/librus_api.json` Auth folder)
- **FR-008**: During credential validation, the system MUST display a generic loading message (e.g., "Validating credentials…") with a loading indicator while the five-step flow runs
- **FR-009**: The system MUST NOT retry failed steps; the first failure MUST immediately surface an error to the user
- **FR-010**: On validation failure, the system MUST discard any temporary session or cookie state from prior steps and MUST NOT reuse it on subsequent validation attempts

### Key Entities

- **Credentials**: Username and password provided by the user. Valid only when all five auth steps succeed.
- **Auth session**: Temporary state established during the five-step flow. Not persisted beyond validation.
- **Integration configuration**: Stored only after successful credential validation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with valid Librus credentials can complete integration setup in under 30 seconds
- **SC-002**: Users with invalid credentials receive clear feedback within 15 seconds of submitting the form
- **SC-003**: Zero false positives: credentials that fail any step are never stored or marked as valid
- **SC-004**: Users attempting to configure the integration experience no partial states (e.g., no "configured" integration that later fails when fetching data due to incomplete auth)
- **SC-005**: Connection and timeout errors are distinguishable from invalid-credential errors in user-facing messages

## Out of Scope

- Token refresh / session renewal (runtime session management)
- Multi-account support (multiple Librus accounts in one integration)

## Assumptions

- The five-step sequence is derived from the Postman collection and reflects the current Librus API behavior
- Steps must run in the specified order (init → login → grant → token info → activate) due to dependencies (e.g., session cookies, token identifiers)
- The external Librus service may change its API; this spec defines the expected sequence, not the exact implementation
- Home Assistant integration config flow provides mechanisms for showing errors and aborting on validation failure
