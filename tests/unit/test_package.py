"""Tests for the thoughtbase package-level API surface.

Ensures that __init__.py correctly re-exports everything from core,
that __all__ is accurate and sorted, and that __version__ is present.
These tests catch import regressions when functions are added, renamed,
or removed in core.py but __init__.py is not updated to match.
"""

import importlib

import thoughtbase
from thoughtbase import core


# -----------------------------------------------------------------------
# Public API completeness
# -----------------------------------------------------------------------


class TestPublicApiSurface:
    """Verify that the package-level imports match __all__."""

    def test_all_entries_are_importable(self):
        """Every name in __all__ should be importable from thoughtbase."""
        for name in thoughtbase.__all__:
            assert hasattr(thoughtbase, name), f"{name} in __all__ but not importable"

    def test_all_is_sorted(self):
        """__all__ should be in alphabetical order to stay maintainable."""
        assert sorted(thoughtbase.__all__) == list(thoughtbase.__all__)

    def test_all_contains_expected_functions(self):
        """Key public functions must appear in __all__."""
        expected = {
            "set_api_key",
            "deploy_agent",
            "update_agent",
            "list_agents",
            "get_agent_info",
            "test_agent",
            "call_agent",
            "get_balance",
            "get_user_info",
            "update_user_info",
            "gen_key",
            "del_key",
            "set_secrets",
            "list_secrets",
            "delete_secrets",
            "supported",
            "welcome",
            "SUPPORTED",
            "__version__",
        }
        actual = set(thoughtbase.__all__)
        missing = expected - actual
        assert not missing, f"missing from __all__: {missing}"

    def test_no_private_names_in_all(self):
        """__all__ should not export names starting with underscore."""
        for name in thoughtbase.__all__:
            if name == "__version__":
                continue
            assert not name.startswith("_"), f"private name in __all__: {name}"

    def test_core_public_functions_reexported(self):
        """Every callable in core that doesn't start with _ should be
        accessible from the top-level thoughtbase package."""
        for name in dir(core):
            if name.startswith("_"):
                continue
            obj = getattr(core, name)
            if callable(obj):
                assert hasattr(thoughtbase, name), (
                    f"core.{name} is public and callable but not re-exported"
                )


# -----------------------------------------------------------------------
# Version
# -----------------------------------------------------------------------


class TestVersion:
    """Tests for __version__ metadata."""

    def test_version_is_string(self):
        """__version__ should be a string."""
        assert isinstance(thoughtbase.__version__, str)

    def test_version_is_not_empty(self):
        """__version__ should not be an empty string."""
        assert len(thoughtbase.__version__) > 0

    def test_version_has_dot_separated_parts(self):
        """__version__ should follow a major.minor.patch pattern."""
        parts = thoughtbase.__version__.split(".")
        assert len(parts) >= 2, f"unexpected version format: {thoughtbase.__version__}"


# -----------------------------------------------------------------------
# Module-level constants
# -----------------------------------------------------------------------


class TestModuleConstants:
    """Verify that important module-level constants are accessible."""

    def test_supported_constant_accessible(self):
        """SUPPORTED should be importable from the top-level package."""
        assert thoughtbase.SUPPORTED is core.SUPPORTED

    def test_functions_are_same_objects(self):
        """Re-exported functions should be the same objects as in core."""
        assert thoughtbase.deploy_agent is core.deploy_agent
        assert thoughtbase.call_agent is core.call_agent
        assert thoughtbase.set_api_key is core.set_api_key

    def test_importlib_reimport_works(self):
        """Reimporting the package should not raise."""
        mod = importlib.import_module("thoughtbase")
        assert hasattr(mod, "deploy_agent")
