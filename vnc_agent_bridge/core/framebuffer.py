"""Framebuffer management for VNC screen capture.

This module provides the FramebufferManager class that handles VNC framebuffer
state, updates, and pixel data management. It works with numpy arrays for
efficient image processing and supports real-time screen updates.

The framebuffer stores screen data as RGBA numpy arrays and handles rectangle
updates from the VNC server. It provides methods for capturing regions,
checking for updates, and managing framebuffer state.

Example:
    Initialize and use framebuffer manager:
        config = FramebufferConfig(width=1920, height=1080, ...)
        fb = FramebufferManager(connection, config)
        fb.initialize_buffer()

        # Request and process updates
        fb.request_update()
        rectangles = connection.read_framebuffer_update()
        fb.process_update(rectangles)

        # Get current screen data
        screen = fb.get_buffer()
"""

import numpy as np
from typing import Optional, List, Tuple, Any

from ..types.common import FramebufferConfig
from .base_connection import VNCConnectionBase


class FramebufferManager:
    """Manages framebuffer state and updates."""

    def __init__(self, connection: VNCConnectionBase, config: FramebufferConfig):
        """Initialize framebuffer manager.

        Args:
            connection: VNC connection for protocol communication
            config: Framebuffer configuration
        """
        self.connection = connection
        self.config = config
        self._buffer: Optional[Any] = None
        self._is_dirty = False

    def initialize_buffer(self) -> None:
        """Create initial framebuffer array."""
        # Create RGBA buffer (4 bytes per pixel)
        self._buffer = np.zeros(
            (self.config.height, self.config.width, 4), dtype=np.uint8
        )
        self._is_dirty = False

    def request_update(
        self,
        incremental: bool = True,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Request framebuffer update.

        Args:
            incremental: True for incremental update, False for full refresh
            x: X coordinate of update region
            y: Y coordinate of update region
            width: Width of update region (None for full width)
            height: Height of update region (None for full height)
        """
        if width is None:
            width = self.config.width
        if height is None:
            height = self.config.height

        self.connection.request_framebuffer_update(
            incremental=incremental, x=x, y=y, width=width, height=height
        )

    def process_update(
        self, rectangles: List[Tuple[int, int, int, int, bytes]]
    ) -> None:
        """Process received framebuffer update.

        Args:
            rectangles: List of (x, y, width, height, pixel_data) tuples
        """
        if self._buffer is None:
            raise RuntimeError("Framebuffer not initialized")

        for x, y, width, height, pixel_data in rectangles:
            self.update_rectangle(x, y, width, height, pixel_data)

        self._is_dirty = True

    def update_rectangle(
        self, x: int, y: int, width: int, height: int, pixel_data: bytes
    ) -> None:
        """Update specific rectangle in framebuffer.

        Args:
            x: X coordinate of rectangle
            y: Y coordinate of rectangle
            width: Rectangle width
            height: Rectangle height
            pixel_data: Raw pixel data (RGBA format)
        """
        if self._buffer is None:
            raise RuntimeError("Framebuffer not initialized")

        # Convert bytes to numpy array and reshape
        # Assuming 32-bit RGBA pixels (4 bytes per pixel)
        expected_size = width * height * 4
        if len(pixel_data) != expected_size:
            raise ValueError(
                f"Pixel data size mismatch: expected {expected_size}, "
                f"got {len(pixel_data)}"
            )

        # Reshape pixel data to (height, width, 4)
        pixels = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width, 4))

        # Update the buffer region
        self._buffer[y : y + height, x : x + width] = pixels

    def get_buffer(self) -> Any:
        """Get current framebuffer as numpy array.

        Returns:
            RGBA numpy array with shape (height, width, 4)
        """
        if self._buffer is None:
            raise RuntimeError("Framebuffer not initialized")
        return self._buffer.copy()

    def get_region(self, x: int, y: int, width: int, height: int) -> Any:
        """Get specific region of framebuffer.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Region width
            height: Region height

        Returns:
            RGBA numpy array with shape (height, width, 4)
        """
        if self._buffer is None:
            raise RuntimeError("Framebuffer not initialized")

        # Validate bounds
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid region coordinates")

        if x + width > self.config.width or y + height > self.config.height:
            raise ValueError("Region extends beyond framebuffer bounds")

        return self._buffer[y : y + height, x : x + width].copy()

    def reset(self) -> None:
        """Reset framebuffer state."""
        self._buffer = None
        self._is_dirty = False

    @property
    def width(self) -> int:
        """Framebuffer width."""
        return self.config.width

    @property
    def height(self) -> int:
        """Framebuffer height."""
        return self.config.height

    @property
    def is_dirty(self) -> bool:
        """Check if buffer has been updated since last check."""
        dirty = self._is_dirty
        self._is_dirty = False  # Reset dirty flag
        return dirty
