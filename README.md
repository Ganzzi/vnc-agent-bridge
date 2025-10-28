# VNC Agent Bridge

[![Coverage](https://codecov.io/gh/Ganzzi/vnc-agent-bridge/branch/main/graph/badge.svg)](https://codecov.io/gh/Ganzzi/vnc-agent-bridge)
[![PyPI](https://img.shields.io/pypi/v/vnc-agent-bridge)](https://pypi.org/project/vnc-agent-bridge/)
[![Python](https://img.shields.io/pypi/pyversions/vnc-agent-bridge)](https://pypi.org/project/vnc-agent-bridge/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Open-source Python package for AI agents to interact with VNC servers**

VNC Agent Bridge provides high-level abstractions for AI agents to control mouse, keyboard, and scroll operations on remote systems via VNC (Virtual Network Computing) protocol.

## ✨ Features

- **Mouse Control**: Click, move, drag, and position tracking
- **Keyboard Input**: Type text, press keys, hotkeys, key combinations
- **Scroll Control**: Scroll up/down at specific positions
- **Screenshot Capture**: Save screen images in multiple formats (PNG, JPEG, BMP)
- **Video Recording**: Record screen activity with configurable FPS
- **Clipboard Management**: Get, set, and clear clipboard text
- **WebSocket VNC Support**: Connect to WebSocket-based VNC servers with URL templates
- **Multiple Connection Types**: TCP and WebSocket connections with strategy pattern
- **Type Safety**: 100% mypy strict compliance
- **Flexible Timing**: Optional delay parameters for realistic agent behavior
- **Context Manager**: Automatic connection management
- **Enhanced Performance**: Framebuffer optimization for capture features
- **Optional Dependencies**: numpy, Pillow, and websocket-client for advanced features
- **Comprehensive Testing**: 85%+ code coverage with 300+ test cases
- **Zero Core Dependencies**: Uses only Python standard library (for core features)
- **Server-Agnostic**: Works with any WebSocket VNC server (Proxmox, noVNC, custom)

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install vnc-agent-bridge
```

### With WebSocket Support
```bash
pip install vnc-agent-bridge[websocket]
```

### With All Features
```bash
pip install vnc-agent-bridge[full]
```

### With WebSocket Support
```bash
pip install vnc-agent-bridge[websocket]
```

### From Source
```bash
git clone https://github.com/Ganzzi/vnc-agent-bridge.git
cd vnc-agent-bridge
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/Ganzzi/vnc-agent-bridge.git
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

    # Screenshot capture
    screenshot = vnc.screenshot.capture()
    vnc.screenshot.save_image("screen.png")

    # Video recording
    vnc.video.start_recording(fps=10)
    # ... perform actions ...
    vnc.video.stop_recording()

    # Clipboard operations
    vnc.clipboard.send_text("Copied text!")
    text = vnc.clipboard.get_text()
```

### WebSocket VNC Connection
```python
from vnc_agent_bridge import create_websocket_vnc

# Connect to WebSocket VNC server (e.g., Proxmox)
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?port=${vnc_port}&vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    vnc_port=5900,
    ticket="vncticket123"
)

with bridge:
    bridge.mouse.move_to(100, 100)
    bridge.keyboard.type_text("Hello WebSocket VNC!")
    screenshot = bridge.screenshot.capture()
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

### Screenshot Controller
```python
vnc.screenshot.capture(incremental=False, delay=0)  # Capture screen -> np.ndarray
vnc.screenshot.save_image(path, format='PNG', delay=0)  # Save to file
vnc.screenshot.capture_region(x, y, width, height, delay=0)  # Region capture
```

### Video Controller
```python
vnc.video.start_recording(fps=10, duration=None)  # Start recording
vnc.video.stop_recording()  # Stop and save video
vnc.video.record_for(duration=5.0, fps=10)  # Record for time period
vnc.video.get_recording_status()  # Check recording state
```

### Clipboard Controller
```python
vnc.clipboard.send_text(text, delay=0)  # Send text to clipboard
vnc.clipboard.get_text()  # Get clipboard content -> str
vnc.clipboard.clear()  # Clear clipboard
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
git clone https://github.com/Ganzzi/vnc-agent-bridge.git
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
- **85%+ coverage target**: Comprehensive test suite with 130+ test cases
- **Type safety**: 100% mypy strict compliance
- **Cross-platform**: Tests run on Linux, macOS, Windows

### Current Project Status
- ✅ **v0.1.0**: Core functionality released on PyPI
- ✅ **v0.2.0**: Stable release with capture features on PyPI and GitHub
- ✅ **v0.3.0**: WebSocket VNC support and modular architecture on PyPI and GitHub
- ✅ **v0.3.0 Fixes**: Screenshot format errors fixed, WebSocket authentication corrected
- 🎯 **v0.3.0 Features**: WebSocket connections, URL templates, server-agnostic design
-  **Next Milestone**: Community feedback and future enhancements

### Quality Metrics
- **Test Coverage**: 85% (391 statements, 59 missed)
- **Type Checking**: 100% mypy strict compliance (0 errors)
- **Linting**: 0 flake8 errors
- **Formatting**: 100% black compliant
- **Test Cases**: 303 total (303 passing, 100% pass rate)

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

- Built with Ganzzi
- Inspired by the need for reliable AI agent automation
- Thanks to the VNC and RFB protocol specifications

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Ganzzi/vnc-agent-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ganzzi/vnc-agent-bridge/discussions)
- **Documentation**: [Full Docs](https://github.com/Ganzzi/vnc-agent-bridge#readme)

---

**Made with ❤️ by Ganzzi**