# Contract: Homework Sensor Entity

**Branch**: `004-auth-homeworks` | **Domain**: Home Assistant integration

## Entity Type

Home Assistant sensor (or equivalent) exposing a single structured list of homework entries.

## Entity Identification

- **Platform**: `librus` (or `sensor` with `librus` integration)
- **Unique ID**: `homework` or `librus_homework` (integration-scoped)

## State

- **Value**: Count of homework entries, or a serialized list (e.g. JSON string) depending on Home Assistant patterns
- **Attributes**: Structured list of homework entries per data-model.md

## Attribute: homework_entries

List of objects conforming to `HomeworkEntry`:

| Attribute | Type | Example |
|-----------|------|---------|
| `id` | number | 6671271 |
| `date` | string | "2025-09-11" |
| `subject` | string | "Historia" |
| `creator` | string | "Krzysztof Krupa" |
| `category` | string | "kartkówka" |
| `lesson_no` | string | "1" (optional) |
| `time_from` | string | "07:45:00" (optional) |
| `time_to` | string | "08:30:00" (optional) |
| `content` | string | "Homework description..." (optional) |
| `add_date` | string | "2025-09-03 11:12:16" (optional) |

## Availability

- **Unavailable** when: integration not loaded, auth failed, last refresh failed
- **Unknown** when: never refreshed yet
- **Available** when: at least one successful refresh completed

## On-Demand Refresh

Expose a mechanism (service call or entity button) to trigger refresh. Per FR-008.
