# Quickstart: Auth Flow and Homework Integration

**Branch**: `004-auth-homeworks`

## Prerequisites

- Home Assistant with Librus integration
- Valid Librus credentials (username, password)
- Python 3.x, `requests` library (for librus_client)

## Verify Auth Flow

1. Add Librus integration in Home Assistant (Settings → Devices & Services → Add Integration).
2. Enter Librus username and password.
3. Validation runs the five-step OAuth flow; integration is created only when all steps succeed.
4. Invalid credentials show "invalid_auth" error.

## Verify Homework Feature (after implementation)

1. Ensure integration is configured and running.
2. Wait for initial refresh or trigger on-demand refresh via service `librus.refresh_homework`.
3. Check `sensor.librus_homework` (or equivalent) entity.
4. Entity attributes should contain a list of homework entries with date, subject, creator, category.
5. Entries are scoped to past 7 days and next 14 days.

### Performance validation (SC-001, SC-005)

- **Setup time**: Integration setup with valid credentials should complete in under 30 seconds.
- **On-demand refresh**: Calling `librus.refresh_homework` should update entities within 60 seconds under normal network conditions.

## API Testing (Postman)

1. Import `docs/postman/librus_api.json`.
2. Set Variables: `login`, `password`.
3. Run Auth folder: Step 1 → Step 2 → Step 3 → Step 4a → Step 4b.
4. Run `Get HomeWorks`, `Get HomeWork Categories`, `Get Subjects`, `Get Users`.
5. Sample responses in `docs/postman/responses/`.

## Key Files

| File | Purpose |
|------|---------|
| `custom_components/librus/librus_client.py` | Auth validation (already implemented) |
| `custom_components/librus/config_flow.py` | Integration setup, credential validation |
| `docs/postman/librus_api.json` | API reference |
| `docs/postman/responses/` | Sample API responses |
