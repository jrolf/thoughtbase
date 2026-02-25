# Changelog

All notable changes to ThoughtBase will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [0.0.4] - 2026-02-25

### Fixed
- README logo now uses absolute GitHub raw URL so it renders correctly on PyPI
- Added explicit HTTP request timeouts (10s connect, 120s read) to all API calls to prevent indefinite hangs

---

## [0.0.3] - 2026-02-24

### Added
- Secrets management: `set_secrets()`, `list_secrets()`, `delete_secrets()` for storing credentials server-side
- `secrets` parameter on `call_agent()` and `test_agent()` for passing request-level secrets per-call
- New README with secrets management docs, ThoughtFlow agent hero example, "Why ThoughtBase?" section, and use cases
- Example: `02_deploy_thoughtflow_agent.py` — deploy a real ThoughtFlow summarization agent
- Example: `03_secrets_and_llm_agent.py` — end-to-end secrets setup + LLM classification agent
- Example: `00_validate_endpoints.py` — end-to-end endpoint validation script

### Changed
- Exec endpoint migrated to `thoughtbase_exec_v01` (new API Gateway)
- README fully rewritten around AI agent deployment narrative

---

## [0.0.2] - 2025-02-23

### Added
- Initial release
- Core functions: `deploy_agent`, `update_agent`, `call_agent`, `test_agent`
- Agent management: `list_agents`, `get_agent_info`
- Account management: `get_balance`, `get_user_info`, `update_user_info`
- Key management: `gen_key`, `del_key`
- Utilities: `supported()`, `welcome()`
- `set_api_key()` for environment-based authentication
- 200+ supported Python modules in the cloud runtime (including `thoughtflow`)
- GitHub Actions workflow for automated PyPI publishing
- Comprehensive test suite with mocked HTTP calls
- Ruff linting and formatting configuration
- Full README with quick start, examples, and API reference

---

<!-- Release links -->
[Unreleased]: https://github.com/jrolf/thoughtbase/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/jrolf/thoughtbase/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/jrolf/thoughtbase/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/jrolf/thoughtbase/releases/tag/v0.0.2
