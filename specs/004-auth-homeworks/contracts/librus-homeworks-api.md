# Contract: Librus Homework API

**Branch**: `004-auth-homeworks` | **Base URL**: `https://synergia.librus.pl/gateway/api/2.0`

**Reference**: `docs/postman/librus_api.json`, `docs/postman/responses/`

## Prerequisites

- Valid OAuth session (five-step auth flow from Postman Auth folder)
- Session cookies set on `synergia.librus.pl`

## Endpoints Used for Homework Feature

### GET /HomeWorks

**Purpose**: Fetch all homework for the logged-in student.

**Request**:
- Method: GET
- Headers: User-Agent (browser-like)
- Query params: None (API does not support date filtering)

**Response**: `200 OK` with JSON body:

```json
{
  "HomeWorks": [
    {
      "Id": 6671271,
      "Content": "Homework description text...",
      "Date": "2025-09-11",
      "Category": { "Id": 8556, "Url": "..." },
      "LessonNo": "1",
      "TimeFrom": "07:45:00",
      "TimeTo": "08:30:00",
      "CreatedBy": { "Id": 1493507, "Url": "..." },
      "Subject": { "Id": 25678, "Url": "..." },
      "Class": { "Id": 69300, "Url": "..." },
      "AddDate": "2025-09-03 11:12:16"
    }
  ]
}
```

**Notes**:
- `Subject` may be absent (e.g. school-wide events)
- `Content` contains the full homework description
- Client must filter by date (past 7, next 14 days) per FR-005a

---

### GET /HomeWorks/Categories

**Purpose**: Fetch all homework categories for ID→Name resolution.

**Request**: GET, no params.

**Response**: `200 OK` with JSON:

```json
{
  "Categories": [
    { "Id": 8363, "Name": "kartkówka", "Color": { "Id": 21, "Url": "..." } }
  ]
}
```

---

### GET /Subjects

**Purpose**: Fetch all subjects for ID→Name resolution.

**Request**: GET, no params.

**Response**: `200 OK` with JSON:

```json
{
  "Subjects": [
    { "Id": 25678, "Name": "Historia", "Short": "hi", "No": 7, ... }
  ]
}
```

---

### GET /Users

**Purpose**: Fetch all users (teachers) for CreatedBy ID→Name resolution.

**Request**: GET, no params.

**Response**: `200 OK` with JSON:

```json
{
  "Users": [
    { "Id": 1493507, "FirstName": "Krzysztof", "LastName": "Krupa", ... }
  ]
}
```

**Notes**:
- `FirstName` may be null; use `LastName` only or "Unknown"

---

## Refresh Sequence (minimize API calls)

1. `GET /HomeWorks` — primary data
2. `GET /HomeWorks/Categories` — category names
3. `GET /Subjects` — subject names
4. `GET /Users` — creator names

Total: 4 requests per refresh. Order can be parallelized where the HTTP client supports it.
