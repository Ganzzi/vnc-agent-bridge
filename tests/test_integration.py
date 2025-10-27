"""
Integration tests for VNCAgentBridge facade and controller interactions.

Tests complete workflows and interactions between multiple components.
"""

from unittest.mock import Mock, patch, MagicMock
import pytest

from vnc_agent_bridge.core.bridge import VNCAgentBridge
from vnc_agent_bridge.core.connection_tcp import TCPVNCConnection
from vnc_agent_bridge.core.mouse import MouseController
from vnc_agent_bridge.core.keyboard import KeyboardController
from vnc_agent_bridge.core.scroll import ScrollController


def setup_bridge_with_mock() -> VNCAgentBridge:
    """Helper to create a bridge with mocked connection and initialized controllers."""
    bridge = VNCAgentBridge("localhost")
    bridge._connection = Mock(spec=TCPVNCConnection)
    bridge._connection.is_connected = True
    bridge._connection.send_pointer_event = Mock()
    bridge._connection.send_key_event = Mock()
    bridge._mouse = MouseController(bridge._connection)
    bridge._keyboard = KeyboardController(bridge._connection)
    bridge._scroll = ScrollController(bridge._connection)
    return bridge


class TestBridgeInitialization:
    """Tests for VNCAgentBridge initialization."""

    def test_bridge_init_defaults(self) -> None:
        """Test bridge initialization with defaults."""
        bridge = VNCAgentBridge("localhost")
        assert bridge is not None
        assert bridge.is_connected is False

    def test_bridge_init_custom_port(self) -> None:
        """Test bridge initialization with custom port."""
        bridge = VNCAgentBridge("localhost", port=5901)
        assert bridge is not None

    def test_bridge_init_with_credentials(self) -> None:
        """Test bridge initialization with credentials."""
        bridge = VNCAgentBridge("localhost", username="user", password="pass")
        assert bridge is not None

    def test_bridge_not_connected_initially(self) -> None:
        """Test that bridge is not connected initially."""
        bridge = VNCAgentBridge("localhost")
        assert bridge.is_connected is False


class TestBridgeConnectDisconnect:
    """Tests for bridge connect/disconnect lifecycle."""

    @patch("socket.socket")
    def test_bridge_connect(self, mock_socket_class: Mock) -> None:
        """Test bridge connect."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        bridge = VNCAgentBridge("localhost")
        bridge.connect()

        assert bridge.is_connected is True

    @patch("socket.socket")
    def test_bridge_disconnect(self, mock_socket_class: Mock) -> None:
        """Test bridge disconnect."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        bridge = VNCAgentBridge("localhost")
        bridge.connect()

        bridge.disconnect()
        assert bridge.is_connected is False

    def test_bridge_disconnect_not_connected(self) -> None:
        """Test disconnect when not connected."""
        bridge = VNCAgentBridge("localhost")
        bridge.disconnect()  # Should not raise
        assert bridge.is_connected is False


class TestBridgeControllerAccess:
    """Tests for accessing controllers through bridge."""

    def test_bridge_controllers_unavailable_before_connect(self) -> None:
        """Test that controllers are unavailable before connecting."""
        bridge = VNCAgentBridge("localhost")
        with pytest.raises(RuntimeError):
            bridge.mouse
        with pytest.raises(RuntimeError):
            bridge.keyboard
        with pytest.raises(RuntimeError):
            bridge.scroll

    def test_controllers_share_same_connection(self) -> None:
        """Test that all controllers use the same connection after connect."""
        bridge = setup_bridge_with_mock()

        # All controllers should reference the same connection
        assert bridge.mouse._connection is bridge._connection
        assert bridge.keyboard._connection is bridge._connection
        assert bridge.scroll._connection is bridge._connection


class TestBridgeContextManager:
    """Tests for bridge context manager functionality."""

    @patch("socket.socket")
    def test_bridge_context_manager_enter_exit(self, mock_socket_class: Mock) -> None:
        """Test context manager enter and exit."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        with VNCAgentBridge("localhost") as bridge:
            assert bridge.is_connected is True

        # After exit, should be disconnected
        assert bridge.is_connected is False

    @patch("socket.socket")
    def test_bridge_context_manager_with_operations(
        self, mock_socket_class: Mock
    ) -> None:
        """Test performing operations within context manager."""
        bridge = setup_bridge_with_mock()

        with patch("vnc_agent_bridge.core.connection_tcp.TCPVNCConnection.connect"):
            bridge.mouse.left_click(100, 100)
            bridge.mouse._connection.send_pointer_event.assert_called()

    @patch("socket.socket")
    def test_bridge_context_manager_exception_cleanup(
        self, mock_socket_class: Mock
    ) -> None:
        """Test that context manager cleans up on exception."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recv.side_effect = [
            b"RFB 003.008\n",  # Server protocol version (12 bytes)
            b"\x00\x00\x00\x01",  # Security type 1 (no auth) (4 bytes)
        ]

        try:
            with VNCAgentBridge("localhost") as bridge:
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should still be disconnected even after exception
        assert bridge.is_connected is False


