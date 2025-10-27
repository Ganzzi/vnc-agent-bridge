"""Common type definitions for VNC Agent Bridge.

This module defines type aliases and enumerations used throughout the VNC
Agent Bridge library. These types provide semantic meaning and improve code
clarity compared to using raw integers.

Type Aliases:
    - Position: (x, y) coordinate tuple for screen positions

Enumerations:
    - MouseButton: VNC mouse button constants (LEFT, MIDDLE, RIGHT)
    - ScrollDirection: Scroll direction (UP, DOWN)
    - KeyAction: Key event action type (PRESS, RELEASE)
    - DelayType: Type alias for timing parameters

Example:
    Using position type:
        from types.common import Position
        pos: Position = (100, 200)  # x=100, y=200

    Using button enumeration:
        from types.common import MouseButton
        button = MouseButton.LEFT
"""

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
