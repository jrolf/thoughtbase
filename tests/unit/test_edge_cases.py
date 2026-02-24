"""Edge-case and regression tests for thoughtbase.core.

Complements the happy-path tests in test_core.py by exercising:
- key resolution logic (_resolve_key)
- response-parse fallback branches (_admin_request, exec calls)
- default argument handling (input_obj defaults to {})
- protocol-level fields (encoded, zipped)
- optional user_id forwarding across multiple functions
- update_agent parameter combinations
- SUPPORTED list structural integrity
"""

import os

from thoughtbase import core
from thoughtbase.core import (
    _ENV_KEY,
    SUPPORTED,
    _resolve_key,
    call_agent,
    deploy_agent,
    gen_key,
    get_balance,
    get_user_info,
    list_agents,
    set_api_key,
    update_agent,
    update_user_info,
)

# Aliased to prevent pytest from collecting it as a test function
from thoughtbase.core import test_agent as run_test_agent


# -----------------------------------------------------------------------
# Key resolution
# -----------------------------------------------------------------------


class TestResolveKey:
    """Tests for the _resolve_key internal helper.

    This function is the authentication gate for every public call,
    so regressions here would break every function silently.
    """

    def test_explicit_key_returned_as_is(self):
        """An explicitly provided key should be returned unchanged."""
        assert _resolve_key("my-key") == "my-key"

    def test_empty_string_falls_back_to_env(self, monkeypatch):
        """An empty key should fall back to the THB_API_KEY env var."""
        monkeypatch.setenv(_ENV_KEY, "env-key-999")
        assert _resolve_key("") == "env-key-999"

    def test_explicit_key_overrides_env(self, monkeypatch):
        """An explicit key should take priority over the env var."""
        monkeypatch.setenv(_ENV_KEY, "env-key-999")
        assert _resolve_key("explicit-key") == "explicit-key"

    def test_missing_env_returns_empty_string(self, monkeypatch):
        """When no key is passed and env var is unset, return empty string."""
        monkeypatch.delenv(_ENV_KEY, raising=False)
        assert _resolve_key("") == ""

    def test_default_argument_is_empty_string(self, monkeypatch):
        """Calling _resolve_key() with no args should behave like key=''."""
        monkeypatch.setenv(_ENV_KEY, "default-test")
        assert _resolve_key() == "default-test"


class TestSetApiKeyEdgeCases:
    """Edge-case tests for set_api_key."""

    def test_empty_string_key(self, monkeypatch):
        """Setting an empty string should still write to the env var."""
        monkeypatch.setenv(_ENV_KEY, "old")
        set_api_key("")
        assert os.environ[_ENV_KEY] == ""


# -----------------------------------------------------------------------
# Response fallback paths
# -----------------------------------------------------------------------


class TestAdminResponseFallback:
    """Tests for when the admin backend returns unexpected JSON.

    _admin_request has a try/except that returns raw data when the
    response doesn't match the expected output.response structure.
    """

    def test_malformed_response_returns_raw_json(self, monkeypatch):
        """If the response lacks output.response, return the raw dict."""
        malformed = {"error": "something broke", "code": 500}

        class FakeResp:
            status_code = 200
            def json(self):
                return malformed

        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: FakeResp())
        result = deploy_agent(code="x", key="k")
        assert result == malformed

    def test_missing_output_key_returns_raw(self, monkeypatch):
        """A response with no 'output' key should fall through."""
        no_output = {"status": "error", "message": "unauthorized"}

        class FakeResp:
            status_code = 200
            def json(self):
                return no_output

        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: FakeResp())
        result = list_agents(key="k")
        assert result == no_output

    def test_missing_response_inside_output(self, monkeypatch):
        """A response with 'output' but no 'response' key should fall through."""
        partial = {"output": {"something_else": 42}}

        class FakeResp:
            status_code = 200
            def json(self):
                return partial

        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: FakeResp())
        result = get_balance(key="k")
        assert result == partial


