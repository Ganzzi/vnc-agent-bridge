# Main Facade for VNC Agent Bridge

from typing import Any, Optional

from .connection import VNCConnection
from .mouse import MouseController
from .keyboard import KeyboardController
from .scroll import ScrollController


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

    def connect(self) -> None:
        """Connect to VNC server and initialize controllers."""
        self._connection.connect()

        # Initialize controllers after successful connection
        self._mouse = MouseController(self._connection)
        self._keyboard = KeyboardController(self._connection)
        self._scroll = ScrollController(self._connection)

    def disconnect(self) -> None:
        """Disconnect from VNC server."""
        self._connection.disconnect()

        # Clear controller references
        self._mouse = None
        self._keyboard = None
        self._scroll = None

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
