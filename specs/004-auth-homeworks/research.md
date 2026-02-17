# Research: Auth Flow and Homework Integration

**Branch**: `004-auth-homeworks` | **Date**: 2025-02-17

## API Strategy

### Decision: Bulk Fetch for Lookup Data

Use `/HomeWorks`, `/HomeWorks/Categories`, `/Subjects`, and `/Users` in a single refresh cycle. Fetch all lookup data (categories, subjects, users) once per refresh rather than per-homework-entry lookups.

**Rationale**:
- Minimizes API calls: 4 requests per refresh instead of 4 + N (where N = number of homework entries)
- Home Assistant integrations should avoid excessive external calls (rate limiting, latency)
- Lookup data (subjects, categories, teachers) changes rarely; bulk fetch is sufficient for hourly refresh

**Alternatives considered**:
- Per-ID lookups: Rejected — would multiply API calls by homework count
- Caching lookup data across refreshes: Deferred — can optimize later if needed; hourly refresh keeps data fresh enough

### Decision: Use Content Field for Homework Description

The homework description/body comes from the `Content` field in the `/HomeWorks` response. No separate endpoint is required.

**Rationale**:
- `docs/postman/responses/Homeworks.json` shows `Content` contains the full homework text (e.g., "W ramach diagnozy wiedzy z chronologii zrobimy krótką kartkówkę...")
- FR-006 requires date, subject, creator, category; Content provides the assignment details for display

**Alternatives considered**:
- Separate content endpoint: Not present in Librus JSON API; Content is inline

### Decision: Client-Side Date Filtering

The `/HomeWorks` endpoint returns all homework with no date range parameters. Filter client-side to past 7 days and next 14 days (per FR-005a).

**Rationale**:
- Postman collection and `docs/postman/librus_api.json` show `GET {{api_url}}/HomeWorks` with no query params
- Spec requires scoping to upcoming and recent; client filtering is the only option

### Decision: Resolve IDs from Bulk Endpoints

| Homework Field | Source Endpoint | Resolution |
|----------------|-----------------|------------|
| `Category.Id` | `GET /HomeWorks/Categories` | Match `Categories[].Id` → `Name` |
| `CreatedBy.Id` | `GET /Users` | Match `Users[].Id` → `FirstName` + `LastName` |
| `Subject.Id` | `GET /Subjects` | Match `Subjects[].Id` → `Name` |

**Rationale**:
- Homeworks response uses nested objects with `Id` and `Url`; Names come from bulk endpoints
- Users may have `FirstName: null`; fallback to `LastName` only or "Unknown" when both missing

### Reference: API Response Structures

From `docs/postman/responses/`:

**Homeworks.json**:
- `HomeWorks[]`: `Id`, `Content`, `Date`, `Category.Id`, `LessonNo`, `TimeFrom`, `TimeTo`, `CreatedBy.Id`, `Subject.Id` (optional), `AddDate`
- `Subject` can be absent (e.g., "Zajęcia profilaktyczne DEBATA" entry)

**Homeworks_Categories.json**:
- `Categories[]`: `Id`, `Name`, `Color`

**Subjects.json**:
- `Subjects[]`: `Id`, `Name`, `Short`, `No`, etc.

**Users.json**:
- `Users[]`: `Id`, `FirstName`, `LastName` (FirstName can be null)

## API Base URLs (from librus_api.json)

- **JSON API**: `https://synergia.librus.pl/gateway/api/2.0`
- **OAuth**: `https://api.librus.pl`

## Auth Flow (Already Implemented)

The existing `librus_client.validate_credentials` implements all five steps from the Postman Auth folder. No changes needed for config flow validation.
