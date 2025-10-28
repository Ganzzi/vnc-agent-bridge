# VNC Agent Bridge
# Open-source Python package for AI agents to interact with VNC servers

__version__ = "0.3.0"

from typing import Dict, Optional

# Import main classes and exceptions
from .core.bridge import VNCAgentBridge
from .core.connection_tcp import TCPVNCConnection
from .core.connection_websocket import WebSocketVNCConnection
from .core.clipboard import ClipboardController
from .exceptions import (
    VNCException,
    VNCConnectionError,
    VNCTimeoutError,
    VNCInputError,
    VNCStateError,
    VNCProtocolError,
)

# Backward compatibility alias
VNCConnection = TCPVNCConnection


"""WebSocket-based VNC connection implementation.

This module implements VNCConnectionBase for WebSocket connections to VNC servers.
It supports flexible URL templates with placeholder substitution for different
WebSocket VNC server implementations (Proxmox, custom servers, etc.).

The implementation uses the websocket-client library to establish WebSocket
connections and wraps RFB 3.8 protocol messages in WebSocket frames.
"""


def create_websocket_vnc(
    url_template: str,
    host: str,
    host_port: int,
    ticket: Optional[str] = None,
    vnc_port: Optional[int] = None,
    certificate_pem: Optional[str] = None,
    verify_ssl: bool = True,
    timeout: float = 10.0,
    headers: Dict[str, str] = None,
) -> VNCAgentBridge:
    """Create VNCAgentBridge instance with WebSocket VNC connection.

    This convenience function creates a WebSocket-based VNC connection using
    URL templates and returns a fully configured VNCAgentBridge instance.

    The URL template supports placeholders that get substituted with connection
    parameters:
    - ${host}: Connection hostname
    - ${port}: WebSocket server port
    - ${vnc_port}: VNC display port (optional)
    - ${ticket}: Authentication ticket/token

    Example usage:
        # Proxmox WebSocket VNC
        bridge = create_websocket_vnc(
            url_template="wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?port=${vnc_port}&vncticket=${ticket}",
            host="proxmox.example.com",
            port=8006,
            vnc_port=5900,
            ticket="vncticket123"
        )

        # Custom WebSocket VNC server with VNC port
        bridge = create_websocket_vnc(
            url_template="wss://${host}:${port}/vnc/${vnc_port}/websocket?token=${ticket}",
            host="vnc.example.com",
            port=6900,
            vnc_port=5901,
            ticket="auth_token"
        )

    Args:
        url_template: URL template with ${} placeholders (host, host_port, port, ticket)
        host: VNC server hostname
        host_port: WebSocket server port
        ticket: Authentication ticket/token (substitutes ${ticket})
        vnc_port: VNC display port (substitutes ${vnc_port}, optional)
        certificate_pem: Optional PEM certificate for SSL verification
        verify_ssl: Whether to verify SSL certificates (default True)
        timeout: Connection timeout in seconds
        headers: Optional dict of additional HTTP headers

    Returns:
        VNCAgentBridge: Configured bridge instance with WebSocket connection

    Raises:
        ValueError: If required parameters are missing
        VNCConnectionError: If connection fails
    """
    connection = WebSocketVNCConnection(
        url_template=url_template,
        host=host,
        host_port=host_port,
        ticket=ticket,
        vnc_port=vnc_port,
        certificate_pem=certificate_pem,
        verify_ssl=verify_ssl,
        timeout=timeout,
        headers=headers,
    )
    return VNCAgentBridge(connection=connection)


__all__ = [
    "VNCAgentBridge",
    "VNCConnection",  # Backward compatibility alias
    "TCPVNCConnection",  # New explicit name
    "WebSocketVNCConnection",  # WebSocket connection class
    "create_websocket_vnc",  # WebSocket convenience function
    "ClipboardController",
    "VNCException",
    "VNCConnectionError",
    "VNCTimeoutError",
    "VNCInputError",
    "VNCStateError",
    "VNCProtocolError",
]
