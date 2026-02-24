"""
ThoughtBase: Secrets Setup + LLM Agent (End-to-End)

This example walks through the complete workflow:
    1. Store your LLM API key as a ThoughtBase secret
    2. Deploy an agent that uses ThoughtFlow to classify text
    3. Call the agent and see the classification result

This is the recommended pattern for deploying LLM-powered agents.
Your credentials are stored securely server-side and injected
automatically — they never appear in your deployed code.

Before running, set your ThoughtBase API key:
    export THB_API_KEY="your-key-here"
"""

from thoughtbase import (
    call_agent,
    delete_secrets,
    deploy_agent,
    list_secrets,
    set_secrets,
)


# -- Step 1: Store your LLM key (one-time setup) --------------------------

print("Step 1: Storing secrets...")
set_secrets({"OPENAI_API_KEY": "sk-your-openai-key-here"})

names = list_secrets()
print(f"  Stored secrets: {names}")


# -- Step 2: Deploy a classification agent ---------------------------------

agent_code = '''
from thoughtflow import LLM, MEMORY, THOUGHT

def classify(text):
    """Classify text as positive, negative, or neutral."""
    llm = LLM("openai:gpt-4o", key=SECRETS["OPENAI_API_KEY"])

    memory = MEMORY()
    memory.set_var("text", text)

    thought = THOUGHT(
        name="classify",
        llm=llm,
        prompt=(
            "Classify the sentiment of the following text as exactly one of: "
            "positive, negative, or neutral.\\n\\n"
            "Text: {text}\\n\\n"
            "Respond with a single word."
        ),
    )
    memory = thought(memory)

    return memory.get_var("classify_result")
'''

print("\nStep 2: Deploying classification agent...")
result = deploy_agent(agent_code)
agent_id = result["api_id"]
print(f"  Agent ID: {agent_id}")


# -- Step 3: Call the agent ------------------------------------------------

print("\nStep 3: Classifying text...")
samples = [
    "I absolutely love this product, it changed my life!",
    "The service was terrible and the staff was rude.",
    "The package arrived on Tuesday as expected.",
]

for text in samples:
    label = call_agent(agent_id, "classify", text)
    print(f"  [{label}] {text[:50]}...")


# -- Cleanup (optional) ----------------------------------------------------

# If you want to remove the stored key afterward:
# delete_secrets(["OPENAI_API_KEY"])