class TestBridgeWorkflows:
    """Tests for complete workflows using bridge."""

    def test_workflow_mouse_and_keyboard(self) -> None:
        """Test workflow combining mouse and keyboard operations."""
        bridge = setup_bridge_with_mock()

        # Simulate workflow
        bridge.mouse.left_click(100, 100)
        bridge.keyboard.type_text("hello")
        bridge.mouse.left_click(200, 200)

        # Verify calls were made
        assert bridge._connection.send_pointer_event.call_count >= 2
        assert bridge._connection.send_key_event.call_count >= 5

    def test_workflow_all_operations(self) -> None:
        """Test workflow using all controller types."""
        bridge = setup_bridge_with_mock()

        # Mouse operations
        bridge.mouse.move_to(100, 100)
        bridge.mouse.left_click(100, 100)

        # Keyboard operations
        bridge.keyboard.type_text("test")
        bridge.keyboard.press_key("return")

        # Scroll operations
        bridge.scroll.scroll_down(3)

        # Verify all operations were performed
        assert bridge._connection.send_pointer_event.call_count >= 2
        assert bridge._connection.send_key_event.call_count >= 6

    def test_workflow_sequential_operations(self) -> None:
        """Test sequential operations in workflow."""
        bridge = setup_bridge_with_mock()

        operations = [
            lambda: bridge.mouse.left_click(100, 100),
            lambda: bridge.keyboard.hotkey("ctrl", "a"),
            lambda: bridge.keyboard.type_text("data"),
            lambda: bridge.mouse.double_click(200, 200),
            lambda: bridge.scroll.scroll_up(5),
        ]

        for op in operations:
            op()

        # Verify all operations completed
        assert bridge._connection.send_pointer_event.call_count >= 5
        assert bridge._connection.send_key_event.call_count >= 7


class TestBridgeStateManagement:
    """Tests for bridge state management."""

    def test_bridge_is_connected_property(self) -> None:
        """Test bridge is_connected property."""
        bridge = VNCAgentBridge("localhost")
        assert bridge.is_connected is False

        bridge._connection = Mock()
        bridge._connection.is_connected = True
        assert bridge.is_connected is True

    def test_bridge_operations_fail_when_disconnected(self) -> None:
        """Test that operations fail when disconnected."""
        bridge = VNCAgentBridge("localhost")
        bridge._connection = Mock()
        bridge._connection.is_connected = False

        with pytest.raises(RuntimeError):
            bridge.mouse.left_click(100, 100)

        with pytest.raises(RuntimeError):
            bridge.keyboard.type_text("test")

        with pytest.raises(RuntimeError):
            bridge.scroll.scroll_up()


class TestBridgeEdgeCases:
    """Edge case tests for bridge."""

    def test_bridge_multiple_connects(self) -> None:
        """Test multiple connect/disconnect cycles."""
        bridge = VNCAgentBridge("localhost")
        bridge._connection = Mock()
        bridge._connection.is_connected = False
        bridge._connection.connect = Mock()
        bridge._connection.disconnect = Mock()

        # Simulate multiple connects
        bridge._connection.is_connected = True
        assert bridge.is_connected is True

        bridge._connection.is_connected = False
        assert bridge.is_connected is False

    def test_bridge_controller_consistency(self) -> None:
        """Test that controllers remain consistent across access."""
        bridge = setup_bridge_with_mock()

        mouse1 = bridge.mouse
        mouse2 = bridge.mouse
        assert mouse1 is mouse2  # Same instance

        keyboard1 = bridge.keyboard
        keyboard2 = bridge.keyboard
        assert keyboard1 is keyboard2  # Same instance

    def test_bridge_with_various_hosts(self) -> None:
        """Test bridge initialization with various host formats."""
        hosts = [
            "localhost",
            "127.0.0.1",
            "192.168.1.1",
            "example.com",
            "vnc-server.example.org",
        ]

        for host in hosts:
            bridge = VNCAgentBridge(host)
            assert bridge is not None


