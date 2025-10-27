# Scroll Controller for VNC Agent Bridge

import time

from ..types.common import ScrollDirection
from ..exceptions import VNCInputError
from .connection import VNCConnection


class ScrollController:
    """Control mouse wheel scrolling operations."""

    def __init__(self, connection: VNCConnection) -> None:
        """Initialize with VNC connection.

        Args:
            connection: VNCConnection instance for protocol communication
        """
        self._connection = connection

    def scroll_up(self, amount: int = 3, delay: float = 0) -> None:
        """Scroll up using mouse wheel.

        Args:
            amount: Number of scroll steps (default 3)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If amount is negative
            VNCStateError: If not connected
        """
        if amount < 0:
            raise VNCInputError(f"Scroll amount must be non-negative: {amount}")

        # Send scroll up events (button 4 in VNC protocol)
        for _ in range(amount):
            self._send_scroll_event(ScrollDirection.UP)
            time.sleep(0.01)  # Small delay between scroll events

        self._apply_delay(delay)

    def scroll_down(self, amount: int = 3, delay: float = 0) -> None:
        """Scroll down using mouse wheel.

        Args:
            amount: Number of scroll steps (default 3)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If amount is negative
            VNCStateError: If not connected
        """
        if amount < 0:
            raise VNCInputError(f"Scroll amount must be non-negative: {amount}")

        # Send scroll down events (button 3 in VNC protocol)
        for _ in range(amount):
            self._send_scroll_event(ScrollDirection.DOWN)
            time.sleep(0.01)  # Small delay between scroll events

        self._apply_delay(delay)

    def scroll_to(self, x: int, y: int, delay: float = 0) -> None:
        """Scroll at specific position (performs scroll down).

        Args:
            x: X coordinate (0-65535)
            y: Y coordinate (0-65535)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        self._validate_coordinates(x, y)

        # Move to position first
        self._connection.send_pointer_event(x, y, 0)

        # Perform scroll down at position (default 3 steps)
        self.scroll_down(3, delay)

    def _send_scroll_event(self, direction: ScrollDirection) -> None:
        """Send scroll button event.

        Args:
            direction: Scroll direction (UP or DOWN)
        """
        # VNC scroll buttons: 3=down, 4=up
        button = direction.value  # ScrollDirection.UP=4, ScrollDirection.DOWN=3
        self._connection.send_pointer_event(0, 0, button)

    def _validate_coordinates(self, x: int, y: int) -> None:
        """Validate coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Raises:
            VNCInputError: If coordinates are invalid
        """
        if x < 0 or y < 0:
            raise VNCInputError(f"Coordinates must be non-negative: ({x}, {y})")

        # VNC coordinates are 16-bit unsigned (0-65535)
        if x > 65535 or y > 65535:
            raise VNCInputError(f"Coordinates must be <= 65535: ({x}, {y})")

    def _apply_delay(self, delay: float) -> None:
        """Apply delay in seconds.

        Args:
            delay: Delay duration
        """
        if delay > 0:
            time.sleep(delay)