class TestExecResponseFallback:
    """Tests for when exec calls return unexpected JSON.

    Both test_agent and call_agent try output.result and fall back to
    returning the raw response on failure.
    """

    def test_test_agent_malformed_returns_raw(self, monkeypatch):
        """test_agent should return raw JSON when output.result is missing."""
        raw = {"error": "timeout"}

        class FakeResp:
            status_code = 200
            def json(self):
                return raw

        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: FakeResp())
        result = run_test_agent("code", "fn", key="k")
        assert result == raw

    def test_call_agent_malformed_returns_raw(self, monkeypatch):
        """call_agent should return raw JSON when output.result is missing."""
        raw = {"error": "agent not found"}

        class FakeResp:
            status_code = 200
            def json(self):
                return raw

        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: FakeResp())
        result = call_agent("bad-id", "fn", key="k")
        assert result == raw


# -----------------------------------------------------------------------
# Default input_obj handling
# -----------------------------------------------------------------------


class TestDefaultInputObj:
    """Verify that input_obj defaults to {} when not provided."""

    def test_test_agent_default_input(self, capture_post):
        """test_agent with no input_obj should send {} as input."""
        cap = capture_post("ok", admin=False)
        run_test_agent("code", "fn", key="k")
        assert cap["json"]["input"] == {}

    def test_call_agent_default_input(self, capture_post):
        """call_agent with no input_obj should send {} as input."""
        cap = capture_post("ok", admin=False)
        call_agent("agent-1", "fn", key="k")
        assert cap["json"]["input"] == {}


# -----------------------------------------------------------------------
# call_agent protocol fields
# -----------------------------------------------------------------------


class TestCallAgentProtocol:
    """Verify protocol-level fields sent by call_agent.

    The backend expects encoded=1 and zipped=0 in every exec call.
    If these drift, deployed agents break silently.
    """

    def test_sends_encoded_flag(self, capture_post):
        """call_agent should send encoded=1."""
        cap = capture_post("ok", admin=False)
        call_agent("agent-1", "fn", key="k")
        assert cap["json"]["encoded"] == 1

    def test_sends_zipped_flag(self, capture_post):
        """call_agent should send zipped=0."""
        cap = capture_post("ok", admin=False)
        call_agent("agent-1", "fn", key="k")
        assert cap["json"]["zipped"] == 0

    def test_sends_api_key_in_body(self, capture_post):
        """call_agent should include the api_key in the request body."""
        cap = capture_post("ok", admin=False)
        call_agent("agent-1", "fn", key="my-key")
        assert cap["json"]["api_key"] == "my-key"


# -----------------------------------------------------------------------
# update_agent parameter combinations
# -----------------------------------------------------------------------


