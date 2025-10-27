"""
Unit tests for TCPVNCConnection.

Tests connection lifecycle, protocol handling, and error scenarios
with mock socket connections.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest

from vnc_agent_bridge.core.connection_tcp import TCPVNCConnection
from vnc_agent_bridge.exceptions import (
    VNCConnectionError,
    VNCStateError,
    VNCProtocolError,
)


class TestConnectionInit:
    """Tests for TCPVNCConnection initialization."""

    def test_connection_init_defaults(self) -> None:
        """Test connection initialization with default parameters."""
        conn = TCPVNCConnection("localhost")
        assert conn.host == "localhost"
        assert conn.port == 5900
        assert conn.username is None
        assert conn.password is None

    def test_connection_init_custom_port(self) -> None:
        """Test connection initialization with custom port."""
        conn = TCPVNCConnection("192.168.1.1", port=5901)
        assert conn.host == "192.168.1.1"
        assert conn.port == 5901

    def test_connection_init_with_credentials(self) -> None:
        """Test connection initialization with username and password."""
        conn = TCPVNCConnection("localhost", username="user", password="pass")
        assert conn.username == "user"
        assert conn.password == "pass"

    def test_connection_not_connected_initially(self) -> None:
        """Test that connection is not connected on initialization."""
        conn = TCPVNCConnection("localhost")
        assert conn.is_connected is False


class TestConnectionConnect:
    """Tests for TCPVNCConnection.connect() method."""

    @patch("socket.socket")
    def test_connection_connect_success(self, mock_socket_class: Mock) -> None:
        """Test successful connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        mock_socket.connect.assert_called_once()
        assert conn.is_connected is True

    @patch("socket.socket")
    def test_connection_connect_failure(self, mock_socket_class: Mock) -> None:
        """Test connection failure."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = OSError("Connection refused")

        conn = TCPVNCConnection("localhost")
        with pytest.raises(VNCConnectionError):
            conn.connect()

    @patch("socket.socket")
    def test_connection_connect_already_connected(
        self, mock_socket_class: Mock
    ) -> None:
        """Test that connecting when already connected raises error."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        # Try to connect again
        with pytest.raises(VNCStateError):
            conn.connect()


class TestConnectionDisconnect:
    """Tests for TCPVNCConnection.disconnect() method."""

    @patch("socket.socket")
    def test_connection_disconnect_when_connected(
        self, mock_socket_class: Mock
    ) -> None:
        """Test disconnecting when connected."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        conn.disconnect()
        assert conn.is_connected is False
        mock_socket.close.assert_called_once()

    def test_connection_disconnect_when_not_connected(self) -> None:
        """Test disconnecting when not connected."""
        conn = TCPVNCConnection("localhost")
        # Should not raise an error
        conn.disconnect()
        assert conn.is_connected is False


class TestConnectionStatus:
    """Tests for connection status checking."""

    def test_is_connected_property_disconnected(self) -> None:
        """Test is_connected property when not connected."""
        conn = TCPVNCConnection("localhost")
        assert conn.is_connected is False

    @patch("socket.socket")
    def test_is_connected_property_connected(self, mock_socket_class: Mock) -> None:
        """Test is_connected property when connected."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        assert conn.is_connected is True


class TestConnectionSendPointerEvent:
    """Tests for sending pointer events."""

    @patch("socket.socket")
    def test_send_pointer_event(self, mock_socket_class: Mock) -> None:
        """Test sending pointer event."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        conn.send_pointer_event(100, 150, 1)
        mock_socket.sendall.assert_called()

    def test_send_pointer_event_not_connected(self) -> None:
        """Test sending pointer event when not connected."""
        conn = TCPVNCConnection("localhost")
        with pytest.raises(VNCStateError):
            conn.send_pointer_event(100, 150, 1)


class TestConnectionSendKeyEvent:
    """Tests for sending key events."""

    @patch("socket.socket")
    def test_send_key_event(self, mock_socket_class: Mock) -> None:
        """Test sending key event."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        conn = TCPVNCConnection("localhost")
        conn.connect()

        conn.send_key_event(0xFF0D, True)
        mock_socket.sendall.assert_called()

    def test_send_key_event_not_connected(self) -> None:
        """Test sending key event when not connected."""
        conn = TCPVNCConnection("localhost")
        with pytest.raises(VNCStateError):
            conn.send_key_event(0xFF0D, True)


class TestConnectionErrorHandling:
    """Tests for error handling in connection."""

    @patch("socket.socket")
    def test_connection_protocol_version_mismatch(
        self, mock_socket_class: Mock
    ) -> None:
        """Test handling protocol version mismatch."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.return_value = b"RFB 002.003\n"  # Unsupported version

        conn = TCPVNCConnection("localhost")
        with pytest.raises(VNCProtocolError):
            conn.connect()

    @patch("socket.socket")
    def test_connection_invalid_protocol_response(
        self, mock_socket_class: Mock
    ) -> None:
        """Test handling invalid protocol response."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.return_value = b"INVALID RESPONSE\n"

        conn = TCPVNCConnection("localhost")
        with pytest.raises(VNCProtocolError):
            conn.connect()


class TestConnectionEdgeCases:
    """Edge case tests for TCPVNCConnection."""

    def test_connection_multiple_disconnect_calls(self) -> None:
        """Test calling disconnect multiple times."""
        conn = TCPVNCConnection("localhost")
        conn.disconnect()
        conn.disconnect()  # Should not raise

    @patch("socket.socket")
    def test_connection_attributes_correct_after_init(
        self, mock_socket_class: Mock
    ) -> None:
        """Test that connection attributes are correct after initialization."""
        conn = TCPVNCConnection(
            "example.com", port=5902, username="admin", password="secret"
        )
        assert conn.host == "example.com"
        assert conn.port == 5902
        assert conn.username == "admin"
        assert conn.password == "secret"
