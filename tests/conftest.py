"""Fixtures for Librus integration tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.librus.const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

# ---------------------------------------------------------------------------
# Sample API response data (based on docs/postman/responses/)
# ---------------------------------------------------------------------------

SAMPLE_HOMEWORKS_RESPONSE = {
    "HomeWorks": [
        {
            "Id": 6671271,
            "Content": "Kartkówka z chronologii",
            "Date": "2026-02-20",
            "Category": {"Id": 8556, "Url": "https://api.librus.pl/2.0/HomeWorks/Categories/8556"},
            "LessonNo": "1",
            "TimeFrom": "07:45:00",
            "TimeTo": "08:30:00",
            "CreatedBy": {"Id": 1493507, "Url": "https://api.librus.pl/2.0/Users/1493507"},
            "Class": {"Id": 69300, "Url": "https://api.librus.pl/2.0/Classes/69300"},
            "Subject": {"Id": 25678, "Url": "https://api.librus.pl/2.0/Subjects/25678"},
            "AddDate": "2026-02-15 11:12:16",
        },
        {
            "Id": 6674588,
            "Content": "Zajęcia profilaktyczne DEBATA",
            "Date": "2026-02-22",
            "Category": {"Id": 8556, "Url": "https://api.librus.pl/2.0/HomeWorks/Categories/8556"},
            "LessonNo": "4",
            "TimeFrom": "10:30:00",
            "TimeTo": "11:15:00",
            "CreatedBy": {"Id": 1589959, "Url": "https://api.librus.pl/2.0/Users/1589959"},
            "Class": {"Id": 69300, "Url": "https://api.librus.pl/2.0/Classes/69300"},
            "AddDate": "2026-02-17 17:45:30",
        },
        {
            "Id": 9999999,
            "Content": "Very old homework",
            "Date": "2020-01-01",
            "Category": {"Id": 8363, "Url": "https://api.librus.pl/2.0/HomeWorks/Categories/8363"},
            "LessonNo": "2",
            "TimeFrom": "08:35:00",
            "TimeTo": "09:20:00",
            "CreatedBy": {"Id": 1493507, "Url": "https://api.librus.pl/2.0/Users/1493507"},
            "Class": {"Id": 69300, "Url": "https://api.librus.pl/2.0/Classes/69300"},
            "Subject": {"Id": 25678, "Url": "https://api.librus.pl/2.0/Subjects/25678"},
            "AddDate": "2020-01-01 08:00:00",
        },
    ]
}

SAMPLE_CATEGORIES_RESPONSE = {
    "Categories": [
        {"Id": 8363, "Name": "kartkówka", "Color": {"Id": 21}},
        {"Id": 8556, "Name": "inne wydarzenia", "Color": {"Id": 25}},
        {"Id": 8364, "Name": "praca dodatkowa", "Color": {"Id": 29}},
    ]
}

SAMPLE_SUBJECTS_RESPONSE = {
    "Subjects": [
        {"Id": 25678, "Name": "Historia", "Short": "hi", "No": 7},
        {"Id": 25683, "Name": "Język polski", "Short": "jp", "No": 12},
    ]
}

SAMPLE_USERS_RESPONSE = {
    "Users": [
        {"Id": 1493507, "FirstName": "Krzysztof", "LastName": "Krupa"},
        {"Id": 1589959, "FirstName": None, "LastName": "Nowak"},
        {"Id": 1890192, "FirstName": "Anna", "LastName": "Kowalska"},
    ]
}


@pytest.fixture
def sample_homeworks():
    """Return sample HomeWorks API response."""
    return SAMPLE_HOMEWORKS_RESPONSE


@pytest.fixture
def sample_categories():
    """Return sample Categories API response."""
    return SAMPLE_CATEGORIES_RESPONSE


@pytest.fixture
def sample_subjects():
    """Return sample Subjects API response."""
    return SAMPLE_SUBJECTS_RESPONSE


@pytest.fixture
def sample_users():
    """Return sample Users API response."""
    return SAMPLE_USERS_RESPONSE


@pytest.fixture
async def mock_config_entry(hass: HomeAssistant):
    """Create a mock config entry."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        version=2,
        minor_version=1,
        domain=DOMAIN,
        title="Librus",
        data={CONF_USERNAME: "testuser", CONF_PASSWORD: "testpass"},
        entry_id="test_entry_id",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_homework_entries():
    """Return expected resolved homework entries (matching sample data, only in-window ones)."""
    return [
        {
            "id": 6671271,
            "date": "2026-02-20",
            "subject": "Historia",
            "creator": "Krzysztof Krupa",
            "category": "inne wydarzenia",
            "lesson_no": "1",
            "time_from": "07:45:00",
            "time_to": "08:30:00",
            "content": "Kartkówka z chronologii",
            "add_date": "2026-02-15 11:12:16",
        },
        {
            "id": 6674588,
            "date": "2026-02-22",
            "subject": "Unknown",
            "creator": "Nowak",
            "category": "inne wydarzenia",
            "lesson_no": "4",
            "time_from": "10:30:00",
            "time_to": "11:15:00",
            "content": "Zajęcia profilaktyczne DEBATA",
            "add_date": "2026-02-17 17:45:30",
        },
    ]
