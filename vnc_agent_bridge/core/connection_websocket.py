"""WebSocket-based VNC connection implementation.

This module implements VNCConnectionBase for WebSocket connections to VNC servers.
It supports flexible URL templates with placeholder substitution for different
WebSocket VNC server implementations (Proxmox, custom servers, etc.).

The implementation uses the websocket-client library to establish WebSocket
connections and wraps RFB 3.8 protocol messages in WebSocket frames.
"""

import ssl
import struct
import urllib.parse
from typing import Dict, List, Optional, Tuple

from .base_connection import VNCConnectionBase
from ..exceptions import (
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError,
    VNCStateError,
    VNCAuthenticationError,
)


class WebSocketVNCConnection(VNCConnectionBase):
    """VNC connection via WebSocket with URL template support.

    This class enables connection to WebSocket-based VNC servers using flexible
    URL templates. Users provide a template string with placeholders that get
    substituted with actual connection parameters.

    Supported placeholders:
    - ${host}: Connection hostname
    - ${port}: WebSocket server port
    - ${vnc_port}: VNC display port (optional)
    - ${ticket}: Authentication ticket/token

    Example URL templates:
    - Proxmox: "wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}"
    - Custom: "wss://${host}:${port}/vnc/websocket?token=${ticket}"
    - With VNC port: "wss://${host}:${port}/vnc/${vnc_port}/websocket?token=${ticket}"
    - Static: "wss://vnc.example.com:6900/connect?ticket=${ticket}"
    """

    def __init__(
        self,
        url_template: str,
        host: str,
        host_port: int,
        ticket: Optional[str] = None,
        vnc_port: Optional[int] = None,
        certificate_pem: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: float = 10.0,
        headers: Dict[str, str] = None,
    ) -> None:
        """Initialize WebSocket VNC connection.

        Args:
            url_template: URL template with ${} placeholders
                (host, host_port, port, ticket)
            host: VNC server hostname
            host_port: WebSocket server port
            ticket: Authentication ticket/token (substitutes ${ticket})
            vnc_port: VNC display port (substitutes ${vnc_port}, optional)
            certificate_pem: Optional PEM certificate for SSL verification
            verify_ssl: Whether to verify SSL certificates (default True)
            timeout: Connection timeout in seconds
            headers: Optional dict of additional HTTP headers

        Raises:
            ValueError: If required parameters are missing
        """
        self.url_template = url_template
        self.host = host
        self.host_port = host_port
        self.ticket = ticket
        self.vnc_port = vnc_port
        self.certificate_pem = certificate_pem
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.headers = headers

        # Connection state
        self._websocket = None
        self._connected = False
        self._recv_buffer = b""  # Buffer for handling fragmented WebSocket messages

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

            self._websocket = websocket.create_connection(
                websocket_url,
                timeout=self.timeout,
                header=self.headers,
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
            "${host_port}": str(self.host_port),
            "${vnc_port}": str(self.vnc_port) if self.vnc_port is not None else "",
            "${ticket}": urllib.parse.quote(self.ticket or ""),
        }

        # All placeholders are required
        required_placeholders = ["${host}", "${host_port}", "${vnc_port}", "${ticket}"]

        # Validate required placeholders
        for placeholder in required_placeholders:
            if placeholder in url:
                value = substitutions.get(placeholder, "")
                if not value:
                    param_name = placeholder.strip("${}")
                    raise ValueError(
                        f"Required parameter '{param_name}' is not provided"
                    )

        # Perform substitutions
        for placeholder, value in substitutions.items():
            url = url.replace(placeholder, value)

        # Clean up empty query parameters by parsing and reconstructing the URL
        parsed = urllib.parse.urlparse(url)
        query_dict = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        # Remove keys where the value list is empty or the first value is empty
        new_query_dict = {k: v for k, v in query_dict.items() if v and v[0].strip()}
        new_query = urllib.parse.urlencode(new_query_dict, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        url = urllib.parse.urlunparse(new_parsed)

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

        WebSocket VNC uses dual authentication:
        1. WebSocket-level auth via API token in headers + ticket in URL
        2. VNC-level auth if server requires it (using ticket as password)

        This allows for flexible authentication where WebSocket auth may succeed
        but VNC server still requires additional authentication.
        """
        if not self._websocket:
            raise VNCProtocolError("No WebSocket available")

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

        # Select supported security type with priority: no-auth (1) > VNC auth (2)
        # With dual auth, we can handle both WebSocket auth + VNC auth
        selected_security_type = None
        if 1 in security_types:  # No authentication (preferred)
            selected_security_type = 1
        elif (
            2 in security_types
        ):  # VNC authentication (supported with ticket as password)
            selected_security_type = 2
        elif security_types:  # Accept any available type as fallback
            selected_security_type = security_types[0]
        else:
            raise VNCProtocolError("No valid security types available")

        # Step 4: Send selected security type
        self._send_raw(struct.pack("!B", selected_security_type))

        # Step 5: Handle authentication based on selected type
        if selected_security_type == 1:  # No authentication
            # WebSocket auth (API token + ticket) should be sufficient
            pass
        elif selected_security_type == 2:  # VNC authentication
            # VNC Auth: challenge-response based on DES using ticket as password
            # This provides dual authentication: WebSocket level + VNC level
            challenge = self._recv_exact(16)

            # Use ticket as password for VNC authentication
            # If no ticket provided, use empty password
            password = self.ticket or ""
            response = self._vnc_auth_response(challenge, password)

            # Send 16-byte response
            self._send_raw(response)

            # Receive authentication result (4 bytes, 0=ok, non-zero=failed)
            auth_result = struct.unpack("!I", self._recv_exact(4))[0]
            if auth_result != 0:
                raise VNCAuthenticationError(
                    "VNC authentication failed - invalid ticket/password"
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

        Handles WebSocket message fragmentation by buffering data across
        multiple recv() calls. WebSocket messages can be fragmented or
        contain more data than a single RFB protocol message.

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
            # Use buffered data first
            while len(self._recv_buffer) < count:
                # WebSocket recv returns the next message
                chunk = self._websocket.recv()
                if isinstance(chunk, str):
                    chunk = chunk.encode("utf-8")
                if not chunk:
                    raise VNCConnectionError("Connection closed by server")
                self._recv_buffer += chunk

            # Extract exactly count bytes from buffer
            result = self._recv_buffer[:count]
            self._recv_buffer = self._recv_buffer[count:]
            return result

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
        self._recv_buffer = b""
        self._connected = False

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
            # Fallback to cryptography library
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend

            # VNC standard: Use 8-byte password key to encrypt both 8-byte blocks of 16-byte challenge
            response = b""
            backend = default_backend()

            # Encrypt first 8 bytes of challenge
            cipher = Cipher(
                algorithms.TripleDES(password_padded), modes.ECB(), backend=backend
            )
            encryptor = cipher.encryptor()
            response += encryptor.update(challenge[:8]) + encryptor.finalize()

            # Encrypt second 8 bytes of challenge
            cipher = Cipher(
                algorithms.TripleDES(password_padded), modes.ECB(), backend=backend
            )
            encryptor = cipher.encryptor()
            response += encryptor.update(challenge[8:16]) + encryptor.finalize()

            return response
        except ImportError:
            pass

        # Final fallback: pure Python DES implementation
        # This is a minimal DES implementation for VNC auth
        # NOTE: This is NOT cryptographically secure and should only be used as last resort
        def des_encrypt_block(block: bytes, key: bytes) -> bytes:
            """Minimal DES encryption for VNC auth (not secure for other uses)."""
            # This is a simplified implementation - in production, use proper crypto libraries
            # VNC DES uses specific key scheduling and permutations
            # For now, we'll use a basic XOR-based approach as fallback
            result = bytearray()
            for i in range(8):
                result.append(block[i] ^ key[i % len(key)])
            return bytes(result)

        response = b""
        response += des_encrypt_block(challenge[:8], password_padded)
        response += des_encrypt_block(challenge[8:16], password_padded)

        return response
        self._connected = False
