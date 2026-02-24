"""
ThoughtBase core module.

Contains all public functions for deploying, managing, and calling
ThoughtFlow agents (or any Python code) as serverless cloud APIs.
"""

import os

import requests


# ---------------------------------------------------------------------------
# Backend endpoints (AWS API Gateway -> Lambda)
# ---------------------------------------------------------------------------

_ADMIN_FUNC = "apimagic_admin_v02"       # not yet migrated
_EXEC_FUNC = "thoughtbase_exec_v01"

_SUFFIX = ".amazonaws.com/prod/invoke"
_ADMIN_URL = "https://9fwiqamsta.execute-api.us-east-1" + _SUFFIX
_EXEC_URL = "https://bdxwb8xftj.execute-api.us-east-1" + _SUFFIX

# Environment variable used to store the user's API key
_ENV_KEY = "THB_API_KEY"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_key(key=""):
    """Return the API key to use for a request.

    If *key* is provided it is returned as-is.  Otherwise the value of
    the ``THB_API_KEY`` environment variable is used.

    Parameters
    ----------
    key : str, optional
        Explicit API key.  Defaults to ``""``.

    Returns
    -------
    str
        The resolved API key.
    """
    if key == "":
        key = os.getenv(_ENV_KEY, "")
    return key


def _admin_request(key, request):
    """Send a request to the admin backend and return the response.

    This is the low-level transport used by every management function
    (deploy, list, update, user info, keys, balance, etc.).

    Parameters
    ----------
    key : str
        API key for authentication.
    request : dict
        The request payload describing the operation.

    Returns
    -------
    dict or str
        The ``output.response`` value from the backend, or the raw
        JSON response if parsing fails.
    """
    body = {"api_key": key, "request": request}
    response = requests.post(_ADMIN_URL, json=body)
    data = response.json()
    try:
        return data["output"]["response"]
    except Exception:
        return data


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def set_api_key(user_key):
    """Store your ThoughtBase API key in the environment.

    Once set, every subsequent function call will use this key
    automatically so you don't have to pass it each time.

    Parameters
    ----------
    user_key : str
        Your ThoughtBase API key.

    Example
    -------
    >>> from thoughtbase import set_api_key
    >>> set_api_key("tb-abc123...")
    """
    os.environ[_ENV_KEY] = user_key


# ---------------------------------------------------------------------------
# Agent deployment and management
# ---------------------------------------------------------------------------


def deploy_agent(code="", info=None, key=""):
    """Deploy Python code as a new serverless agent.

    The *code* argument is a string of valid Python.  The backend stores
    it and returns metadata including an ``agent_id`` that you use to
    call the agent later.

    Parameters
    ----------
    code : str, optional
        Python source code to deploy.
    info : dict, optional
        Arbitrary metadata to attach to the agent.
    key : str, optional
        API key.  Falls back to the ``THB_API_KEY`` environment variable.

    Returns
    -------
    dict
        Response from the backend, typically containing ``agent_id``.

    Example
    -------
    >>> code = "def greet(name): return f'Hello, {name}!'"
    >>> result = deploy_agent(code, key="tb-abc123...")
    >>> print(result["api_id"])
    """
    if info is None:
        info = {}
    key = _resolve_key(key)
    request = {"func_name": "deploy_api"}
    if len(code) > 0:
        request["code"] = code
    if len(info) > 0:
        request["info"] = info
    return _admin_request(key, request)


def update_agent(agent_id, code="", info=None, key=""):
    """Update the code or metadata of an existing agent.

    Parameters
    ----------
    agent_id : str
        The ID of the agent to update.
    code : str, optional
        New Python source code.
    info : dict, optional
        New metadata to attach.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Response from the backend.
    """
    if info is None:
        info = {}
    key = _resolve_key(key)
    request = {"func_name": "update_api", "api_id": agent_id}
    if len(code) > 0:
        request["code"] = code
    if len(info) > 0:
        request["info"] = info
    return _admin_request(key, request)


