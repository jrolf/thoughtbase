# Changelog

All notable changes to ThoughtBase will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Fixed
- Nothing yet

---

## [0.1.0] - 2025-02-23

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
[Unreleased]: https://github.com/jrolf/thoughtbase/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jrolf/thoughtbase/releases/tag/v0.1.0
