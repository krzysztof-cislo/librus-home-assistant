# Data Model: Auth Flow and Homework Integration

**Branch**: `004-auth-homeworks` | **Date**: 2025-02-17

## Entities

### HomeworkEntry (exposed in Home Assistant)

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| `id` | string/number | yes | HomeWorks[].Id | Unique identifier |
| `date` | string (YYYY-MM-DD) | yes | HomeWorks[].Date | Due date |
| `subject` | string | yes* | Resolved from Subjects | Subject.Name; "Unknown" when Subject absent |
| `creator` | string | yes* | Resolved from Users | "FirstName LastName"; fallback to LastName or "Unknown" when missing |
| `category` | string | yes* | Resolved from HomeWorks/Categories | Category.Name; "Unknown" when unresolved |
| `lesson_no` | string | no | HomeWorks[].LessonNo | Lesson number; omit when not available |
| `time_from` | string | no | HomeWorks[].TimeFrom | e.g. "07:45:00" |
| `time_to` | string | no | HomeWorks[].TimeTo | e.g. "08:30:00" |
| `content` | string | no | HomeWorks[].Content | Homework description/body |
| `add_date` | string | no | HomeWorks[].AddDate | When homework was added |

*Required for display; use "Unknown" when API data is missing (FR-009, edge cases).

### HomeworkSensor (Home Assistant entity)

- **Type**: Single sensor (or similar) exposing a structured list
- **Value**: List of HomeworkEntry objects (e.g., JSON array)
- **Attributes**: Optional metadata (last_updated, count, etc.)

### Lookup Entities (in-memory, not exposed)

| Entity | Source | Key | Resolved Field |
|--------|--------|-----|----------------|
| Category | GET /HomeWorks/Categories | Categories[].Id | Name |
| Subject | GET /Subjects | Subjects[].Id | Name |
| User | GET /Users | Users[].Id | FirstName + LastName |

### Validation Rules (from spec)

- Date scope: Include only entries where `Date` is within [today - 7 days, today + 14 days]
- Missing Subject: Use "Unknown" (some homeworks have no Subject, e.g. school events)
- Missing creator name: Use "Unknown" when User not found or FirstName/LastName both null

## API Response Shapes (reference)

### GET /HomeWorks

```json
{
  "HomeWorks": [
    {
      "Id": 6671271,
      "Content": "...",
      "Date": "2025-09-11",
      "Category": { "Id": 8556, "Url": "..." },
      "LessonNo": "1",
      "TimeFrom": "07:45:00",
      "TimeTo": "08:30:00",
      "CreatedBy": { "Id": 1493507, "Url": "..." },
      "Subject": { "Id": 25678, "Url": "..." },
      "AddDate": "2025-09-03 11:12:16"
    }
  ]
}
```

### GET /HomeWorks/Categories

```json
{
  "Categories": [
    { "Id": 8363, "Name": "kartkówka", "Color": { "Id": 21, "Url": "..." } }
  ]
}
```

### GET /Subjects

```json
{
  "Subjects": [
    { "Id": 25678, "Name": "Historia", "Short": "hi", ... }
  ]
}
```

### GET /Users

```json
{
  "Users": [
    { "Id": 1493507, "FirstName": "Krzysztof", "LastName": "Krupa", ... }
  ]
}
```

## State Transitions

- **Homework refresh**: Idle → Fetching → Updating → Idle (or Error)
- **On error**: Preserve previous sensor state; mark entity unavailable or set error attribute
- **Empty result**: Sensor value = empty list; distinguishable from "refresh failed" per SC-006
