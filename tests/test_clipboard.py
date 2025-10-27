"""Tests for ClipboardController."""

import pytest
from unittest.mock import Mock, patch

from vnc_agent_bridge.core.clipboard import ClipboardController
from vnc_agent_bridge.core.connection import VNCConnection
from vnc_agent_bridge.exceptions import VNCInputError


class TestClipboardController:
    """Test ClipboardController functionality."""

    @pytest.fixture
    def mock_connection(self):
        """Mock VNCConnection for testing."""
        conn = Mock(spec=VNCConnection)
        conn.is_connected = True
        conn.send_clipboard_text = Mock()
        conn.receive_clipboard_text = Mock(return_value=None)
        return conn

    @pytest.fixture
    def clipboard_controller(self, mock_connection):
        """ClipboardController with mock connection."""
        return ClipboardController(mock_connection)

    def test_init(self, mock_connection):
        """Test ClipboardController initialization."""
        controller = ClipboardController(mock_connection)
        assert controller._connection == mock_connection
        assert controller._cached_content is None

    def test_send_text_valid(self, clipboard_controller, mock_connection):
        """Test sending valid text to clipboard."""
        clipboard_controller.send_text("Hello, World!")

        mock_connection.send_clipboard_text.assert_called_once_with("Hello, World!")
        assert clipboard_controller._cached_content == "Hello, World!"

    def test_send_text_with_delay(self, clipboard_controller, mock_connection):
        """Test sending text with delay."""
        with patch("time.sleep") as mock_sleep:
            clipboard_controller.send_text("Test", delay=0.5)

        mock_sleep.assert_called_once_with(0.5)
        mock_connection.send_clipboard_text.assert_called_once_with("Test")

    def test_send_text_empty_string(self, clipboard_controller):
        """Test sending empty string raises error."""
        with pytest.raises(VNCInputError, match="Text cannot be empty"):
            clipboard_controller.send_text("")

    def test_send_text_encoding_error(self, clipboard_controller):
        """Test sending text with unsupported characters."""
        # Create text that can't be encoded in latin-1
        invalid_text = "Hello 😀"  # Emoji not in latin-1

        with pytest.raises(VNCInputError, match="unsupported characters"):
            clipboard_controller.send_text(invalid_text)

    def test_get_text_success(self, clipboard_controller, mock_connection):
        """Test getting text from clipboard successfully."""
        mock_connection.receive_clipboard_text.return_value = "Received text"

        result = clipboard_controller.get_text()

        assert result == "Received text"
        assert clipboard_controller._cached_content == "Received text"
        mock_connection.receive_clipboard_text.assert_called_once()

    def test_get_text_none(self, clipboard_controller, mock_connection):
        """Test getting text when none available."""
        mock_connection.receive_clipboard_text.return_value = None

        result = clipboard_controller.get_text()

        assert result is None
        assert clipboard_controller._cached_content is None

    def test_get_text_with_timeout(self, clipboard_controller, mock_connection):
        """Test getting text with custom timeout."""
        mock_connection.receive_clipboard_text.return_value = "Text"

        result = clipboard_controller.get_text(timeout=2.0)

        assert result == "Text"
        mock_connection.receive_clipboard_text.assert_called_once()

    def test_get_text_negative_timeout(self, clipboard_controller):
        """Test getting text with negative timeout raises error."""
        with pytest.raises(VNCInputError, match="Timeout cannot be negative"):
            clipboard_controller.get_text(timeout=-1.0)

    def test_clear_clipboard(self, clipboard_controller, mock_connection):
        """Test clearing clipboard."""
        # Set some cached content first
        clipboard_controller._cached_content = "Some text"

        clipboard_controller.clear()

        mock_connection.send_clipboard_text.assert_called_once_with("")
        assert clipboard_controller._cached_content is None

    def test_clear_clipboard_with_delay(self, clipboard_controller, mock_connection):
        """Test clearing clipboard with delay."""
        with patch("time.sleep") as mock_sleep:
            clipboard_controller.clear(delay=1.0)

        mock_sleep.assert_called_once_with(1.0)
        mock_connection.send_clipboard_text.assert_called_once_with("")

    def test_has_text_true(self, clipboard_controller):
        """Test has_text returns True when content exists."""
        clipboard_controller._cached_content = "Some text"
        assert clipboard_controller.has_text() is True

    def test_has_text_false_empty(self, clipboard_controller):
        """Test has_text returns False when content is empty."""
        clipboard_controller._cached_content = ""
        assert clipboard_controller.has_text() is False

    def test_has_text_false_none(self, clipboard_controller):
        """Test has_text returns False when content is None."""
        clipboard_controller._cached_content = None
        assert clipboard_controller.has_text() is False

    def test_content_property_with_text(self, clipboard_controller):
        """Test content property returns cached text."""
        clipboard_controller._cached_content = "Cached text"
        assert clipboard_controller.content == "Cached text"

    def test_content_property_empty(self, clipboard_controller):
        """Test content property returns empty string when no content."""
        clipboard_controller._cached_content = None
        assert clipboard_controller.content == ""

    def test_content_property_empty_string(self, clipboard_controller):
        """Test content property returns empty string when empty content."""
        clipboard_controller._cached_content = ""
        assert clipboard_controller.content == ""

    def test_send_text_connection_error(self, mock_connection):
        """Test send_text when connection fails."""
        mock_connection.send_clipboard_text.side_effect = Exception("Connection failed")

        controller = ClipboardController(mock_connection)

        with pytest.raises(Exception, match="Connection failed"):
            controller.send_text("Test")

    def test_get_text_connection_error(self, mock_connection):
        """Test get_text when connection fails."""
        mock_connection.receive_clipboard_text.side_effect = Exception(
            "Connection failed"
        )

        controller = ClipboardController(mock_connection)

        with pytest.raises(Exception, match="Connection failed"):
            controller.get_text()

    def test_clear_connection_error(self, mock_connection):
        """Test clear when connection fails."""
        mock_connection.send_clipboard_text.side_effect = Exception("Connection failed")

        controller = ClipboardController(mock_connection)

        with pytest.raises(Exception, match="Connection failed"):
            controller.clear()

    def test_unicode_text_handling(self, clipboard_controller, mock_connection):
        """Test handling of Unicode text that can be encoded in latin-1."""
        # Latin-1 compatible Unicode text
        text = "Café résumé naïve"
        clipboard_controller.send_text(text)

        mock_connection.send_clipboard_text.assert_called_once_with(text)
        assert clipboard_controller._cached_content == text

    def test_cache_consistency(self, clipboard_controller, mock_connection):
        """Test that cache is properly updated."""
        # Initially no content
        assert clipboard_controller._cached_content is None

        # Send text
        clipboard_controller.send_text("First text")
        assert clipboard_controller._cached_content == "First text"

        # Get text (mock returns different content)
        mock_connection.receive_clipboard_text.return_value = "Second text"
        result = clipboard_controller.get_text()
        assert result == "Second text"
        assert clipboard_controller._cached_content == "Second text"

        # Clear
        clipboard_controller.clear()
        assert clipboard_controller._cached_content is None

    def test_delay_zero_no_sleep(self, clipboard_controller):
        """Test that delay=0 doesn't call sleep."""
        with patch("time.sleep") as mock_sleep:
            clipboard_controller.send_text("Test", delay=0)

        mock_sleep.assert_not_called()

    def test_delay_negative_no_sleep(self, clipboard_controller):
        """Test that negative delay doesn't call sleep."""
        with patch("time.sleep") as mock_sleep:
            clipboard_controller.send_text("Test", delay=-1.0)

        mock_sleep.assert_not_called()
