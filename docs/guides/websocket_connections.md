# WebSocket VNC Connections

This guide covers how to use WebSocket-based VNC connections with the VNC Agent Bridge. WebSocket connections enable secure, real-time communication with VNC servers over standard web protocols.

## Overview

WebSocket VNC connections provide several advantages over traditional TCP connections:

- **Security**: WebSocket Secure (WSS) provides encrypted communication
- **Compatibility**: Works through firewalls and proxies that allow HTTP/HTTPS
- **Flexibility**: URL-based configuration supports various VNC server implementations
- **Authentication**: Built-in support for ticket-based and password authentication

## Installation

WebSocket support requires the `websocket-client` library. Install it using:

```bash
pip install vnc-agent-bridge[websocket]
# or
pip install websocket-client
```

## Quick Start

The easiest way to create a WebSocket VNC connection is using the convenience function:

```python
from vnc_agent_bridge import create_websocket_vnc

# Connect to a Proxmox WebSocket VNC server
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    ticket="vncticket123"
)

# Use the bridge for VNC operations
with bridge:
    bridge.mouse.move_to(100, 100)
    bridge.mouse.left_click()
    bridge.keyboard.type_text("Hello VNC!")
```

## URL Templates

WebSocket connections use URL templates with placeholder substitution. The following placeholders are supported:

- `${host}`: VNC server hostname
- `${port}`: VNC server port
- `${ticket}`: Authentication ticket/token
- `${password}`: Authentication password (optional)

### Common URL Templates

#### Proxmox VE

```python
url_template = "wss://${host}:${port}/api2/json/nodes/${node}/qemu/${vmid}/vncwebsocket?vncticket=${ticket}"
```

Example:
```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    ticket="vncticket123"
)
```

#### noVNC (Standard WebSocket VNC)

```python
url_template = "wss://${host}:${port}/websockify"
```

Example:
```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="vnc.example.com",
    port=6080
)
```

#### Custom VNC WebSocket Server

```python
url_template = "wss://${host}:${port}/vnc/websocket?token=${ticket}&password=${password}"
```

Example:
```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}&password=${password}",
    host="vnc.example.com",
    port=6900,
    ticket="auth_token",
    password="secret_password"
)
```

## SSL/TLS Configuration

WebSocket connections support various SSL configurations for secure communication.

### Default SSL Verification

By default, SSL certificates are verified:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="secure-vnc.example.com",
    port=443,
    ticket="auth_token"
    # verify_ssl=True by default
)
```

### Disable SSL Verification (Development Only)

For testing with self-signed certificates:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="dev-vnc.example.com",
    port=8080,
    ticket="auth_token",
    verify_ssl=False  # WARNING: Only for development!
)
```

### Custom SSL Certificate

For servers with specific certificates:

```python
# Load certificate from file
with open("server.crt", "r") as f:
    cert_pem = f.read()

bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="custom-vnc.example.com",
    port=8443,
    ticket="auth_token",
    certificate_pem=cert_pem,
    verify_ssl=True
)
```

## Authentication Methods

### Ticket-Based Authentication

Most WebSocket VNC servers use ticket-based authentication:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    ticket="vncticket_abc123def456"
)
```

### Password Authentication

Some servers support password authentication:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?password=${password}",
    host="vnc.example.com",
    port=6900,
    password="my_vnc_password"
)
```

### Combined Authentication

Use both ticket and password when required:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?ticket=${ticket}&password=${password}",
    host="secure-vnc.example.com",
    port=8443,
    ticket="session_ticket",
    password="user_password"
)
```

## Advanced Usage

### Manual Connection Creation

For more control, create the connection manually:

```python
from vnc_agent_bridge import VNCAgentBridge, WebSocketVNCConnection

# Create connection with custom settings
connection = WebSocketVNCConnection(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="vnc.example.com",
    port=6900,
    ticket="auth_token",
    timeout=30.0,  # Custom timeout
    verify_ssl=True
)

# Create bridge with the connection
bridge = VNCAgentBridge(connection=connection)

# Use the bridge
with bridge:
    # VNC operations...
    pass
```

### Connection Timeout Configuration

Adjust connection timeouts for different network conditions:

```python
# Fast network
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="local-vnc.example.com",
    port=6900,
    ticket="auth_token",
    timeout=5.0  # 5 second timeout
)

# Slow network
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="remote-vnc.example.com",
    port=6900,
    ticket="auth_token",
    timeout=60.0  # 60 second timeout
)
```

## Error Handling

WebSocket connections can fail for various reasons. Handle errors appropriately:

```python
from vnc_agent_bridge import (
    create_websocket_vnc,
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError
)

