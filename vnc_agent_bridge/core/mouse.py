# Mouse Controller for VNC Agent Bridge

import time
from typing import Optional

from ..types.common import Position, MouseButton
from ..exceptions import VNCInputError
from .connection import VNCConnection


class MouseController:
    """Control mouse/pointer operations."""

    def __init__(self, connection: VNCConnection) -> None:
        """Initialize with VNC connection.

        Args:
            connection: VNCConnection instance for protocol communication
        """
        self._connection = connection
        self._current_position: Position = (0, 0)
        self._button_mask = 0

    def left_click(
        self, x: Optional[int] = None, y: Optional[int] = None, delay: float = 0
    ) -> None:
        """Click left mouse button at specified or current position.

        Args:
            x: X coordinate (0-65535), uses current position if None
            y: Y coordinate (0-65535), uses current position if None
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        self._click(MouseButton.LEFT, x, y, delay)

    def right_click(
        self, x: Optional[int] = None, y: Optional[int] = None, delay: float = 0
    ) -> None:
        """Click right mouse button at specified or current position.

        Args:
            x: X coordinate (0-65535), uses current position if None
            y: Y coordinate (0-65535), uses current position if None
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        self._click(MouseButton.RIGHT, x, y, delay)

    def double_click(
        self, x: Optional[int] = None, y: Optional[int] = None, delay: float = 0
    ) -> None:
        """Double click left mouse button at specified or current position.

        Args:
            x: X coordinate (0-65535), uses current position if None
            y: Y coordinate (0-65535), uses current position if None
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        # First click
        self._click(MouseButton.LEFT, x, y, 0.05)  # Small delay between clicks

        # Second click at same position
        self._click(MouseButton.LEFT, x, y, delay)

    def move_to(self, x: int, y: int, delay: float = 0) -> None:
        """Move mouse to absolute position.

        Args:
            x: X coordinate (0-65535)
            y: Y coordinate (0-65535)
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        self._validate_coordinates(x, y)

        # Send pointer event with no button press (button_mask=0)
        self._connection.send_pointer_event(x, y, 0)

        # Update current position
        self._current_position = (x, y)

        self._apply_delay(delay)

    def drag_to(self, x: int, y: int, duration: float = 1.0, delay: float = 0) -> None:
        """Drag mouse from current position to new position.

        Args:
            x: Target X coordinate (0-65535)
            y: Target Y coordinate (0-65535)
            duration: Time in seconds to perform the drag
            delay: Delay in seconds after operation

        Raises:
            VNCInputError: If coordinates are invalid
            VNCStateError: If not connected
        """
        self._validate_coordinates(x, y)

        start_x, start_y = self._current_position

        # Press left button down at current position
        self._connection.send_pointer_event(
            start_x, start_y, 1 << MouseButton.LEFT.value
        )
        self._button_mask |= 1 << MouseButton.LEFT.value

        # Calculate drag path (simple linear interpolation)
        steps = max(1, int(duration * 10))  # 10 steps per second
        for i in range(steps + 1):
            t = i / steps
            current_x = int(start_x + (x - start_x) * t)
            current_y = int(start_y + (y - start_y) * t)

            self._connection.send_pointer_event(current_x, current_y, self._button_mask)

            if i < steps:  # Don't sleep on last step
                time.sleep(duration / steps)

        # Release button at final position
        self._connection.send_pointer_event(x, y, 0)
        self._button_mask = 0
        self._current_position = (x, y)

        self._apply_delay(delay)

    def get_position(self) -> Position:
        """Get current mouse position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return self._current_position

    def _click(
        self, button: MouseButton, x: Optional[int], y: Optional[int], delay: float
    ) -> None:
        """Internal method to perform a button click.

        Args:
            button: Mouse button to click
            x: X coordinate or None for current position
            y: Y coordinate or None for current position
            delay: Delay after operation
        """
        from ..exceptions import VNCStateError

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        # Use current position if coordinates not specified
        click_x = x if x is not None else self._current_position[0]
        click_y = y if y is not None else self._current_position[1]

        self._validate_coordinates(click_x, click_y)

        # Move to position if different from current
        if (click_x, click_y) != self._current_position:
            self._connection.send_pointer_event(click_x, click_y, 0)
            self._current_position = (click_x, click_y)

        # Press button down
        button_mask = 1 << button.value
        self._connection.send_pointer_event(click_x, click_y, button_mask)
        self._button_mask |= button_mask

        # Small delay for realistic click
        time.sleep(0.01)

        # Release button
        self._connection.send_pointer_event(click_x, click_y, 0)
        self._button_mask = 0

        self._apply_delay(delay)

    def _validate_coordinates(self, x: int, y: int) -> None:
        """Validate mouse coordinates.

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
