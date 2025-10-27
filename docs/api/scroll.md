# Scroll Controller API Reference

The `ScrollController` class provides mouse wheel scrolling control for remote VNC servers.

## Overview

The scroll controller enables:
- Scrolling up and down
- Scrolling at specific screen positions
- Configurable scroll amount (number of ticks)
- Optional timing control for each operation

## Class: ScrollController

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    vnc.scroll.scroll_up(amount=5)
    vnc.scroll.scroll_down(amount=3)
    vnc.scroll.scroll_to(400, 300)
```

## Methods

### scroll_up(amount=3, delay=0)

Scroll up using mouse wheel.

**Parameters:**
- `amount` (int): Number of scroll ticks (default: 3)
- `delay` (float): Delay in seconds after operation (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If amount is negative
- `VNCStateError`: If not connected to VNC server

**Example:**
```python
# Scroll up (default 3 ticks)
vnc.scroll.scroll_up()

# Scroll up more
vnc.scroll.scroll_up(amount=10)

# Scroll up with delay
vnc.scroll.scroll_up(amount=5, delay=0.3)
```

### scroll_down(amount=3, delay=0)

Scroll down using mouse wheel.

**Parameters:**
- `amount` (int): Number of scroll ticks (default: 3)
- `delay` (float): Delay in seconds after operation (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If amount is negative
- `VNCStateError`: If not connected

**Example:**
```python
# Scroll down (default 3 ticks)
vnc.scroll.scroll_down()

# Scroll down more
vnc.scroll.scroll_down(amount=5)

# Scroll down with delay
vnc.scroll.scroll_down(amount=10, delay=0.5)
```

### scroll_to(x, y, delay=0)

Scroll at a specific screen position.

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
# Scroll at center of screen
vnc.scroll.scroll_to(400, 300)

# Scroll at specific window
vnc.scroll.scroll_to(500, 400, delay=0.3)

# Scroll at top of screen
vnc.scroll.scroll_to(400, 100)
```

## Scroll Amount

The `amount` parameter specifies the number of scroll wheel "ticks" or "clicks":

- **1-3**: Small scrolls (single line or small amount)
- **5-10**: Medium scrolls (few lines)
- **10+**: Large scrolls (multiple screens)

Typical values:
- `amount=1`: Minimum scroll
- `amount=3`: Default (one standard scroll)
- `amount=5`: Page-like scroll
- `amount=10`: Large scroll (10 lines)

## Coordinate System

When using `scroll_to()`, coordinates represent the position on screen where scrolling occurs:

- **X-axis:** 0 (left) to 65535 (right)
- **Y-axis:** 0 (top) to 65535 (bottom)
- **Common positions:**
  - Center: (32768, 32768) or approximate (400, 300)
  - Top-left: (0, 0)
  - Top-right: (65535, 0)
  - Bottom-left: (0, 65535)
  - Bottom-right: (65535, 65535)

## Common Patterns

### Scroll Page

```python
# Scroll down one page
vnc.scroll.scroll_down(amount=10)

# Scroll up one page
vnc.scroll.scroll_up(amount=10)
```

### Progressive Scrolling

```python
# Scroll gradually
for i in range(5):
    vnc.scroll.scroll_down(amount=2, delay=0.2)
    # Page updates between scrolls
```

### Scroll Specific Area

```python
# Scroll in a specific window/panel
window_center_x = 500
window_center_y = 400

vnc.scroll.scroll_to(window_center_x, window_center_y)
```

### Find Content by Scrolling

```python
# Scroll to find content
while content_not_found:
    vnc.scroll.scroll_down(amount=5, delay=0.5)
    # Check if content visible (would need screen analysis)
```

### Scroll with Mouse Position

```python
# Move to target area and scroll
vnc.mouse.move_to(400, 300)
vnc.scroll.scroll_down(amount=5)

# Or use scroll_to
vnc.scroll.scroll_to(400, 300)
```

### Reset to Top

```python
# Go to top of page
vnc.keyboard.hotkey("ctrl", "home")

# Or scroll up significantly
vnc.scroll.scroll_up(amount=100)
```

### Go to Bottom

```python
# Go to bottom of page
vnc.keyboard.hotkey("ctrl", "end")

# Or scroll down significantly
vnc.scroll.scroll_down(amount=100)
```

## Error Handling

```python
from vnc_agent_bridge import VNCInputError, VNCStateError

try:
    vnc.scroll.scroll_down(amount=-5)  # Invalid amount
except VNCInputError as e:
    print(f"Invalid amount: {e}")

try:
    vnc.scroll.scroll_down(amount=5)  # Not connected
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Delay Parameter

All methods support optional delay for timing:

```python
# Fast scroll
vnc.scroll.scroll_down(amount=5, delay=0)

# Quick scroll
vnc.scroll.scroll_down(amount=5, delay=0.2)

# Standard scroll (allows UI to update)
vnc.scroll.scroll_down(amount=5, delay=0.5)

# Slow scroll
vnc.scroll.scroll_down(amount=5, delay=1.0)
```

## Browser Scrolling

```python
# Scroll down in browser
vnc.scroll.scroll_down(amount=5, delay=0.3)

# Scroll up in browser
vnc.scroll.scroll_up(amount=5, delay=0.3)

# Scroll to search result
vnc.scroll.scroll_to(400, 300)

# Page down equivalent
vnc.scroll.scroll_down(amount=10)

# Page up equivalent
vnc.scroll.scroll_up(amount=10)
```

## Application Scrolling

```python
# Scroll in list box
vnc.scroll.scroll_to(250, 350)
vnc.scroll.scroll_down(amount=3)

# Scroll in document
vnc.scroll.scroll_down(amount=5, delay=0.2)

# Scroll in text editor
vnc.scroll.scroll_to(400, 400)
vnc.scroll.scroll_down(amount=10)
```

## Related

- [MouseController API](mouse.md)
- [KeyboardController API](keyboard.md)
- [VNCConnection API](connection.md)
- [Main API Reference](../index.md)
