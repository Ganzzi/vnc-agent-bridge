"""
Unit tests for ScrollController.

Tests scroll operations including scroll up, scroll down,
and scroll to position with mock VNC connections.
"""

from unittest.mock import Mock
import pytest

from vnc_agent_bridge.core.scroll import ScrollController
from vnc_agent_bridge.exceptions import VNCInputError, VNCStateError


class TestScrollUp:
    """Tests for ScrollController.scroll_up() method."""

    def test_scroll_up_default_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll up with default amount."""
        scroll_controller.scroll_up()
        mock_vnc_connection.send_pointer_event.assert_called()

    def test_scroll_up_custom_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll up with custom amount."""
        scroll_controller.scroll_up(5)
        # Should send multiple scroll events
        assert mock_vnc_connection.send_pointer_event.call_count >= 5

    def test_scroll_up_amount_one(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll up with amount of 1."""
        scroll_controller.scroll_up(1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_up_large_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll up with large amount."""
        scroll_controller.scroll_up(50)
        assert mock_vnc_connection.send_pointer_event.call_count >= 50

    def test_scroll_up_with_delay(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll_up with delay parameter."""
        scroll_controller.scroll_up(3, delay=0.1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_scroll_up_zero_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll up with zero amount."""
        scroll_controller.scroll_up(0)
        # Should not send scroll events for zero amount
        mock_vnc_connection.send_pointer_event.assert_not_called()

    def test_scroll_up_negative_amount(
        self, scroll_controller: ScrollController
    ) -> None:
        """Test that scroll_up with negative amount raises VNCInputError."""
        with pytest.raises(VNCInputError):
            scroll_controller.scroll_up(-1)

    def test_scroll_up_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that scroll_up when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = ScrollController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.scroll_up()


class TestScrollDown:
    """Tests for ScrollController.scroll_down() method."""

    def test_scroll_down_default_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll down with default amount."""
        scroll_controller.scroll_down()
        mock_vnc_connection.send_pointer_event.assert_called()

    def test_scroll_down_custom_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll down with custom amount."""
        scroll_controller.scroll_down(5)
        # Should send multiple scroll events
        assert mock_vnc_connection.send_pointer_event.call_count >= 5

    def test_scroll_down_amount_one(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll down with amount of 1."""
        scroll_controller.scroll_down(1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_down_large_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll down with large amount."""
        scroll_controller.scroll_down(50)
        assert mock_vnc_connection.send_pointer_event.call_count >= 50

    def test_scroll_down_with_delay(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll_down with delay parameter."""
        scroll_controller.scroll_down(3, delay=0.1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_scroll_down_zero_amount(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll down with zero amount."""
        scroll_controller.scroll_down(0)
        # Should not send scroll events for zero amount
        mock_vnc_connection.send_pointer_event.assert_not_called()

    def test_scroll_down_negative_amount(
        self, scroll_controller: ScrollController
    ) -> None:
        """Test that scroll_down with negative amount raises VNCInputError."""
        with pytest.raises(VNCInputError):
            scroll_controller.scroll_down(-1)

    def test_scroll_down_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that scroll_down when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = ScrollController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.scroll_down()


class TestScrollTo:
    """Tests for ScrollController.scroll_to() method."""

    def test_scroll_to_position(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling at specific position."""
        scroll_controller.scroll_to(100, 200)
        # Should move cursor and send scroll events
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_to_origin(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling at origin."""
        scroll_controller.scroll_to(0, 0)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_to_large_coordinates(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling at large coordinates."""
        scroll_controller.scroll_to(1920, 1080)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_to_with_delay(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scroll_to with delay parameter."""
        scroll_controller.scroll_to(100, 200, delay=0.1)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1

    def test_scroll_to_negative_x(self, scroll_controller: ScrollController) -> None:
        """Test that scroll_to with negative x raises VNCInputError."""
        with pytest.raises(VNCInputError):
            scroll_controller.scroll_to(-1, 100)

    def test_scroll_to_negative_y(self, scroll_controller: ScrollController) -> None:
        """Test that scroll_to with negative y raises VNCInputError."""
        with pytest.raises(VNCInputError):
            scroll_controller.scroll_to(100, -1)

    def test_scroll_to_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that scroll_to when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = ScrollController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.scroll_to(100, 200)


class TestScrollEdgeCases:
    """Edge case tests for ScrollController."""

    def test_scroll_up_then_down(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling up then down."""
        scroll_controller.scroll_up(3)
        up_count = mock_vnc_connection.send_pointer_event.call_count
        mock_vnc_connection.reset_mock()
        scroll_controller.scroll_down(3)
        down_count = mock_vnc_connection.send_pointer_event.call_count
        assert up_count >= 3
        assert down_count >= 3

    def test_multiple_scroll_to_positions(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling at multiple positions."""
        scroll_controller.scroll_to(100, 100)
        scroll_controller.scroll_to(200, 200)
        scroll_controller.scroll_to(300, 300)
        assert mock_vnc_connection.send_pointer_event.call_count >= 3

    def test_alternating_up_down_scrolls(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test alternating scroll up and down."""
        scroll_controller.scroll_up(2)
        scroll_controller.scroll_down(2)
        scroll_controller.scroll_up(2)
        assert mock_vnc_connection.send_pointer_event.call_count >= 6

    def test_scroll_maximum_values(
        self, scroll_controller: ScrollController, mock_vnc_connection: Mock
    ) -> None:
        """Test scrolling with maximum valid values."""
        scroll_controller.scroll_to(65535, 65535)
        assert mock_vnc_connection.send_pointer_event.call_count >= 1
