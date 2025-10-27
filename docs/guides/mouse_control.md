# Mouse Control Guide

Comprehensive guide to mouse and pointer operations with VNC Agent Bridge.

## Overview

The Mouse Controller provides:
- Clicking (left, right, double-click)
- Cursor movement
- Dragging operations
- Position tracking
- Precise coordinate control

## Basic Clicks

### Left Click (Primary Button)

```python
with VNCAgentBridge('localhost') as vnc:
    # Click at specific position
    vnc.mouse.left_click(100, 100)
    
    # Click at current position
    vnc.mouse.left_click()
    
    # Click with timing
    vnc.mouse.left_click(100, 100, delay=0.5)
```

### Right Click (Context Menu)

```python
with VNCAgentBridge('localhost') as vnc:
    # Right-click to open context menu
    vnc.mouse.right_click(200, 200)
    
    # Right-click at current position
    vnc.mouse.right_click()
```

### Double Click

```python
with VNCAgentBridge('localhost') as vnc:
    # Double-click to open file/folder
    vnc.mouse.double_click(150, 150)
    
    # Double-click at current position
    vnc.mouse.double_click()
```

## Cursor Movement

### Move To Position

```python
with VNCAgentBridge('localhost') as vnc:
    # Move to specific coordinates
    vnc.mouse.move_to(300, 400)
    
    # Move with timing
    vnc.mouse.move_to(300, 400, delay=0.3)
    
    # Multiple movements
    vnc.mouse.move_to(100, 100)
    vnc.mouse.move_to(200, 200)
    vnc.mouse.move_to(300, 300)
```

### Get Current Position

```python
with VNCAgentBridge('localhost') as vnc:
    # Get current mouse position
    x, y = vnc.mouse.get_position()
    print(f"Mouse at ({x}, {y})")
```

## Dragging Operations

### Simple Drag

```python
with VNCAgentBridge('localhost') as vnc:
    # Drag from current position to target
    vnc.mouse.drag_to(300, 300)
    
    # Drag over specific time
    vnc.mouse.drag_to(300, 300, duration=1.5)
    
    # Drag with delay
    vnc.mouse.drag_to(300, 300, delay=0.5)
```

### Move and Drag

```python
with VNCAgentBridge('localhost') as vnc:
    # Move to starting position
    vnc.mouse.move_to(100, 100, delay=0.2)
    
    # Then drag to target
    vnc.mouse.drag_to(300, 300, duration=1.0)
```

### Drag and Drop

```python
with VNCAgentBridge('localhost') as vnc:
    import time
    
    # Move to draggable item
    vnc.mouse.move_to(150, 150, delay=0.3)
    
    # Drag to drop location
    vnc.mouse.drag_to(400, 200, duration=1.5, delay=0.5)
    
    # Item is now dropped
```

## Click Patterns

### Single Click Pattern

```python
vnc.mouse.left_click(100, 100)
```

### Double Click Pattern

```python
# Method 1: Use double_click()
vnc.mouse.double_click(100, 100)

# Method 2: Two clicks in quick succession
vnc.mouse.left_click(100, 100, delay=0.05)
vnc.mouse.left_click(100, 100, delay=0.05)
```

### Triple Click (Select Line)

```python
# Click three times to select line
vnc.mouse.left_click(100, 100, delay=0.1)
vnc.mouse.left_click(100, 100, delay=0.1)
vnc.mouse.left_click(100, 100, delay=0.1)
```

### Click Sequence

```python
# Multiple clicks at different positions
positions = [(100, 100), (200, 150), (300, 200)]

for x, y in positions:
    vnc.mouse.left_click(x, y, delay=0.2)
```

## Text Selection

### Select with Drag

```python
with VNCAgentBridge('localhost') as vnc:
    # Click at start of text
    vnc.mouse.left_click(100, 100)
    
    # Drag to end of text to select
    vnc.mouse.drag_to(300, 100, duration=0.5)
```

### Select All with Keyboard

```python
with VNCAgentBridge('localhost') as vnc:
    # Select all (keyboard method)
    vnc.keyboard.hotkey("ctrl", "a")
    
    # Or triple-click to select paragraph
    vnc.mouse.triple_click(150, 200)
```

### Select Line

```python
with VNCAgentBridge('localhost') as vnc:
    # Click at start of line
    vnc.mouse.left_click(50, 200)
    
    # Shift+End to select to end of line
    vnc.keyboard.hotkey("shift", "end")
```

## Finding Elements

### Click by Position

```python
with VNCAgentBridge('localhost') as vnc:
    # You need to know the position (usually from UI analysis)
    vnc.mouse.left_click(button_x, button_y)
```

### Search Pattern (Pseudo-code)

