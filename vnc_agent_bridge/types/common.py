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

from enum import IntEnum, Enum
from typing import Tuple, Union, TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    import numpy as np
    from PIL import Image
else:
    np = None  # type: ignore
    Image = None  # type: ignore

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


# Image formats for screenshot export
class ImageFormat(str, Enum):
    """Image format constants for screenshot export."""

    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"


# Frame data type for numpy arrays
FrameData = Any  # np.ndarray with shape: (height, width, 4) RGBA uint8

# Image type union for flexible image handling
ImageType = Any  # Union[np.ndarray, Image.Image]


# Video frame dataclass for recording
@dataclass
class VideoFrame:
    """Single video frame with metadata."""

    timestamp: float
    data: Any  # np.ndarray
    frame_number: int


# Framebuffer configuration
@dataclass
class FramebufferConfig:
    """Framebuffer configuration."""

    width: int
    height: int
    pixel_format: bytes
    name: str


__all__ = [
    "Position",
    "MouseButton",
    "ScrollDirection",
    "KeyAction",
    "DelayType",
    "KeyType",
    "ButtonType",
    "ImageFormat",
    "FrameData",
    "ImageType",
    "VideoFrame",
    "FramebufferConfig",
]
