# Common type definitions for VNC Agent Bridge

from enum import IntEnum
from typing import Tuple, Union

# Position type for coordinates
Position = Tuple[int, int]


# Mouse button enumeration
class MouseButton(IntEnum):
    """Mouse button constants for VNC protocol."""

    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


# Scroll direction enumeration
class ScrollDirection(IntEnum):
    """Scroll direction constants."""

    UP = 0
    DOWN = 1


# Key action enumeration
class KeyAction(IntEnum):
    """Key action types for keyboard operations."""

    PRESS = 0
    RELEASE = 1
    HOLD = 2


# Delay type for timing control
DelayType = Union[int, float]

# Key type for flexible key input
KeyType = Union[str, int]

# Button type for mouse operations
ButtonType = Union[str, int, MouseButton]

__all__ = [
    "Position",
    "MouseButton",
    "ScrollDirection",
    "KeyAction",
    "DelayType",
    "KeyType",
    "ButtonType",
]