```python
# In a real application, you might use image recognition:
# 1. Capture screen
# 2. Find element by image/text
# 3. Click at found position

with VNCAgentBridge('localhost') as vnc:
    # Example: Click known button location
    SUBMIT_BUTTON_X = 400
    SUBMIT_BUTTON_Y = 500
    
    vnc.mouse.left_click(SUBMIT_BUTTON_X, SUBMIT_BUTTON_Y)
```

## Coordinate Systems

### Understanding Coordinates

```
(0, 0) ──────────────────────────────→ (width, 0)
│
│                                      
│                                      
└──────────────────────────────────────→ (width, height)
```

- **X-axis:** 0 (left) to 65535 (right)
- **Y-axis:** 0 (top) to 65535 (bottom)
- **Origin:** Top-left corner

### Common Screen Positions

```python
with VNCAgentBridge('localhost') as vnc:
    # Center of screen (approximate)
    CENTER_X, CENTER_Y = 32768, 32768
    
    # Top-left
    vnc.mouse.left_click(100, 100)
    
    # Top-right
    vnc.mouse.left_click(65400, 100)
    
    # Bottom-left
    vnc.mouse.left_click(100, 65400)
    
    # Bottom-right
    vnc.mouse.left_click(65400, 65400)
    
    # Center (approximate)
    vnc.mouse.left_click(32768, 32768)
```

## Timing and Animation

### No Delay (Fast)

```python
# Instant clicks for testing
vnc.mouse.left_click(100, 100, delay=0)
```

### Quick Delay (Responsive)

```python
# 100ms delay for quick operations
vnc.mouse.left_click(100, 100, delay=0.1)
```

### Human-like Delay

```python
# 300-500ms delay for realistic interaction
vnc.mouse.left_click(100, 100, delay=0.3)
```

### Smooth Dragging

```python
# Long duration for smooth drag animation
vnc.mouse.drag_to(300, 300, duration=2.0, delay=0.5)
```

## Multi-Step Workflows

### Form Interaction

```python
with VNCAgentBridge('localhost') as vnc:
    # Click first field
    vnc.mouse.left_click(100, 100, delay=0.2)
    
    # Type name
    vnc.keyboard.type_text("John Doe")
    
    # Tab to next field
    vnc.keyboard.press_key("tab", delay=0.1)
    
    # Type email
    vnc.keyboard.type_text("john@example.com")
    
    # Click submit
    vnc.mouse.left_click(300, 300, delay=0.3)
```

### Window Navigation

```python
with VNCAgentBridge('localhost') as vnc:
    # Move window by dragging title bar
    TITLE_BAR_Y = 25
    
    vnc.mouse.move_to(400, TITLE_BAR_Y)
    vnc.mouse.drag_to(600, TITLE_BAR_Y, duration=0.5)
```

### Context Menu Selection

```python
with VNCAgentBridge('localhost') as vnc:
    # Right-click to open menu
    vnc.mouse.right_click(200, 200, delay=0.2)
    
    # Click menu option
    vnc.mouse.left_click(200, 250, delay=0.2)
```

## Error Handling

### Invalid Coordinates

```python
from vnc_agent_bridge import VNCInputError

try:
    vnc.mouse.left_click(-1, 100)  # Invalid negative coordinate
except VNCInputError as e:
    print(f"Invalid position: {e}")
```

### Not Connected

```python
from vnc_agent_bridge import VNCStateError

vnc = VNCAgentBridge('localhost')
try:
    vnc.mouse.left_click(100, 100)  # Not connected yet
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Performance Tips

### Use Appropriate Delays

```python
# Fast for testing
vnc.mouse.left_click(100, 100, delay=0)

# Human-like for automation
vnc.mouse.left_click(100, 100, delay=0.3)
```

### Batch Operations

```python
# Good: Grouped operations
with VNCAgentBridge('localhost') as vnc:
    vnc.mouse.move_to(100, 100)
    vnc.mouse.left_click()
    vnc.keyboard.type_text("text")
```

### Reuse Position Variables

```python
# Good: Store positions
BUTTON_X, BUTTON_Y = 300, 400

with VNCAgentBridge('localhost') as vnc:
    vnc.mouse.left_click(BUTTON_X, BUTTON_Y)
    # Use again...
    vnc.mouse.left_click(BUTTON_X, BUTTON_Y)
```

## Related Guides

- **[Keyboard Input Guide](keyboard_input.md)** - Keyboard operations
- **[Scrolling Guide](scrolling.md)** - Scroll wheel operations
- **[Advanced Guide](advanced.md)** - Complex workflows
- **[Getting Started](getting_started.md)** - Quick start guide
- **[Mouse API Reference](../api/mouse.md)** - Complete API

## Next Steps

1. Try the [Getting Started](getting_started.md) guide
2. Explore [Keyboard Input Guide](keyboard_input.md)
3. Check [Advanced Guide](advanced.md) for complex patterns
4. Review [Mouse API Reference](../api/mouse.md) for all methods