def list_agents(user_id="", key=""):
    """List all agents you have deployed.

    Parameters
    ----------
    user_id : str, optional
        Restrict listing to a specific user (admin use).
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    list or dict
        List of deployed agent records, or error dict.
    """
    key = _resolve_key(key)
    request = {"func_name": "list_apis"}
    if user_id != "":
        request["user_id"] = user_id
    return _admin_request(key, request)


def get_agent_info(agent_id, key=""):
    """Get metadata about a deployed agent.

    Parameters
    ----------
    agent_id : str
        The ID of the agent to inspect.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Agent metadata from the backend.
    """
    key = _resolve_key(key)
    request = {"func_name": "get_api_info", "api_id": agent_id}
    return _admin_request(key, request)


# ---------------------------------------------------------------------------
# Execution and testing
# ---------------------------------------------------------------------------


def test_agent(code, fname, input_obj=None, key="", full=False,
               secrets=None):
    """Execute code on the cloud without deploying it.

    This is a one-shot test run.  The code is sent to the serverless
    backend, the function named *fname* is called with *input_obj*,
    and the result is returned.

    Parameters
    ----------
    code : str
        Python source code containing the target function.
    fname : str
        Name of the function to call inside *code*.
    input_obj : object, optional
        Argument passed to the function.  Defaults to ``{}``.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.
    full : bool, optional
        If ``True``, return the full backend response instead of just
        the result value.
    secrets : dict, optional
        Request-level secrets to inject into the sandbox for this call.
        These are merged with any stored secrets (and override on name
        collision).  Useful for passing credentials at call time.

    Returns
    -------
    object
        The return value of the called function, or the full response
        dict when *full* is ``True``.

    Example
    -------
    >>> code = "def double(n): return n * 2"
    >>> test_agent(code, "double", 21)
    42
    """
    if input_obj is None:
        input_obj = {}
    key = _resolve_key(key)
    body = {
        "api_key": key,
        "code": code,
        "fname": fname,
        "input": input_obj,
    }
    if secrets is not None:
        body["secrets"] = secrets
    res = requests.post(_EXEC_URL, json=body).json()
    if full:
        return res
    try:
        return res["output"]["result"]
    except Exception:
        return res


def call_agent(agent_id, fname, input_obj=None, key="", full=False,
               secrets=None):
    """Call a function inside a deployed agent.

    Parameters
    ----------
    agent_id : str
        The ID returned by :func:`deploy_agent`.
    fname : str
        Name of the function to call.
    input_obj : object, optional
        Argument passed to the function.  Defaults to ``{}``.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.
    full : bool, optional
        If ``True``, return the full backend response.
    secrets : dict, optional
        Request-level secrets to inject into the sandbox for this call.
        These are merged with any stored secrets (and override on name
        collision).  Useful for passing credentials at call time without
        persisting them.

    Returns
    -------
    object
        The return value of the called function, or the full response
        dict when *full* is ``True``.

    Example
    -------
    >>> result = call_agent("agent-abc123", "greet", "World")
    >>> print(result)
    'Hello, World!'
    """
    if input_obj is None:
        input_obj = {}
    key = _resolve_key(key)
    body = {
        "api_key": key,
        "api_id": agent_id,
        "fname": fname,
        "encoded": 1,
        "zipped": 0,
        "input": input_obj,
    }
    if secrets is not None:
        body["secrets"] = secrets
    res = requests.post(_EXEC_URL, json=body).json()
    if full:
        return res
    try:
        return res["output"]["result"]
    except Exception:
        return res


# ---------------------------------------------------------------------------
# Account and key management
# ---------------------------------------------------------------------------


def get_balance(user_id="", key=""):
    """Check your remaining credit balance.

    Parameters
    ----------
    user_id : str, optional
        User to check (admin use).  Defaults to the authenticated user.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Balance information.
    """
    key = _resolve_key(key)
    request = {"func_name": "get_balance"}
    if user_id != "":
        request["user_id"] = user_id
    return _admin_request(key, request)


