"""Abstract base class for VNC connection implementations.

This module defines the VNCConnectionBase abstract class that provides
a common interface for different VNC connection types (TCP, WebSocket, etc.).

The abstract base class ensures that all connection implementations provide
the same interface for sending VNC protocol messages and managing connections.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class VNCConnectionBase(ABC):
    """Abstract base class for VNC connection implementations.

    This class defines the interface that all VNC connection types must implement,
    including TCP connections, WebSocket connections, and future connection types.

    The interface supports the full RFB 3.8 protocol for mouse, keyboard, clipboard,
    and framebuffer operations.
    """

    # VNC Protocol Constants (shared across implementations)
    PROTOCOL_VERSION = b"RFB 003.008\n"
    POINTER_EVENT = 5
    KEY_EVENT = 4
    FRAMEBUFFER_UPDATE_REQUEST = 3
    SET_ENCODINGS = 2
    FRAMEBUFFER_UPDATE = 0
    SET_PIXEL_FORMAT = 0
    CLIPBOARD_TEXT_CLIENT = 6
    CLIPBOARD_TEXT_SERVER = 3

    @abstractmethod
    def connect(self) -> None:
        """Connect to VNC server and complete handshake.

        Raises:
            VNCConnectionError: If connection fails
            VNCTimeoutError: If connection times out
            VNCProtocolError: If protocol handshake fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection gracefully."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to VNC server."""
        pass

    @abstractmethod
    def send_pointer_event(self, x: int, y: int, button_mask: int) -> None:
        """Send mouse pointer event to server.

        Args:
            x: X coordinate (0-65535)
            y: Y coordinate (0-65535)
            button_mask: Button state mask (bitfield)

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        pass

    @abstractmethod
    def send_key_event(self, keycode: int, pressed: bool) -> None:
        """Send keyboard event to server.

        Args:
            keycode: X11 KEYSYM value
            pressed: True for key down, False for key up

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        pass

    @abstractmethod
    def request_framebuffer_update(
        self,
        incremental: bool = True,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Request framebuffer update from server.

        Args:
            incremental: True for incremental update, False for full refresh
            x: X coordinate of update region
            y: Y coordinate of update region
            width: Width of update region (None for full width)
            height: Height of update region (None for full height)

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        pass

    @abstractmethod
    def read_framebuffer_update(self) -> List[Tuple[int, int, int, int, bytes]]:
        """Read framebuffer update response from server.

        Returns:
            List of rectangles: [(x, y, width, height, pixel_data), ...]

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If receive fails
            VNCProtocolError: If message format is invalid
        """
        pass

    @abstractmethod
    def set_encodings(self, encodings: List[int]) -> None:
        """Tell server which encodings we support.

        Args:
            encodings: List of encoding numbers we support

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        pass

    @abstractmethod
    def send_clipboard_text(self, text: str) -> None:
        """Send clipboard text to server.

        Args:
            text: Text to send to remote clipboard

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If send fails
        """
        pass

    @abstractmethod
    def receive_clipboard_text(self) -> Optional[str]:
        """Receive clipboard text from server.

        Returns:
            Clipboard text if available, None if no clipboard message pending

        Raises:
            VNCStateError: If not connected
            VNCConnectionError: If receive fails
        """
        pass
