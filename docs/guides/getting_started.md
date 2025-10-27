# Getting Started with VNC Agent Bridge

Welcome to VNC Agent Bridge! This guide will help you get up and running with the library in minutes.

## Installation

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

## Requirements

- **Python:** 3.8 or higher
- **VNC Server:** Running and accessible
- **Network:** TCP connection to VNC server (default port 5900)

## Quick Start (2 minutes)

### Basic Example

The simplest way to use VNC Agent Bridge:

```python
from vnc_agent_bridge import VNCAgentBridge

# Connect using context manager (auto-cleanup)
with VNCAgentBridge('localhost', port=5900) as vnc:
    # Click at position
    vnc.mouse.left_click(100, 100)
    
    # Type text
    vnc.keyboard.type_text("Hello World")
    
    # Scroll down
    vnc.scroll.scroll_down(amount=3)
```

That's it! The connection is automatically closed when exiting the `with` block.

### Manual Connection Management

```python
from vnc_agent_bridge import VNCAgentBridge

vnc = VNCAgentBridge('localhost', port=5900)
try:
    vnc.connect()
    vnc.mouse.left_click(100, 100)
finally:
    vnc.disconnect()
```

## Common Use Cases

### Fill Out a Form

```python
with VNCAgentBridge('localhost') as vnc:
    # Click on name field
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.type_text("John Doe")
    
    # Click on email field
    vnc.mouse.left_click(100, 150)
    vnc.keyboard.type_text("john@example.com")
    
    # Click submit button
    vnc.mouse.left_click(200, 300)
```

### Navigate a Website

```python
with VNCAgentBridge('localhost') as vnc:
    # Focus address bar
    vnc.keyboard.hotkey("ctrl", "l")
    
    # Type URL
    vnc.keyboard.type_text("example.com")
    
    # Navigate
    vnc.keyboard.press_key("return")
    
    # Scroll to see content
    vnc.scroll.scroll_down(amount=5)
```

### Copy and Paste

```python
with VNCAgentBridge('localhost') as vnc:
    # Select all
    vnc.keyboard.hotkey("ctrl", "a")
    
    # Copy
    vnc.keyboard.hotkey("ctrl", "c")
    
    # Click another field
    vnc.mouse.left_click(300, 200)
    
    # Paste
    vnc.keyboard.hotkey("ctrl", "v")
```

## Key Concepts

### Connection Parameters

```python
# Host (required)
vnc = VNCAgentBridge('localhost')        # Local machine
vnc = VNCAgentBridge('192.168.1.100')    # LAN IP
vnc = VNCAgentBridge('vnc.example.com')  # Hostname

# Port (optional, default 5900)
vnc = VNCAgentBridge('host', port=5900)   # Standard
vnc = VNCAgentBridge('host', port=5901)   # Display :1

# Timeout (optional, default 10 seconds)
vnc = VNCAgentBridge('host', timeout=30.0)  # Longer timeout

# Authentication (if required)
vnc = VNCAgentBridge('host', username='user', password='pass')
```

### Timing Control

All operations support an optional `delay` parameter for timing:

```python
# Fast (no delay)
vnc.mouse.left_click(100, 100, delay=0)

# Quick (100ms)
vnc.mouse.left_click(100, 100, delay=0.1)

# Human-like (500ms)
vnc.mouse.left_click(100, 100, delay=0.5)

# Deliberate (1+ second)
vnc.mouse.left_click(100, 100, delay=1.0)
```

### Controllers

Three main controllers available:

```python
# Mouse/Pointer operations
vnc.mouse.left_click(100, 100)
vnc.mouse.move_to(200, 200)
vnc.mouse.drag_to(300, 300, duration=1.0)

# Keyboard input
vnc.keyboard.type_text("text")
vnc.keyboard.press_key("return")
vnc.keyboard.hotkey("ctrl", "a")

# Scroll wheel
vnc.scroll.scroll_up(amount=5)
vnc.scroll.scroll_down(amount=3)
```

## Error Handling

### Basic Error Handling