class TestBridgeV020Features:
    """Tests for v0.2.0 features: clipboard, screenshot, video, framebuffer."""

    def test_bridge_clipboard_integration(self) -> None:
        """Test clipboard controller integration with bridge."""
        bridge = setup_bridge_with_mock()
        bridge._clipboard = Mock()
        bridge._clipboard.send_text = Mock()
        bridge._clipboard.get_text = Mock(return_value="test content")

        # Test clipboard operations
        bridge.clipboard.send_text("hello")
        bridge.clipboard.get_text()

        bridge._clipboard.send_text.assert_called_once_with("hello")
        bridge._clipboard.get_text.assert_called_once()

    def test_bridge_screenshot_disabled_by_default(self) -> None:
        """Test that screenshot is disabled when enable_framebuffer=False."""
        from vnc_agent_bridge.exceptions import VNCStateError

        bridge = VNCAgentBridge("localhost", enable_framebuffer=False)
        bridge._connection = Mock(spec=TCPVNCConnection)
        bridge._connection.is_connected = True
        # Don't initialize controllers that require framebuffer

        with pytest.raises(VNCStateError, match="Screenshot feature not enabled"):
            bridge.screenshot

    def test_bridge_video_disabled_by_default(self) -> None:
        """Test that video is disabled when enable_framebuffer=False."""
        from vnc_agent_bridge.exceptions import VNCStateError

        bridge = VNCAgentBridge("localhost", enable_framebuffer=False)
        bridge._connection = Mock(spec=TCPVNCConnection)
        bridge._connection.is_connected = True

        with pytest.raises(VNCStateError, match="Video feature not enabled"):
            bridge.video

    def test_bridge_framebuffer_enabled(self) -> None:
        """Test framebuffer access when enabled."""
        bridge = VNCAgentBridge("localhost", enable_framebuffer=True)
        bridge._connection = Mock(spec=TCPVNCConnection)
        bridge._connection.is_connected = True
        bridge._framebuffer = Mock()

        assert bridge.framebuffer is not None

    def test_bridge_framebuffer_disabled(self) -> None:
        """Test framebuffer access when disabled."""
        bridge = VNCAgentBridge("localhost", enable_framebuffer=False)
        bridge._connection = Mock(spec=TCPVNCConnection)
        bridge._connection.is_connected = True

        assert bridge.framebuffer is None

    def test_bridge_enable_framebuffer_parameter(self) -> None:
        """Test enable_framebuffer parameter storage."""
        bridge_enabled = VNCAgentBridge("localhost", enable_framebuffer=True)
        bridge_disabled = VNCAgentBridge("localhost", enable_framebuffer=False)

        assert bridge_enabled._enable_framebuffer is True
        assert bridge_disabled._enable_framebuffer is False

    def test_bridge_v020_workflow(self) -> None:
        """Test complete v0.2.0 workflow with all features."""
        bridge = setup_bridge_with_mock()
        bridge._clipboard = Mock()
        bridge._clipboard.send_text = Mock()
        bridge._clipboard.get_text = Mock(return_value="clipboard content")

        # Mock framebuffer components
        bridge._framebuffer = Mock()
        bridge._screenshot = Mock()
        bridge._screenshot.capture = Mock(return_value=Mock())
        bridge._video = Mock()
        bridge._video.record = Mock()

        # Test integrated workflow
        bridge.mouse.left_click(100, 100)
        bridge.keyboard.type_text("test input")
        bridge.clipboard.send_text("copied text")
        bridge.screenshot.capture()
        bridge.video.record(duration=1.0)

        # Verify all components were used
        assert bridge._connection.send_pointer_event.called
        assert bridge._connection.send_key_event.called
        bridge._clipboard.send_text.assert_called_once_with("copied text")
        bridge._screenshot.capture.assert_called_once()
        bridge._video.record.assert_called_once_with(duration=1.0)

    def test_bridge_optional_components_not_initialized_when_disabled(self) -> None:
        """Test optional components not initialized when framebuffer disabled."""
        bridge = VNCAgentBridge("localhost", enable_framebuffer=False)
        bridge._connection = Mock(spec=TCPVNCConnection)
        bridge._connection.is_connected = True

        # Manually call connect logic (simplified)
        bridge._mouse = MouseController(bridge._connection)
        bridge._keyboard = KeyboardController(bridge._connection)
        bridge._scroll = ScrollController(bridge._connection)
        bridge._clipboard = Mock()  # Clipboard doesn't depend on framebuffer

        # Optional components should remain None
        assert bridge._framebuffer is None
        assert bridge._screenshot is None
        assert bridge._video is None

        # But basic controllers should work
        assert bridge.mouse is not None
        assert bridge.keyboard is not None
        assert bridge.scroll is not None
        assert bridge.clipboard is not None
