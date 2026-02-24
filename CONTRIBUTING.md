# Contributing to ThoughtBase

Thank you for your interest in contributing to ThoughtBase! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### First-Time Contributors

1. Look for issues labeled `good first issue` or `help wanted`
2. Comment on the issue to let others know you're working on it
3. Fork the repository and create a branch
4. Make your changes and submit a pull request

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/thoughtbase.git
cd thoughtbase
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install in editable mode with all dev dependencies
pip install -e ".[dev]"
```

### 4. Verify Setup

```bash
# Run tests
pytest tests/unit/ -v

# Run linter
ruff check src/ tests/

# Run formatter check
ruff format --check src/ tests/
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-batch-deploy` - New features
- `fix/key-fallback` - Bug fixes
- `docs/update-quickstart` - Documentation
- `refactor/simplify-request` - Refactoring

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Longer description if needed.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

---

## Pull Request Process

### 1. Before Submitting

- [ ] All tests pass: `pytest tests/unit/ -v`
- [ ] Code is formatted: `ruff format src/ tests/`
- [ ] Linter passes: `ruff check src/ tests/`
- [ ] Documentation is updated (if applicable)
- [ ] CHANGELOG.md is updated (for features/fixes)

### 2. PR Description

Include:

- **What**: Clear description of changes
- **Why**: Motivation and context
- **How**: Technical approach (if complex)
- **Testing**: How you verified the changes

### 3. Review Process

1. Automated checks run (CI)
2. Maintainer reviews code
3. Address any feedback
4. Once approved, maintainer merges

---

## Coding Standards

### Style Guide

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Format code
ruff format src/ tests/

# Check and fix lint issues
ruff check --fix src/ tests/
```

### Docstrings

Every public function and class must have a docstring explaining:

- What it does
- Key parameters
- Return behavior
- Example usage (when helpful)

### Import Organization

Imports are automatically organized by Ruff. The order is:

1. Standard library
2. Third-party packages
3. Local imports

---

## Testing Guidelines

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
└── unit/                # Fast, deterministic, no external dependencies
    └── test_core.py
```

### Running Tests

```bash
# All unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ -v --cov=src/thoughtbase --cov-report=html
```

### What Makes a Good Test

- **Deterministic**: Same result every time
- **Isolated**: No dependencies on other tests or external services
- **Fast**: Unit tests should run in milliseconds
- **Focused**: Test one thing per test
- **Readable**: Clear what's being tested

---

## Questions?

- Open an [Issue](https://github.com/jrolf/thoughtbase/issues) for bugs or feature requests
- Email maintainers: james@think.dev

Thank you for contributing to ThoughtBase!
