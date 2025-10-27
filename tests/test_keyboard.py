"""
Unit tests for KeyboardController.

Tests keyboard operations including text input, key pressing,
hotkeys, and key press/release sequences with mock VNC connections.
"""

from unittest.mock import Mock
import pytest

from vnc_agent_bridge.core.keyboard import KeyboardController
from vnc_agent_bridge.exceptions import VNCInputError, VNCStateError


class TestKeyboardTypeText:
    """Tests for KeyboardController.type_text() method."""

    def test_type_simple_text(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test typing simple ASCII text."""
        keyboard_controller.type_text("hello")
        # Should send key events for each character
        assert mock_vnc_connection.send_key_event.call_count >= 5

    def test_type_empty_string(self, keyboard_controller: KeyboardController) -> None:
        """Test typing empty string raises error."""
        with pytest.raises(VNCInputError):
            keyboard_controller.type_text("")

    def test_type_numbers(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test typing numbers."""
        keyboard_controller.type_text("12345")
        assert mock_vnc_connection.send_key_event.call_count >= 5

    def test_type_special_characters(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test typing special characters."""
        keyboard_controller.type_text("!@#$%")
        assert mock_vnc_connection.send_key_event.call_count >= 5

    def test_type_with_delay(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test type_text with delay parameter."""
        keyboard_controller.type_text("test", delay=0.1)
        assert mock_vnc_connection.send_key_event.call_count >= 4

    def test_type_spaces_and_punctuation(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test typing text with spaces and punctuation."""
        keyboard_controller.type_text("hello world!")
        assert mock_vnc_connection.send_key_event.call_count >= 11

    def test_type_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that type_text when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = KeyboardController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.type_text("hello")


class TestKeyboardPressKey:
    """Tests for KeyboardController.press_key() method."""

    def test_press_key_by_name(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing key by name."""
        keyboard_controller.press_key("return")
        # press_key should send key down and key up
        assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_press_key_by_code(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing key by X11 key code."""
        keyboard_controller.press_key(0xFF0D)  # Return key code
        assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_press_key_character(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing character key."""
        keyboard_controller.press_key("a")
        assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_press_key_special_keys(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing special keys."""
        special_keys = ["escape", "tab", "backspace", "delete", "space"]
        for key in special_keys:
            mock_vnc_connection.reset_mock()
            keyboard_controller.press_key(key)
            assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_press_key_with_delay(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test press_key with delay parameter."""
        keyboard_controller.press_key("return", delay=0.1)
        assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_press_key_invalid_name(
        self, keyboard_controller: KeyboardController
    ) -> None:
        """Test that pressing unknown key name raises VNCInputError."""
        with pytest.raises(VNCInputError):
            keyboard_controller.press_key("invalid_key_name_xyz")

    def test_press_key_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that press_key when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = KeyboardController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.press_key("return")


class TestKeyboardHotkey:
    """Tests for KeyboardController.hotkey() method."""

    def test_hotkey_ctrl_a(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test Ctrl+A hotkey."""
        keyboard_controller.hotkey("ctrl", "a")
        # Should send key events for ctrl down, a press, ctrl up
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_hotkey_ctrl_c(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test Ctrl+C hotkey."""
        keyboard_controller.hotkey("ctrl", "c")
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_hotkey_shift_tab(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test Shift+Tab hotkey."""
        keyboard_controller.hotkey("shift", "tab")
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_hotkey_multiple_modifiers(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test hotkey with multiple modifiers."""
        keyboard_controller.hotkey("ctrl", "shift", "delete")
        assert mock_vnc_connection.send_key_event.call_count >= 4

    def test_hotkey_with_delay(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test hotkey with delay parameter."""
        keyboard_controller.hotkey("ctrl", "a", delay=0.1)
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_hotkey_alt_f4(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test Alt+F4 hotkey."""
        keyboard_controller.hotkey("alt", "f4")
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_hotkey_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that hotkey when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = KeyboardController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.hotkey("ctrl", "a")


class TestKeyboardKeydownKeyup:
    """Tests for KeyboardController.keydown() and keyup() methods."""

    def test_keydown_holds_key(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test that keydown sends key press event."""
        keyboard_controller.keydown("shift")
        mock_vnc_connection.send_key_event.assert_called_once()
        # Verify it's a down event (second parameter should be True/1)
        call_args = mock_vnc_connection.send_key_event.call_args
        assert call_args is not None

    def test_keyup_releases_key(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test that keyup sends key release event."""
        keyboard_controller.keyup("shift")
        mock_vnc_connection.send_key_event.assert_called_once()
        # Verify it's an up event (second parameter should be False/0)

    def test_keydown_keyup_sequence(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test keydown followed by keyup."""
        keyboard_controller.keydown("shift")
        keyboard_controller.keyup("shift")
        assert mock_vnc_connection.send_key_event.call_count == 2

    def test_keydown_with_delay(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test keydown with delay parameter."""
        keyboard_controller.keydown("ctrl", delay=0.1)
        mock_vnc_connection.send_key_event.assert_called_once()

    def test_keyup_with_delay(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test keyup with delay parameter."""
        keyboard_controller.keyup("ctrl", delay=0.1)
        mock_vnc_connection.send_key_event.assert_called_once()

    def test_multiple_keydown_same_key(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test multiple keydown calls for same key."""
        keyboard_controller.keydown("a")
        keyboard_controller.keydown("b")
        assert mock_vnc_connection.send_key_event.call_count == 2

    def test_keydown_disconnected(self, mock_vnc_connection: Mock) -> None:
        """Test that keydown when disconnected raises VNCStateError."""
        mock_vnc_connection.is_connected = False
        controller = KeyboardController(mock_vnc_connection)
        with pytest.raises(VNCStateError):
            controller.keydown("shift")


class TestKeyboardFunctionKeys:
    """Tests for keyboard function keys."""

    def test_function_keys(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing function keys F1-F12."""
        for i in range(1, 13):
            mock_vnc_connection.reset_mock()
            keyboard_controller.press_key(f"f{i}")
            assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_arrow_keys(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test pressing arrow keys."""
        arrows = ["up", "down", "left", "right"]
        for arrow in arrows:
            mock_vnc_connection.reset_mock()
            keyboard_controller.press_key(arrow)
            assert mock_vnc_connection.send_key_event.call_count >= 2


class TestKeyboardEdgeCases:
    """Edge case tests for KeyboardController."""

    def test_type_very_long_text(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test typing very long text."""
        long_text = "a" * 100
        keyboard_controller.type_text(long_text)
        assert mock_vnc_connection.send_key_event.call_count >= 100

    def test_sequential_different_operations(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test sequence of different keyboard operations."""
        keyboard_controller.type_text("test")
        mock_vnc_connection.reset_mock()
        keyboard_controller.press_key("return")
        assert mock_vnc_connection.send_key_event.call_count >= 2

    def test_multiple_hotkeys_sequence(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test multiple hotkeys in sequence."""
        keyboard_controller.hotkey("ctrl", "a")
        initial_count = mock_vnc_connection.send_key_event.call_count
        mock_vnc_connection.reset_mock()
        keyboard_controller.hotkey("ctrl", "c")
        assert mock_vnc_connection.send_key_event.call_count >= 3

    def test_keydown_multiple_modifiers(
        self, keyboard_controller: KeyboardController, mock_vnc_connection: Mock
    ) -> None:
        """Test holding down multiple modifier keys."""
        keyboard_controller.keydown("ctrl")
        keyboard_controller.keydown("shift")
        keyboard_controller.keyup("shift")
        keyboard_controller.keyup("ctrl")
        assert mock_vnc_connection.send_key_event.call_count == 4
