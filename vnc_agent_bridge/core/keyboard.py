# Keyboard Controller for VNC Agent Bridge

import time
from typing import Union

from ..exceptions import VNCInputError
from .connection import VNCConnection


class KeyboardController:
    """Control keyboard input operations."""

    # X11 key code mappings (KEYSYMs)
    KEY_CODES = {
        # Navigation keys
        "left": 0xFF51,
        "right": 0xFF53,
        "up": 0xFF52,
        "down": 0xFF54,
        "home": 0xFF50,
        "end": 0xFF57,
        "pageup": 0xFF55,
        "pagedown": 0xFF56,
        # Editing keys
        "return": 0xFF0D,
        "enter": 0xFF0D,
        "escape": 0xFF1B,
        "esc": 0xFF1B,
        "tab": 0xFF09,
        "backspace": 0xFF08,
        "delete": 0xFFFF,
        "del": 0xFFFF,
        "space": 0x0020,
        # Function keys
        "f1": 0xFFBE,
        "f2": 0xFFBF,
        "f3": 0xFFC0,
        "f4": 0xFFC1,
        "f5": 0xFFC2,
        "f6": 0xFFC3,
        "f7": 0xFFC4,
        "f8": 0xFFC5,
        "f9": 0xFFC6,
        "f10": 0xFFC7,
        "f11": 0xFFC8,
        "f12": 0xFFC9,
        # Modifier keys
        "shift": 0xFFE1,
        "lshift": 0xFFE1,
        "rshift": 0xFFE2,
        "ctrl": 0xFFE3,
        "lctrl": 0xFFE3,
        "rctrl": 0xFFE4,
        "alt": 0xFFE9,
        "lalt": 0xFFE9,
        "ralt": 0xFFEA,
        "meta": 0xFFED,
        "cmd": 0xFFEB,
        "windows": 0xFFEB,
        "capslock": 0xFFE5,
        "numlock": 0xFF7F,
        "scrolllock": 0xFF14,
    }

    # Modifier keys for hotkey combinations
    MODIFIER_KEYS = {
        "shift",
        "lshift",
        "rshift",
        "ctrl",
        "lctrl",
        "rctrl",
        "alt",
        "lalt",
        "ralt",
        "meta",
        "cmd",
        "windows",
    }

    def __init__(self, connection: VNCConnection) -> None:
        """Initialize with VNC connection.

        Args:
            connection: VNCConnection instance for protocol communication
        """
        self._connection = connection

    def type_text(self, text: str, delay: float = 0) -> None:
        """Type text character by character.

        Args:
            text: Text string to type
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If text contains unsupported characters
            VNCStateError: If not connected
        """
        from ..exceptions import VNCStateError

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        if not text:
            raise VNCInputError("Text cannot be empty")

        for char in text:
            keycode = self._get_keycode(char)
            if keycode is None:
                raise VNCInputError(f"Unsupported character: '{char}'")

            # Press and release each key
            self._connection.send_key_event(keycode, True)  # Key down
            time.sleep(0.01)  # Small delay between press/release
            self._connection.send_key_event(keycode, False)  # Key up

            # Small delay between characters for realistic typing
            time.sleep(0.02)

        self._apply_delay(delay)

    def press_key(self, key: Union[str, int], delay: float = 0) -> None:
        """Press and release single key.

        Args:
            key: Key name (str) or X11 key code (int)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If key is unknown
            VNCStateError: If not connected
        """
        from ..exceptions import VNCStateError

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        keycode = self._get_keycode(key)
        if keycode is None:
            raise VNCInputError(f"Unknown key: {key}")

        # Press and release
        self._connection.send_key_event(keycode, True)  # Key down
        time.sleep(0.01)  # Small delay
        self._connection.send_key_event(keycode, False)  # Key up

        self._apply_delay(delay)

    def hotkey(self, *keys: Union[str, int], delay: float = 0) -> None:
        """Press multiple keys simultaneously (modifier + main key).

        Args:
            *keys: Variable number of key names/codes. Modifiers first, then main key.
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If keys are invalid or no main key provided
            VNCStateError: If not connected

        Example:
            hotkey('ctrl', 'c')  # Ctrl+C
            hotkey('alt', 'f4')  # Alt+F4
        """
        from ..exceptions import VNCStateError

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        if len(keys) < 2:
            raise VNCInputError("Hotkey requires at least 2 keys (modifier + main)")

        # Separate modifiers from main key
        modifier_names = []
        main_key = None

        for key in keys[:-1]:  # All but last are modifiers
            key_name = key.lower() if isinstance(key, str) else str(key)
            modifier_names.append(key_name)

        main_key = keys[-1]  # Last key is main key

        # Validate modifiers
        for mod_name in modifier_names:
            if mod_name not in self.MODIFIER_KEYS:
                raise VNCInputError(f"Invalid modifier key: {mod_name}")

        # Get key codes
        modifier_codes = []
        for mod_name in modifier_names:
            code = self._get_keycode(mod_name)
            if code is None:
                raise VNCInputError(f"Unknown modifier key: {mod_name}")
            modifier_codes.append(code)

        main_code = self._get_keycode(main_key)
        if main_code is None:
            raise VNCInputError(f"Unknown main key: {main_key}")

        # Press all modifiers first
        for code in modifier_codes:
            self._connection.send_key_event(code, True)

        # Small delay
        time.sleep(0.01)

        # Press main key
        self._connection.send_key_event(main_code, True)
        time.sleep(0.01)

        # Release main key
        self._connection.send_key_event(main_code, False)
        time.sleep(0.01)

        # Release modifiers (in reverse order)
        for code in reversed(modifier_codes):
            self._connection.send_key_event(code, False)

        self._apply_delay(delay)

    def keydown(self, key: Union[str, int], delay: float = 0) -> None:
        """Press and hold key down.

        Args:
            key: Key name (str) or X11 key code (int)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If key is unknown
            VNCStateError: If not connected
        """
        from ..exceptions import VNCStateError

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        keycode = self._get_keycode(key)
        if keycode is None:
            raise VNCInputError(f"Unknown key: {key}")

        self._connection.send_key_event(keycode, True)  # Key down only
        self._apply_delay(delay)

    def keyup(self, key: Union[str, int], delay: float = 0) -> None:
        """Release held key.

        Args:
            key: Key name (str) or X11 key code (int)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If key is unknown
            VNCStateError: If not connected
        """
        keycode = self._get_keycode(key)
        if keycode is None:
            raise VNCInputError(f"Unknown key: {key}")

        self._connection.send_key_event(keycode, False)  # Key up only
        self._apply_delay(delay)

    def _get_keycode(self, key: Union[str, int]) -> Union[int, None]:
        """Convert key name or code to X11 KEYSYM.

        Args:
            key: Key name (str) or key code (int)

        Returns:
            X11 KEYSYM value or None if unknown
        """
        if isinstance(key, int):
            return key

        if isinstance(key, str):
            # Handle single characters
            if len(key) == 1:
                return ord(key)

            # Handle named keys
            return self.KEY_CODES.get(key.lower())

        # This should never happen due to type hints, but mypy requires it
        raise ValueError(f"Invalid key type: {type(key)}")

    def _apply_delay(self, delay: float) -> None:
        """Apply delay in seconds.

        Args:
            delay: Delay duration
        """
        if delay > 0:
            time.sleep(delay)
