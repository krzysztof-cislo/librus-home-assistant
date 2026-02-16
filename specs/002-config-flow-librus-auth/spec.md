# Feature Specification: Config Flow with Librus Credentials

**Feature Branch**: `002-config-flow-librus-auth`  
**Created**: 2026-02-16  
**Status**: Draft  
**Input**: User description: "improve integration by adding config flow, the config requires login and password for librus to be used later in the login to Librus. These values are secrets and should be stored in home assistant in the secure way if possible."

## Clarifications

### Session 2026-02-16

- Q: Should the config flow validate credentials against Librus when the user submits, or only collect and store (defer validation to first use)? → A: Validate against Librus during config flow submit; verify credentials before saving and show error if login fails
- Q: When login or password is empty, how should the config flow respond? → A: Show inline error under each empty field and block submit until both are filled
- Q: If secure credential storage fails when saving, what should happen? → A: Show error message and keep user on form so they can correct and retry
- Q: What format is the Librus login (email vs username)? → A: No validation for email or password; use them as provided
- Q: Should the reconfigure/update credentials flow also validate against Librus before saving? → A: Yes - validate against Librus before saving updated credentials; show error and allow retry if validation fails

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Integration with Librus Credentials (Priority: P1)

A Home Assistant user wants to add the integration and provide their Librus account credentials (login and password) so the integration can authenticate with Librus on their behalf in future operations.

**Why this priority**: Without credentials collection, the integration cannot authenticate with Librus. This is the core value proposition of the feature—enabling authenticated access to Librus services from Home Assistant.

**Independent Test**: Can be fully tested by completing the configuration flow with valid login and password fields, submitting the form, and verifying the integration is configured. This delivers a configured integration ready for Librus authentication.

**Acceptance Scenarios**:

1. **Given** the integration is installed, **When** a user adds the integration via the config flow, **Then** the user is prompted to enter login and password
2. **Given** the config flow is displayed, **When** a user enters valid login and password and submits, **Then** credentials are validated against Librus, and on success the integration configures and appears in the configured integrations list
3. **Given** the config flow is displayed with invalid credentials entered, **When** the user submits, **Then** an error is shown and the user can correct or retry; credentials are not saved
4. **Given** the integration is configured, **When** the integration needs to authenticate with Librus, **Then** it uses the stored credentials for login

---

### User Story 2 - Credentials Stored Securely (Priority: P2)

A Home Assistant user expects that their Librus login and password are stored securely within Home Assistant, not exposed in configuration files or logs.

**Why this priority**: Credentials are sensitive data. Users must trust that their credentials are protected according to Home Assistant’s best practices.

**Independent Test**: Can be fully tested by verifying that credentials are not visible in plain text in configuration files, logs, or integration configuration UI after setup.

**Acceptance Scenarios**:

1. **Given** credentials are entered during config flow, **When** configuration is saved, **Then** credentials are stored using the platform’s recommended secure storage mechanism
2. **Given** credentials are stored, **When** a user views integration configuration details, **Then** password is never displayed in plain text (masked or omitted)
3. **Given** credentials are stored, **When** configuration is exported or backed up, **Then** credentials are not included in plain text

---

### User Story 3 - Reconfigure or Update Credentials (Priority: P3)

A Home Assistant user who has already configured the integration wants to update their Librus credentials (e.g., after a password change).

**Why this priority**: Users need to maintain their configuration over time. Credential updates are a common maintenance task.

**Independent Test**: Can be fully tested by opening the integration’s configuration options and updating the credentials, then verifying the new credentials are used for subsequent authentications.

**Acceptance Scenarios**:

1. **Given** the integration is configured, **When** a user accesses integration options/reconfigure flow, **Then** they can update login and password
2. **Given** the reconfigure flow is displayed, **When** the user submits valid credentials, **Then** credentials are validated against Librus and on success replace the old ones and are stored securely
3. **Given** the reconfigure flow is displayed with invalid credentials, **When** the user submits, **Then** an error is shown and the user can correct or retry; credentials are not updated until validation succeeds
4. **Given** credentials are updated, **When** the integration authenticates with Librus, **Then** it uses the most recent credentials

---

### Edge Cases

- What happens when the user submits empty login or password fields? (Show inline error under empty field(s), block submit until both filled)
- How does the system handle invalid or incorrect credentials during configuration? (MUST show error and allow user to correct or retry; credentials are not saved until validation succeeds)
- What happens when the user cancels the config flow midway?
- How does the system handle credential storage failure? (Show error message, keep user on form to correct and retry)
- What happens when a user attempts to configure a second instance when one is already configured? (align with single-instance constraint from skeleton spec)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The configuration flow MUST prompt the user to enter a login and password for Librus; no format validation is applied—values are used as provided and validated only against Librus during authentication
- **FR-002**: The configuration flow MUST validate that both login and password are provided before allowing the configuration to complete; when either is empty, show an inline error under the empty field(s) and block submit until both are filled
- **FR-003**: The configuration flow MUST validate credentials against Librus before saving; if authentication fails, the flow MUST display an error and allow the user to correct or retry
- **FR-004**: Credentials (login and password) MUST be stored using the platform’s secure storage mechanism
- **FR-005**: The password MUST NOT be displayed in plain text in the integration configuration UI after setup
- **FR-006**: Credentials MUST be available to the integration for use when authenticating with Librus
- **FR-007**: Users MUST be able to reconfigure or update credentials after initial setup; the reconfigure flow MUST validate credentials against Librus before saving—if validation fails, display an error and allow the user to correct or retry
- **FR-008**: The integration MUST support only a single configured instance (one configuration entry per Home Assistant instance)

### Key Entities

- **Credentials**: Represents the Librus authentication data—login and password, used as provided (no format validation). Stored securely, used by the integration for Librus authentication.
- **Configuration Entry**: Represents the configured instance of the integration, including reference to stored credentials and integration metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the config flow with login and password in under 2 minutes
- **SC-002**: Credentials are never exposed in plain text in configuration files, logs, or UI after setup
- **SC-003**: 100% of successful configurations result in credentials stored in secure storage
- **SC-004**: Users can update their credentials through the integration options without reinstalling
- **SC-005**: Integration configuration completes without errors when valid credentials are provided

## Assumptions

- Home Assistant provides a standard secure storage mechanism for sensitive integration data
- Librus authentication uses username and password (no OAuth or token-based flow for this scope)
- Single instance constraint from the existing HACS integration skeleton remains (one configuration entry per Home Assistant instance)
- Users have valid Librus accounts and know their credentials
- Credentials are validated against Librus during config flow submit; configuration completes only after successful authentication

## Out of Scope

- Actual Librus API calls or data fetching (credentials are for future use)
- Multi-factor authentication handling
- OAuth or token-based Librus authentication
- Credential rotation or automatic refresh mechanisms
