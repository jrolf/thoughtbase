"""
ThoughtBase: Hello World

The simplest possible example — deploy a function, then call it.

Before running, set your API key:
    export TB_API_KEY="your-key-here"
"""

from thoughtbase import call_agent, deploy_agent


# -- Step 1: Define a function as a Python string --------------------------

code = "def times2(n): return n * 2"


# -- Step 2: Deploy it as a cloud agent ------------------------------------

result = deploy_agent(code)
agent_id = result["api_id"]
print(f"Deployed!  Agent ID: {agent_id}")


# -- Step 3: Call it -------------------------------------------------------

output = call_agent(agent_id, "times2", 21)
print(f"times2(21) = {output}")
# -> times2(21) = 42
