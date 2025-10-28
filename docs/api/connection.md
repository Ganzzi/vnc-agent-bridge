# VNCAgentBridge API Reference

The `VNCAgentBridge` class is the main entry point for the VNC Agent Bridge library, providing unified access to all VNC interaction features.

## Overview

The VNCAgentBridge class acts as a facade that:
- Manages connection to VNC servers (TCP or WebSocket)
- Provides access to mouse, keyboard, and scroll controllers
- Supports context manager protocol for automatic cleanup
- Handles connection lifecycle and resource management

## Connection Types

VNC Agent Bridge supports two connection types:

### TCP Connections (Default)

Traditional TCP socket connections to VNC servers:

```python
from vnc_agent_bridge import VNCAgentBridge

# TCP connection (default)
with VNCAgentBridge('localhost', port=5900) as vnc:
    vnc.mouse.left_click(100, 100)
```

### WebSocket Connections

Secure WebSocket connections for modern VNC servers:

```python
from vnc_agent_bridge import create_websocket_vnc

# WebSocket connection
with create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="vnc.example.com",
    port=6080
) as vnc:
    vnc.mouse.left_click(100, 100)
```

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

---

# WebSocket VNC Connections

WebSocket connections provide secure, real-time communication with VNC servers over standard web protocols.

## Function: create_websocket_vnc()

Convenience function for creating WebSocket-based VNC connections.

```python
from vnc_agent_bridge import create_websocket_vnc

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="vnc.example.com",
    port=6080,
    ticket="auth_token"
)
```

### Parameters

- `url_template` (str, required): URL template with placeholders
  - Supported placeholders: `${host}`, `${port}`, `${ticket}`, `${password}`
  - Examples:
    - `"wss://${host}:${port}/websockify"` (noVNC)
    - `"wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}"` (Proxmox)

- `host` (str, required): VNC server hostname
  - Examples: `'localhost'`, `'192.168.1.100'`, `'vnc.example.com'`

- `port` (int, required): VNC server port
  - Examples: `6080` (noVNC), `8006` (Proxmox), `8443` (custom SSL)

- `ticket` (str, optional): Authentication ticket/token
  - Substitutes `${ticket}` in URL template
  - Required for authenticated connections

- `password` (str, optional): Authentication password
  - Substitutes `${password}` in URL template
  - Alternative to ticket-based authentication

- `certificate_pem` (str, optional): Custom SSL certificate
  - PEM-encoded certificate string for SSL verification
  - Useful for self-signed certificates

- `verify_ssl` (bool): Enable SSL certificate verification (default: True)
  - Set to False for development with self-signed certificates
  - WARNING: Only disable in development environments

- `timeout` (float): Connection timeout in seconds (default: 10.0)
  - Examples: `5.0` (fast), `10.0` (default), `30.0` (slow networks)

### Returns

- `VNCAgentBridge`: Configured bridge instance with WebSocket connection

### Raises

- `ValueError`: If required parameters are missing or invalid
- `VNCConnectionError`: If WebSocket connection fails
- `VNCTimeoutError`: If connection times out
- `VNCProtocolError`: If WebSocket/RFB protocol negotiation fails

### Examples

#### Basic WebSocket Connection

```python
from vnc_agent_bridge import create_websocket_vnc

# noVNC WebSocket server
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="vnc.example.com",
    port=6080
)
```

#### Proxmox VE Connection

```python
# Proxmox WebSocket VNC
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?port=${vnc_port}&vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    vnc_port=5900,
    ticket="PVEVNC:abc123..."
)
```

#### Custom SSL Configuration

```python
# With custom certificate
with open("server.crt", "r") as f:
    cert_pem = f.read()

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket",
    host="secure-vnc.example.com",
    port=8443,
    certificate_pem=cert_pem,
    verify_ssl=True
)
```

#### Development Mode (SSL Disabled)

```python
# WARNING: Only for development!
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket",
    host="dev-vnc.example.com",
    port=8080,
    verify_ssl=False  # Development only
)
```

## Class: WebSocketVNCConnection

Low-level WebSocket VNC connection class for advanced usage.

```python
from vnc_agent_bridge import WebSocketVNCConnection, VNCAgentBridge

# Create connection manually
connection = WebSocketVNCConnection(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="vnc.example.com",
    port=6900,
    ticket="auth_token"
)

# Use with VNCAgentBridge
bridge = VNCAgentBridge(connection=connection)
```

### Constructor Parameters

Same as `create_websocket_vnc()` function parameters.

### Methods

#### connect()

Establish WebSocket connection and initialize RFB protocol.

**Returns:** None

**Raises:**
- `VNCConnectionError`: Connection failed
- `VNCTimeoutError`: Connection timed out
- `VNCProtocolError`: Protocol negotiation failed

#### disconnect()

Close WebSocket connection and cleanup resources.

**Returns:** None

#### send_pointer_event(button_mask, x, y)

Send mouse pointer event.

**Parameters:**
- `button_mask` (int): Button state bitmask
- `x` (int): X coordinate
- `y` (int): Y coordinate

