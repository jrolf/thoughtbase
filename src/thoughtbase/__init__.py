"""
ThoughtBase: Deploy ThoughtFlow agents to the cloud as serverless APIs.

ThoughtBase is the deployment companion for ThoughtFlow.  It provides a
minimal Python SDK for packaging any Python code — especially ThoughtFlow
agent scripts — and deploying them as callable cloud endpoints backed by
AWS Lambda.

Core workflow:
    1. Write Python code (functions, classes, agents)
    2. Deploy it with ``deploy_agent(code)``
    3. Call it from anywhere with ``call_agent(agent_id, fname, input)``

Quick example:
    >>> from thoughtbase import set_api_key, deploy_agent, call_agent
    >>>
    >>> set_api_key("tb-abc123...")
    >>>
    >>> code = "def double(n): return n * 2"
    >>> info = deploy_agent(code)
    >>> agent_id = info["api_id"]
    >>>
    >>> result = call_agent(agent_id, "double", 21)
    >>> print(result)  # 42
"""

from __future__ import annotations

from thoughtbase.core import (
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
    test_agent,
    update_agent,
    update_user_info,
    welcome,
)


# Version
try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("thoughtbase")
except Exception:
    __version__ = "0.0.0"

# Public API
__all__ = [
    "SUPPORTED",
    "__version__",
    "call_agent",
    "del_key",
    "deploy_agent",
    "gen_key",
    "get_agent_info",
    "get_balance",
    "get_user_info",
    "list_agents",
    "set_api_key",
    "supported",
    "test_agent",
    "update_agent",
    "update_user_info",
    "welcome",
]
