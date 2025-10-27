"""Main facade for VNC Agent Bridge.

This module provides the primary entry point for interacting with VNC servers.
The VNCAgentBridge class acts as a facade, managing the connection and providing
access to specialized controllers for mouse, keyboard, and scroll operations.

The class supports both context manager (recommended) and manual connection
management patterns.

Example:
    Using context manager (recommended):
        with VNCAgentBridge('localhost', port=5900) as vnc:
            vnc.mouse.left_click(100, 100)
            vnc.keyboard.type_text("text")

    Using manual connection management:
        vnc = VNCAgentBridge('localhost')
        try:
            vnc.connect()
            vnc.mouse.left_click(100, 100)
        finally:
            vnc.disconnect()
"""

from typing import TYPE_CHECKING, Any, Optional

from .connection import VNCConnection
from .mouse import MouseController
from .keyboard import KeyboardController
from .scroll import ScrollController
from vnc_agent_bridge.exceptions import VNCStateError

if TYPE_CHECKING:
    from .framebuffer import FramebufferManager
    from .screenshot import ScreenshotController
    from .video import VideoRecorder


class VNCAgentBridge:
    """Main entry point for VNC Agent Bridge.

    Provides unified access to mouse, keyboard, and scroll controllers
    with automatic connection management.
    """

    def __init__(
        self,
        host: str,
        port: int = 5900,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize VNC bridge.

        Args:
            host: VNC server hostname or IP address
            port: VNC server port (default 5900)
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Connection timeout in seconds
        """
        self._connection = VNCConnection(host, port, username, password, timeout)
        self._mouse: Optional[MouseController] = None
        self._keyboard: Optional[KeyboardController] = None
        self._scroll: Optional[ScrollController] = None
        self._framebuffer: Optional["FramebufferManager"] = None
        self._screenshot: Optional["ScreenshotController"] = None
        self._video: Optional["VideoRecorder"] = None

    def connect(self) -> None:
        """Connect to VNC server and initialize controllers."""
        self._connection.connect()

        # Initialize controllers after successful connection
        self._mouse = MouseController(self._connection)
        self._keyboard = KeyboardController(self._connection)
        self._scroll = ScrollController(self._connection)

        # Initialize framebuffer-dependent components if dependencies available
        try:
            from .framebuffer import FramebufferManager
            from .screenshot import ScreenshotController
            from .video import VideoRecorder
            from ..types.common import FramebufferConfig

            # Create framebuffer config from connection
            config = FramebufferConfig(
                width=1920,  # Default, will be updated by VNC server
                height=1080,  # Default, will be updated by VNC server
                pixel_format=b"",
                name="VNC Screen",
            )

            # Create framebuffer manager
            self._framebuffer = FramebufferManager(self._connection, config)

            # Create screenshot controller
            self._screenshot = ScreenshotController(self._connection, self._framebuffer)

            # Create video recorder
            self._video = VideoRecorder(
                self._connection, self._framebuffer, self._screenshot
            )

        except (ImportError, TypeError, AttributeError):
            # Optional dependencies not available or framebuffer not supported
            # Video features will be unavailable but basic input control works
            pass

    def disconnect(self) -> None:
        """Disconnect from VNC server."""
        self._connection.disconnect()

        # Clear controller references
        self._mouse = None
        self._keyboard = None
        self._scroll = None
        self._framebuffer = None
        self._screenshot = None
        self._video = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to VNC server."""
        return self._connection.is_connected

    @property
    def mouse(self) -> MouseController:
        """Access mouse controller.

        Returns:
            MouseController instance

        Raises:
            RuntimeError: If not connected
        """
        if self._mouse is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._mouse

    @property
    def keyboard(self) -> KeyboardController:
        """Access keyboard controller.

        Returns:
            KeyboardController instance

        Raises:
            RuntimeError: If not connected
        """
        if self._keyboard is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._keyboard

    @property
    def scroll(self) -> ScrollController:
        """Access scroll controller.

        Returns:
            ScrollController instance

        Raises:
            RuntimeError: If not connected
        """
        if self._scroll is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._scroll

    @property
    def screenshot(self) -> "ScreenshotController":
        """Access screenshot controller.

        Returns:
            ScreenshotController instance

        Raises:
            VNCStateError: If screenshot feature not available (dependencies missing)
            RuntimeError: If not connected
        """
        if self._screenshot is None:
            raise VNCStateError(
                "Screenshot feature not available. "
                "Install with: pip install vnc-agent-bridge[capture]"
            )
        return self._screenshot

    @property
    def video(self) -> "VideoRecorder":
        """Access video recorder.

        Returns:
            VideoRecorder instance

        Raises:
            VNCStateError: If video feature not available (dependencies missing)
            RuntimeError: If not connected
        """
        if self._video is None:
            raise VNCStateError(
                "Video feature not available. "
                "Install with: pip install vnc-agent-bridge[video]"
            )
        return self._video

    @property
    def framebuffer(self) -> Optional["FramebufferManager"]:
        """Access framebuffer manager (if available).

        Returns:
            FramebufferManager instance or None if not available
        """
        return self._framebuffer

    def __enter__(self) -> "VNCAgentBridge":
        """Context manager entry - connect automatically."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit - disconnect automatically."""
        self.disconnect()