def get_user_info(user_id="", key=""):
    """Get information about your account.

    Parameters
    ----------
    user_id : str, optional
        User to look up (admin use).  Defaults to the authenticated user.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        User account information.
    """
    key = _resolve_key(key)
    request = {"func_name": "get_user_info"}
    if user_id != "":
        request["user_id"] = user_id
    return _admin_request(key, request)


def update_user_info(new_info, user_id="", key=""):
    """Update your account information.

    Parameters
    ----------
    new_info : dict
        Fields to update.
    user_id : str, optional
        Target user (admin use).  Defaults to the authenticated user.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Confirmation from the backend.
    """
    key = _resolve_key(key)
    request = {"func_name": "update_user_info", "user_info": new_info}
    if user_id != "":
        request["user_id"] = user_id
    return _admin_request(key, request)


def gen_key(role="", user_id="", key=""):
    """Generate a new API key.

    Parameters
    ----------
    role : str, optional
        Role for the new key (e.g. ``"CREATOR"``).
    user_id : str, optional
        Target user (admin use).
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        The newly generated key details.
    """
    key = _resolve_key(key)
    request = {"func_name": "gen_key"}
    if role != "":
        request["role"] = role
    if user_id != "":
        request["user_id"] = user_id
    return _admin_request(key, request)


def del_key(key_to_delete, key=""):
    """Delete an API key.

    Parameters
    ----------
    key_to_delete : str
        The key to revoke.
    key : str, optional
        API key used for authentication.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Confirmation from the backend.
    """
    key = _resolve_key(key)
    request = {"func_name": "del_key", "key_to_delete": key_to_delete}
    return _admin_request(key, request)


# ---------------------------------------------------------------------------
# Secrets management
# ---------------------------------------------------------------------------


def set_secrets(secrets, key=""):
    """Store one or more secrets in your account.

    Secrets are key-value pairs persisted server-side and automatically
    injected into every code execution sandbox as a ``SECRETS`` dict.
    This is the recommended way to provide LLM API keys, database
    credentials, and other sensitive values to your deployed agents
    without embedding them in code.

    Existing secret names are overwritten; new names are created.
    Values must be strings.

    Parameters
    ----------
    secrets : dict
        Mapping of secret names to secret values, e.g.
        ``{"OPENAI_API_KEY": "sk-...", "DB_URL": "postgres://..."}``.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Confirmation with the list of stored names, e.g.
        ``{"stored": ["OPENAI_API_KEY", "DB_URL"]}``.

    Example
    -------
    >>> from thoughtbase import set_secrets
    >>> set_secrets({"OPENAI_API_KEY": "sk-abc123..."})
    {'stored': ['OPENAI_API_KEY']}
    """
    key = _resolve_key(key)
    request = {"func_name": "set_secrets", "secrets": secrets}
    return _admin_request(key, request)


def list_secrets(key=""):
    """List the names of your stored secrets.

    Returns secret **names only** — values are never exposed through
    this endpoint.  Secret values are only accessible inside the
    execution sandbox via the ``SECRETS`` dict.

    Parameters
    ----------
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        A dict with a ``secret_names`` key, e.g.
        ``{"secret_names": ["OPENAI_API_KEY", "DB_URL"]}``.

    Example
    -------
    >>> from thoughtbase import list_secrets
    >>> list_secrets()
    {'secret_names': ['OPENAI_API_KEY', 'DB_URL']}
    """
    key = _resolve_key(key)
    request = {"func_name": "list_secrets"}
    return _admin_request(key, request)


