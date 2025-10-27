# Scrolling Guide

Comprehensive guide to scroll wheel operations with VNC Agent Bridge.

## Overview

The Scroll Controller provides:
- Scroll up and down
- Scroll to specific position
- Direction control
- Amount specification
- Timing control

## Basic Scrolling

### Scroll Down

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll down once
    vnc.scroll.down()
    
    # Scroll down 5 times
    vnc.scroll.down(amount=5)
    
    # Scroll down with delay
    vnc.scroll.down(amount=3, delay=0.2)
```

### Scroll Up

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll up once
    vnc.scroll.up()
    
    # Scroll up 5 times
    vnc.scroll.up(amount=5)
    
    # Scroll up with delay
    vnc.scroll.up(amount=3, delay=0.2)
```

## Understanding Scroll Amount

### Amount = Wheel Clicks

The `amount` parameter represents number of wheel click units to scroll.

```python
with VNCAgentBridge('localhost') as vnc:
    # 1 click (minimal scroll)
    vnc.scroll.down(amount=1)
    
    # 3 clicks (typical scroll)
    vnc.scroll.down(amount=3)
    
    # 10 clicks (large scroll)
    vnc.scroll.down(amount=10)
```

### Typical Amounts

| Amount | Use Case |
|--------|----------|
| 1-2 | Fine-tuned scrolling, reading |
| 3-5 | Normal browsing |
| 5-10 | Quick page navigation |
| 10+ | Large jumps in content |

## Scroll Positioning

### Scroll to Position

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll to y-coordinate
    vnc.scroll.to_position(100)  # Scroll to top region
    
    # Scroll to middle
    vnc.scroll.to_position(360)
    
    # Scroll to bottom
    vnc.scroll.to_position(600)
```

### Position with Delay

```python
with VNCAgentBridge('localhost') as vnc:
    vnc.scroll.to_position(200, delay=0.3)
```

## Web Browser Scrolling

### Page Navigation

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll through page
    vnc.scroll.down(amount=5, delay=0.2)
    
    # Read more content
    vnc.scroll.down(amount=3, delay=0.2)
    
    # Scroll back up
    vnc.scroll.up(amount=5, delay=0.2)
```

### Find Element by Scrolling

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll until element is visible
    for _ in range(10):
        vnc.scroll.down(amount=2, delay=0.3)
        # Check if element visible (would require vision/OCR)
        # If visible, break
```

### Pagination

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll to bottom for "Load More"
    vnc.scroll.to_position(800, delay=0.2)
    
    # Click load more button
    vnc.mouse.left_click(400, 750, delay=0.3)
    
    # Scroll back up to read new content
    vnc.scroll.to_position(200, delay=0.2)
```

## Document Reading

### Long Document Navigation

```python
with VNCAgentBridge('localhost') as vnc:
    # Start at top
    vnc.scroll.to_position(0, delay=0.2)
    
    # Read section 1
    import time
    time.sleep(2)  # Read for 2 seconds
    
    # Move to section 2
    vnc.scroll.down(amount=5, delay=0.2)
    
    # Read section 2
    time.sleep(2)
    
    # Move to section 3
    vnc.scroll.down(amount=5, delay=0.2)
    
    # Read section 3
    time.sleep(2)
```

### Page Scrolling Pattern

```python
with VNCAgentBridge('localhost') as vnc:
    # Read first page
    vnc.scroll.to_position(0)
    
    # Scroll to next page
    vnc.scroll.down(amount=10, delay=0.5)
    
    # Scroll to next page
    vnc.scroll.down(amount=10, delay=0.5)
```

## Application-Specific Examples

### Dropdown Menu

```python
with VNCAgentBridge('localhost') as vnc:
    # Click dropdown
    vnc.mouse.left_click(100, 100, delay=0.3)
    
    # Scroll down in dropdown
    vnc.scroll.down(amount=3, delay=0.2)
    
    # Click option
    vnc.mouse.left_click(100, 150, delay=0.2)
```

### List Selection

```python
with VNCAgentBridge('localhost') as vnc:
    # Move to list
    vnc.mouse.move(200, 200, delay=0.2)
    
    # Scroll through list
    vnc.scroll.down(amount=5, delay=0.3)
    
    # Select item
    vnc.mouse.left_click(200, 250, delay=0.2)
```

### Data Table Navigation

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll right in table (using horizontal scroll)
    # Most applications: right-click or use keyboard
    vnc.keyboard.hotkey("shift", "right")
    
    # Scroll down in table
    vnc.scroll.down(amount=3, delay=0.2)
    
    # Scroll down more
    vnc.scroll.down(amount=3, delay=0.2)
```

### Chat/Message Window

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll up to read history
    vnc.scroll.up(amount=10, delay=0.2)
    
    # Read messages
    import time
    time.sleep(1)
    
    # Scroll to bottom for new messages
    vnc.scroll.to_position(800, delay=0.2)
    
    # Type reply
    vnc.keyboard.type_text("Reply message", delay=0.05)
    vnc.keyboard.press_key("return", delay=0.2)
```

### IDE/Code Editor

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll through code
    vnc.scroll.down(amount=5, delay=0.2)
    
    # Find function using Ctrl+F
    vnc.keyboard.hotkey("ctrl", "f", delay=0.3)
    vnc.keyboard.type_text("function_name", delay=0.05)
    vnc.keyboard.press_key("return", delay=0.2)
    
    # Scroll to see context
    vnc.scroll.up(amount=2, delay=0.2)
