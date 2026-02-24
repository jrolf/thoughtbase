"""Unit tests for thoughtbase.core."""

import os

from thoughtbase.core import (
    _ADMIN_URL,
    _EXEC_URL,
    SUPPORTED,
    call_agent,
    del_key,
    deploy_agent,
    gen_key,
    get_agent_info,
    get_balance,
    get_user_info,
    list_agents,
    set_api_key,
    supported,
    update_agent,
    update_user_info,
    welcome,
)

# Aliased to avoid pytest collecting it as a test function
from thoughtbase.core import test_agent as run_test_agent


# -----------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------


class TestSetApiKey:
    """Tests for set_api_key()."""

    def test_sets_env_var(self, monkeypatch):
        """set_api_key should store the key in THB_API_KEY."""
        monkeypatch.delenv("THB_API_KEY", raising=False)
        set_api_key("my-secret-key")
        assert os.environ["THB_API_KEY"] == "my-secret-key"

    def test_overwrites_existing(self, mock_api_key):  # noqa: ARG002
        """set_api_key should overwrite a previously set key."""
        set_api_key("new-key")
        assert os.environ["THB_API_KEY"] == "new-key"


# -----------------------------------------------------------------------
# Supported libraries
# -----------------------------------------------------------------------


class TestSupported:
    """Tests for the SUPPORTED list and supported() helper."""

    def test_returns_list(self):
        """supported() should return a list."""
        result = supported()
        assert isinstance(result, list)

    def test_contains_thoughtflow(self):
        """The runtime must support thoughtflow."""
        assert "thoughtflow" in supported()

    def test_contains_common_modules(self):
        """Standard-library and common third-party modules are present."""
        for mod in ("numpy", "pandas", "requests", "json", "os", "boto3"):
            assert mod in SUPPORTED, f"{mod} missing from SUPPORTED"

    def test_is_sorted(self):
        """The SUPPORTED list should be in alphabetical order."""
        assert sorted(SUPPORTED) == SUPPORTED


# -----------------------------------------------------------------------
# Welcome
# -----------------------------------------------------------------------


class TestWelcome:
    """Tests for welcome()."""

    def test_prints_without_error(self, capsys):
        """welcome() should print the onboarding message."""
        welcome()
        captured = capsys.readouterr()
        assert "THOUGHTBASE" in captured.out
        assert "Deploy" in captured.out


# -----------------------------------------------------------------------
# Agent deployment
# -----------------------------------------------------------------------


class TestDeployAgent:
    """Tests for deploy_agent()."""

    def test_sends_correct_request(self, capture_post):
        """deploy_agent should POST to the admin URL with func_name deploy_api."""
        cap = capture_post({"api_id": "agent-xyz"})
        result = deploy_agent(code="def f(): pass", key="k")
        assert cap["url"] == _ADMIN_URL
        assert cap["json"]["request"]["func_name"] == "deploy_api"
        assert cap["json"]["request"]["code"] == "def f(): pass"
        assert result["api_id"] == "agent-xyz"

    def test_omits_empty_code(self, capture_post):
        """deploy_agent with no code should not include a code key."""
        cap = capture_post({"api_id": "agent-xyz"})
        deploy_agent(key="k")
        assert "code" not in cap["json"]["request"]

    def test_includes_info(self, capture_post):
        """deploy_agent should forward the info dict."""
        cap = capture_post({"api_id": "agent-xyz"})
        deploy_agent(code="x", info={"name": "test"}, key="k")
        assert cap["json"]["request"]["info"] == {"name": "test"}

    def test_falls_back_to_env_key(self, mock_api_key, capture_post):  # noqa: ARG002
        """deploy_agent with no explicit key should use THB_API_KEY."""
        cap = capture_post({"api_id": "agent-xyz"})
        deploy_agent(code="x")
        assert cap["json"]["api_key"] == "test-key-abc123"


class TestUpdateAgent:
    """Tests for update_agent()."""

    def test_sends_agent_id(self, capture_post):
        """update_agent should include the api_id in the request."""
        cap = capture_post({"status": "ok"})
        update_agent("agent-xyz", code="def g(): pass", key="k")
        assert cap["json"]["request"]["api_id"] == "agent-xyz"
        assert cap["json"]["request"]["func_name"] == "update_api"


