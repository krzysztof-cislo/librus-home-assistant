"""Librus Synergia OAuth client for credential validation and homework fetching.

Uses the same Synergia OAuth flow as the reference JS implementation
(https://github.com/Mati365/librus-api). No external Librus library needed.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)

LIBRUS_OAUTH_URL = "https://api.librus.pl/OAuth/Authorization"
LIBRUS_OAUTH_GRANT_URL = "https://api.librus.pl/OAuth/Authorization/Grant"
LIBRUS_API_URL = "https://synergia.librus.pl/gateway/api/2.0"
OAUTH_CLIENT_ID = "46"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
}


class LibrusAuthError(Exception):
    """Raised when Librus credentials are invalid."""


class LibrusConnectionError(Exception):
    """Raised when unable to connect to Librus."""


class LibrusTimeoutError(LibrusConnectionError):
    """Raised when a request to Librus times out."""


def _create_authenticated_session(
    username: str, password: str
) -> requests.Session:
    """Create an authenticated Librus session via the five-step OAuth flow.

    Follows the Postman Auth folder sequence (librus_api.json):
    1. GET OAuth/Authorization — initiate OAuth session
    2. POST credentials to OAuth/Authorization — login
    3. GET OAuth/Authorization/Grant — set session cookies via redirects
    4. GET Auth/TokenInfo — extract UserIdentifier
    5. GET Auth/UserInfo/{UserIdentifier} — activate API access

    Returns an authenticated requests.Session on success.
    Raises LibrusAuthError on invalid credentials.
    Raises LibrusTimeoutError on request timeout.
    Raises LibrusConnectionError on other network/connection issues.
    Fresh session per call (FR-010).
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # Step 1: OAuth Init
    _LOGGER.debug("Librus auth step 1: initiating OAuth flow")
    response = session.get(
        LIBRUS_OAUTH_URL,
        params={
            "client_id": OAUTH_CLIENT_ID,
            "response_type": "code",
            "scope": "mydata",
        },
        timeout=REQUEST_TIMEOUT,
    )
    _LOGGER.debug(
        "Librus auth step 1: HTTP %s, URL: %s",
        response.status_code,
        response.url,
    )

    # Step 2: OAuth Login
    _LOGGER.debug("Librus auth step 2: submitting credentials")
    response = session.post(
        f"{LIBRUS_OAUTH_URL}?client_id={OAUTH_CLIENT_ID}",
        data={
            "action": "login",
            "login": username,
            "pass": password,
        },
        timeout=REQUEST_TIMEOUT,
    )
    _LOGGER.debug(
        "Librus auth step 2: HTTP %s, URL: %s",
        response.status_code,
        response.url,
    )

    body_text = response.text
    if "error" in body_text or "Nieprawidłowy" in body_text:
        _LOGGER.debug("Librus auth step 2: invalid credentials detected")
        raise LibrusAuthError("Invalid login or password")

    # Step 3: OAuth Grant (sets session cookies via redirects)
    _LOGGER.debug("Librus auth step 3: OAuth Grant")
    response = session.get(
        LIBRUS_OAUTH_GRANT_URL,
        params={"client_id": OAUTH_CLIENT_ID},
        timeout=REQUEST_TIMEOUT,
    )
    _LOGGER.debug(
        "Librus auth step 3: HTTP %s, URL: %s",
        response.status_code,
        response.url,
    )

    # Step 4: Get TokenInfo — extract UserIdentifier
    _LOGGER.debug("Librus auth step 4: getting TokenInfo")
    response = session.get(
        f"{LIBRUS_API_URL}/Auth/TokenInfo",
        timeout=REQUEST_TIMEOUT,
    )
    _LOGGER.debug(
        "Librus auth step 4: HTTP %s",
        response.status_code,
    )

    if not response.ok:
        _LOGGER.debug(
            "Librus auth step 4: TokenInfo failed with HTTP %s",
            response.status_code,
        )
        raise LibrusAuthError("Failed to obtain token info")

    try:
        token_data = response.json()
        user_identifier = token_data["UserIdentifier"]
    except (ValueError, KeyError) as err:
        _LOGGER.debug("Librus auth step 4: failed to parse UserIdentifier")
        raise LibrusAuthError("Failed to parse UserIdentifier") from err

    # Step 5: Activate API Access via UserInfo
    _LOGGER.debug("Librus auth step 5: activating API access")
    response = session.get(
        f"{LIBRUS_API_URL}/Auth/UserInfo/{user_identifier}",
        timeout=REQUEST_TIMEOUT,
    )
    _LOGGER.debug(
        "Librus auth step 5: HTTP %s",
        response.status_code,
    )

    if not response.ok:
        _LOGGER.debug(
            "Librus auth step 5: UserInfo failed with HTTP %s",
            response.status_code,
        )
        raise LibrusAuthError("Failed to activate API access")

    _LOGGER.debug("Librus auth: all five steps completed successfully")
    return session


