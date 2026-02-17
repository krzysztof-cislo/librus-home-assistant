"""Tests for the Librus API client (librus_client.py)."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
import requests

from custom_components.librus.librus_client import (
    LibrusAuthError,
    LibrusConnectionError,
    LibrusTimeoutError,
    _build_category_map,
    _build_subject_map,
    _build_user_map,
    _create_authenticated_session,
    _filter_by_date,
    _resolve_homework_entry,
    fetch_homework_data,
    validate_credentials,
)


# -----------------------------------------------------------------------
# _build_category_map
# -----------------------------------------------------------------------
class TestBuildCategoryMap:
    """Tests for category lookup map builder."""

    def test_builds_map_from_valid_data(self, sample_categories):
        result = _build_category_map(sample_categories)
        assert result == {
            8363: "kartkówka",
            8556: "inne wydarzenia",
            8364: "praca dodatkowa",
        }

    def test_empty_categories(self):
        result = _build_category_map({"Categories": []})
        assert result == {}

    def test_missing_categories_key(self):
        result = _build_category_map({})
        assert result == {}

    def test_category_without_name_uses_unknown(self):
        result = _build_category_map({"Categories": [{"Id": 1}]})
        assert result == {1: "Unknown"}

    def test_category_without_id_skipped(self):
        result = _build_category_map({"Categories": [{"Name": "test"}]})
        assert result == {}


# -----------------------------------------------------------------------
# _build_subject_map
# -----------------------------------------------------------------------
class TestBuildSubjectMap:
    """Tests for subject lookup map builder."""

    def test_builds_map_from_valid_data(self, sample_subjects):
        result = _build_subject_map(sample_subjects)
        assert result == {25678: "Historia", 25683: "Język polski"}

    def test_empty_subjects(self):
        result = _build_subject_map({"Subjects": []})
        assert result == {}

    def test_missing_subjects_key(self):
        result = _build_subject_map({})
        assert result == {}

    def test_subject_without_name_uses_unknown(self):
        result = _build_subject_map({"Subjects": [{"Id": 1}]})
        assert result == {1: "Unknown"}


# -----------------------------------------------------------------------
# _build_user_map
# -----------------------------------------------------------------------
class TestBuildUserMap:
    """Tests for user lookup map builder."""

    def test_builds_full_names(self, sample_users):
        result = _build_user_map(sample_users)
        assert result[1493507] == "Krzysztof Krupa"
        assert result[1890192] == "Anna Kowalska"

    def test_null_first_name_uses_last_only(self, sample_users):
        result = _build_user_map(sample_users)
        assert result[1589959] == "Nowak"

    def test_null_last_name_uses_first_only(self):
        data = {"Users": [{"Id": 1, "FirstName": "Jan", "LastName": None}]}
        result = _build_user_map(data)
        assert result[1] == "Jan"

    def test_both_names_null_uses_unknown(self):
        data = {"Users": [{"Id": 1, "FirstName": None, "LastName": None}]}
        result = _build_user_map(data)
        assert result[1] == "Unknown"

    def test_both_names_missing_uses_unknown(self):
        data = {"Users": [{"Id": 1}]}
        result = _build_user_map(data)
        assert result[1] == "Unknown"

    def test_empty_users(self):
        result = _build_user_map({"Users": []})
        assert result == {}

    def test_user_without_id_skipped(self):
        data = {"Users": [{"FirstName": "Jan", "LastName": "Kowalski"}]}
        result = _build_user_map(data)
        assert result == {}


# -----------------------------------------------------------------------
# _filter_by_date
# -----------------------------------------------------------------------
class TestFilterByDate:
    """Tests for client-side date filtering."""

    def test_filters_within_window(self):
        today = date.today()
        homeworks = [
            {"Date": (today - timedelta(days=3)).isoformat(), "Id": 1},
            {"Date": (today + timedelta(days=5)).isoformat(), "Id": 2},
            {"Date": (today - timedelta(days=30)).isoformat(), "Id": 3},
            {"Date": (today + timedelta(days=30)).isoformat(), "Id": 4},
        ]
        result = _filter_by_date(homeworks, past_days=7, future_days=14)
        assert len(result) == 2
        assert result[0]["Id"] == 1
        assert result[1]["Id"] == 2

    def test_includes_boundary_dates(self):
        today = date.today()
        homeworks = [
            {"Date": (today - timedelta(days=7)).isoformat(), "Id": 1},
            {"Date": (today + timedelta(days=14)).isoformat(), "Id": 2},
        ]
        result = _filter_by_date(homeworks, past_days=7, future_days=14)
        assert len(result) == 2

    def test_excludes_just_outside_boundary(self):
        today = date.today()
        homeworks = [
            {"Date": (today - timedelta(days=8)).isoformat(), "Id": 1},
            {"Date": (today + timedelta(days=15)).isoformat(), "Id": 2},
        ]
        result = _filter_by_date(homeworks, past_days=7, future_days=14)
        assert len(result) == 0

    def test_today_is_included(self):
        today = date.today()
        homeworks = [{"Date": today.isoformat(), "Id": 1}]
        result = _filter_by_date(homeworks)
        assert len(result) == 1

    def test_skips_entries_without_date(self):
        homeworks = [{"Id": 1}, {"Date": None, "Id": 2}]
        result = _filter_by_date(homeworks)
        assert len(result) == 0

    def test_skips_invalid_date_format(self):
        homeworks = [{"Date": "not-a-date", "Id": 1}]
        result = _filter_by_date(homeworks)
        assert len(result) == 0

    def test_empty_list(self):
        result = _filter_by_date([])
        assert result == []


# -----------------------------------------------------------------------
# _resolve_homework_entry
# -----------------------------------------------------------------------
class TestResolveHomeworkEntry:
    """Tests for homework entry ID resolution."""

    def setup_method(self):
        self.cat_map = {8556: "inne wydarzenia", 8363: "kartkówka"}
        self.subj_map = {25678: "Historia"}
        self.user_map = {1493507: "Krzysztof Krupa"}

    def test_resolves_all_fields(self):
        hw = {
            "Id": 6671271,
            "Date": "2026-02-20",
            "Content": "Test content",
            "Category": {"Id": 8556},
            "Subject": {"Id": 25678},
            "CreatedBy": {"Id": 1493507},
            "LessonNo": "1",
            "TimeFrom": "07:45:00",
            "TimeTo": "08:30:00",
            "AddDate": "2026-02-15 11:12:16",
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert result["id"] == 6671271
        assert result["date"] == "2026-02-20"
        assert result["subject"] == "Historia"
        assert result["creator"] == "Krzysztof Krupa"
        assert result["category"] == "inne wydarzenia"
        assert result["lesson_no"] == "1"
        assert result["time_from"] == "07:45:00"
        assert result["time_to"] == "08:30:00"
        assert result["content"] == "Test content"
        assert result["add_date"] == "2026-02-15 11:12:16"

    def test_missing_subject_uses_unknown(self):
        hw = {
            "Id": 1,
            "Date": "2026-02-20",
            "Category": {"Id": 8556},
            "CreatedBy": {"Id": 1493507},
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert result["subject"] == "Unknown"

    def test_unresolvable_category_uses_unknown(self):
        hw = {
            "Id": 1,
            "Date": "2026-02-20",
            "Category": {"Id": 99999},
            "Subject": {"Id": 25678},
            "CreatedBy": {"Id": 1493507},
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert result["category"] == "Unknown"

    def test_unresolvable_creator_uses_unknown(self):
        hw = {
            "Id": 1,
            "Date": "2026-02-20",
            "Category": {"Id": 8556},
            "Subject": {"Id": 25678},
            "CreatedBy": {"Id": 99999},
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert result["creator"] == "Unknown"

    def test_optional_fields_omitted_when_absent(self):
        hw = {
            "Id": 1,
            "Date": "2026-02-20",
            "Category": {"Id": 8556},
            "CreatedBy": {"Id": 1493507},
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert "lesson_no" not in result
        assert "time_from" not in result
        assert "time_to" not in result
        assert "content" not in result
        assert "add_date" not in result

    def test_lesson_no_converted_to_string(self):
        hw = {
            "Id": 1,
            "Date": "2026-02-20",
            "Category": {"Id": 8556},
            "CreatedBy": {"Id": 1493507},
            "LessonNo": 3,
        }
        result = _resolve_homework_entry(hw, self.cat_map, self.subj_map, self.user_map)
        assert result["lesson_no"] == "3"
        assert isinstance(result["lesson_no"], str)


# -----------------------------------------------------------------------
# _create_authenticated_session
# -----------------------------------------------------------------------
class TestCreateAuthenticatedSession:
    """Tests for the five-step OAuth flow."""

    def _mock_session_responses(self, mock_session_cls, login_body="ok", token_ok=True, userinfo_ok=True):
        """Set up mock session with configurable responses for each auth step."""
        session = MagicMock()
        mock_session_cls.return_value = session

        step1_resp = MagicMock(status_code=200, url="https://api.librus.pl/OAuth/Authorization")
        step2_resp = MagicMock(status_code=200, url="https://api.librus.pl/OAuth/Authorization", text=login_body)
        step3_resp = MagicMock(status_code=200, url="https://synergia.librus.pl/")
        step4_resp = MagicMock(status_code=200 if token_ok else 401, ok=token_ok)
        step4_resp.json.return_value = {"UserIdentifier": "abc123"} if token_ok else {}
        step5_resp = MagicMock(status_code=200 if userinfo_ok else 500, ok=userinfo_ok)

        session.get.side_effect = [step1_resp, step3_resp, step4_resp, step5_resp]
        session.post.return_value = step2_resp
        session.headers = {}

        return session

    @patch("custom_components.librus.librus_client.requests.Session")
    def test_returns_session_on_success(self, mock_session_cls):
        self._mock_session_responses(mock_session_cls)
        session = _create_authenticated_session("user", "pass")
        assert session is not None

    @patch("custom_components.librus.librus_client.requests.Session")
    def test_raises_auth_error_on_invalid_credentials(self, mock_session_cls):
        self._mock_session_responses(mock_session_cls, login_body="error: Nieprawidłowy login lub hasło")
        with pytest.raises(LibrusAuthError):
            _create_authenticated_session("user", "wrongpass")

    @patch("custom_components.librus.librus_client.requests.Session")
    def test_raises_auth_error_on_token_failure(self, mock_session_cls):
        self._mock_session_responses(mock_session_cls, token_ok=False)
        with pytest.raises(LibrusAuthError, match="token info"):
            _create_authenticated_session("user", "pass")

    @patch("custom_components.librus.librus_client.requests.Session")
    def test_raises_auth_error_on_userinfo_failure(self, mock_session_cls):
        self._mock_session_responses(mock_session_cls, userinfo_ok=False)
        with pytest.raises(LibrusAuthError, match="activate API access"):
            _create_authenticated_session("user", "pass")

    @patch("custom_components.librus.librus_client.requests.Session")
    def test_calls_all_five_steps(self, mock_session_cls):
        session = self._mock_session_responses(mock_session_cls)
        _create_authenticated_session("user", "pass")
        assert session.get.call_count == 4  # steps 1, 3, 4, 5
        assert session.post.call_count == 1  # step 2


# -----------------------------------------------------------------------
# validate_credentials
# -----------------------------------------------------------------------
class TestValidateCredentials:
    """Tests for the credential validation wrapper."""

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_returns_true_on_success(self, mock_auth):
        mock_auth.return_value = MagicMock()
        assert validate_credentials("user", "pass") is True

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_returns_false_on_auth_error(self, mock_auth):
        mock_auth.side_effect = LibrusAuthError("bad creds")
        assert validate_credentials("user", "wrong") is False

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_raises_timeout_error(self, mock_auth):
        mock_auth.side_effect = requests.exceptions.Timeout("timed out")
        with pytest.raises(LibrusTimeoutError):
            validate_credentials("user", "pass")

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_raises_connection_error(self, mock_auth):
        mock_auth.side_effect = requests.exceptions.ConnectionError("no route")
        with pytest.raises(LibrusConnectionError):
            validate_credentials("user", "pass")


# -----------------------------------------------------------------------
# fetch_homework_data
# -----------------------------------------------------------------------
class TestFetchHomeworkData:
    """Tests for the full homework fetch flow."""

    @patch("custom_components.librus.librus_client._fetch_api_data")
    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_returns_resolved_filtered_entries(
        self,
        mock_auth,
        mock_fetch,
        sample_homeworks,
        sample_categories,
        sample_subjects,
        sample_users,
        mock_homework_entries,
    ):
        mock_auth.return_value = MagicMock()
        mock_fetch.side_effect = [
            sample_homeworks,
            sample_categories,
            sample_subjects,
            sample_users,
        ]

        result = fetch_homework_data("user", "pass")

        # The old homework (2020-01-01) should be filtered out
        assert len(result) == 2
        assert result[0]["id"] == 6671271
        assert result[0]["subject"] == "Historia"
        assert result[0]["creator"] == "Krzysztof Krupa"
        assert result[0]["category"] == "inne wydarzenia"

        # Second entry has no Subject — should be "Unknown"
        assert result[1]["id"] == 6674588
        assert result[1]["subject"] == "Unknown"
        # User 1589959 has FirstName=None, LastName="Nowak"
        assert result[1]["creator"] == "Nowak"

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_raises_auth_error_on_invalid_creds(self, mock_auth):
        mock_auth.side_effect = LibrusAuthError("bad")
        with pytest.raises(LibrusAuthError):
            fetch_homework_data("user", "wrong")

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_raises_timeout_error(self, mock_auth):
        mock_auth.side_effect = requests.exceptions.Timeout("timed out")
        with pytest.raises(LibrusTimeoutError):
            fetch_homework_data("user", "pass")

    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_raises_connection_error(self, mock_auth):
        mock_auth.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(LibrusConnectionError):
            fetch_homework_data("user", "pass")

    @patch("custom_components.librus.librus_client._fetch_api_data")
    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_makes_four_api_calls(self, mock_auth, mock_fetch):
        mock_auth.return_value = MagicMock()
        mock_fetch.return_value = {"HomeWorks": [], "Categories": [], "Subjects": [], "Users": []}

        fetch_homework_data("user", "pass")

        assert mock_fetch.call_count == 4
        endpoints = [call.args[1] for call in mock_fetch.call_args_list]
        assert "HomeWorks" in endpoints
        assert "HomeWorks/Categories" in endpoints
        assert "Subjects" in endpoints
        assert "Users" in endpoints

    @patch("custom_components.librus.librus_client._fetch_api_data")
    @patch("custom_components.librus.librus_client._create_authenticated_session")
    def test_returns_empty_list_when_no_homeworks(self, mock_auth, mock_fetch):
        mock_auth.return_value = MagicMock()
        mock_fetch.side_effect = [
            {"HomeWorks": []},
            {"Categories": []},
            {"Subjects": []},
            {"Users": []},
        ]

        result = fetch_homework_data("user", "pass")
        assert result == []
