# Contributing to VNC Agent Bridge

Thank you for your interest in contributing to VNC Agent Bridge! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## 🤝 Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- uv (recommended) or pip
- Git

### Quick Setup
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/vnc-agent-bridge.git
cd vnc-agent-bridge

# Install development dependencies
uv pip install --system -e ".[dev]"

# Run tests to ensure everything works
pytest
```

## 🛠️ Development Setup

### 1. Fork the Repository
Click the "Fork" button on GitHub to create your own copy of the repository.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/vnc-agent-bridge.git
cd vnc-agent-bridge
```

### 3. Set Up Development Environment
```bash
# Install uv (if not already installed)
pip install uv

# Install the package in development mode with all dependencies
uv pip install --system -e ".[dev]"

# Verify installation
python -c "import vnc_agent_bridge; print('Installation successful!')"
```

### 4. Run Initial Checks
```bash
# Run tests
pytest

# Type checking
mypy vnc_agent_bridge --strict

# Linting
flake8 vnc_agent_bridge tests

# Formatting check
black vnc_agent_bridge tests --check
```

## 🔄 Development Workflow

### 1. Choose an Issue
- Check [GitHub Issues](https://github.com/github-copilot/vnc-agent-bridge/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Feature Branch
```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Your Changes
- Write code following our [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Your Changes
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new feature description

- What was changed
- Why it was changed
- Any breaking changes
"

# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create a Pull Request
- Go to the original repository on GitHub
- Click "New Pull Request"
- Select your branch and fill out the PR template
- Wait for review and address any feedback

## 💻 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters (Black default)

### Type Hints
- **100% type coverage required**
- Use strict mypy mode
- No implicit `Any` types
- Use `from __future__ import annotations` for forward references

### Naming Conventions
```python
# Classes
class MouseController:
    pass

# Functions and methods
def left_click(self, x: int, y: int) -> None:
    pass

# Variables
mouse_position = (100, 200)
max_retries = 3

# Constants
DEFAULT_DELAY = 0.1
BUTTON_LEFT = 1
```

### Imports
```python
# Standard library imports first
import time
from typing import Optional, Tuple

# Third-party imports (none in this project)

# Local imports
from .connection import VNCConnection
from .exceptions import VNCInputError
```

### Error Handling
```python
# Use specific exception types
def validate_coordinates(self, x: int, y: int) -> None:
    if x < 0 or y < 0:
        raise VNCInputError(f"Coordinates must be non-negative: ({x}, {y})")
```

## 🧪 Testing

### Test Structure
- Tests go in `tests/` directory
- One test file per module: `test_mouse.py`, `test_keyboard.py`, etc.
- Test class names: `TestMouseController`, `TestKeyboardController`
- Test method names: `test_left_click_valid_coords`

### Writing Tests
```python
import pytest
from unittest.mock import Mock
from vnc_agent_bridge.core.mouse import MouseController

class TestMouseController:
    def test_left_click_at_position(self, mock_connection):
        """Test left click at specific coordinates."""
        controller = MouseController(mock_connection)
        controller.left_click(100, 100)

        # Verify the connection was called correctly
        mock_connection.send.assert_called_once()

    def test_left_click_negative_coords_raises_error(self, mock_connection):
        """Test that negative coordinates raise VNCInputError."""
        controller = MouseController(mock_connection)

        with pytest.raises(VNCInputError):
            controller.left_click(-1, 100)
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mouse.py

# Run specific test
pytest tests/test_mouse.py::TestMouseController::test_left_click

# Run with coverage
pytest --cov=vnc_agent_bridge --cov-report=html

# Run failed tests only
pytest --lf
```

### Coverage Requirements
- Overall coverage: 85%+
- Core modules: 90%+
- Public API: 100%
- Exception handling: 100%

## 📚 Documentation

### Code Documentation
- All public functions/methods must have docstrings
- Use Google-style docstrings
- Include type information in docstrings
- Document parameters, return values, and exceptions

```python
def left_click(self, x: Optional[int] = None, y: Optional[int] = None, delay: float = 0) -> None:
    """Perform a left mouse button click.

    Args:
        x: X coordinate for click. If None, uses current mouse position.
        y: Y coordinate for click. If None, uses current mouse position.
        delay: Delay in seconds before performing the click.

    Raises:
        VNCInputError: If coordinates are invalid.
        VNCStateError: If not connected to VNC server.
    """
```

### Documentation Updates
- Update README.md for new features
- Add examples to docs/guides/
- Update API documentation
- Update CHANGELOG.md

## 📝 Submitting Changes

### Pull Request Process
1. **Ensure tests pass**: All tests must pass locally
2. **Type checking**: `mypy vnc_agent_bridge --strict` passes
3. **Linting**: `flake8 vnc_agent_bridge tests` passes
4. **Formatting**: `black vnc_agent_bridge tests --check` passes
5. **Coverage**: Maintain or improve coverage
6. **Documentation**: Update docs for any API changes

### PR Template
Please fill out the PR template completely:
- Description of changes
- Type of change (bug fix, feature, documentation, etc.)
- Breaking changes (if any)
- Testing done
- Screenshots (if UI changes)

### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, package version
- **Error messages**: Full traceback if applicable
- **Code sample**: Minimal code to reproduce the issue

### Feature Requests
For new features, please include:
- **Use case**: Why do you need this feature?
- **Proposed API**: How should it work?
- **Alternatives**: Have you considered other approaches?
- **Additional context**: Screenshots, examples, etc.

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and stability improvements
- Performance optimizations
- Additional test coverage
- Documentation improvements

### Medium Priority
- New VNC protocol features
- Enhanced error handling
- International keyboard support
- Async/await support

### Future Enhancements
- Screen capture capabilities
- Image recognition helpers
- Multi-monitor support
- Connection pooling

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check docs/ for detailed guides

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub's contributor insights
- Release notes

Thank you for contributing to VNC Agent Bridge! 🚀