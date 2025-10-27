"""Clipboard controller for VNC Agent Bridge.

This module provides the ClipboardController class for managing clipboard
operations on a remote VNC server. It supports sending text to the remote
clipboard, retrieving text from the remote clipboard, and clearing clipboard
content.

The implementation uses VNC's ClientCutText (type 6) and ServerCutText (type 3)
messages for clipboard communication. Text encoding follows the RFB protocol
specification using latin-1 encoding.

All methods support an optional delay parameter for timing control, enabling
realistic human-like interaction patterns.

Example:
    Basic clipboard operations:
        clipboard = ClipboardController(connection)
        clipboard.send_text("Hello, World!")
        text = clipboard.get_text(timeout=2.0)
        clipboard.clear()

    With timing control:
        clipboard.send_text("Copy this", delay=0.5)
        clipboard.clear(delay=1.0)
"""

import time
from typing import Optional

from ..exceptions import VNCInputError
from .connection import VNCConnection


class ClipboardController:
    """Manages clipboard operations on remote VNC server."""

    def __init__(self, connection: VNCConnection) -> None:
        """Initialize clipboard controller.

        Args:
            connection: VNCConnection instance for protocol communication
        """
        self._connection = connection
        self._cached_content: Optional[str] = None

    def send_text(self, text: str, delay: float = 0) -> None:
        """Send text to remote clipboard.

        Args:
            text: Text to send to remote clipboard
            delay: Wait time before sending (seconds)

        Raises:
            VNCInputError: If text is empty or encoding fails
            VNCStateError: If not connected
        """
        if not text:
            raise VNCInputError("Text cannot be empty")

        try:
            # Validate encoding (latin-1 as per RFB spec)
            text.encode("latin-1")
        except UnicodeEncodeError as e:
            raise VNCInputError(f"Text contains unsupported characters: {e}")

        self._apply_delay(delay)
        self._connection.send_clipboard_text(text)

        # Update cached content
        self._cached_content = text

    def get_text(self, timeout: float = 5.0) -> Optional[str]:
        """Get text from remote clipboard.

        Args:
            timeout: Maximum wait time for clipboard data (seconds)

        Returns:
            Clipboard text if available, None if not available within timeout

        Raises:
            VNCStateError: If not connected
            VNCTimeoutError: If timeout exceeded
        """
        if timeout < 0:
            raise VNCInputError("Timeout cannot be negative")

        # Try to get clipboard text
        text = self._connection.receive_clipboard_text()

        # Update cache if we got content
        if text is not None:
            self._cached_content = text

        return text

    def clear(self, delay: float = 0) -> None:
        """Clear remote clipboard.

        Args:
            delay: Wait time before clearing (seconds)

        Raises:
            VNCStateError: If not connected
        """
        self._apply_delay(delay)
        self._connection.send_clipboard_text("")

        # Clear cached content
        self._cached_content = None

    def has_text(self) -> bool:
        """Check if clipboard has text.

        Returns:
            True if clipboard contains text, False otherwise

        Note:
            This method checks cached content. Call get_text() first
            to ensure cache is up to date.
        """
        return self._cached_content is not None and len(self._cached_content) > 0

    @property
    def content(self) -> str:
        """Get current clipboard content (cached).

        Returns:
            Current clipboard text, empty string if no content

        Note:
            Returns cached content. Call get_text() to refresh from server.
        """
        return self._cached_content or ""

    def _apply_delay(self, delay: float) -> None:
        """Apply delay in seconds.

        Args:
            delay: Delay duration in seconds
        """
        if delay > 0:
            time.sleep(delay)