try:
    bridge = create_websocket_vnc(
        url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
        host="vnc.example.com",
        port=6900,
        ticket="invalid_ticket"
    )

    with bridge:
        bridge.mouse.move_to(100, 100)

except VNCConnectionError as e:
    print(f"Connection failed: {e}")
    # Handle connection issues (wrong host, port, SSL problems)

except VNCTimeoutError as e:
    print(f"Connection timeout: {e}")
    # Handle timeout issues (network problems, slow server)

except VNCProtocolError as e:
    print(f"Protocol error: {e}")
    # Handle WebSocket/RFB protocol issues

except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other unexpected errors
```

## Troubleshooting

### Common Issues

#### SSL Certificate Verification Failed

**Problem**: `VNCConnectionError: SSL certificate verification failed`

**Solutions**:
1. Check if the server certificate is valid
2. Use `verify_ssl=False` for testing (not recommended for production)
3. Provide custom certificate with `certificate_pem` parameter

#### Connection Timeout

**Problem**: `VNCTimeoutError: Connection timeout`

**Solutions**:
1. Increase timeout value: `timeout=30.0`
2. Check network connectivity
3. Verify server is running and accessible

#### Invalid Ticket/Token

**Problem**: `VNCConnectionError: Authentication failed`

**Solutions**:
1. Verify ticket/token is correct and not expired
2. Check ticket format (some servers require URL encoding)
3. Ensure ticket has proper permissions

#### WebSocket Subprotocol Not Supported

**Problem**: `VNCProtocolError: WebSocket subprotocol negotiation failed`

**Solutions**:
1. Verify URL template matches server expectations
2. Check if server supports the expected WebSocket subprotocol
3. Some servers may require specific query parameters

### Debugging Connections

Enable debug logging to troubleshoot connection issues:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Create connection with debug logging
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="vnc.example.com",
    port=6900,
    ticket="auth_token"
)
```

## Performance Considerations

### Connection Pooling

For applications that need multiple simultaneous connections:

```python
# Create multiple bridges for different VMs/sessions
bridges = []
for vm_id in [100, 101, 102]:
    bridge = create_websocket_vnc(
        url_template=f"wss://${{host}}:${{port}}/api2/json/nodes/pve/qemu/{vm_id}/vncwebsocket?vncticket=${{ticket}}",
        host="proxmox.example.com",
        port=8006,
        ticket=f"ticket_{vm_id}"
    )
    bridges.append(bridge)
```

### Connection Reuse

WebSocket connections can be reused for multiple operations:

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
    host="vnc.example.com",
    port=6900,
    ticket="auth_token"
)

with bridge:
    # Connection established once
    for i in range(10):
        bridge.mouse.move_to(i * 10, i * 10)
        bridge.keyboard.type_text(f"Step {i}")
        # Connection stays open
```

## Migration from TCP Connections

If you're migrating from TCP-based connections:

```python
# Old TCP connection
from vnc_agent_bridge import VNCAgentBridge, TCPVNCConnection

bridge_tcp = VNCAgentBridge(TCPVNCConnection("vnc.example.com", 5900))

# New WebSocket connection
from vnc_agent_bridge import create_websocket_vnc

bridge_ws = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="vnc.example.com",
    port=6080
)

# API remains the same!
with bridge_ws:
    bridge_ws.mouse.move_to(100, 100)
    bridge_ws.keyboard.type_text("Hello!")
```

## Server-Specific Examples

### Proxmox VE 7+

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/api2/json/nodes/${node}/qemu/${vmid}/vncwebsocket?vncticket=${ticket}",
    host="proxmox.example.com",
    port=8006,
    ticket="PVEVNC:1234567890ABCDEF..."
)
```

### OpenStack Nova VNC

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vnc_auto.html?token=${ticket}",
    host="openstack.example.com",
    port=6080,
    ticket="nova_vnc_token"
)
```

### Docker Container with noVNC

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/websockify",
    host="docker-host.example.com",
    port=6080
)
```

### Custom VNC Proxy

```python
bridge = create_websocket_vnc(
    url_template="wss://${host}:${port}/vncproxy/${session_id}?auth=${ticket}",
    host="vnc-proxy.example.com",
    port=8443,
    ticket="session_auth_token"
)
```

This guide covers the most common WebSocket VNC connection scenarios. For server-specific configurations not covered here, refer to your VNC server's documentation for WebSocket URL formats and authentication requirements.