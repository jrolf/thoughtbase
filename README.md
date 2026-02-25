<p align="center">
  <img src="https://raw.githubusercontent.com/jrolf/thoughtbase/main/assets/logo.png" alt="ThoughtBase logo" width="400">
</p>

<h1 align="center">ThoughtBase</h1>

<p align="center">
  <strong>Deploy ThoughtFlow Agents to the Cloud in 3 Lines of Python</strong>
</p>

<p align="center">
  <em>"Simple things should be simple.  Difficult things should be possible."</em>
</p>

<!-- Primary badges: trust signals -->
<p align="center">
  <a href="https://pypi.org/project/thoughtbase/"><img src="https://img.shields.io/pypi/v/thoughtbase?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/thoughtbase/"><img src="https://img.shields.io/pypi/pyversions/thoughtbase" alt="Python versions"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://github.com/jrolf/thoughtbase"><img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build"></a>
  <a href="https://pepy.tech/project/thoughtbase"><img src="https://static.pepy.tech/badge/thoughtbase/month" alt="Downloads/month"></a>
</p>

<!-- Secondary badges: social + quality -->
<p align="center">
  <a href="https://github.com/jrolf/thoughtbase/stargazers"><img src="https://img.shields.io/github/stars/jrolf/thoughtbase?style=flat" alt="GitHub stars"></a>
  <a href="https://github.com/jrolf/thoughtbase/commits/main"><img src="https://img.shields.io/github/last-commit/jrolf/thoughtbase" alt="Last commit"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</p>

<!-- Navigation -->
<p align="center">
  <a href="#what-is-thoughtbase">About</a> &bull;
  <a href="#why-thoughtbase">Why</a> &bull;
  <a href="#getting-access">Access</a> &bull;
  <a href="#installation">Install</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#secrets-management">Secrets</a> &bull;
  <a href="#deploy-a-thoughtflow-agent">Agent Example</a> &bull;
  <a href="#api-reference">API Reference</a>
</p>

---

## What is ThoughtBase?

