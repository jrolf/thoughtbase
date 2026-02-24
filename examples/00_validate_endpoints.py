"""
ThoughtBase: End-to-End Endpoint Validation

Confirms that the ThoughtBase library can:
  1. Reach the admin endpoint (deploy a simple agent)
  2. Reach the exec endpoint (call the deployed agent)
  3. Get the correct result back

Before running, set your API key:
    export THB_API_KEY="your-key-here"

Usage:
    python examples/00_validate_endpoints.py
"""

import sys
import time

from thoughtbase import call_agent, deploy_agent, get_balance, test_agent


DIVIDER = "-" * 60


def validate():
    """Run a full round-trip validation against both endpoints.

    Tests admin (deploy, balance) and exec (test_agent, call_agent)
    in sequence, printing results and a final pass/fail summary.

    Returns
    -------
    bool
        True if all checks passed, False otherwise.
    """
    results = []

    def check(label, passed, detail=""):
        """Record and print a single check result."""
        tag = "PASS" if passed else "FAIL"
        msg = f"  [{tag}] {label}"
        if detail:
            msg += f"  ({detail})"
        print(msg)
        results.append(passed)

    print()
    print(DIVIDER)
    print("  ThoughtBase — Endpoint Validation")
    print(DIVIDER)
    print()

    # --- 1. Admin: get_balance (lightweight admin round-trip) ---
    print("1. Admin endpoint — get_balance()")
    try:
        balance = get_balance()
        is_dict = isinstance(balance, dict)
        check("Reached admin endpoint", is_dict, f"response type: {type(balance).__name__}")
    except Exception as exc:
        check("Reached admin endpoint", False, str(exc))

    print()

    # --- 2. Exec: test_agent (one-shot execution, no deploy) ---
    print("2. Exec endpoint — test_agent() (one-shot, no deploy)")
    try:
        code = "def double(n): return n * 2"
        result = test_agent(code, "double", 21)
        check("test_agent returned correct result", result == 42, f"got {result!r}")
    except Exception as exc:
        check("test_agent returned correct result", False, str(exc))

    print()

    # --- 3. Admin + Exec: deploy_agent then call_agent ---
    print("3. Full round-trip — deploy_agent() + call_agent()")
    agent_id = None
    try:
        deploy_code = "def greet(name): return 'Hello, ' + str(name) + '!'"
        deploy_result = deploy_agent(deploy_code)
        agent_id = deploy_result.get("api_id", "")
        check("deploy_agent succeeded", len(agent_id) > 0, f"agent_id={agent_id!r}")
    except Exception as exc:
        check("deploy_agent succeeded", False, str(exc))

    if agent_id:
        # Brief pause to let the deployment propagate
        time.sleep(1)
        try:
            output = call_agent(agent_id, "greet", "World")
            expected = "Hello, World!"
            check("call_agent returned correct result", output == expected, f"got {output!r}")
        except Exception as exc:
            check("call_agent returned correct result", False, str(exc))
    else:
        check("call_agent returned correct result", False, "skipped — no agent_id")

    # --- Summary ---
    passed = sum(results)
    total = len(results)
    all_ok = passed == total

    print()
    print(DIVIDER)
    tag = "ALL PASSED" if all_ok else "SOME FAILED"
    print(f"  Result: {passed}/{total} checks passed — {tag}")
    print(DIVIDER)
    print()

    return all_ok


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
