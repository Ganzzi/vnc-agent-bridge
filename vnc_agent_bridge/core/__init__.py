"""Core modules for VNC Agent Bridge.

This package contains the core implementation of the VNC Agent Bridge library,
including protocol handling, input controllers, and the main facade.

Modules:
    - bridge: Main VNCAgentBridge facade class
    - base_connection: Abstract base class for VNC connections
    - connection_tcp: TCP socket implementation for VNC protocol
    - connection_websocket: WebSocket implementation for VNC protocol
    - mouse: MouseController for mouse/pointer operations
    - keyboard: KeyboardController for keyboard input
    - scroll: ScrollController for scroll wheel operations
    - framebuffer: FramebufferManager for video frame management
    - screenshot: ScreenshotController for screen capture
    - video: VideoRecorder for video recording
    - clipboard: ClipboardController for clipboard operations

Example:
    Basic usage with context manager (TCP connection):
        from vnc_agent_bridge import VNCAgentBridge

        with VNCAgentBridge('localhost', port=5900) as vnc:
            vnc.mouse.left_click(100, 100)
            vnc.keyboard.type_text("Hello World")
            vnc.scroll.scroll_down(3)

    WebSocket connection with URL template:
        from vnc_agent_bridge import create_websocket_vnc

        bridge = create_websocket_vnc(
            url_template="wss://${host}:${port}/websockify",
            host="localhost",
            port=6080
        )
        with bridge:
            vnc.mouse.left_click(100, 100)
"""

# For backward compatibility and convenience
from .connection_tcp import TCPVNCConnection as VNCConnection  # noqa: F401
from .base_connection import VNCConnectionBase  # noqa: F401
from .connection_tcp import TCPVNCConnection  # noqa: F401
from .connection_websocket import WebSocketVNCConnection  # noqa: F401

__all__ = [
    "VNCConnection",  # Backward compatible alias for TCP
    "VNCConnectionBase",
    "TCPVNCConnection",
    "WebSocketVNCConnection",
]