```

## Timing Strategies

### No Delay (Fast Scrolling)

```python
with VNCAgentBridge('localhost') as vnc:
    # For automated testing
    vnc.scroll.down(amount=10, delay=0)
```

### With Delay (Human-like)

```python
with VNCAgentBridge('localhost') as vnc:
    # Natural scrolling pace
    vnc.scroll.down(amount=5, delay=0.3)
```

### Slow Reading Pace

```python
with VNCAgentBridge('localhost') as vnc:
    import time
    
    # Scroll and read
    vnc.scroll.down(amount=3, delay=0.3)
    time.sleep(1)  # Read content
    
    # Scroll and read
    vnc.scroll.down(amount=3, delay=0.3)
    time.sleep(1)  # Read content
```

## Common Scroll Workflows

### Browse and Click

```python
with VNCAgentBridge('localhost') as vnc:
    # Start at top
    vnc.scroll.to_position(0, delay=0.2)
    
    # Scroll to find item
    vnc.scroll.down(amount=3, delay=0.3)
    vnc.scroll.down(amount=3, delay=0.3)
    
    # Click found item
    vnc.mouse.left_click(200, 250, delay=0.2)
```

### Multi-Step Form Completion

```python
with VNCAgentBridge('localhost') as vnc:
    # Fill first field
    vnc.mouse.left_click(100, 100, delay=0.2)
    vnc.keyboard.type_text("Value 1", delay=0.05)
    
    # Scroll to next field
    vnc.scroll.down(amount=2, delay=0.2)
    
    # Fill second field
    vnc.mouse.left_click(100, 200, delay=0.2)
    vnc.keyboard.type_text("Value 2", delay=0.05)
    
    # Scroll to submit button
    vnc.scroll.down(amount=2, delay=0.2)
    
    # Click submit
    vnc.mouse.left_click(100, 300, delay=0.2)
```

### Content Search

```python
with VNCAgentBridge('localhost') as vnc:
    # Start at top
    vnc.scroll.to_position(0, delay=0.2)
    
    # Search for content by scrolling
    found = False
    for _ in range(20):
        # Would check if target visible here
        vnc.scroll.down(amount=3, delay=0.2)
        if found:  # Pseudo-code
            break
```

## Scroll Combinations

### Scroll + Mouse Movement

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll to area
    vnc.scroll.down(amount=5, delay=0.3)
    
    # Move mouse to element
    vnc.mouse.move(200, 250, delay=0.2)
    
    # Click
    vnc.mouse.left_click(200, 250, delay=0.2)
```

### Scroll + Keyboard

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll through list
    vnc.scroll.down(amount=3, delay=0.2)
    
    # Select with keyboard
    vnc.keyboard.press_key("down", delay=0.1)
    vnc.keyboard.press_key("down", delay=0.1)
    
    # Confirm selection
    vnc.keyboard.press_key("return", delay=0.2)
```

## Error Handling

### Invalid Position

```python
from vnc_agent_bridge import VNCInputError

try:
    vnc.scroll.to_position(-100)  # Invalid position
except VNCInputError as e:
    print(f"Invalid scroll position: {e}")
```

### Not Connected

```python
from vnc_agent_bridge import VNCStateError

vnc = VNCAgentBridge('localhost')
try:
    vnc.scroll.down()
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Performance Tips

### Batch Scrolling

```python
# Good: Group scroll operations
with VNCAgentBridge('localhost') as vnc:
    vnc.scroll.down(amount=10, delay=0.2)
    vnc.mouse.left_click(200, 300, delay=0.2)
```

### Scroll Efficiency

```python
# Less efficient: Multiple small scrolls
vnc.scroll.down(amount=1)
vnc.scroll.down(amount=1)
vnc.scroll.down(amount=1)

# More efficient: Single large scroll
vnc.scroll.down(amount=3)
```

### Position Accuracy

```python
# When exact position needed
vnc.scroll.to_position(250, delay=0.3)

# When approximate position acceptable
vnc.scroll.down(amount=5, delay=0.2)
```

## Troubleshooting

### Scroll Not Working

```python
# Check connection first
with VNCAgentBridge('localhost') as vnc:
    # Verify connected
    vnc.scroll.down(amount=1, delay=0.5)
```

### Content Not Reaching Target

```python
# Use larger amounts
vnc.scroll.down(amount=10)

# Or use scroll to position
vnc.scroll.to_position(800)
```

### Scroll Direction Confused

```python
# down() scrolls page down (content moves up)
vnc.scroll.down()

# up() scrolls page up (content moves down)
vnc.scroll.up()
```

## Related Guides

- **[Mouse Control Guide](mouse_control.md)** - Mouse operations
- **[Keyboard Input Guide](keyboard_input.md)** - Keyboard operations
- **[Advanced Guide](advanced.md)** - Complex workflows
- **[Getting Started](getting_started.md)** - Quick start guide
- **[Scroll API Reference](../api/scroll.md)** - Complete API

## Next Steps

1. Combine scrolling with [Mouse Control Guide](mouse_control.md)
2. Use with [Keyboard Input Guide](keyboard_input.md)
3. Check [Advanced Guide](advanced.md) for complex patterns
4. Review [Scroll API Reference](../api/scroll.md) for all methods