```python
from vnc_agent_bridge import VNCException, VNCConnectionError

try:
    with VNCAgentBridge('invalid-host') as vnc:
        vnc.mouse.left_click(100, 100)
except VNCConnectionError as e:
    print(f"Failed to connect: {e}")
except VNCException as e:
    print(f"VNC error: {e}")
```

### Common Error Types

```python
from vnc_agent_bridge import (
    VNCConnectionError,   # Connection failed
    VNCTimeoutError,      # Operation timed out
    VNCInputError,        # Invalid input (e.g., bad coordinates)
    VNCStateError,        # Wrong state (e.g., not connected)
)

try:
    vnc.mouse.left_click(-1, 100)  # Invalid coordinate
except VNCInputError as e:
    print(f"Invalid input: {e}")
```

## Workflow Examples

### Search and Click

```python
with VNCAgentBridge('localhost') as vnc:
    import time
    
    # Click search box
    vnc.mouse.left_click(400, 50)
    
    # Type search query
    vnc.keyboard.type_text("python vnc", delay=0.05)
    
    # Press Enter
    vnc.keyboard.press_key("return")
    
    # Wait for results
    time.sleep(2)
    
    # Click first result
    vnc.mouse.left_click(300, 200)
```

### Multi-Step Task

```python
with VNCAgentBridge('localhost') as vnc:
    # Step 1: Find and open menu
    vnc.keyboard.hotkey("alt", "f")  # File menu
    
    # Step 2: Click option
    vnc.mouse.left_click(100, 100)
    
    # Step 3: Fill form
    vnc.keyboard.type_text("input data")
    
    # Step 4: Submit
    vnc.keyboard.press_key("return")
```

### Keyboard Shortcuts

```python
with VNCAgentBridge('localhost') as vnc:
    # Select all text
    vnc.keyboard.hotkey("ctrl", "a")
    
    # Copy
    vnc.keyboard.hotkey("ctrl", "c")
    
    # Undo (if needed)
    vnc.keyboard.hotkey("ctrl", "z")
    
    # Redo
    vnc.keyboard.hotkey("ctrl", "y")
    
    # Save
    vnc.keyboard.hotkey("ctrl", "s")
```

## Testing Without Real Server

For development and testing without a real VNC server, check out the error_handling.py example which demonstrates error recovery patterns that work without a VNC connection.

## Next Steps

- **[Mouse Control Guide](mouse_control.md)** - Detailed mouse operations
- **[Keyboard Input Guide](keyboard_input.md)** - Detailed keyboard operations
- **[Scrolling Guide](scrolling.md)** - Detailed scroll operations
- **[Advanced Guide](advanced.md)** - Complex workflows and patterns
- **[API Reference](../api/)** - Complete API documentation

## Troubleshooting

### Connection Refused
- Check VNC server is running
- Verify host and port are correct
- Check firewall isn't blocking connection

### Timeout
- Increase timeout parameter: `VNCAgentBridge('host', timeout=30.0)`
- Check network connectivity
- Verify VNC server is responding

### Invalid Coordinates
- Coordinates must be non-negative
- Use `vnc.mouse.get_position()` to check current position
- Verify coordinates are within screen bounds

### Key Not Found
- Check key name spelling
- Refer to [Keyboard Input Guide](keyboard_input.md) for supported keys
- Use single character for alphanumeric keys

## Support

- **Documentation:** See [API Reference](../api/) and [Guides](.)
- **Issues:** Report on [GitHub Issues](https://github.com/github-copilot/vnc-agent-bridge/issues)
- **Questions:** Ask on [GitHub Discussions](https://github.com/github-copilot/vnc-agent-bridge/discussions)

## What's Next?

You're ready to use VNC Agent Bridge! Check out the guides for more detailed information on specific features:

1. **Mouse control** - Clicking, moving, dragging
2. **Keyboard input** - Typing, hotkeys, special keys
3. **Scrolling** - Scroll wheel operations
4. **Advanced** - Complex workflows and patterns

Happy automating! 🎉