#### send_key_event(key_code, down_flag)

Send keyboard key event.

**Parameters:**
- `key_code` (int): X11 key code
- `down_flag` (bool): True for key down, False for key up

## URL Template Guide

### Supported Placeholders

- `${host}`: Replaced with the `host` parameter
- `${port}`: Replaced with the `port` parameter
- `${ticket}`: Replaced with the `ticket` parameter
- `${password}`: Replaced with the `password` parameter

### Common Templates

#### noVNC (Standard)

```
wss://${host}:${port}/websockify
```

#### Proxmox VE

```
wss://${host}:${port}/api2/json/nodes/${node}/qemu/${vmid}/vncwebsocket?vncticket=${ticket}
```

#### OpenStack Nova

```
wss://${host}:${port}/vnc_auto.html?token=${ticket}
```

#### Custom Server

```
wss://${host}:${port}/vnc/websocket?auth=${ticket}&pass=${password}
```

### Template Examples

```python
# Simple WebSocket
template = "wss://${host}:${port}/websockify"

# With authentication
template = "wss://${host}:${port}/vnc/websocket?token=${ticket}"

# Complex Proxmox
template = "wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}"

# Custom parameters
template = "wss://${host}:${port}/proxy/vnc?session=${ticket}&key=${password}"
```

## SSL/TLS Configuration

### Certificate Verification

```python
# Default: verify SSL certificates
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="vnc.example.com",
    port=8443
    # verify_ssl=True by default
)

# Disable verification (development only)
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="dev.example.com",
    port=8080,
    verify_ssl=False  # WARNING: Development only!
)
```

### Custom Certificates

```python
# Load certificate from file
with open("server.crt", "r") as f:
    cert_pem = f.read()

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/secure/vnc",
    host="internal.example.com",
    port=8443,
    certificate_pem=cert_pem,
    verify_ssl=True
)
```

## Authentication

### Ticket-Based Authentication

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc?token=${ticket}",
    host="vnc.example.com",
    port=6900,
    ticket="session_ticket_12345"
)
```

## Error Handling

```python
from vnc_agent_bridge import (
    create_websocket_vnc,
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError
)

try:
    bridge = create_websocket_vnc(
        url_template="wss://${host}:${port}/vnc",
        host="vnc.example.com",
        port=6080
    )

    with bridge:
        bridge.mouse.left_click(100, 100)

except VNCConnectionError as e:
    print(f"WebSocket connection failed: {e}")

except VNCTimeoutError as e:
    print(f"Connection timeout: {e}")

except VNCProtocolError as e:
    print(f"WebSocket/RFB protocol error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Migration from TCP

### Before (TCP)

```python
from vnc_agent_bridge import VNCAgentBridge

bridge = VNCAgentBridge('localhost', port=5900)
```

### After (WebSocket)

```python
from vnc_agent_bridge import create_websocket_vnc

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="localhost",
    port=6080
)
```

### API Compatibility

The VNCAgentBridge API remains identical:

```python
# Works with both TCP and WebSocket connections
with bridge:
    bridge.mouse.move_to(100, 100)
    bridge.keyboard.type_text("Hello")
    bridge.scroll.scroll_down(3)
```

## Performance Considerations

### Connection Reuse

WebSocket connections can be reused for multiple operations:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="vnc.example.com",
    port=6080
)

with bridge:
    # Connection established once
    for i in range(10):
        bridge.mouse.move_to(i * 10, i * 10)
        bridge.keyboard.type_text(f"Step {i}")
        # Connection stays open
```

### Timeout Configuration

Adjust timeouts based on network conditions:

```python
# Fast LAN
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="local-vnc.example.com",
    port=6080,
    timeout=5.0
)

# Slow WAN
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="remote-vnc.example.com",
    port=6080,
    timeout=30.0
)
```

## Troubleshooting

### Common Issues

#### SSL Certificate Errors

**Error:** `VNCConnectionError: SSL certificate verification failed`

**Solutions:**
- Use `verify_ssl=False` for development
- Provide `certificate_pem` for custom certificates
- Check certificate validity and hostname matching

#### Connection Timeouts

**Error:** `VNCTimeoutError: Connection timeout`

**Solutions:**
- Increase `timeout` value
- Check network connectivity
- Verify server is running and accessible

#### Invalid Authentication

**Error:** `VNCConnectionError: Authentication failed`

**Solutions:**
- Verify ticket/password is correct
- Check ticket format and encoding
- Ensure authentication method matches server requirements

#### WebSocket Subprotocol Errors

**Error:** `VNCProtocolError: WebSocket subprotocol negotiation failed`

**Solutions:**
- Verify URL template matches server expectations
- Check if server supports required WebSocket subprotocol
- Some servers require specific query parameters

### Debugging

Enable debug logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc",
    host="vnc.example.com",
    port=6080
)
```

## Related

- [WebSocket Connections Guide](../../guides/websocket_connections.md)
- [WebSocket Usage Examples](../../examples/websocket_usage.py)
- [VNCAgentBridge API](connection.md)
- [Exception Reference](../exceptions.md)
