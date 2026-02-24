"""Shared fixtures for ThoughtBase tests."""

import pytest

from thoughtbase import core


class MockResponse:
    """Fake requests.Response for mocking HTTP calls."""

    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        """Return the stored JSON payload."""
        return self._json


def make_admin_response(payload):
    """Wrap *payload* in the backend's admin response envelope."""
    return {"output": {"response": payload}}


def make_exec_response(payload):
    """Wrap *payload* in the backend's exec response envelope."""
    return {"output": {"result": payload}}


@pytest.fixture()
def mock_api_key(monkeypatch):
    """Set a fake THB_API_KEY environment variable for the test."""
    monkeypatch.setenv("THB_API_KEY", "test-key-abc123")
    return "test-key-abc123"


@pytest.fixture()
def clear_api_key(monkeypatch):
    """Ensure THB_API_KEY is not set."""
    monkeypatch.delenv("THB_API_KEY", raising=False)


@pytest.fixture()
def mock_admin_post(monkeypatch):
    """Return a helper that patches requests.post for admin calls.

    Usage in tests::

        def test_something(mock_admin_post):
            mock_admin_post({"api_id": "agent-123"})
            result = deploy_agent(code="...", key="k")
            assert result["api_id"] == "agent-123"
    """

    def _setup(response_payload):
        resp = MockResponse(make_admin_response(response_payload))
        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: resp)
        return resp

    return _setup


@pytest.fixture()
def mock_exec_post(monkeypatch):
    """Return a helper that patches requests.post for exec calls.

    Usage in tests::

        def test_something(mock_exec_post):
            mock_exec_post(42)
            result = call_agent("id", "fn", 21, key="k")
            assert result == 42
    """

    def _setup(result_payload):
        resp = MockResponse(make_exec_response(result_payload))
        monkeypatch.setattr(core.requests, "post", lambda *_a, **_kw: resp)
        return resp

    return _setup


@pytest.fixture()
def capture_post(monkeypatch):
    """Capture the arguments sent to requests.post.

    Returns a dict with ``url``, ``json``, and ``response`` keys after
    the patched function is called.

    Usage::

        def test_body(capture_post, mock_api_key):
            cap = capture_post({"status": "ok"})
            deploy_agent(code="x", key="k")
            assert cap["json"]["request"]["func_name"] == "deploy_api"
    """

    def _setup(response_payload, admin=True):
        captured = {}
        if admin:
            envelope = make_admin_response(response_payload)
        else:
            envelope = make_exec_response(response_payload)
        resp = MockResponse(envelope)

        def fake_post(url, json=None, **_kwargs):
            captured["url"] = url
            captured["json"] = json
            captured["response"] = resp
            return resp

        monkeypatch.setattr(core.requests, "post", fake_post)
        return captured

    return _setup