class TestUpdateAgentVariations:
    """Tests for the different parameter combinations of update_agent."""

    def test_code_only_omits_info(self, capture_post):
        """update_agent with code but no info should omit the info key."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-1", code="def f(): pass", key="k")
        assert cap["json"]["request"]["code"] == "def f(): pass"
        assert "info" not in cap["json"]["request"]

    def test_info_only_omits_code(self, capture_post):
        """update_agent with info but no code should omit the code key."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-1", info={"name": "new"}, key="k")
        assert cap["json"]["request"]["info"] == {"name": "new"}
        assert "code" not in cap["json"]["request"]

    def test_both_code_and_info(self, capture_post):
        """update_agent with both code and info should include both."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-1", code="x = 1", info={"v": 2}, key="k")
        assert cap["json"]["request"]["code"] == "x = 1"
        assert cap["json"]["request"]["info"] == {"v": 2}

    def test_falls_back_to_env_key(self, mock_api_key, capture_post):  # noqa: ARG002
        """update_agent with no explicit key should use THB_API_KEY."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-1", code="x")
        assert cap["json"]["api_key"] == "test-key-abc123"

    def test_sends_update_api_func_name(self, capture_post):
        """update_agent should always send func_name update_api."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-1", key="k")
        assert cap["json"]["request"]["func_name"] == "update_api"


# -----------------------------------------------------------------------
# Optional user_id forwarding
# -----------------------------------------------------------------------


class TestUserIdForwarding:
    """Verify that optional user_id is included when provided.

    Several functions accept user_id for admin-level lookups.
    These tests ensure the param actually reaches the request body.
    """

    def test_get_balance_includes_user_id(self, capture_post):
        """get_balance with user_id should include it in the request."""
        cap = capture_post({"credits": 100})
        get_balance(user_id="user-42", key="k")
        assert cap["json"]["request"]["user_id"] == "user-42"

    def test_get_balance_omits_empty_user_id(self, capture_post):
        """get_balance with no user_id should not include the key."""
        cap = capture_post({"credits": 100})
        get_balance(key="k")
        assert "user_id" not in cap["json"]["request"]

    def test_get_user_info_includes_user_id(self, capture_post):
        """get_user_info with user_id should include it."""
        cap = capture_post({"name": "admin"})
        get_user_info(user_id="user-42", key="k")
        assert cap["json"]["request"]["user_id"] == "user-42"

    def test_get_user_info_omits_empty_user_id(self, capture_post):
        """get_user_info with no user_id should not include the key."""
        cap = capture_post({"name": "me"})
        get_user_info(key="k")
        assert "user_id" not in cap["json"]["request"]

    def test_update_user_info_includes_user_id(self, capture_post):
        """update_user_info with user_id should forward it."""
        cap = capture_post({"status": "ok"})
        update_user_info({"email": "x@y.com"}, user_id="user-42", key="k")
        assert cap["json"]["request"]["user_id"] == "user-42"

    def test_update_user_info_omits_empty_user_id(self, capture_post):
        """update_user_info with no user_id should not include the key."""
        cap = capture_post({"status": "ok"})
        update_user_info({"email": "x@y.com"}, key="k")
        assert "user_id" not in cap["json"]["request"]

    def test_gen_key_includes_user_id(self, capture_post):
        """gen_key with user_id should include it."""
        cap = capture_post({"key": "new"})
        gen_key(user_id="user-42", key="k")
        assert cap["json"]["request"]["user_id"] == "user-42"

    def test_gen_key_omits_empty_user_id(self, capture_post):
        """gen_key with no user_id should not include the key."""
        cap = capture_post({"key": "new"})
        gen_key(key="k")
        assert "user_id" not in cap["json"]["request"]

    def test_list_agents_omits_empty_user_id(self, capture_post):
        """list_agents with no user_id should not include the key."""
        cap = capture_post([])
        list_agents(key="k")
        assert "user_id" not in cap["json"]["request"]


# -----------------------------------------------------------------------
# SUPPORTED list structural integrity
# -----------------------------------------------------------------------


class TestSupportedListIntegrity:
    """Structural invariants for the SUPPORTED constant.

    These catch accidental copy-paste duplicates or formatting errors
    when the list is extended in the future.
    """

    def test_no_duplicates(self):
        """Every entry in SUPPORTED should be unique."""
        assert len(SUPPORTED) == len(set(SUPPORTED))

    def test_no_empty_strings(self):
        """SUPPORTED should not contain empty strings."""
        assert "" not in SUPPORTED

    def test_all_entries_are_strings(self):
        """Every entry in SUPPORTED should be a plain string."""
        for entry in SUPPORTED:
            assert isinstance(entry, str), f"non-string entry: {entry!r}"

    def test_no_leading_or_trailing_whitespace(self):
        """Entries should not have accidental whitespace."""
        for entry in SUPPORTED:
            assert entry == entry.strip(), f"whitespace in: {entry!r}"

    def test_minimum_expected_count(self):
        """The list should contain at least 200 modules."""
        assert len(SUPPORTED) >= 200
