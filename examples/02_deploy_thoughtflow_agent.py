"""
ThoughtBase: Deploy a ThoughtFlow Agent

This example deploys a real ThoughtFlow agent that uses LLM, MEMORY,
and THOUGHT to summarize text.  It reads the OpenAI API key from the
SECRETS dict, which is automatically injected by ThoughtBase.

Prerequisites:
    1. Set your ThoughtBase API key:
       export THB_API_KEY="your-key-here"

    2. Store your OpenAI key as a ThoughtBase secret (one-time):
       >>> from thoughtbase import set_secrets
       >>> set_secrets({"OPENAI_API_KEY": "sk-..."})
"""

from thoughtbase import call_agent, deploy_agent


# -- Define the ThoughtFlow agent code ------------------------------------

agent_code = '''
from thoughtflow import LLM, MEMORY, THOUGHT

def summarize(text):
    """Summarize text using ThoughtFlow + OpenAI."""
    llm = LLM("openai:gpt-4o", key=SECRETS["OPENAI_API_KEY"])

    memory = MEMORY()
    memory.set_var("text", text)

    thought = THOUGHT(
        name="summarize",
        llm=llm,
        prompt="Summarize the following in 2-3 concise sentences:\\n\\n{text}",
    )
    memory = thought(memory)

    return memory.get_var("summarize_result")
'''


# -- Deploy it -------------------------------------------------------------

result = deploy_agent(agent_code)
agent_id = result["api_id"]
print(f"Deployed!  Agent ID: {agent_id}")


# -- Call it ---------------------------------------------------------------

article = """
ThoughtFlow is a Pythonic cognitive engine for building LLM-powered agents.
It provides four primitives — LLM, MEMORY, THOUGHT, and ACTION — that
compose into arbitrarily complex workflows.  The library has zero
dependencies and is designed for serverless deployment with sub-100ms
cold starts.  ThoughtBase is its deployment companion, letting you ship
agents to the cloud in a single function call.
"""

summary = call_agent(agent_id, "summarize", article)
print(f"\nSummary:\n{summary}")
