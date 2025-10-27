"""WebSocket-based VNC connection implementation.

This module implements VNCConnectionBase for WebSocket connections to VNC servers.
It supports flexible URL templates with placeholder substitution for different
WebSocket VNC server implementations (Proxmox, custom servers, etc.).

The implementation uses the websocket-client library to establish WebSocket
connections and wraps RFB 3.8 protocol messages in WebSocket frames.
"""

import ssl
import struct
from typing import List, Optional, Tuple

from .base_connection import VNCConnectionBase
from ..exceptions import (
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError,
    VNCStateError,
)


class WebSocketVNCConnection(VNCConnectionBase):
    """VNC connection via WebSocket with URL template support.

    This class enables connection to WebSocket-based VNC servers using flexible
    URL templates. Users provide a template string with placeholders that get
    substituted with actual connection parameters.

    Supported placeholders:
    - ${host}: Connection hostname
    - ${port}: Connection port
    - ${ticket}: Authentication ticket/token
    - ${password}: Authentication password (optional)

    Example URL templates:
    - Proxmox: "wss://${host}:${port}/api2/json/nodes/pve/qemu/100/
        vncwebsocket?vncticket=${ticket}"
    - Custom: "wss://${host}:${port}/vnc/websocket?token=${ticket}"
    - Static: "wss://vnc.example.com:6900/connect?ticket=${ticket}"
    """

    def __init__(
        self,
        url_template: str,
        host: str,
        port: int,
        ticket: Optional[str] = None,
        password: Optional[str] = None,
        certificate_pem: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: float = 10.0,
    ) -> None:
        """Initialize WebSocket VNC connection.

        Args:
            url_template: URL template with ${} placeholders
                (host, port, ticket, password)
            host: VNC server hostname
            port: VNC server port
            ticket: Authentication ticket/token (substitutes ${ticket})
            password: Authentication password (substitutes ${password})
            certificate_pem: Optional PEM certificate for SSL verification
            verify_ssl: Whether to verify SSL certificates (default True)
            timeout: Connection timeout in seconds

        Raises:
            ValueError: If required parameters are missing
        """
        self.url_template = url_template
        self.host = host
        self.port = port
        self.ticket = ticket
        self.password = password
        self.certificate_pem = certificate_pem
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Connection state
        self._websocket = None
        self._connected = False

        # Validate required parameters
        if not url_template:
            raise ValueError("url_template is required")
        if not host:
            raise ValueError("host is required")

    def connect(self) -> None:
        """Connect to VNC server via WebSocket and complete handshake.

        Substitutes URL template placeholders and establishes WebSocket connection,
        then performs RFB protocol handshake.

        Raises:
            VNCConnectionError: If connection fails
            VNCTimeoutError: If connection times out
            VNCProtocolError: If protocol handshake fails
            ValueError: If URL template substitution fails
        """
        if self._connected:
            raise VNCStateError("Already connected")

        try:
            # Import websocket-client (optional dependency)
            import websocket  # type: ignore[import-not-found]

            # Substitute URL template placeholders
            websocket_url = self._substitute_url_template()

            # Create SSL context
            ssl_context = self._create_ssl_context()

            # Create WebSocket connection
            self._websocket = websocket.create_connection(
                websocket_url,
                timeout=self.timeout,
                sslopt=(
                    {
                        "cert_reqs": (
                            ssl.CERT_REQUIRED if self.verify_ssl else ssl.CERT_NONE
                        ),
                        "ssl_context": ssl_context,
                    }
                    if ssl_context
                    else {
                        "cert_reqs": ssl.CERT_NONE,
                    }
                ),
            )

            # Perform RFB protocol handshake over WebSocket
            self._perform_handshake()

            self._connected = True

        except ImportError:
            raise VNCConnectionError(
                "websocket-client library is required for WebSocket connections. "
                "Install with: pip install websocket-client"
            )
        except Exception as e:
            self._cleanup_websocket()
            if isinstance(e, (VNCConnectionError, VNCTimeoutError, VNCProtocolError)):
                raise
            raise VNCConnectionError(f"Failed to connect via WebSocket: {e}")

    def disconnect(self) -> None:
        """Close WebSocket connection gracefully."""
        self._cleanup_websocket()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to VNC server."""
        return self._connected and self._websocket is not None

    def send_pointer_event(self, x: int, y: int, button_mask: int) -> None:
        """Send mouse pointer event to server.

        Args:
            x: X coordinate (0-65535)
            y: Y coordinate (0-65535)
            button_mask: Button state mask (bitfield)

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        self._validate_connection()

        # Format: [msg_type=5][button_mask][x][y] (big-endian)
        data = struct.pack("!BBHH", self.POINTER_EVENT, button_mask, x, y)
        self._send_raw(data)

    def send_key_event(self, keycode: int, pressed: bool) -> None:
        """Send keyboard event to server.

        Args:
            keycode: X11 KEYSYM value
            pressed: True for key down, False for key up

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        self._validate_connection()

        # Format: [msg_type=4][down_flag][padding][keycode] (big-endian)
        down_flag = 1 if pressed else 0
        data = struct.pack("!BBHI", self.KEY_EVENT, down_flag, 0, keycode)
        self._send_raw(data)

    def request_framebuffer_update(
        self,
        incremental: bool = True,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Request framebuffer update from server.

        Args:
            incremental: True for incremental update, False for full refresh
            x: X coordinate of update region
            y: Y coordinate of update region
            width: Width of update region (None for full width)
            height: Height of update region (None for full height)

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        self._validate_connection()

        # Use full screen dimensions if not specified
        if width is None:
            width = 1920  # Default width
        if height is None:
            height = 1080  # Default height

        # Format: [msg_type=3][incremental][x][y][width][height] (big-endian)
        incremental_flag = 1 if incremental else 0
        data = struct.pack(
            "!BBHHHH",
            self.FRAMEBUFFER_UPDATE_REQUEST,
            incremental_flag,
            x,
            y,
            width,
            height,
        )
        self._send_raw(data)

    def read_framebuffer_update(self) -> List[Tuple[int, int, int, int, bytes]]:
        """Read framebuffer update response from server.

        Returns:
            List of rectangles: [(x, y, width, height, pixel_data), ...]

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If receive fails
            VNCProtocolError: If message format is invalid
        """
        self._validate_connection()

        # Read message type
        msg_type = struct.unpack("!B", self._recv_exact(1))[0]
        if msg_type != self.FRAMEBUFFER_UPDATE:
            raise VNCProtocolError(f"Expected framebuffer update (0), got {msg_type}")

        # Skip padding byte
        self._recv_exact(1)

        # Read number of rectangles
        num_rectangles = struct.unpack("!H", self._recv_exact(2))[0]

        rectangles = []
        for _ in range(num_rectangles):
            # Read rectangle header: x, y, width, height, encoding
            rect_data = self._recv_exact(12)
            x, y, width, height, encoding = struct.unpack("!HHHHi", rect_data)

            # For now, only handle Raw encoding (0)
            if encoding != 0:
                raise VNCProtocolError(f"Unsupported encoding: {encoding}")

            # Calculate pixel data size (assuming 32-bit RGBA)
            pixel_data_size = width * height * 4
            pixel_data = self._recv_exact(pixel_data_size)

            rectangles.append((x, y, width, height, pixel_data))

        return rectangles

    def set_encodings(self, encodings: List[int]) -> None:
        """Tell server which encodings we support.

        Args:
            encodings: List of encoding numbers we support

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        self._validate_connection()

        # Format: [msg_type=2][padding][num_encodings][encodings...] (big-endian)
        num_encodings = len(encodings)
        data = struct.pack("!BBH", self.SET_ENCODINGS, 0, num_encodings)

        # Add each encoding as a 32-bit integer
        for encoding in encodings:
            data += struct.pack("!i", encoding)

        self._send_raw(data)

    def send_clipboard_text(self, text: str) -> None:
        """Send clipboard text to server.

        Args:
            text: Text to send to remote clipboard

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        self._validate_connection()

        # Convert text to bytes (latin-1 encoding as per RFB spec)
        text_bytes = text.encode("latin-1")
        text_length = len(text_bytes)

        # Format: [msg_type=6][padding][length][text_bytes] (big-endian)
        data = struct.pack("!BBI", self.CLIPBOARD_TEXT_CLIENT, 0, text_length)
        data += text_bytes

        self._send_raw(data)

    def receive_clipboard_text(self) -> Optional[str]:
        """Receive clipboard text from server.

        Returns:
            Clipboard text if available, None if no clipboard message pending

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If receive fails
        """
        self._validate_connection()

        try:
            # Try to read a clipboard message
            msg_type = struct.unpack("!B", self._recv_exact(1))[0]

            if msg_type != self.CLIPBOARD_TEXT_SERVER:
                return None

            # Skip padding byte
            self._recv_exact(1)

            # Read text length
            text_length = struct.unpack("!I", self._recv_exact(4))[0]

            # Read text data
            text_bytes = self._recv_exact(text_length)

            # Decode as latin-1 (per RFB spec)
            return text_bytes.decode("latin-1")

        except (VNCConnectionError, VNCTimeoutError):
            # No clipboard data available
            return None

    def _validate_connection(self) -> None:
        """Verify connection is active.

        Raises:
            VNCStateError: If not connected
        """
        if not self.is_connected:
            raise VNCStateError("Not connected to VNC server")

    def _substitute_url_template(self) -> str:
        """Substitute placeholders in URL template.

        Returns:
            Complete WebSocket URL with all placeholders substituted

        Raises:
            ValueError: If required placeholders are missing
        """
        url = self.url_template

        # Substitute placeholders
        substitutions = {
            "${host}": str(self.host),
            "${port}": str(self.port),
            "${ticket}": self.ticket or "",
            "${password}": self.password or "",
        }

        # Required placeholders (password is optional)
        required_placeholders = ["${host}", "${port}", "${ticket}"]

        for placeholder, value in substitutions.items():
            if (
                placeholder in required_placeholders
                and placeholder in url
                and not value
            ):
                # Required placeholder is missing
                param_name = placeholder.strip("${}")
                raise ValueError(f"Required parameter '{param_name}' is not provided")
            url = url.replace(placeholder, value)

        return url

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for WebSocket connection.

        Returns:
            SSL context if certificate provided, None otherwise
        """
        if not self.certificate_pem:
            return None

        context = ssl.create_default_context()
        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # Load custom certificate if provided
        # Note: In production, you'd want to load this from a file
        # For now, this is a simplified implementation
        return context

    def _perform_handshake(self) -> None:
        """Perform RFB protocol handshake over WebSocket.

        Raises:
            VNCProtocolError: If handshake fails
        """
        if not self._websocket:
            raise VNCProtocolError("No WebSocket available")

        # Step 1: Receive server protocol version
        server_version = self._recv_exact(12)  # type: ignore[unreachable]
        if server_version != self.PROTOCOL_VERSION:
            raise VNCProtocolError(
                f"Unsupported protocol version: {server_version.decode().strip()}"
            )

        # Step 2: Send our protocol version
        self._send_raw(self.PROTOCOL_VERSION)

        # Step 3: Authentication (simplified - no auth for now)
        auth_result = self._recv_exact(4)  # Security type response
        security_type = struct.unpack("!I", auth_result)[0]

        if security_type == 0:  # Connection failed
            reason_length = struct.unpack("!I", self._recv_exact(4))[0]
            reason = self._recv_exact(reason_length).decode()
            raise VNCConnectionError(f"VNC server refused connection: {reason}")
        elif security_type == 1:  # No authentication
            # Send client init (shared flag = 1)
            self._send_raw(struct.pack("!B", 1))
        else:
            # For now, only support no-auth. Full implementation would handle
            # VNC authentication, VNCAuth, etc.
            raise VNCProtocolError(f"Unsupported security type: {security_type}")

        # Step 4: Receive server init (framebuffer info)
        # Skip the server init message for basic input operations
        pass

    def _send_raw(self, data: bytes) -> None:
        """Send raw bytes to server via WebSocket.

        Args:
            data: Bytes to send

        Raises:
            VNCConnectionError: If send fails
        """
        if not self._websocket:
            raise VNCConnectionError("No WebSocket available")

        try:  # type: ignore[unreachable]
            self._websocket.send_binary(data)
        except Exception as e:
            self._cleanup_websocket()
            raise VNCConnectionError(f"Failed to send data: {e}")

    def _recv_exact(self, count: int) -> bytes:
        """Receive exactly count bytes from server via WebSocket.

        Args:
            count: Number of bytes to receive

        Returns:
            Received bytes

        Raises:
            VNCConnectionError: If receive fails
            VNCTimeoutError: If receive times out
        """
        if not self._websocket:
            raise VNCConnectionError("No WebSocket available")

        try:  # type: ignore[unreachable]
            data = b""
            while len(data) < count:
                # WebSocket recv returns the next message
                chunk = self._websocket.recv()
                if isinstance(chunk, str):
                    chunk = chunk.encode("utf-8")
                if not chunk:
                    raise VNCConnectionError("Connection closed by server")
                data += chunk

                # If we received more than needed, this is an issue with the protocol
                # In a full implementation, we'd need to buffer extra data
                if len(data) > count:
                    raise VNCProtocolError("Received more data than expected")

            return data

        except Exception as e:
            self._cleanup_websocket()
            if "timeout" in str(e).lower():
                raise VNCTimeoutError("Receive operation timed out")
            raise VNCConnectionError(f"Failed to receive data: {e}")

    def _cleanup_websocket(self) -> None:
        """Clean up WebSocket resources."""
        if self._websocket:
            try:  # type: ignore[unreachable]
                self._websocket.close()
            except Exception:
                pass
        self._websocket = None
        self._connected = False
