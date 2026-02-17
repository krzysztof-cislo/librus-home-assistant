"""Librus Synergia OAuth client for credential validation.

Uses the same Synergia OAuth flow as the reference JS implementation
(https://github.com/Mati365/librus-api). No external Librus library needed.
"""

from __future__ import annotations

import logging

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


def validate_credentials(username: str, password: str) -> bool:
    """Validate Librus credentials using the full five-step OAuth flow.

    Follows the Postman Auth folder sequence (librus_api.json):
    1. GET OAuth/Authorization — initiate OAuth session
    2. POST credentials to OAuth/Authorization — login
    3. GET OAuth/Authorization/Grant — set session cookies via redirects
    4. GET Auth/TokenInfo — extract UserIdentifier
    5. GET Auth/UserInfo/{UserIdentifier} — activate API access

    Returns True if all five steps succeed, False on auth failure.
    Raises LibrusTimeoutError on request timeout.
    Raises LibrusConnectionError on other network/connection issues.
    Does not retry on failure (FR-009). Fresh session per call (FR-010).
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
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
            return False

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
            return False

        try:
            token_data = response.json()
            user_identifier = token_data["UserIdentifier"]
        except (ValueError, KeyError):
            _LOGGER.debug("Librus auth step 4: failed to parse UserIdentifier")
            return False

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
            return False

        _LOGGER.debug("Librus auth: all five steps completed successfully")
        return True

    except requests.exceptions.Timeout as err:
        _LOGGER.debug("Librus auth: timeout - %s", err)
        raise LibrusTimeoutError("Connection to Librus timed out") from err
    except requests.exceptions.ConnectionError as err:
        _LOGGER.debug("Librus auth: connection error - %s", err)
        raise LibrusConnectionError("Could not connect to Librus") from err
    except requests.exceptions.RequestException as err:
        _LOGGER.debug("Librus auth: request error - %s", err)
        raise LibrusConnectionError(f"Librus request failed: {err}") from err
