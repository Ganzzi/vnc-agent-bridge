"""VNC Connection protocol implementation.

This module implements low-level VNC (Remote Framebuffer) protocol communication
for interacting with VNC servers. It handles connection management, protocol
handshaking, and sending VNC events (pointer and key events).

The implementation uses the RFB 3.8 protocol specification and communicates
over TCP sockets. It abstracts the binary protocol details and provides
higher-level methods for sending input events.

Protocol Overview:
    - Handshake: Protocol version negotiation
    - Connection: TCP socket to VNC server
    - Events: Pointer (mouse) and Key events are the primary messages
    - Data Format: Big-endian binary format with specific message structures

Message Types:
    - Pointer Event (Type 5): Mouse position and button state
    - Key Event (Type 4): Keyboard input with key code and press/release state

Example:
    Low-level protocol usage:
        conn = VNCConnection('localhost', port=5900)
        conn.connect()
        conn.send_pointer_event(100, 100, 1)  # Click at (100, 100)
        conn.send_key_event(0xFF0D, True)     # Press Return key
        conn.disconnect()
"""

import socket
import struct
from typing import Optional, List, Tuple

from ..exceptions import (
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError,
    VNCStateError,
)


class VNCConnection:
    """Manages low-level VNC protocol communication."""

    # VNC Protocol Constants
    PROTOCOL_VERSION = b"RFB 003.008\n"
    POINTER_EVENT = 5
    KEY_EVENT = 4

    # Framebuffer message types (v0.2.0)
    FRAMEBUFFER_UPDATE_REQUEST = 3
    SET_ENCODINGS = 2
    FRAMEBUFFER_UPDATE = 0
    SET_PIXEL_FORMAT = 0
    CLIPBOARD_TEXT_CLIENT = 6
    CLIPBOARD_TEXT_SERVER = 3

    def __init__(
        self,
        host: str,
        port: int = 5900,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize VNC connection parameters.

        Args:
            host: VNC server hostname or IP address
            port: VNC server port (default 5900)
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        # Connection state
        self._socket: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> None:
        """Connect to VNC server and complete handshake.

        Raises:
            VNCConnectionError: If connection fails
            VNCTimeoutError: If connection times out
            VNCProtocolError: If protocol handshake fails
        """
        if self._connected:
            raise VNCStateError("Already connected")

        try:
            # Create TCP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)

            # Connect to server
            self._socket.connect((self.host, self.port))

            # Perform RFB protocol handshake
            self._perform_handshake()

            self._connected = True

        except socket.timeout:
            self._cleanup_socket()
            raise VNCTimeoutError(f"Connection to {self.host}:{self.port} timed out")
        except socket.error as e:
            self._cleanup_socket()
            raise VNCConnectionError(
                f"Failed to connect to {self.host}:{self.port}: {e}"
            )
        except Exception as e:
            self._cleanup_socket()
            raise VNCProtocolError(f"Protocol error during handshake: {e}")

    def disconnect(self) -> None:
        """Close connection gracefully."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass  # Ignore errors during cleanup
            self._socket = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to VNC server."""
        return self._connected and self._socket is not None

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
        # In a full implementation, we'd get these from server init
        # For now, use reasonable defaults that can be overridden
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

        # This is a simplified implementation
        # In a full implementation, we'd need to handle the server's message loop
        # For now, this method can be called when we expect clipboard data

        try:
            # Try to read a clipboard message (non-blocking check)
            # Read message type
            msg_type = struct.unpack("!B", self._recv_exact(1))[0]

            if msg_type != self.CLIPBOARD_TEXT_SERVER:
                # Not a clipboard message, put it back (this is tricky with TCP)
                # For now, return None if it's not clipboard data
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

    def _perform_handshake(self) -> None:
        """Perform RFB protocol handshake.

        Raises:
            VNCProtocolError: If handshake fails
        """
        if not self._socket:
            raise VNCProtocolError("No socket available")

        # Step 1: Receive server protocol version
        server_version = self._recv_exact(12)
        if server_version != self.PROTOCOL_VERSION:
            raise VNCProtocolError(
                f"Unsupported protocol version: {server_version.decode().strip()}"
            )

        # Step 2: Send our protocol version
        self._send_raw(self.PROTOCOL_VERSION)

        # Step 3: Authentication (simplified - no auth for now)
        # In full implementation, this would handle various auth types
        # For now, assume no authentication required
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
        # We don't need the full framebuffer info for basic input operations
        # Skip the server init message for now
        # In full implementation: width, height, pixel format, name, etc.
        pass

    def _send_raw(self, data: bytes) -> None:
        """Send raw bytes to server.

        Args:
            data: Bytes to send

        Raises:
            VNCConnectionError: If send fails
        """
        if not self._socket:
            raise VNCConnectionError("No socket available")

        try:
            self._socket.sendall(data)
        except Exception as e:
            self._cleanup_socket()
            raise VNCConnectionError(f"Failed to send data: {e}")

    def _recv_exact(self, count: int) -> bytes:
        """Receive exactly count bytes from server.

        Args:
            count: Number of bytes to receive

        Returns:
            Received bytes

        Raises:
            VNCConnectionError: If receive fails
            VNCTimeoutError: If receive times out
        """
        if not self._socket:
            raise VNCConnectionError("No socket available")

        try:
            data = b""
            while len(data) < count:
                chunk = self._socket.recv(count - len(data))
                if not chunk:
                    raise VNCConnectionError("Connection closed by server")
                data += chunk
            return data
        except socket.timeout:
            raise VNCTimeoutError("Receive operation timed out")
        except Exception as e:
            self._cleanup_socket()
            raise VNCConnectionError(f"Failed to receive data: {e}")

    def _cleanup_socket(self) -> None:
        """Clean up socket resources."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
        self._socket = None
        self._connected = False