def delete_secrets(names, key=""):
    """Delete one or more secrets by name.

    Only secrets that actually existed are reported as deleted.

    Parameters
    ----------
    names : list
        List of secret name strings to remove.
    key : str, optional
        API key.  Falls back to ``THB_API_KEY``.

    Returns
    -------
    dict
        Confirmation with the names that were deleted, e.g.
        ``{"deleted": ["OPENAI_API_KEY"]}``.

    Example
    -------
    >>> from thoughtbase import delete_secrets
    >>> delete_secrets(["OPENAI_API_KEY"])
    {'deleted': ['OPENAI_API_KEY']}
    """
    key = _resolve_key(key)
    request = {"func_name": "delete_secrets", "names": names}
    return _admin_request(key, request)


# ---------------------------------------------------------------------------
# Supported libraries
# ---------------------------------------------------------------------------

SUPPORTED = [
    "abc",
    "aifc",
    "argparse",
    "array",
    "ast",
    "asyncio",
    "atexit",
    "audioop",
    "awslambdaric",
    "base64",
    "bdb",
    "binascii",
    "bisect",
    "bootstrap",
    "boto3",
    "botocore",
    "bson",
    "builtins",
    "bz2",
    "cProfile",
    "calendar",
    "certifi",
    "cgi",
    "cgitb",
    "charset_normalizer",
    "chunk",
    "cmath",
    "cmd",
    "code",
    "codecs",
    "codeop",
    "collections",
    "colorsys",
    "compileall",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "copyreg",
    "crypt",
    "csv",
    "ctypes",
    "curses",
    "dataclasses",
    "datetime",
    "dateutil",
    "dbm",
    "decimal",
    "difflib",
    "dill",
    "dis",
    "doctest",
    "email",
    "encodings",
    "ensurepip",
    "enum",
    "errno",
    "faulthandler",
    "fcntl",
    "filecmp",
    "fileinput",
    "fnmatch",
    "fractions",
    "ftplib",
    "functools",
    "gc",
    "genericpath",
    "getopt",
    "getpass",
    "gettext",
    "glob",
    "graphlib",
    "gridfs",
    "grp",
    "gzip",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "idlelib",
    "idna",
    "imaplib",
    "imghdr",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "itertools",
    "jmespath",
    "json",
    "keyword",
    "lib2to3",
    "linecache",
    "locale",
    "logging",
    "lzma",
    "mailbox",
    "mailcap",
    "marshal",
    "math",
    "mimetypes",
    "mmap",
    "modulefinder",
    "multiprocessing",
    "netrc",
    "nntplib",
    "ntpath",
    "nturl2path",
    "numbers",
    "numpy",
    "opcode",
    "operator",
    "optparse",
    "os",
    "ossaudiodev",
    "pandas",
    "pathlib",
    "pdb",
    "pickle",
    "pickletools",
    "pip",
    "pipes",
    "pkgutil",
    "platform",
    "plistlib",
    "poplib",
    "posix",
    "posixpath",
    "pprint",
    "profile",
    "pstats",
    "psycopg2",
    "pty",
    "pwd",
    "py_compile",
    "pyclbr",
    "pydoc",
    "pydoc_data",
    "pyexpat",
    "pymongo",
    "pymysql",
    "pytz",
    "queue",
    "quopri",
    "random",
    "re",
    "readline",
    "redis",
    "reprlib",
    "requests",
    "resource",
    "rlcompleter",
    "runpy",
    "runtime_client",
    "s3transfer",
    "sched",
    "secrets",
    "select",
    "selectors",
    "shelve",
    "shlex",
    "shutil",
    "signal",
    "simplejson",
    "site",
    "six",
    "smtplib",
    "snapshot_restore_py",
    "sndhdr",
    "socket",
    "socketserver",
    "spwd",
    "sqlalchemy",
    "sqlite3",
    "sre_compile",
    "sre_constants",
    "sre_parse",
    "ssl",
    "stat",
    "statistics",
    "string",
    "stringprep",
    "struct",
    "subprocess",
    "sunau",
    "symtable",
    "sys",
    "sysconfig",
    "syslog",
    "tabnanny",
    "tarfile",
    "telnetlib",
    "tempfile",
    "termios",
    "test",
    "textwrap",
    "thoughtflow",
    "threading",
    "time",
    "timeit",
    "token",
    "tokenize",
    "tomllib",
    "trace",
    "traceback",
    "tracemalloc",
    "tty",
    "types",
    "typing",
    "typing_extensions",
    "tzdata",
    "unicodedata",
    "unittest",
    "urllib",
    "urllib3",
    "uu",
    "uuid",
    "venv",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "wsgiref",
    "xdrlib",
    "xml",
    "xmlrpc",
    "xxlimited",
    "xxlimited_35",
    "xxsubtype",
    "zipapp",
    "zipfile",
    "zipimport",
    "zlib",
]


