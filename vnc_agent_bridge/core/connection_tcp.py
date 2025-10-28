"""TCP-based VNC connection implementation.

This module implements VNCConnectionBase for standard TCP socket connections
to VNC servers. It handles the RFB 3.8 protocol over raw TCP sockets.

This is the refactored version of the original VNCConnection class, now
inheriting from VNCConnectionBase to support multiple connection types.
"""

import socket
import struct
from typing import List, Optional, Tuple

from .base_connection import VNCConnectionBase
from ..exceptions import (
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError,
    VNCStateError,
    VNCAuthenticationError,
)


class TCPVNCConnection(VNCConnectionBase):
    """Manages low-level VNC protocol communication over TCP sockets."""

    def __init__(
        self,
        host: str,
        port: int = 5900,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize TCP VNC connection parameters.

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

        # Step 3: Receive and handle security type(s)
        # RFB 3.8+ sends: 1 byte (number of security types) + N bytes (security types)
        # RFB 3.3-3.7 sends: 4 bytes (single security type, big-endian integer)
        num_security_types = struct.unpack("!B", self._recv_exact(1))[0]

        if num_security_types == 0:
            # Connection failed - server sends reason string
            reason_length = struct.unpack("!I", self._recv_exact(4))[0]
            reason = self._recv_exact(reason_length).decode()
            raise VNCConnectionError(f"VNC server refused connection: {reason}")

        # Read the security types list
        security_types = []
        for _ in range(num_security_types):
            security_type = struct.unpack("!B", self._recv_exact(1))[0]
            security_types.append(security_type)

        # Select supported security type priority: no-auth (1) > VNC auth (2)
        selected_security_type = None
        if 1 in security_types:  # No authentication (preferred)
            selected_security_type = 1
        elif 2 in security_types:  # VNC authentication
            selected_security_type = 2
        elif security_types:  # Accept any available type as fallback
            selected_security_type = security_types[0]
        else:
            raise VNCProtocolError("No valid security types available")

        # Step 4: Send selected security type
        self._send_raw(struct.pack("!B", selected_security_type))

        # Step 5: Handle authentication based on selected type
        if selected_security_type == 1:  # No authentication
            # No auth needed, proceed directly to ClientInit
            pass
        elif selected_security_type == 2:  # VNC authentication
            # VNC Auth: challenge-response based on DES
            # Receive 16-byte challenge from server
            challenge = self._recv_exact(16)

            # Generate response using password
            # If no password provided, use empty password
            password = self.password or ""
            response = self._vnc_auth_response(challenge, password)

            # Send 16-byte response
            self._send_raw(response)

            # Receive authentication result (4 bytes, 0=ok, non-zero=failed)
            auth_result = struct.unpack("!I", self._recv_exact(4))[0]
            if auth_result != 0:
                raise VNCAuthenticationError(
                    "VNC authentication failed - invalid password"
                )
        else:
            # Other auth types not yet supported
            raise VNCProtocolError(
                f"Unsupported security type: {selected_security_type}"
            )

        # Step 6: Send ClientInit message
        # Format: [1 byte: shared flag] (1 = shared desktop)
        self._send_raw(struct.pack("!B", 1))

        # Step 7: Receive ServerInit message (minimal parsing)
        # Format: [2 bytes: framebuffer width][2 bytes: framebuffer height]
        #         [pixel_format (16 bytes)][4 bytes: name length][name string]
        # We skip most of this but need to read it to maintain protocol sync
        server_init_header = self._recv_exact(4)
        width, height = struct.unpack("!HH", server_init_header)

        # Skip pixel format (16 bytes) and name length (4 bytes)
        pixel_format = self._recv_exact(16)
        name_length = struct.unpack("!I", self._recv_exact(4))[0]

        # Skip name string
        if name_length > 0:
            self._recv_exact(name_length)

    def _vnc_auth_response(self, challenge: bytes, password: str) -> bytes:
        """Generate VNC authentication response.

        Implements the VNC authentication challenge-response mechanism using DES.
        Per RFC 6143 Section 7.2.2.

        IMPORTANT NOTES:
        1. VNC authentication truncates passwords to 8 bytes maximum
        2. Each password byte must have its bits reversed (RFB protocol quirk)
        3. Padded to 8-byte boundary with null bytes
        4. Each 8-byte block of challenge encrypted with DES-ECB using password bytes as key

        Args:
            challenge: 16-byte challenge from server
            password: Password string (will be truncated to 8 bytes)

        Returns:
            16-byte response for server
        """
        import sys

        # Encode password to bytes
        password_encoded = password.encode("latin-1")

        # VNC truncates password to 8 bytes maximum (historical limitation)
        password_encoded = password_encoded[:8]

        # CRITICAL FIX: VNC requires bit-reversal of password bytes!
        # This is a historical quirk of the RFB protocol, necessary for compatibility
        def reverse_bits(byte_val: int) -> int:
            """Reverse the bits of a byte (0-255)."""
            result = 0
            for i in range(8):
                result = (result << 1) | ((byte_val >> i) & 1)
            return result

        # Reverse bits in each password byte
        password_encoded = bytes(reverse_bits(b) for b in password_encoded)

        # Pad password to 8 bytes with nulls
        password_padded = (password_encoded + b"\x00" * 8)[:8]

        try:
            # Try pycryptodome first (most reliable)
            from Crypto.Cipher import DES  # type: ignore

            # VNC standard: Use 8-byte password key to encrypt both 8-byte blocks of 16-byte challenge
            response = b""
            cipher = DES.new(password_padded, DES.MODE_ECB)

            # Encrypt first 8 bytes of challenge
            response += cipher.encrypt(challenge[:8])

            # Encrypt second 8 bytes of challenge
            response += cipher.encrypt(challenge[8:16])

            return response
        except ImportError:
            pass

        try:
            # Try pyDES library as fallback
            from des import DES  # type: ignore

            response = b""
            des = DES(password_padded, DES.MODE_ECB)
            response += des.encrypt(challenge[:8])
            response += des.encrypt(challenge[8:16])

            return response
        except ImportError:
            pass

        try:
            # Try using cryptography library with DES
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
            from cryptography.hazmat.backends import default_backend

            response = b""
            cipher = Cipher(
                algorithms.DES(password_padded), mode=None, backend=default_backend()
            )
            encryptor = cipher.encryptor()
            response += encryptor.update(challenge[:8]) + encryptor.finalize()

            encryptor2 = cipher.encryptor()
            response += encryptor2.update(challenge[8:16]) + encryptor2.finalize()

            return response
        except (ImportError, AttributeError):
            pass

        # All DES libraries failed - provide helpful error
        raise VNCProtocolError(
            "DES encryption not available. Install one of:\n"
            "  - pip install pycryptodome (recommended)\n"
            "  - pip install pyDES\n"
            "VNC authentication (Type 2) requires proper DES-ECB encryption."
        )

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
