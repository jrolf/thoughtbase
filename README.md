<!--
  ████████╗██╗  ██╗ ██████╗ ██╗   ██╗ ██████╗ ██╗  ██╗████████╗██████╗  █████╗ ███████╗███████╗
  ╚══██╔══╝██║  ██║██╔═══██╗██║   ██║██╔════╝ ██║  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
     ██║   ███████║██║   ██║██║   ██║██║  ███╗███████║   ██║   ██████╔╝███████║███████╗█████╗
     ██║   ██╔══██║██║   ██║██║   ██║██║   ██║██╔══██║   ██║   ██╔══██╗██╔══██║╚════██║██╔══╝
     ██║   ██║  ██║╚██████╔╝╚██████╔╝╚██████╔╝██║  ██║   ██║   ██████╔╝██║  ██║███████║███████╗
     ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
-->

<h1 align="center">ThoughtBase</h1>

<p align="center">
  <strong>Deploy ThoughtFlow Agents to the Cloud in 3 Lines of Python</strong>
</p>

<p align="center">
  <em>"Simple things should be simple.  Difficult things should be possible."</em>
</p>

<!-- Badges -->
<p align="center">
  <a href="https://pypi.org/project/thoughtbase/"><img src="https://img.shields.io/pypi/v/thoughtbase?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/thoughtbase/"><img src="https://img.shields.io/pypi/pyversions/thoughtbase" alt="Python versions"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://github.com/jrolf/thoughtbase"><img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</p>

<!-- Navigation -->
<p align="center">
  <a href="#-installation">Install</a> &bull;
  <a href="#-quick-start">Quick Start</a> &bull;
  <a href="#-deploy-a-thoughtflow-agent">Agent Example</a> &bull;
  <a href="#-api-reference">API Reference</a> &bull;
  <a href="#-supported-libraries">Libraries</a> &bull;
  <a href="#-philosophy">Philosophy</a>
</p>

---

## What is ThoughtBase?

