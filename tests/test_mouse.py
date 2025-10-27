"""
Unit tests for MouseController.

Tests all mouse operations including clicks, movement, dragging,
and position queries with mock VNC connections.
"""

from unittest.mock import Mock, call
import pytest

from vnc_agent_bridge.core.mouse import MouseController
from vnc_agent_bridge.exceptions import VNCInputError, VNCStateError


class TestMouseLeftClick:
    """Tests for MouseController.left_click() method."""

    def test_left_click_at_position(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test left click at specified position."""
        mouse_controller.left_click(100, 150)
        # Click sends 2+ events: button press, release
        assert mock_vnc_connection.send_pointer_event.call_count >= 2
        # Verify last call releases the button (button_mask=0)
        last_call = mock_vnc_connection.send_pointer_event.call_args_list[-1]
        assert last_call[0][2] == 0  # button mask 0 for release

    def test_left_click_with_delay(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test left click with delay parameter."""
        mouse_controller.left_click(100, 150, delay=0.1)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_left_click_at_origin(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test left click at origin (0, 0)."""
        mouse_controller.left_click(0, 0)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_left_click_at_large_coordinates(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test left click at large but valid coordinates."""
        mouse_controller.left_click(1920, 1080)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_left_click_negative_x(self, mouse_controller: MouseController) -> None:
        """Test that left click with negative x raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.left_click(-1, 100)

    def test_left_click_negative_y(self, mouse_controller: MouseController) -> None:
        """Test that left click with negative y raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.left_click(100, -1)

    def test_left_click_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that left click when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = MouseController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.left_click(100, 100)


class TestMouseRightClick:
    """Tests for MouseController.right_click() method."""

    def test_right_click_at_position(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test right click at specified position."""
        mouse_controller.right_click(100, 150)
        # Right click sends 2+ events: button press, release
        assert mock_vnc_connection.send_pointer_event.call_count >= 2
        last_call = mock_vnc_connection.send_pointer_event.call_args_list[-1]
        assert last_call[0][2] == 0  # button mask 0 for release

    def test_right_click_with_delay(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test right click with delay parameter."""
        mouse_controller.right_click(100, 150, delay=0.1)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_right_click_negative_coordinates(
        self, mouse_controller: MouseController
    ) -> None:
        """Test that right click with negative coordinates raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.right_click(-5, 100)


class TestMouseDoubleClick:
    """Tests for MouseController.double_click() method."""

    def test_double_click_at_position(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test double click at specified position."""
        mouse_controller.double_click(100, 150)
        # Should generate multiple pointer events for double-click
        assert mock_vnc_connection.send_pointer_event.call_count >= 2

    def test_double_click_with_delay(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test double click with delay parameter."""
        mouse_controller.double_click(100, 150, delay=0.1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 2

    def test_double_click_negative_coordinates(
        self, mouse_controller: MouseController
    ) -> None:
        """Test that double click with negative coordinates raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.double_click(-1, 100)


class TestMouseMoveTo:
    """Tests for MouseController.move_to() method."""

    def test_move_to_position(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test moving cursor to position."""
        mouse_controller.move_to(200, 300)
        mock_vnc_connection.send_pointer_event.assert_called_once()
        call_args = mock_vnc_connection.send_pointer_event.call_args
        assert call_args is not None
        assert call_args[0][0] == 200  # x
        assert call_args[0][1] == 300  # y
        assert call_args[0][2] == 0  # button mask for move (no buttons)

    def test_move_to_origin(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test moving cursor to origin."""
        mouse_controller.move_to(0, 0)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_move_to_with_delay(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test move_to with delay parameter."""
        mouse_controller.move_to(200, 300, delay=0.1)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_move_to_negative_x(self, mouse_controller: MouseController) -> None:
        """Test that move_to with negative x raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.move_to(-1, 300)

    def test_move_to_negative_y(self, mouse_controller: MouseController) -> None:
        """Test that move_to with negative y raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.move_to(200, -1)


class TestMouseDragTo:
    """Tests for MouseController.drag_to() method."""

    def test_drag_to_basic(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test basic drag operation."""
        mouse_controller.drag_to(200, 300)
        # Drag should generate multiple events (down, move, up)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_drag_to_with_duration(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test drag with specified duration."""
        mouse_controller.drag_to(200, 300, duration=0.5)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_drag_to_with_delay(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test drag with delay parameter."""
        mouse_controller.drag_to(200, 300, delay=0.1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_drag_to_negative_coordinates(
        self, mouse_controller: MouseController
    ) -> None:
        """Test that drag_to with negative coordinates raises VNCInputError."""
        with pytest.raises(VNCInputError):
            mouse_controller.drag_to(-1, 300)

    def test_drag_to_zero_duration(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test drag with zero duration."""
        mouse_controller.drag_to(200, 300, duration=0)
        # Should still generate pointer events
        assert mock_vnc_connection.send_pointer_event.call_count >= 1


class TestMouseGetPosition:
    """Tests for MouseController.get_position() method."""

    def test_get_position_returns_tuple(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test that get_position returns a tuple."""
        mock_vnc_connection.get_position = Mock(return_value=(100, 150))
        result = mouse_controller.get_position()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_position_valid_coordinates(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test that get_position returns valid coordinates."""
        mock_vnc_connection.get_position = Mock(return_value=(1920, 1080))
        x, y = mouse_controller.get_position()
        assert x == 1920
        assert y == 1080
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_get_position_at_origin(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test get_position when cursor is at origin."""
        mock_vnc_connection.get_position = Mock(return_value=(0, 0))
        x, y = mouse_controller.get_position()
        assert x == 0
        assert y == 0


class TestMouseEdgeCases:
    """Edge case tests for MouseController."""

    def test_multiple_operations_in_sequence(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test multiple mouse operations in sequence."""
        mouse_controller.move_to(100, 100)
        mouse_controller.left_click(100, 100)
        mouse_controller.move_to(200, 200)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_click_without_connection_fail(self, mock_vnc_connection: Mock) -> None:
        """Test that operations fail when not connected."""
        mock_vnc_connection.is_connected = False
        controller = MouseController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.left_click(100, 100)

    def test_very_large_coordinates(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test with very large but valid coordinates."""
        mouse_controller.left_click(65535, 65535)
        mock_vnc_connection.send_pointer_event.assert_called_once()

    def test_sequential_different_operations(
        self, mouse_controller: MouseController, mock_vnc_connection: Mock
    ) -> None:
        """Test sequence of different mouse operations."""
        mouse_controller.left_click(100, 100)
        mouse_controller.right_click(200, 200)
        mouse_controller.double_click(300, 300)
        assert mock_vnc_connection.send_pointer_event.call_count >= 4