**ThoughtBase** is the cloud deployment layer for
[ThoughtFlow](https://github.com/jrolf/thoughtflow).

Build your AI agent locally with ThoughtFlow — then deploy it as a live,
callable cloud API with a single function call.  No Docker, no Terraform,
no YAML, no deployment pipelines.  Just Python.

Your deployed agent runs in a pre-warmed **Python 3.12** environment with
**200+ libraries** already installed — including ThoughtFlow itself.  Store
your LLM API keys and credentials securely with built-in **secrets
management**, and they are automatically available to your agent at runtime.

ThoughtBase also works with *any* Python code — functions, classes, scripts —
but it is purpose-built for shipping ThoughtFlow agents into production.

---

## Why ThoughtBase?

| Without ThoughtBase | With ThoughtBase |
|---|---|
| Package code into a Docker image or Lambda zip | `deploy_agent(code)` |
| Configure IAM roles, API Gateway, environment variables | Handled automatically |
| Set up CI/CD pipeline for updates | `update_agent(agent_id, new_code)` |
| Manage secrets in AWS Secrets Manager or SSM | `set_secrets({"OPENAI_API_KEY": "sk-..."})` |
| Provision a server, scale manually | Serverless — scales to zero, scales up on demand |
| Install dependencies in the deployment target | 200+ libraries pre-installed |

**One dependency** (`requests`).  **One function call** to deploy.  **Zero
infrastructure** to manage.

---

## Getting Access

ThoughtBase is in **early access**.

To get your **free API key** and **free starter credits**, connect with the
creator, James Rolfsen, on LinkedIn:

**[Connect on LinkedIn](https://www.linkedin.com/in/jamesrolfsen/)**

You'll typically receive your key within 24 hours.  Once you have it, you're
ready to install and start deploying.

---

## Installation

```bash
pip install thoughtbase
```

The library has **one dependency** — `requests` — and works with Python 3.9+.

```bash
# Upgrade to the latest version
pip install --upgrade thoughtbase

# Check your installed version
python -c "import thoughtbase; print(thoughtbase.__version__)"
```

If you also want ThoughtFlow locally (for authoring agents):

```bash
pip install thoughtbase[thoughtflow]
```

---

## Quick Start

### 1. Set your API key

You can set it as an environment variable (recommended):

```bash
export THB_API_KEY="your-key-here"
```

Or set it in your Python code:

```python
from thoughtbase import set_api_key

set_api_key("your-key-here")
```

Once set, every subsequent function call uses it automatically — you don't
have to pass it again.

### 2. Deploy an agent (3 lines)

```python
from thoughtbase import deploy_agent

code = "def greet(name): return f'Hello, {name}!'"
result = deploy_agent(code)

print(result)
# {'api_id': 'abc123...', ...}
```

Your function is now a **live cloud API**.

### 3. Call it from anywhere (3 lines)

```python
from thoughtbase import call_agent

agent_id = result["api_id"]
output = call_agent(agent_id, "greet", "World")

print(output)
# Hello, World!
```

That's it.  **Deploy in 3 lines.  Call in 3 lines.**

---

## Test Before You Deploy

Don't want to deploy yet?  Use `test_agent` for a one-shot cloud execution:

```python
from thoughtbase import test_agent

code = "def double(n): return n * 2"
result = test_agent(code, "double", 21)

print(result)
# 42
```

The code runs in the cloud but is not persisted as a permanent endpoint.
This is useful for validating that your code works in the cloud runtime
before committing it to a deployed agent.

---

## Secrets Management

ThoughtBase provides built-in secrets management so your deployed agents can
access LLM API keys, database credentials, and other sensitive values
**without embedding them in code**.

### Store secrets (one-time setup)

```python
from thoughtbase import set_secrets, list_secrets

# Store one or more secrets — values are encrypted at rest
set_secrets({
    "OPENAI_API_KEY": "sk-abc123...",
    "DB_URL": "postgres://user:pass@host/db",
})

# Verify what's stored (names only — values are never returned)
print(list_secrets())
# {'secret_names': ['OPENAI_API_KEY', 'DB_URL']}
```

### Access secrets in your deployed code

Inside the cloud sandbox, all stored secrets are automatically available as a
plain Python dict named `SECRETS`:

```python
# This code runs in the cloud — SECRETS is injected automatically
def my_agent(query):
    import openai
    openai.api_key = SECRETS["OPENAI_API_KEY"]
    # ... use the key normally ...
```

### Request-level secrets (per-call override)

You can also pass secrets at call time.  These are merged with stored secrets
and take priority on name collision:

```python
result = call_agent(agent_id, "my_fn", input_data,
                    secrets={"TEMP_TOKEN": "tok-xyz..."})
```

### Delete secrets

```python
from thoughtbase import delete_secrets

delete_secrets(["DB_URL"])
```

### Design notes

- **Per-user, not per-agent.** All of your agents share the same secret store.
- **No value retrieval.** Secret values can never be read back through the API —
  they are only injected into the sandbox at runtime.
- **String values only.** If you need structured data, JSON-encode it and parse
  inside your function.

---

## Deploy a ThoughtFlow Agent

This is the full workflow: store your LLM credentials, deploy a ThoughtFlow
agent, and call it from anywhere.

```python
from thoughtbase import set_secrets, deploy_agent, call_agent

# -- Step 1: Store your LLM key (one-time) --------------------------------

set_secrets({"OPENAI_API_KEY": "sk-abc123..."})

# -- Step 2: Define a ThoughtFlow agent ------------------------------------

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

# -- Step 3: Deploy it ----------------------------------------------------

result = deploy_agent(agent_code)
agent_id = result["api_id"]
print(f"Deployed!  Agent ID: {agent_id}")

# -- Step 4: Call it from anywhere ----------------------------------------

article = """
ThoughtFlow is a Pythonic cognitive engine for building LLM-powered agents.
It provides four primitives — LLM, MEMORY, THOUGHT, and ACTION — that
compose into arbitrarily complex workflows.  The library has zero
dependencies and is designed for serverless deployment with sub-100ms
cold starts.
"""

summary = call_agent(agent_id, "summarize", article)
print(summary)
```

### Passing credentials at call time

If you prefer not to store secrets server-side, you can pass them per-call
instead:

```python
output = call_agent(
    agent_id, "summarize", article,
    secrets={"OPENAI_API_KEY": "sk-abc123..."},
)
```

This is useful when different callers need to use their own API keys.

---

## How It Works

```
 Your Machine                         ThoughtBase Cloud
┌──────────────────┐              ┌─────────────────────────┐
│                  │  set_secrets │                         │
│  Store LLM keys  ├─────────────►  Encrypted secret store  │
│  and credentials │              │                         │
└──────────────────┘              └────────────┬────────────┘
                                               │
┌──────────────────┐              ┌────────────▼────────────┐
│                  │ deploy_agent │                         │
│  Python / TF     ├─────────────►  Stored as serverless    │
│  agent code      │              │  API (AWS Lambda)       │
└──────────────────┘              └────────────┬────────────┘
                                               │
┌──────────────────┐              ┌────────────▼────────────┐
│                  │  call_agent  │  Executes your code     │
│  Any Python      ├─────────────►  with SECRETS injected,  │
│  environment     │◄─────────────┤  returns the result     │
└──────────────────┘    result    └─────────────────────────┘
```

1. **Store credentials** with `set_secrets()` — they're encrypted and
   available to all your agents automatically.
2. **Write your agent** using ThoughtFlow, plain Python, or both.
3. **Deploy it** with `deploy_agent(code)` — it becomes a serverless API.
4. **Call it** with `call_agent(agent_id, fname, input)` from any Python
   environment.
5. **Get the result** back as a Python object.

There is no container to manage, no server to provision, and no infrastructure
to configure.  Your code runs in a pre-warmed Python 3.12 environment with
200+ libraries already installed.

---

## Use Cases

**AI summarization service** — Deploy a ThoughtFlow agent that summarizes
documents, emails, or articles.  Call it from your web app backend.

**Classification and routing** — Ship an agent that classifies incoming
requests by intent and routes them to the right handler.

**Data enrichment pipeline** — Deploy an agent that fetches data from
multiple APIs, aggregates it, and returns a structured result.

**Multi-agent system** — Deploy multiple agents that call each other via
ThoughtBase, each handling a different stage of a complex workflow.

**Cognitive API endpoint** — Put any ThoughtFlow pipeline
(THOUGHT chains, DECIDE branches, PLAN steps) behind a callable endpoint.

---

## API Reference

### Authentication

| Function | Description |
|---|---|
| `set_api_key(key)` | Store your API key in the `THB_API_KEY` environment variable so all subsequent calls use it automatically. |

Every function below accepts an optional `key` parameter.  If omitted, the
value of the `THB_API_KEY` environment variable is used.

### Agent Deployment

Deploy, update, and manage your serverless agents.

| Function | Description |
|---|---|
| `deploy_agent(code, info, key)` | Deploy Python code as a new serverless agent. Returns a dict containing the `api_id`. |
| `update_agent(agent_id, code, info, key)` | Update the code or metadata of an existing deployed agent. |
| `list_agents(key)` | List all agents you have deployed. |
| `get_agent_info(agent_id, key)` | Get metadata about a deployed agent. |

### Execution

Call your deployed agents or run one-shot tests in the cloud.

| Function | Description |
|---|---|
| `call_agent(agent_id, fname, input_obj, key, secrets)` | Call a function by name inside a deployed agent. Optionally pass request-level `secrets`. |
| `test_agent(code, fname, input_obj, key, secrets)` | One-shot cloud execution without deploying. Optionally pass request-level `secrets`. |

Both `call_agent` and `test_agent` accept a `full=True` option to return the
complete backend response envelope instead of just the result value.

### Secrets Management

Store and manage credentials that are automatically injected into the
execution sandbox as a `SECRETS` dict.

| Function | Description |
|---|---|
| `set_secrets(secrets, key)` | Store one or more secrets (dict of name-value pairs). Existing names are overwritten. |
| `list_secrets(key)` | List stored secret names. Values are never returned through the API. |
| `delete_secrets(names, key)` | Delete one or more secrets by name. |

### Account Management

| Function | Description |
|---|---|
| `get_balance(key)` | Check your remaining credit balance. |
| `get_user_info(key)` | Get information about your account. |
| `update_user_info(new_info, key)` | Update your account information. |
| `gen_key(role, key)` | Generate a new API key for your account. |
| `del_key(key_to_delete, key)` | Revoke and delete an API key. |

### Utilities

| Function | Description |
|---|---|
| `supported()` | Return the list of all 200+ Python modules available in the cloud runtime. |
| `welcome()` | Print the getting-started guide to the console. |

---

## Credits and Billing

ThoughtBase uses a **credit-based** system.  Every API call (deploy, call,
test, list, etc.) consumes a small number of credits from your account.

- New accounts receive **free credits** upon signup.
- Check your balance at any time with `get_balance()`.
- Credits can be replenished by contacting the maintainer.

---

## Supported Libraries

The cloud runtime comes pre-loaded with **200+ Python modules**, including:

- **AI / Agents**: `thoughtflow`
- **Data science**: `numpy`, `pandas`, `statistics`
- **Databases**: `sqlalchemy`, `sqlite3`, `pymongo`, `pymysql`, `psycopg2`, `redis`
- **Networking**: `requests`, `urllib3`, `http`, `socket`
- **AWS**: `boto3`, `botocore`, `s3transfer`
- **Serialization**: `json`, `csv`, `pickle`, `xml`
- **Standard library**: the full Python 3.12 stdlib

To see the complete list:

```python
from thoughtbase import supported
print(supported())
```

---

## Philosophy

ThoughtBase extends ThoughtFlow's design principles to cloud deployment:

**Simple things should be simple.**
Deploying a function should be one line of code.  Calling it should be one line.
No configuration files, no build steps, no deployment ceremonies.

**Difficult things should be possible.**
Deploy complex multi-function agents that call LLMs, process data with
NumPy and Pandas, query databases, and orchestrate ThoughtFlow cognitive
pipelines — all from the same simple interface.

**Python-first.**
Your code is Python.  The deployment interface is Python.  The execution
environment is Python.  There is no transpilation, no containerization, and
no intermediary format.

**Minimal dependencies.**
ThoughtBase itself requires only `requests`.  The cloud runtime ships with
200+ modules so your deployed agents can use whatever they need.

---

## Related Projects

- **[ThoughtFlow](https://github.com/jrolf/thoughtflow)** — The Pythonic
  cognitive engine for LLM systems.  Write agents locally, deploy them with
  ThoughtBase.

---

## Contributing

Contributions are welcome!  Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.

---

## License

ThoughtBase is released under the [MIT License](LICENSE).

---

## Links

- **PyPI**: [pypi.org/project/thoughtbase](https://pypi.org/project/thoughtbase/)
- **GitHub**: [github.com/jrolf/thoughtbase](https://github.com/jrolf/thoughtbase)
- **Issues**: [github.com/jrolf/thoughtbase/issues](https://github.com/jrolf/thoughtbase/issues)
- **ThoughtFlow**: [github.com/jrolf/thoughtflow](https://github.com/jrolf/thoughtflow)
- **Contact**: james@think.dev
