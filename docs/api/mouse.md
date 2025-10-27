# Mouse Controller API Reference

The `MouseController` class provides comprehensive mouse/pointer control for remote VNC servers.

## Overview

The mouse controller enables:
- Clicking at specific coordinates
- Moving the cursor
- Dragging operations
- Getting current mouse position
- Support for left, right, and middle mouse buttons
- Optional timing control for each operation

## Class: MouseController

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    vnc.mouse.left_click(100, 100)
```

## Methods

### left_click(x, y, delay=0)

Perform a left mouse button click at the specified coordinates.

**Parameters:**
- `x` (int, optional): X coordinate (0-65535). If None, uses current position.
- `y` (int, optional): Y coordinate (0-65535). If None, uses current position.
- `delay` (float): Delay in seconds after operation (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If coordinates are invalid (negative or out of bounds)
- `VNCStateError`: If not connected to VNC server

**Example:**
```python
# Click at specific position
vnc.mouse.left_click(100, 100)

# Click at current position
vnc.mouse.left_click()

# Click with delay
vnc.mouse.left_click(100, 100, delay=0.5)
```

### right_click(x, y, delay=0)

Perform a right mouse button click (context menu).

**Parameters:**
- `x` (int, optional): X coordinate
- `y` (int, optional): Y coordinate
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If coordinates invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Right-click to open context menu
vnc.mouse.right_click(200, 200)

# Right-click at current position
vnc.mouse.right_click()
```

### double_click(x, y, delay=0)

Perform a double-click at the specified coordinates.

**Parameters:**
- `x` (int, optional): X coordinate
- `y` (int, optional): Y coordinate
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If coordinates invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Double-click to open file
vnc.mouse.double_click(150, 150)

# Double-click at current position
vnc.mouse.double_click()
```

### move_to(x, y, delay=0)

Move the cursor to absolute screen coordinates without clicking.

**Parameters:**
- `x` (int): X coordinate (required, 0-65535)
- `y` (int): Y coordinate (required, 0-65535)
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If coordinates invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Move cursor to position
vnc.mouse.move_to(100, 100)

# Move with delay
vnc.mouse.move_to(200, 200, delay=0.3)
```

### drag_to(x, y, duration=1.0, delay=0)

Drag from current position to target coordinates.

**Parameters:**
- `x` (int): Target X coordinate (required, 0-65535)
- `y` (int): Target Y coordinate (required, 0-65535)
- `duration` (float): Time to drag over in seconds (default: 1.0)
- `delay` (float): Delay in seconds after operation (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If coordinates invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Drag over 1 second (default)
vnc.mouse.drag_to(300, 300)

# Drag quickly (0.5 seconds)
vnc.mouse.drag_to(300, 300, duration=0.5)

# Drag slowly (2 seconds) with delay
vnc.mouse.drag_to(300, 300, duration=2.0, delay=0.5)
```

### get_position()

Get the current mouse position.

**Returns:** Tuple[int, int] - (x, y) coordinates

**Example:**
```python
x, y = vnc.mouse.get_position()
print(f"Mouse at ({x}, {y})")
```

## Button Constants

The following button constants are available through the `MouseButton` enum:

```python
from vnc_agent_bridge.types.common import MouseButton

MouseButton.LEFT    # Left mouse button (0)
MouseButton.MIDDLE  # Middle mouse button (1)
MouseButton.RIGHT   # Right mouse button (2)
```

## Coordinate System

- **Origin:** Top-left corner is (0, 0)
- **X-axis:** Increases to the right
- **Y-axis:** Increases downward
- **Range:** 0 to 65535 in each dimension
- **Units:** Pixels

## Delay Parameter

All methods support an optional `delay` parameter for timing control:

- `delay=0`: Fast, no delay (default)
- `delay=0.1`: Quick (100ms)
- `delay=0.5`: Normal (500ms)
- `delay=1.0`: Slow (1 second)

Delays are applied **after** the operation completes, useful for:
- Realistic human-like interaction
- Allowing UI to respond
- Timing-dependent operations

## Common Patterns

### Find and Click

```python
# Move to target and click
vnc.mouse.move_to(150, 200, delay=0.2)
vnc.mouse.left_click()
```

### Drag and Drop

```python
# Start position
vnc.mouse.move_to(100, 100)

# Drag to drop location
vnc.mouse.drag_to(200, 200, duration=1.0)
```

### Selection

```python
# Move to start
vnc.mouse.move_to(100, 100)

# Drag to select
vnc.mouse.drag_to(300, 150, duration=0.5)

# Double-click to select all
vnc.mouse.double_click(150, 125)
```

### Click Sequence

```python
# Triple-click to select line
vnc.mouse.left_click(100, 100)
vnc.mouse.left_click(100, 100, delay=0.1)
vnc.mouse.left_click(100, 100, delay=0.1)
```

## Error Handling

```python
from vnc_agent_bridge import VNCInputError, VNCStateError

try:
    vnc.mouse.left_click(-1, 100)  # Invalid coordinate
except VNCInputError as e:
    print(f"Invalid input: {e}")

try:
    vnc.mouse.left_click(100, 100)  # Not connected
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Related

- [KeyboardController API](keyboard.md)
- [ScrollController API](scroll.md)
- [VNCConnection API](connection.md)
- [Main API Reference](../index.md)