def validate_credentials(username: str, password: str) -> bool:
    """Validate Librus credentials using the full five-step OAuth flow.

    Returns True if all five steps succeed, False on auth failure.
    Raises LibrusTimeoutError on request timeout.
    Raises LibrusConnectionError on other network/connection issues.
    Does not retry on failure (FR-009). Fresh session per call (FR-010).
    """
    try:
        _create_authenticated_session(username, password)
        return True
    except LibrusAuthError:
        return False
    except requests.exceptions.Timeout as err:
        raise LibrusTimeoutError("Connection to Librus timed out") from err
    except requests.exceptions.ConnectionError as err:
        raise LibrusConnectionError("Could not connect to Librus") from err
    except requests.exceptions.RequestException as err:
        raise LibrusConnectionError(f"Librus request failed: {err}") from err


def _fetch_api_data(
    session: requests.Session, endpoint: str
) -> dict[str, Any]:
    """Fetch JSON data from a Librus API endpoint using an authenticated session."""
    url = f"{LIBRUS_API_URL}/{endpoint}"
    _LOGGER.debug("Fetching Librus API: %s", url)
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _build_category_map(categories_data: dict[str, Any]) -> dict[int, str]:
    """Build Category ID → Name lookup from GET /HomeWorks/Categories response."""
    result: dict[int, str] = {}
    for cat in categories_data.get("Categories", []):
        cat_id = cat.get("Id")
        if cat_id is not None:
            result[cat_id] = cat.get("Name", "Unknown")
    return result


def _build_subject_map(subjects_data: dict[str, Any]) -> dict[int, str]:
    """Build Subject ID → Name lookup from GET /Subjects response."""
    result: dict[int, str] = {}
    for subj in subjects_data.get("Subjects", []):
        subj_id = subj.get("Id")
        if subj_id is not None:
            result[subj_id] = subj.get("Name", "Unknown")
    return result


def _build_user_map(users_data: dict[str, Any]) -> dict[int, str]:
    """Build User ID → 'FirstName LastName' lookup from GET /Users response."""
    result: dict[int, str] = {}
    for user in users_data.get("Users", []):
        user_id = user.get("Id")
        if user_id is None:
            continue
        first = user.get("FirstName")
        last = user.get("LastName")
        if first and last:
            result[user_id] = f"{first} {last}"
        elif last:
            result[user_id] = last
        elif first:
            result[user_id] = first
        else:
            result[user_id] = "Unknown"
    return result


def _filter_by_date(
    homeworks: list[dict[str, Any]],
    past_days: int = 7,
    future_days: int = 14,
) -> list[dict[str, Any]]:
    """Filter homework entries to [today - past_days, today + future_days] window."""
    today = date.today()
    date_from = today - timedelta(days=past_days)
    date_to = today + timedelta(days=future_days)
    filtered = []
    for hw in homeworks:
        date_str = hw.get("Date")
        if not date_str:
            continue
        try:
            hw_date = date.fromisoformat(date_str)
        except ValueError:
            _LOGGER.debug("Skipping homework with invalid date: %s", date_str)
            continue
        if date_from <= hw_date <= date_to:
            filtered.append(hw)
    return filtered


