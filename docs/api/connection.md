# VNCAgentBridge API Reference

The `VNCAgentBridge` class is the main entry point for the VNC Agent Bridge library, providing unified access to all VNC interaction features.

## Overview

The VNCAgentBridge class acts as a facade that:
- Manages connection to VNC servers
- Provides access to mouse, keyboard, and scroll controllers
- Supports context manager protocol for automatic cleanup
- Handles connection lifecycle and resource management

## Class: VNCAgentBridge

```python
from vnc_agent_bridge import VNCAgentBridge

# Using context manager (recommended)
with VNCAgentBridge('localhost', port=5900) as vnc:
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.type_text("Hello")

# Manual connection management
vnc = VNCAgentBridge('localhost', port=5900)
try:
    vnc.connect()
    vnc.mouse.left_click(100, 100)
finally:
    vnc.disconnect()
```

## Constructor

### VNCAgentBridge(host, port=5900, username=None, password=None, timeout=10.0)

Initialize a VNC Agent Bridge instance.

**Parameters:**
- `host` (str, required): VNC server hostname or IP address
  - Examples: `'localhost'`, `'192.168.1.100'`, `'vnc.example.com'`
  
- `port` (int): VNC server port (default: 5900)
  - Standard VNC ports: 5900, 5901, 5902, etc.
  - Display numbering: `:0` = 5900, `:1` = 5901, etc.
  
- `username` (str, optional): Username for VNC authentication
  - Only required if VNC server enforces authentication
  - Default: None (no authentication)
  
- `password` (str, optional): Password for VNC authentication
  - Only required if VNC server enforces authentication
  - Default: None (no authentication)
  
- `timeout` (float): Connection timeout in seconds (default: 10.0)
  - Useful for network timeouts and hanging connections
  - Examples: `5.0` (short), `10.0` (default), `30.0` (long)

**Raises:**
- `VNCConnectionError`: If initial parameters invalid

**Example:**
```python
# Local VNC server
vnc = VNCAgentBridge('localhost')

# Remote VNC server with custom port
vnc = VNCAgentBridge('192.168.1.100', port=5901)

# With authentication
vnc = VNCAgentBridge('vnc.example.com', username='user', password='pass')

# With longer timeout
vnc = VNCAgentBridge('slow-server.com', timeout=30.0)
```

## Methods

### connect()

Connect to the VNC server and initialize controllers.

**Returns:** None

**Raises:**
- `VNCConnectionError`: If connection fails
- `VNCTimeoutError`: If connection times out
- `VNCProtocolError`: If protocol negotiation fails

**Example:**
```python
vnc = VNCAgentBridge('localhost')
vnc.connect()
print("Connected!")
```

### disconnect()

Disconnect from the VNC server.

**Returns:** None

**Example:**
```python
vnc.connect()
# ... perform operations ...
vnc.disconnect()
```

### __enter__() and __exit__()

Context manager support for automatic connection management.

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    # Automatically connected
    vnc.mouse.left_click(100, 100)
# Automatically disconnected
```

## Properties

### mouse

Get the MouseController for mouse/pointer operations.

**Type:** `MouseController`

**Returns:** MouseController instance

**Example:**
```python
vnc.mouse.left_click(100, 100)
vnc.mouse.move_to(200, 200)
vnc.mouse.drag_to(300, 300)
```

### keyboard

Get the KeyboardController for keyboard input.

**Type:** `KeyboardController`

**Returns:** KeyboardController instance

**Example:**
```python
vnc.keyboard.type_text("Hello World")
vnc.keyboard.press_key("return")
vnc.keyboard.hotkey("ctrl", "a")
```

### scroll

Get the ScrollController for scroll wheel operations.

**Type:** `ScrollController`

**Returns:** ScrollController instance

**Example:**
```python
vnc.scroll.scroll_up(amount=5)
vnc.scroll.scroll_down(amount=3)
vnc.scroll.scroll_to(400, 300)
```

### is_connected

Check if currently connected to VNC server.

**Type:** `bool`

**Returns:** True if connected, False otherwise

**Example:**
```python
if vnc.is_connected:
    vnc.mouse.left_click(100, 100)
else:
    vnc.connect()
```

## Common Patterns

### Context Manager (Recommended)

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost', port=5900) as vnc:
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.type_text("text")
# Automatic cleanup
```

### Manual Connection Management

```python
vnc = VNCAgentBridge('localhost', port=5900)
try:
    vnc.connect()
    # Perform operations
finally:
    vnc.disconnect()
```

### Conditional Connection

```python
vnc = VNCAgentBridge('localhost')

if not vnc.is_connected:
    vnc.connect()

vnc.mouse.left_click(100, 100)
```

### Error Handling

```python
from vnc_agent_bridge import VNCConnectionError, VNCException

try:
    with VNCAgentBridge('invalid-host') as vnc:
        vnc.mouse.left_click(100, 100)
except VNCConnectionError as e:
    print(f"Connection failed: {e}")
except VNCException as e:
    print(f"VNC error: {e}")
```

### Multi-Step Workflow

```python
with VNCAgentBridge('localhost') as vnc:
    # Navigate
    vnc.mouse.left_click(200, 200)
    
    # Input
    vnc.keyboard.type_text("search query")
    vnc.keyboard.press_key("return")
    
    # Scroll and select
    vnc.scroll.scroll_down(amount=5)
    vnc.mouse.left_click(300, 400)
```

## Connection Parameters Guide

### Host Selection

```python
# Local machine
vnc = VNCAgentBridge('localhost')

# Same machine, different display
vnc = VNCAgentBridge('127.0.0.1')

# LAN IP address
vnc = VNCAgentBridge('192.168.1.100')

# Hostname
vnc = VNCAgentBridge('workstation.example.com')

# IPv6
vnc = VNCAgentBridge('[::1]')  # IPv6 localhost
```

### Port Selection

```python
# Standard VNC port
vnc = VNCAgentBridge('host', port=5900)  # Default

# VNC display :1
vnc = VNCAgentBridge('host', port=5901)

# VNC display :2
vnc = VNCAgentBridge('host', port=5902)

# Custom port
vnc = VNCAgentBridge('host', port=6000)
```

### Authentication

```python
# No authentication
vnc = VNCAgentBridge('host')

# Username only
vnc = VNCAgentBridge('host', username='user')

# Username and password
vnc = VNCAgentBridge('host', username='user', password='pass')
```

### Timeout Configuration

```python
# Quick timeout (LAN)
vnc = VNCAgentBridge('host', timeout=5.0)

# Standard timeout
vnc = VNCAgentBridge('host', timeout=10.0)  # Default

# Long timeout (WAN/slow)
vnc = VNCAgentBridge('host', timeout=30.0)

# Very long timeout
vnc = VNCAgentBridge('host', timeout=60.0)
```

## Error Handling

```python
from vnc_agent_bridge import (
    VNCException,
    VNCConnectionError,
    VNCTimeoutError,
    VNCStateError,
)

try:
    with VNCAgentBridge('localhost') as vnc:
        vnc.mouse.left_click(100, 100)

except VNCConnectionError as e:
    print(f"Connection error: {e}")

except VNCTimeoutError as e:
    print(f"Connection timed out: {e}")

except VNCStateError as e:
    print(f"Invalid state: {e}")

except VNCException as e:
    print(f"VNC error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Related

- [MouseController API](mouse.md)
- [KeyboardController API](keyboard.md)
- [ScrollController API](scroll.md)
- [Exception Reference](../exceptions.md)
- [Main API Reference](../index.md)