class TestListAgents:
    """Tests for list_agents()."""

    def test_sends_correct_func_name(self, capture_post):
        """list_agents should request func_name list_apis."""
        cap = capture_post([])
        list_agents(key="k")
        assert cap["json"]["request"]["func_name"] == "list_apis"

    def test_includes_user_id_when_given(self, capture_post):
        """list_agents with a user_id should include it in the request."""
        cap = capture_post([])
        list_agents(user_id="user-1", key="k")
        assert cap["json"]["request"]["user_id"] == "user-1"


class TestGetAgentInfo:
    """Tests for get_agent_info()."""

    def test_sends_agent_id(self, capture_post):
        """get_agent_info should send the api_id."""
        cap = capture_post({"name": "my-agent"})
        get_agent_info("agent-xyz", key="k")
        assert cap["json"]["request"]["api_id"] == "agent-xyz"
        assert cap["json"]["request"]["func_name"] == "get_api_info"


# -----------------------------------------------------------------------
# Execution
# -----------------------------------------------------------------------


class TestTestAgent:
    """Tests for test_agent()."""

    def test_sends_to_exec_url(self, capture_post):
        """test_agent should POST to the exec URL."""
        cap = capture_post(42, admin=False)
        result = run_test_agent("def f(n): return n*2", "f", 21, key="k")
        assert cap["url"] == _EXEC_URL
        assert result == 42

    def test_includes_code_and_fname(self, capture_post):
        """test_agent should send code, fname, and input in the body."""
        cap = capture_post("ok", admin=False)
        run_test_agent("code", "fn", {"x": 1}, key="k")
        assert cap["json"]["code"] == "code"
        assert cap["json"]["fname"] == "fn"
        assert cap["json"]["input"] == {"x": 1}

    def test_full_response(self, capture_post):
        """test_agent with full=True should return the entire envelope."""
        capture_post(42, admin=False)
        result = run_test_agent("code", "fn", key="k", full=True)
        assert "output" in result


class TestCallAgent:
    """Tests for call_agent()."""

    def test_sends_to_exec_url(self, capture_post):
        """call_agent should POST to the exec URL."""
        cap = capture_post("Hello!", admin=False)
        result = call_agent("agent-xyz", "greet", "World", key="k")
        assert cap["url"] == _EXEC_URL
        assert result == "Hello!"

    def test_includes_agent_id(self, capture_post):
        """call_agent should include api_id in the body."""
        cap = capture_post("ok", admin=False)
        call_agent("agent-xyz", "fn", key="k")
        assert cap["json"]["api_id"] == "agent-xyz"

    def test_full_response(self, capture_post):
        """call_agent with full=True should return the entire envelope."""
        capture_post("ok", admin=False)
        result = call_agent("agent-xyz", "fn", key="k", full=True)
        assert "output" in result


# -----------------------------------------------------------------------
# Account and key management
# -----------------------------------------------------------------------


class TestGetBalance:
    """Tests for get_balance()."""

    def test_sends_correct_func_name(self, capture_post):
        """get_balance should request func_name get_balance."""
        cap = capture_post({"credits": 500000})
        get_balance(key="k")
        assert cap["json"]["request"]["func_name"] == "get_balance"


class TestGetUserInfo:
    """Tests for get_user_info()."""

    def test_sends_correct_func_name(self, capture_post):
        """get_user_info should request func_name get_user_info."""
        cap = capture_post({"name": "test"})
        get_user_info(key="k")
        assert cap["json"]["request"]["func_name"] == "get_user_info"


class TestUpdateUserInfo:
    """Tests for update_user_info()."""

    def test_sends_new_info(self, capture_post):
        """update_user_info should include user_info in the request."""
        cap = capture_post({"status": "ok"})
        update_user_info({"email": "new@test.com"}, key="k")
        assert cap["json"]["request"]["user_info"] == {"email": "new@test.com"}


class TestGenKey:
    """Tests for gen_key()."""

    def test_sends_correct_func_name(self, capture_post):
        """gen_key should request func_name gen_key."""
        cap = capture_post({"key": "new-key-xyz"})
        gen_key(key="k")
        assert cap["json"]["request"]["func_name"] == "gen_key"

    def test_includes_role(self, capture_post):
        """gen_key with a role should include it."""
        cap = capture_post({"key": "new-key"})
        gen_key(role="CREATOR", key="k")
        assert cap["json"]["request"]["role"] == "CREATOR"


class TestDelKey:
    """Tests for del_key()."""

    def test_sends_key_to_delete(self, capture_post):
        """del_key should include key_to_delete in the request."""
        cap = capture_post({"status": "ok"})
        del_key("old-key", key="k")
        assert cap["json"]["request"]["key_to_delete"] == "old-key"
        assert cap["json"]["request"]["func_name"] == "del_key"
