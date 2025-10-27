"""Tests for WebSocket VNC connection implementation."""

import pytest
from unittest.mock import Mock, patch

from vnc_agent_bridge.core.connection_websocket import WebSocketVNCConnection
from vnc_agent_bridge.exceptions import (
    VNCConnectionError,
    VNCStateError,
)


class TestWebSocketVNCConnection:
    """Test WebSocket VNC connection functionality."""

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc?ticket=${ticket}",
            host="example.com",
            port=6900,
            ticket="test_ticket",
        )

        assert conn.url_template == "wss://${host}:${port}/vnc?ticket=${ticket}"
        assert conn.host == "example.com"
        assert conn.port == 6900
        assert conn.ticket == "test_ticket"
        assert conn.password is None
        assert conn.verify_ssl is True
        assert conn.timeout == 10.0
        assert not conn.is_connected

    def test_init_missing_required_params(self):
        """Test initialization fails with missing required parameters."""
        with pytest.raises(ValueError, match="url_template is required"):
            WebSocketVNCConnection(
                url_template="",
                host="example.com",
                port=6900,
            )

        with pytest.raises(ValueError, match="host is required"):
            WebSocketVNCConnection(
                url_template="wss://example.com",
                host="",
                port=6900,
            )

    @patch("builtins.__import__")
    def test_connect_success(self, mock_import):
        """Test successful WebSocket connection."""
        # Mock the websocket module
        mock_websocket = Mock()
        mock_ws = Mock()
        mock_websocket.create_connection.return_value = mock_ws

        def mock_import_func(name, *args, **kwargs):
            if name == "websocket":
                return mock_websocket
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = mock_import_func

        # Mock successful handshake
        mock_ws.recv.side_effect = [
            b"RFB 003.008\n",  # Server version
            b"\x00\x00\x00\x01",  # Security type (no auth)
        ]

        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc?ticket=${ticket}",
            host="example.com",
            port=6900,
            ticket="test_ticket",
        )

        conn.connect()

        assert conn.is_connected
        mock_websocket.create_connection.assert_called_once()
        mock_ws.send_binary.assert_called()  # Protocol handshake messages

    @patch("builtins.__import__")
    def test_connect_websocket_import_error(self, mock_import):
        """Test connection fails when websocket library not available."""

        # Mock import to raise ImportError for websocket
        def mock_import_func(name, *args, **kwargs):
            if name == "websocket":
                raise ImportError("No module named 'websocket'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = mock_import_func

        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(
            VNCConnectionError, match="websocket-client library is required"
        ):
            conn.connect()

    def test_url_template_substitution(self):
        """Test URL template placeholder substitution."""
        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/api/vnc?"
            "ticket=${ticket}&pwd=${password}",
            host="proxmox.example.com",
            port=6900,
            ticket="PVE:node:xxxxx",
            password="secret",
        )

        url = conn._substitute_url_template()
        expected = (
            "wss://proxmox.example.com:6900/api/vnc?ticket=PVE:node:xxxxx&pwd=secret"
        )
        assert url == expected

    def test_url_template_missing_required_param(self):
        """Test URL template fails when required parameter is missing."""
        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc?ticket=${ticket}",
            host="example.com",
            port=6900,
            ticket=None,  # Missing required ticket
        )

        with pytest.raises(
            ValueError, match="Required parameter 'ticket' is not provided"
        ):
            conn._substitute_url_template()

    def test_url_template_optional_password(self):
        """Test URL template with optional password parameter."""
        conn = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc?ticket=${ticket}&pwd=${password}",
            host="example.com",
            port=6900,
            ticket="test_ticket",
            password=None,  # Optional password not provided
        )

        url = conn._substitute_url_template()
        expected = "wss://example.com:6900/vnc?ticket=test_ticket&pwd="
        assert url == expected

    def test_disconnect(self):
        """Test disconnecting WebSocket connection."""
        mock_ws = Mock()

        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )
        conn._websocket = mock_ws
        conn._connected = True

        conn.disconnect()

        assert not conn.is_connected
        mock_ws.close.assert_called_once()

    def test_send_pointer_event_not_connected(self):
        """Test sending pointer event fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.send_pointer_event(100, 100, 1)

    def test_send_key_event_not_connected(self):
        """Test sending key event fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.send_key_event(0xFF0D, True)

    def test_send_pointer_event_connected(self):
        """Test sending pointer event when connected."""
        mock_ws = Mock()

        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )
        conn._websocket = mock_ws
        conn._connected = True

        conn.send_pointer_event(100, 200, 1)

        # Verify correct binary data was sent
        mock_ws.send_binary.assert_called_once()
        call_args = mock_ws.send_binary.call_args[0][0]

        # Parse the sent data: [type=5][button_mask=1][x=100][y=200] (big-endian)
        import struct

        msg_type, button_mask, x, y = struct.unpack("!BBHH", call_args)
        assert msg_type == 5  # POINTER_EVENT
        assert button_mask == 1  # Left button
        assert x == 100
        assert y == 200

    def test_send_key_event_connected(self):
        """Test sending key event when connected."""
        mock_ws = Mock()

        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )
        conn._websocket = mock_ws
        conn._connected = True

        conn.send_key_event(0xFF0D, True)  # Return key down

        # Verify correct binary data was sent
        mock_ws.send_binary.assert_called_once()
        call_args = mock_ws.send_binary.call_args[0][0]

        # Parse the sent data: [type=4][down_flag=1][padding=0][keycode] (big-endian)
        import struct

        msg_type, down_flag, padding, keycode = struct.unpack("!BBHI", call_args)
        assert msg_type == 4  # KEY_EVENT
        assert down_flag == 1  # Key down
        assert padding == 0
        assert keycode == 0xFF0D  # Return key

    def test_request_framebuffer_update_not_connected(self):
        """Test framebuffer update request fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.request_framebuffer_update()

    def test_set_encodings_not_connected(self):
        """Test set encodings fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.set_encodings([0])

    def test_send_clipboard_text_not_connected(self):
        """Test send clipboard text fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.send_clipboard_text("test")

    def test_receive_clipboard_text_not_connected(self):
        """Test receive clipboard text fails when not connected."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )

        with pytest.raises(VNCStateError, match="Not connected"):
            conn.receive_clipboard_text()

    def test_receive_clipboard_text_connected(self):
        """Test receiving clipboard text when connected."""
        mock_ws = Mock()

        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )
        conn._websocket = mock_ws
        conn._connected = True

        # Mock clipboard message components
        # Message format: [type=3][padding=0][length=4][data="test"]
        mock_ws.recv.side_effect = [
            b"\x03",  # Message type (CLIPBOARD_TEXT_SERVER)
            b"\x00",  # Padding
            b"\x00\x00\x00\x04",  # Text length (4 bytes)
            b"test",  # Text data
        ]

        result = conn.receive_clipboard_text()
        assert result == "test"

    def test_receive_clipboard_text_no_message(self):
        """Test receiving clipboard text returns None when no clipboard message."""
        mock_ws = Mock()

        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
        )
        conn._websocket = mock_ws
        conn._connected = True

        # Mock non-clipboard message
        mock_ws.recv.return_value = b"\x00"  # Framebuffer update message

        result = conn.receive_clipboard_text()
        assert result is None

    def test_ssl_context_creation(self):
        """Test SSL context creation with certificate."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
            certificate_pem="-----BEGIN CERTIFICATE-----\n"
            "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
            "-----END CERTIFICATE-----",
            verify_ssl=True,
        )

        context = conn._create_ssl_context()
        assert context is not None
        assert context.check_hostname is True
        assert context.verify_mode != 0  # Not CERT_NONE

    def test_ssl_context_no_certificate(self):
        """Test SSL context creation without certificate."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
            certificate_pem=None,
        )

        context = conn._create_ssl_context()
        assert context is None

    def test_ssl_context_no_verification(self):
        """Test SSL context creation with verification disabled."""
        conn = WebSocketVNCConnection(
            url_template="wss://example.com/vnc",
            host="example.com",
            port=6900,
            certificate_pem="dummy_cert",
            verify_ssl=False,
        )

        context = conn._create_ssl_context()
        assert context is not None
        assert context.check_hostname is False
        assert context.verify_mode == 0  # CERT_NONE
