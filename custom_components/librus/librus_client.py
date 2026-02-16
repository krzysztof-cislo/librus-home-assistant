"""Librus Synergia OAuth client for credential validation.

Uses the same Synergia OAuth flow as the reference JS implementation
(https://github.com/Mati365/librus-api). No external Librus library needed.
"""

from __future__ import annotations

import logging

import requests

_LOGGER = logging.getLogger(__name__)

LIBRUS_OAUTH_URL = "https://api.librus.pl/OAuth/Authorization"
LIBRUS_OAUTH_2FA_URL = "https://api.librus.pl/OAuth/Authorization/2FA"
LIBRUS_SYNERGIA_URL = "https://synergia.librus.pl"
OAUTH_CLIENT_ID = "46"
REQUEST_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://portal.librus.pl/rodzina/synergia/loguj",
}


class LibrusAuthError(Exception):
    """Raised when Librus credentials are invalid."""


class LibrusConnectionError(Exception):
    """Raised when unable to connect to Librus."""


def validate_credentials(username: str, password: str) -> bool:
    """Validate Librus credentials using the Synergia OAuth flow.

    Follows the same approach as the JS reference implementation:
    1. GET OAuth/Authorization to initiate session
    2. POST credentials to OAuth/Authorization
    3. GET OAuth/Authorization/2FA to finalize auth
    4. Verify session by accessing a protected Synergia page

    Returns True if credentials are valid, False otherwise.
    Raises LibrusConnectionError on network/connection issues.
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("TestCookie", "1", domain="synergia.librus.pl")

    try:
        # Step 1: Initiate OAuth flow
        _LOGGER.warning("Librus auth: initiating OAuth flow")
        response = session.get(
            LIBRUS_OAUTH_URL,
            params={
                "client_id": OAUTH_CLIENT_ID,
                "response_type": "code",
                "scope": "mydata",
            },
            timeout=REQUEST_TIMEOUT,
        )
        _LOGGER.warning(
            "Librus auth step 1: HTTP %s, URL: %s",
            response.status_code,
            response.url,
        )

        # Step 2: Submit credentials
        response = session.post(
            f"{LIBRUS_OAUTH_URL}?client_id={OAUTH_CLIENT_ID}",
            data={
                "action": "login",
                "login": username,
                "pass": password,
            },
            timeout=REQUEST_TIMEOUT,
        )
        _LOGGER.warning(
            "Librus auth step 2: HTTP %s, URL: %s",
            response.status_code,
            response.url,
        )

        # Check for login error in response body
        if not response.ok:
            _LOGGER.warning(
                "Librus auth: credential submission failed with HTTP %s",
                response.status_code,
            )
            return False

        # Step 3: Complete 2FA/auth redirect
        response = session.get(
            LIBRUS_OAUTH_2FA_URL,
            params={"client_id": OAUTH_CLIENT_ID},
            timeout=REQUEST_TIMEOUT,
        )
        _LOGGER.warning(
            "Librus auth step 3: HTTP %s, URL: %s",
            response.status_code,
            response.url,
        )

        # Step 4: Verify authentication by accessing Synergia
        response = session.get(
            LIBRUS_SYNERGIA_URL,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )
        _LOGGER.warning(
            "Librus auth verify: HTTP %s, Location: %s",
            response.status_code,
            response.headers.get("Location", "N/A"),
        )

        # Authenticated: Synergia returns 200 or redirects to dashboard
        # Not authenticated: redirects to login portal
        if response.status_code == 200:
            return True

        location = response.headers.get("Location", "")
        if "synergia.librus.pl" in location and "loguj" not in location:
            return True

        _LOGGER.warning("Librus auth: not authenticated after OAuth flow")
        return False

    except requests.exceptions.Timeout as err:
        _LOGGER.warning("Librus auth: timeout - %s", err)
        raise LibrusConnectionError("Connection to Librus timed out") from err
    except requests.exceptions.ConnectionError as err:
        _LOGGER.warning("Librus auth: connection error - %s", err)
        raise LibrusConnectionError("Could not connect to Librus") from err
    except requests.exceptions.RequestException as err:
        _LOGGER.warning("Librus auth: request error - %s", err)
        raise LibrusConnectionError(f"Librus request failed: {err}") from err
