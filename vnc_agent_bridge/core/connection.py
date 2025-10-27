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
from typing import Optional

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