def _resolve_homework_entry(
    hw: dict[str, Any],
    category_map: dict[int, str],
    subject_map: dict[int, str],
    user_map: dict[int, str],
) -> dict[str, Any]:
    """Transform a raw HomeWorks API entry into a resolved HomeworkEntry dict."""
    # Resolve Category
    category_ref = hw.get("Category")
    category_id = category_ref.get("Id") if isinstance(category_ref, dict) else None
    category_name = category_map.get(category_id, "Unknown") if category_id else "Unknown"

    # Resolve Subject (may be absent for school-wide events)
    subject_ref = hw.get("Subject")
    subject_id = subject_ref.get("Id") if isinstance(subject_ref, dict) else None
    subject_name = subject_map.get(subject_id, "Unknown") if subject_id else "Unknown"

    # Resolve Creator
    creator_ref = hw.get("CreatedBy")
    creator_id = creator_ref.get("Id") if isinstance(creator_ref, dict) else None
    creator_name = user_map.get(creator_id, "Unknown") if creator_id else "Unknown"

    entry: dict[str, Any] = {
        "id": hw.get("Id"),
        "date": hw.get("Date"),
        "subject": subject_name,
        "creator": creator_name,
        "category": category_name,
    }

    # Optional fields — include when present
    if hw.get("LessonNo") is not None:
        entry["lesson_no"] = str(hw["LessonNo"])
    if hw.get("TimeFrom") is not None:
        entry["time_from"] = hw["TimeFrom"]
    if hw.get("TimeTo") is not None:
        entry["time_to"] = hw["TimeTo"]
    if hw.get("Content") is not None:
        entry["content"] = hw["Content"]
    if hw.get("AddDate") is not None:
        entry["add_date"] = hw["AddDate"]

    return entry


def fetch_homework_data(
    username: str,
    password: str,
    past_days: int = 7,
    future_days: int = 14,
) -> list[dict[str, Any]]:
    """Authenticate and fetch homework data from Librus API.

    Performs the full five-step OAuth flow to create an authenticated session,
    then bulk-fetches HomeWorks, Categories, Subjects, and Users (4 API calls).
    Resolves IDs and filters by date window.

    Returns a list of HomeworkEntry dicts per data-model.md.
    Raises LibrusAuthError on invalid credentials.
    Raises LibrusTimeoutError on request timeout.
    Raises LibrusConnectionError on network/connection issues.
    Does not retry on failure (FR-009). Fresh session per call (FR-010).
    """
    try:
        session = _create_authenticated_session(username, password)

        # Bulk fetch all required data (4 API calls per research.md)
        _LOGGER.debug("Fetching homework data from Librus API")
        homeworks_data = _fetch_api_data(session, "HomeWorks")
        categories_data = _fetch_api_data(session, "HomeWorks/Categories")
        subjects_data = _fetch_api_data(session, "Subjects")
        users_data = _fetch_api_data(session, "Users")

        # Build lookup maps
        category_map = _build_category_map(categories_data)
        subject_map = _build_subject_map(subjects_data)
        user_map = _build_user_map(users_data)

        # Filter by date window (FR-005a)
        raw_homeworks = homeworks_data.get("HomeWorks", [])
        filtered = _filter_by_date(raw_homeworks, past_days, future_days)

        # Resolve IDs and build structured entries
        entries = [
            _resolve_homework_entry(hw, category_map, subject_map, user_map)
            for hw in filtered
        ]

        _LOGGER.debug(
            "Fetched %d homework entries (%d total, %d after date filter)",
            len(entries),
            len(raw_homeworks),
            len(filtered),
        )
        return entries

    except (LibrusAuthError, LibrusTimeoutError, LibrusConnectionError):
        raise
    except requests.exceptions.Timeout as err:
        _LOGGER.debug("Librus homework fetch: timeout - %s", err)
        raise LibrusTimeoutError("Connection to Librus timed out") from err
    except requests.exceptions.ConnectionError as err:
        _LOGGER.debug("Librus homework fetch: connection error - %s", err)
        raise LibrusConnectionError("Could not connect to Librus") from err
    except requests.exceptions.RequestException as err:
        _LOGGER.debug("Librus homework fetch: request error - %s", err)
        raise LibrusConnectionError(f"Librus request failed: {err}") from err
