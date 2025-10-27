"""Screenshot capture operations for VNC screen content.

This module provides the ScreenshotController class that handles screenshot
capture operations from VNC framebuffer data. It supports capturing the full
screen or specific regions, and can save screenshots in multiple image formats
(PNG, JPEG, BMP).

The ScreenshotController works with numpy arrays for efficient image processing
and provides both direct array access and file export capabilities.

Features:
    - Capture full screen or specific regions
    - Save screenshots in PNG, JPEG, BMP formats
    - Convert between numpy arrays and PIL Images
    - Export as bytes for API responses
    - Optional delay before capture
    - Incremental or full framebuffer refresh

Example:
    Capture and save screenshot:
        with VNCAgentBridge('localhost') as vnc:
            # Capture to numpy array
            screenshot = vnc.screenshot.capture()

            # Save to file
            vnc.screenshot.save('screen.png')

            # Capture region
            vnc.screenshot.save_region(
                'window.png',
                x=100, y=100,
                width=400, height=300
            )
"""

import time
import numpy as np
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

from ..types.common import ImageFormat
from .framebuffer import FramebufferManager
from .base_connection import VNCConnectionBase
from ..exceptions import VNCInputError


class ScreenshotController:
    """Handles screenshot capture operations."""

    def __init__(
        self, connection: VNCConnectionBase, framebuffer: FramebufferManager
    ) -> None:
        """Initialize screenshot controller.

        Args:
            connection: VNC connection for protocol communication
            framebuffer: FramebufferManager for screen data access
        """
        self.connection = connection
        self.framebuffer = framebuffer

    def capture(self, incremental: bool = False, delay: float = 0) -> Any:
        """Capture current screen as numpy array.

        Args:
            incremental: Use incremental update (faster) or full refresh
            delay: Wait time before capture in seconds

        Returns:
            RGBA numpy array with shape (height, width, 4)

        Raises:
            ValueError: If framebuffer not initialized
            Exception: If framebuffer update fails
        """
        if delay > 0:
            time.sleep(delay)

        # Request framebuffer update
        self.framebuffer.request_update(incremental=incremental)

        # Read update from server
        rectangles = self.connection.read_framebuffer_update()

        # Process the update
        self.framebuffer.process_update(rectangles)

        # Return copy of framebuffer
        return self.framebuffer.get_buffer()

    def capture_region(
        self, x: int, y: int, width: int, height: int, delay: float = 0
    ) -> Any:
        """Capture specific screen region.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Region width in pixels
            height: Region height in pixels
            delay: Wait time before capture in seconds

        Returns:
            RGBA numpy array with shape (height, width, 4)

        Raises:
            VNCInputError: If coordinates are invalid
            ValueError: If region extends beyond framebuffer bounds
        """
        # Validate coordinates
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise VNCInputError(
                f"Invalid region coordinates: x={x}, y={y}, "
                f"width={width}, height={height}"
            )

        if x + width > self.framebuffer.width or y + height > self.framebuffer.height:
            raise VNCInputError(
                f"Region extends beyond framebuffer bounds: "
                f"({x}, {y}, {width}, {height}) "
                f"exceeds ({self.framebuffer.width}, {self.framebuffer.height})"
            )

        if delay > 0:
            time.sleep(delay)

        # Request update for specific region
        self.framebuffer.request_update(
            incremental=False, x=x, y=y, width=width, height=height
        )

        # Read update from server
        rectangles = self.connection.read_framebuffer_update()

        # Process the update
        self.framebuffer.process_update(rectangles)

        # Return region from framebuffer
        return self.framebuffer.get_region(x, y, width, height)

    def save(
        self,
        filepath: str,
        format: ImageFormat = ImageFormat.PNG,
        incremental: bool = False,
        delay: float = 0,
    ) -> None:
        """Capture and save screenshot to file.

        Args:
            filepath: Output file path
            format: Image format (PNG, JPEG, BMP)
            incremental: Use incremental update for faster capture
            delay: Wait time before capture in seconds

        Raises:
            ValueError: If framebuffer not initialized
            OSError: If file cannot be written
            Exception: If image conversion fails
        """
        # Capture screenshot
        array = self.capture(incremental=incremental, delay=delay)

        # Convert and save
        self._save_array(array, filepath, format)

    def save_region(
        self,
        filepath: str,
        x: int,
        y: int,
        width: int,
        height: int,
        format: ImageFormat = ImageFormat.PNG,
        delay: float = 0,
    ) -> None:
        """Capture and save screen region to file.

        Args:
            filepath: Output file path
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Region width in pixels
            height: Region height in pixels
            format: Image format (PNG, JPEG, BMP)
            delay: Wait time before capture in seconds

        Raises:
            VNCInputError: If coordinates are invalid
            ValueError: If region extends beyond framebuffer bounds
            OSError: If file cannot be written
        """
        # Capture region
        array = self.capture_region(x, y, width, height, delay=delay)

        # Convert and save
        self._save_array(array, filepath, format)

    def to_pil_image(self, array: Any) -> Any:
        """Convert numpy array to PIL Image.

        Args:
            array: RGBA numpy array with shape (height, width, 4)

        Returns:
            PIL Image object in RGBA mode

        Raises:
            ImportError: If PIL/Pillow not installed
            ValueError: If array has invalid shape or dtype
        """
        if Image is None:
            raise ImportError(
                "Pillow is required for image conversion. "
                "Install with: pip install Pillow"
            )

        # Validate array
        if not isinstance(array, np.ndarray):
            raise ValueError(f"Expected numpy array, got {type(array)}")

        if len(array.shape) != 3 or array.shape[2] != 4:
            raise ValueError(
                f"Expected array shape (height, width, 4), got {array.shape}"
            )

        if array.dtype != np.uint8:
            raise ValueError(f"Expected uint8 dtype, got {array.dtype}")

        # Create PIL Image from array
        # PIL expects (height, width, 4) RGBA format
        return Image.fromarray(array, mode="RGBA")

    def to_bytes(self, array: Any, format: ImageFormat = ImageFormat.PNG) -> bytes:
        """Convert numpy array to image bytes.

        Args:
            array: RGBA numpy array with shape (height, width, 4)
            format: Output image format

        Returns:
            Image data as bytes

        Raises:
            ImportError: If PIL/Pillow not installed
            ValueError: If array has invalid shape or dtype
        """
        # Convert to PIL Image
        pil_image = self.to_pil_image(array)

        # Get format string
        format_str = self._get_format_string(format)

        # JPEG doesn't support RGBA, convert to RGB
        if format == ImageFormat.JPEG and pil_image.mode == "RGBA":
            # Create white background
            if Image is None:
                raise ImportError("Pillow is required for image conversion")
            background = Image.new("RGB", pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])  # Use alpha channel
            pil_image = background

        # Save to bytes buffer
        import io

        buffer = io.BytesIO()
        pil_image.save(buffer, format=format_str)
        return buffer.getvalue()

    def _save_array(self, array: Any, filepath: str, format: ImageFormat) -> None:
        """Save numpy array to file.

        Args:
            array: RGBA numpy array
            filepath: Output file path
            format: Image format

        Raises:
            ImportError: If PIL/Pillow not installed
            OSError: If file cannot be written
        """
        # Convert to PIL Image
        pil_image = self.to_pil_image(array)

        # Get format string
        format_str = self._get_format_string(format)

        # JPEG doesn't support RGBA, convert to RGB
        if format == ImageFormat.JPEG and pil_image.mode == "RGBA":
            # Create white background
            if Image is None:
                raise ImportError("Pillow is required for image conversion")
            background = Image.new("RGB", pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])  # Use alpha channel
            pil_image = background

        # Save to file
        pil_image.save(filepath, format=format_str)

    def _get_format_string(self, format: ImageFormat) -> str:
        """Get PIL format string from ImageFormat enum.

        Args:
            format: ImageFormat enum value

        Returns:
            Format string for PIL (e.g., 'PNG', 'JPEG', 'BMP')

        Raises:
            ValueError: If format is not supported
        """
        format_map = {
            ImageFormat.PNG: "PNG",
            ImageFormat.JPEG: "JPEG",
            ImageFormat.BMP: "BMP",
        }

        if format not in format_map:
            raise ValueError(f"Unsupported image format: {format}")

        return format_map[format]