def supported():
    """Return the list of Python libraries available in the cloud runtime.

    The serverless backend comes pre-loaded with 200+ modules including
    the full Python standard library plus popular third-party packages
    such as ``numpy``, ``pandas``, ``requests``, ``boto3``,
    ``thoughtflow``, and many more.

    Returns
    -------
    list[str]
        Sorted list of importable module names.

    Example
    -------
    >>> from thoughtbase import supported
    >>> "thoughtflow" in supported()
    True
    """
    return SUPPORTED


# ---------------------------------------------------------------------------
# Welcome / onboarding
# ---------------------------------------------------------------------------

WELCOME = """
================================================================================
  THOUGHTBASE — Deploy ThoughtFlow Agents to the Cloud
================================================================================

Welcome to ThoughtBase — the cloud deployment layer for ThoughtFlow.

Build AI agents locally with ThoughtFlow, then deploy them as serverless
cloud APIs with a single function call.  No Docker, no Terraform, no YAML.
Just Python.

--------------------------------------------------------------------------------
  GET ACCESS
--------------------------------------------------------------------------------

Connect with the creator, James Rolfsen, on LinkedIn for your FREE API key
and starter credits:

    https://www.linkedin.com/in/jamesrolfsen/

--------------------------------------------------------------------------------
  QUICK START
--------------------------------------------------------------------------------

  1. Set your API key:

    from thoughtbase import set_api_key
    set_api_key("your-key-here")

  2. Deploy an agent:

    from thoughtbase import deploy_agent
    code = "def greet(name): return f'Hello, {name}!'"
    result = deploy_agent(code)

  3. Call it from anywhere:

    from thoughtbase import call_agent
    output = call_agent(result["api_id"], "greet", "World")
    print(output)  # -> Hello, World!

--------------------------------------------------------------------------------
  SECRETS MANAGEMENT
--------------------------------------------------------------------------------

Store LLM API keys and credentials securely — they are automatically
injected into your agent's sandbox at runtime:

    from thoughtbase import set_secrets
    set_secrets({"OPENAI_API_KEY": "sk-..."})

Inside your deployed code, access them via the SECRETS dict:

    openai.api_key = SECRETS["OPENAI_API_KEY"]

--------------------------------------------------------------------------------
  CLOUD RUNTIME
--------------------------------------------------------------------------------

Pre-warmed Python 3.12 with 200+ modules including:

    thoughtflow, numpy, pandas, requests, boto3, sqlalchemy,
    pymongo, redis, psycopg2, and the full standard library.

Run `supported()` to see the complete list.

--------------------------------------------------------------------------------
  LINKS
--------------------------------------------------------------------------------

    PyPI:       https://pypi.org/project/thoughtbase/
    GitHub:     https://github.com/jrolf/thoughtbase
    ThoughtFlow https://github.com/jrolf/thoughtflow
    Contact:    james@think.dev

================================================================================
"""


def welcome():
    """Print the ThoughtBase welcome message and getting-started guide.

    Displays sign-up instructions, a quick-start example, supported
    libraries overview, and contact information.

    Example
    -------
    >>> from thoughtbase import welcome
    >>> welcome()
    """
    print(WELCOME)