**ThoughtBase** is the deployment companion for [ThoughtFlow](https://github.com/jrolf/thoughtflow).

Write your AI agent locally with ThoughtFlow, then deploy it to the cloud as a
serverless API with a single function call.  No Docker, no Terraform, no YAML,
no deployment pipelines.  Just Python.

ThoughtBase works with *any* Python code — functions, classes, scripts — but it
is purpose-built for shipping ThoughtFlow agents into production.

---

## Installation

```bash
pip install thoughtbase
```

The library has **one dependency** — `requests` — and works with Python 3.9+.

```bash
# Upgrade to the latest version
pip install --upgrade thoughtbase

# Pin to a specific version for stability
pip install thoughtbase==0.0.2

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

```python
from thoughtbase import set_api_key

set_api_key("YOUR_API_KEY")
```

Or set it in your environment:

```bash
export TB_API_KEY="YOUR_API_KEY"
```

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

---

## Deploy a ThoughtFlow Agent

This is where it gets powerful.  Any ThoughtFlow agent script can be deployed
as a cloud API.

Here is a complete example that deploys an agent which answers questions about
any US zip code by aggregating data from four different external APIs:

```python
from thoughtbase import set_api_key, deploy_agent, call_agent

set_api_key("YOUR_API_KEY")

# -----------------------------------------------------------------------
# Define the agent code as a Python string
# -----------------------------------------------------------------------

agent_code = '''
import requests, json

def zipcode_location(zipcode):
    """Look up the city, state, and coordinates for a US zip code."""
    r = requests.get("http://api.zippopotam.us/us/" + str(zipcode))
    loc = r.json()["places"][0]
    return {
        "place": loc["place name"],
        "state": loc["state"],
        "lat": float(loc["latitude"]),
        "lon": float(loc["longitude"]),
    }

def location_elevation(loc):
    """Get the elevation for a lat/lon pair."""
    loc_str = str(loc["lat"]) + "," + str(loc["lon"])
    params = {"locations": loc_str}
    r = requests.get("https://api.open-elevation.com/api/v1/lookup", params=params)
    meters = int(float(r.json()["results"][0]["elevation"]))
    return {"elevation_meters": meters, "elevation_feet": int(meters * 3.28084)}

def location_weather(loc):
    """Get the current weather for a lat/lon pair."""
    loc_str = str(loc["lat"]) + "," + str(loc["lon"])
    r = requests.get("https://wttr.in/" + loc_str + "?format=%C+%t")
    return str(r.text)

def location_sunlight(loc):
    """Get sunrise/sunset times for a lat/lon pair."""
    params = {"lat": loc["lat"], "lng": loc["lon"], "formatted": 1}
    r = requests.get("https://api.sunrise-sunset.org/json", params=params)
    sun = r.json()["results"]
    return {
        "sunrise": sun["sunrise"] + " GMT",
        "sunset": sun["sunset"] + " GMT",
        "solar_noon": sun["solar_noon"] + " GMT",
        "day_length": sun["day_length"] + " GMT",
    }

def get_zip_info(zipcode):
    """Aggregate location, elevation, weather, and sunlight for a zip code."""
    info = {"target_zipcode": str(zipcode)}
    try:
        loc = zipcode_location(zipcode)
        info["location"] = loc
    except Exception:
        info["location"] = "Zipcode not found."
        return info
    try:
        info["elevation"] = location_elevation(loc)
    except Exception:
        info["elevation"] = "Elevation data not found."
    try:
        info["weather"] = location_weather(loc)
    except Exception:
        info["weather"] = "Weather data not found."
    try:
        info["sunlight"] = location_sunlight(loc)
    except Exception:
        info["sunlight"] = "Sunlight data not found."
    return info
'''

# -----------------------------------------------------------------------
# Deploy it
# -----------------------------------------------------------------------

result = deploy_agent(agent_code)
agent_id = result["api_id"]

print(f"Deployed!  Agent ID: {agent_id}")

# -----------------------------------------------------------------------
# Call it
# -----------------------------------------------------------------------

output = call_agent(agent_id, "get_zip_info", 78749)

import json
print(json.dumps(output, indent=4))
```

The response looks like:

```json
{
    "target_zipcode": "78749",
    "location": {
        "place": "Austin",
        "state": "Texas",
        "lat": 30.2166,
        "lon": -97.8508
    },
    "elevation": {
        "elevation_meters": 234,
        "elevation_feet": 767
    },
    "weather": "Sunny +74 F.",
    "sunlight": {
        "sunrise": "12:38:05 PM GMT",
        "sunset": "12:41:39 AM GMT",
        "solar_noon": "6:39:52 PM GMT",
        "day_length": "12:03:34 GMT"
    }
}
```

---

## API Reference

### Authentication

| Function | Description |
|---|---|
| `set_api_key(key)` | Store your API key in the environment so all subsequent calls use it automatically |

### Agent Deployment

| Function | Description |
|---|---|
| `deploy_agent(code, info={})` | Deploy Python code as a new serverless agent. Returns dict with `api_id` |
| `update_agent(agent_id, code, info={})` | Update the code or metadata of an existing agent |
| `list_agents()` | List all agents you have deployed |
| `get_agent_info(agent_id)` | Get metadata about a deployed agent |

### Execution

| Function | Description |
|---|---|
| `call_agent(agent_id, fname, input_obj)` | Call a function inside a deployed agent |
| `test_agent(code, fname, input_obj)` | One-shot cloud execution without deploying |

### Account Management

| Function | Description |
|---|---|
| `get_balance()` | Check your remaining credit balance |
| `get_user_info()` | Get information about your account |
| `update_user_info(new_info)` | Update your account information |
| `gen_key(role)` | Generate a new API key |
| `del_key(key_to_delete)` | Delete an API key |

### Utilities

| Function | Description |
|---|---|
| `supported()` | List all 200+ Python modules available in the cloud runtime |
| `welcome()` | Print the getting-started guide |

---

## Supported Libraries

The cloud runtime comes pre-loaded with **200+ Python modules**, including:

- **Data science**: `numpy`, `pandas`, `statistics`
- **Databases**: `sqlalchemy`, `sqlite3`, `pymongo`, `pymysql`, `psycopg2`, `redis`
- **Networking**: `requests`, `urllib3`, `http`, `socket`
- **AWS**: `boto3`, `botocore`, `s3transfer`
- **AI / Agents**: `thoughtflow`
- **Serialization**: `json`, `csv`, `pickle`, `xml`
- **Standard library**: the full Python 3.12 stdlib

To see the complete list:

```python
from thoughtbase import supported
print(supported())
```

---

## How It Works

```
 Your Machine                        AWS Cloud
┌──────────────┐                  ┌──────────────────┐
│              │   deploy_agent   │                  │
│  Python code ├─────────────────►│  Stored as a     │
│  (string)    │                  │  serverless API  │
│              │                  │                  │
└──────────────┘                  └────────┬─────────┘
                                           │
┌──────────────┐                  ┌────────▼─────────┐
│              │   call_agent     │                  │
│  Any Python  ├─────────────────►│  Executes your   │
│  environment │◄─────────────────┤  function, sends │
│              │    result        │  back the result │
└──────────────┘                  └──────────────────┘
```

1. **You write** Python code — functions, classes, ThoughtFlow agents — as a string
2. **`deploy_agent`** sends it to a serverless backend (AWS Lambda behind API Gateway)
3. **The backend stores it** and returns an `agent_id`
4. **`call_agent`** invokes any function inside the deployed code by name
5. **The result** is returned as a Python object

There is no container to manage, no server to provision, and no cold start to
worry about.  Your code runs in a pre-warmed Python 3.12 environment with 200+
libraries already installed.

---

## Philosophy

ThoughtBase follows the same design principles as ThoughtFlow:

**Simple things should be simple.**
Deploying a function should be one line of code.  Calling it should be one line.
No configuration files, no build steps, no deployment ceremonies.

**Difficult things should be possible.**
Deploy complex multi-function agents that call external APIs, process data with
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

## Getting Access

ThoughtBase is currently in **prototype** phase.

To sign up for your **free API key** and **free credits**, connect with the
creator, James Rolfsen, on LinkedIn:

**[Connect on LinkedIn](https://www.linkedin.com/in/jamesrolfsen/)**

Depending on demand, there may be a waitlist to ensure safe and scalable
distribution of the service.

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

Copyright (c) 2025 Think.dev LLC

---

## Links

- **PyPI**: [pypi.org/project/thoughtbase](https://pypi.org/project/thoughtbase/)
- **GitHub**: [github.com/jrolf/thoughtbase](https://github.com/jrolf/thoughtbase)
- **Issues**: [github.com/jrolf/thoughtbase/issues](https://github.com/jrolf/thoughtbase/issues)
- **ThoughtFlow**: [github.com/jrolf/thoughtflow](https://github.com/jrolf/thoughtflow)
- **Contact**: james@think.dev
