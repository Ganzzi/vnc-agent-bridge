# VNC Agent Bridge

[![Tests](https://github.com/github-copilot/vnc-agent-bridge/actions/workflows/tests.yml/badge.svg)](https://github.com/github-copilot/vnc-agent-bridge/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/github-copilot/vnc-agent-bridge/branch/main/graph/badge.svg)](https://codecov.io/gh/github-copilot/vnc-agent-bridge)
[![PyPI](https://img.shields.io/pypi/v/vnc-agent-bridge)](https://pypi.org/project/vnc-agent-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/vnc-agent-bridge)](https://pypi.org/project/vnc-agent-bridge/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Open-source Python package for AI agents to interact with VNC servers**

VNC Agent Bridge provides high-level abstractions for AI agents to control mouse, keyboard, and scroll operations on remote systems via VNC (Virtual Network Computing) protocol.

## ✨ Features

- **Mouse Control**: Click, move, drag, and position tracking
- **Keyboard Input**: Type text, press keys, hotkeys, key combinations
- **Scroll Control**: Scroll up/down at specific positions
- **Type Safety**: 100% mypy strict compliance
- **Flexible Timing**: Optional delay parameters for realistic agent behavior
- **Context Manager**: Automatic connection management
- **Zero Dependencies**: Uses only Python standard library

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install vnc-agent-bridge
```

### From Source
```bash
git clone https://github.com/github-copilot/vnc-agent-bridge.git
cd vnc-agent-bridge
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/github-copilot/vnc-agent-bridge.git
cd vnc-agent-bridge
pip install -e ".[dev]"
```

## 📖 Quick Start

### Basic Usage
```python
from vnc_agent_bridge import VNCAgentBridge

# Connect to VNC server
with VNCAgentBridge('localhost', port=5900) as vnc:
    # Mouse operations
    vnc.mouse.left_click(100, 100)
    vnc.mouse.move_to(200, 200)
    vnc.mouse.drag_to(300, 300, duration=1.0)

    # Keyboard operations
    vnc.keyboard.type_text("Hello, World!")
    vnc.keyboard.press_key('return')
    vnc.keyboard.hotkey('ctrl', 'a')

    # Scroll operations
    vnc.scroll.scroll_up(amount=3)
    vnc.scroll.scroll_down(amount=5)
```

### Manual Connection Management
```python
vnc = VNCAgentBridge('192.168.1.100', username='user', password='pass')
try:
    vnc.connect()
    # Perform operations...
    position = vnc.mouse.get_position()
    print(f"Mouse at: {position}")
finally:
    vnc.disconnect()
```

## 🎯 API Overview

### Mouse Controller
```python
vnc.mouse.left_click(x, y, delay=0)      # Single left click
vnc.mouse.right_click(x, y, delay=0)     # Right click
vnc.mouse.double_click(x, y, delay=0)    # Double click
vnc.mouse.move_to(x, y, delay=0)         # Move cursor
vnc.mouse.drag_to(x, y, duration=1.0, delay=0)  # Drag operation
vnc.mouse.get_position()                 # Get current position -> (x, y)
```

### Keyboard Controller
```python
vnc.keyboard.type_text(text, delay=0)    # Type string
vnc.keyboard.press_key(key, delay=0)     # Press single key
vnc.keyboard.hotkey(*keys, delay=0)      # Key combination
vnc.keyboard.keydown(key, delay=0)       # Hold key down
vnc.keyboard.keyup(key, delay=0)         # Release key
```

### Scroll Controller
```python
vnc.scroll.scroll_up(amount=3, delay=0)  # Scroll up
vnc.scroll.scroll_down(amount=3, delay=0)  # Scroll down
vnc.scroll.scroll_to(x, y, delay=0)      # Scroll at position
```

### Connection Management
```python
vnc = VNCAgentBridge(host, port=5900, username=None, password=None)
vnc.connect()                            # Connect to server
vnc.disconnect()                         # Disconnect from server
vnc.is_connected                         # Check connection status
```

## ⚙️ Configuration

### Connection Parameters
- `host`: VNC server hostname or IP address
- `port`: VNC server port (default: 5900)
- `username`: Optional authentication username
- `password`: Optional authentication password
- `timeout`: Connection timeout in seconds (default: 10.0)

### Delay Parameters
All methods support an optional `delay` parameter:
- `delay=0`: No delay (fast execution)
- `delay=0.1`: Quick operation (100ms)
- `delay=0.5`: Normal human-like timing
- `delay=1.0+`: Deliberate, careful interaction

## 🔧 Supported Keys

### Special Keys
- `'return'`, `'enter'`: Enter/Return key
- `'tab'`: Tab key
- `'escape'`, `'esc'`: Escape key
- `'backspace'`: Backspace key
- `'delete'`, `'del'`: Delete key
- `'space'`: Spacebar

### Function Keys
- `'f1'` through `'f12'`: Function keys

### Arrow Keys
- `'up'`, `'down'`, `'left'`, `'right'`: Arrow keys

### Modifiers
- `'shift'`: Shift key
- `'ctrl'`: Control key
- `'alt'`: Alt key
- `'cmd'`, `'meta'`: Command/Meta key

### Character Keys
- Single characters: `'a'`, `'A'`, `'1'`, `'!'`, etc.
- Unicode characters supported

## 🛠️ Development

### Prerequisites
- Python 3.8+
- uv (recommended) or pip

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/github-copilot/vnc-agent-bridge.git
cd vnc-agent-bridge

# Install development dependencies
uv pip install --system -e ".[dev]"

# Run tests
pytest

# Type checking
mypy vnc_agent_bridge --strict

# Linting
flake8 vnc_agent_bridge tests

# Formatting
black vnc_agent_bridge tests
```

### Testing Strategy
- **Mock-based testing**: No real VNC server required
- **85%+ coverage target**: Comprehensive test suite
- **Type safety**: 100% mypy strict compliance
- **Cross-platform**: Tests run on Linux, macOS, Windows

## 📚 Documentation

- [API Reference](docs/api/)
- [Usage Guides](docs/guides/)
- [Technical Design](docs/plan/TECHNICAL_DESIGN.md)
- [Implementation Checklist](docs/plan/IMPLEMENTATION_CHECKLIST.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with GitHub Copilot
- Inspired by the need for reliable AI agent automation
- Thanks to the VNC and RFB protocol specifications

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/github-copilot/vnc-agent-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/github-copilot/vnc-agent-bridge/discussions)
- **Documentation**: [Full Docs](https://github.com/github-copilot/vnc-agent-bridge#readme)

---

**Made with ❤️ by GitHub Copilot**