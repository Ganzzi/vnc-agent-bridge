# Keyboard Input Guide

Comprehensive guide to keyboard input operations with VNC Agent Bridge.

## Overview

The Keyboard Controller provides:
- Text typing with character-by-character control
- Individual key presses
- Key combinations (hotkeys)
- Key hold/release events
- Support for special keys, function keys, and modifiers

## Basic Text Input

### Type Simple Text

```python
with VNCAgentBridge('localhost') as vnc:
    # Type text string
    vnc.keyboard.type_text("Hello World")
    
    # Type with delay between characters
    vnc.keyboard.type_text("Careful typing", delay=0.1)
```

### Type Special Characters

```python
with VNCAgentBridge('localhost') as vnc:
    # Email address
    vnc.keyboard.type_text("user@example.com")
    
    # URL
    vnc.keyboard.type_text("https://example.com")
    
    # Numbers and symbols
    vnc.keyboard.type_text("Phone: 555-1234")
    
    # Unicode (if supported)
    vnc.keyboard.type_text("Café")
```

### Type with Timing

```python
with VNCAgentBridge('localhost') as vnc:
    # Fast typing (no delay)
    vnc.keyboard.type_text("fast", delay=0)
    
    # Slow typing (human-like)
    vnc.keyboard.type_text("slow", delay=0.15)
    
    # Very slow typing
    vnc.keyboard.type_text("very slow", delay=0.3)
```

## Individual Key Presses

### Press Special Keys

```python
with VNCAgentBridge('localhost') as vnc:
    # Navigation
    vnc.keyboard.press_key("return")  # Enter
    vnc.keyboard.press_key("escape")  # Esc
    vnc.keyboard.press_key("tab")     # Tab
    
    # Editing
    vnc.keyboard.press_key("backspace")  # Backspace
    vnc.keyboard.press_key("delete")     # Delete
    vnc.keyboard.press_key("space")      # Space
```

### Press Function Keys

```python
with VNCAgentBridge('localhost') as vnc:
    # Function keys
    vnc.keyboard.press_key("f1")   # Help
    vnc.keyboard.press_key("f2")   # Rename
    vnc.keyboard.press_key("f5")   # Refresh
    vnc.keyboard.press_key("f12")  # Debug
```

### Press Arrow Keys

```python
with VNCAgentBridge('localhost') as vnc:
    # Navigate with arrow keys
    vnc.keyboard.press_key("up")      # Move up
    vnc.keyboard.press_key("down")    # Move down
    vnc.keyboard.press_key("left")    # Move left
    vnc.keyboard.press_key("right")   # Move right
    
    # Other navigation
    vnc.keyboard.press_key("home")     # Go to start
    vnc.keyboard.press_key("end")      # Go to end
    vnc.keyboard.press_key("pageup")   # Page up
    vnc.keyboard.press_key("pagedown") # Page down
```

### Press Lock Keys

```python
with VNCAgentBridge('localhost') as vnc:
    # Lock keys (typically toggle on/off)
    vnc.keyboard.press_key("capslock")
    vnc.keyboard.press_key("numlock")
    vnc.keyboard.press_key("scrolllock")
```

## Key Combinations (Hotkeys)

### Common Hotkeys

```python
with VNCAgentBridge('localhost') as vnc:
    # File operations
    vnc.keyboard.hotkey("ctrl", "n")  # New
    vnc.keyboard.hotkey("ctrl", "o")  # Open
    vnc.keyboard.hotkey("ctrl", "s")  # Save
    vnc.keyboard.hotkey("ctrl", "p")  # Print
    
    # Edit operations
    vnc.keyboard.hotkey("ctrl", "x")  # Cut
    vnc.keyboard.hotkey("ctrl", "c")  # Copy
    vnc.keyboard.hotkey("ctrl", "v")  # Paste
    vnc.keyboard.hotkey("ctrl", "z")  # Undo
    vnc.keyboard.hotkey("ctrl", "y")  # Redo
    
    # Select operations
    vnc.keyboard.hotkey("ctrl", "a")  # Select all
    vnc.keyboard.hotkey("ctrl", "f")  # Find
```

### Shift Combinations

```python
with VNCAgentBridge('localhost') as vnc:
    # Text selection
    vnc.keyboard.hotkey("shift", "up")    # Select up
    vnc.keyboard.hotkey("shift", "down")  # Select down
    vnc.keyboard.hotkey("shift", "end")   # Select to end of line
    
    # Alt+Shift combinations
    vnc.keyboard.hotkey("alt", "shift", "tab")  # Switch window backward
```

### Alt Combinations

```python
with VNCAgentBridge('localhost') as vnc:
    # Window management
    vnc.keyboard.hotkey("alt", "tab")      # Switch window
    vnc.keyboard.hotkey("alt", "f4")       # Close window
    
    # Menu access (varies by application)
    vnc.keyboard.hotkey("alt", "f")        # File menu
    vnc.keyboard.hotkey("alt", "e")        # Edit menu
    
    # Alt+number for taskbar
    vnc.keyboard.hotkey("alt", "1")        # First taskbar item
```

### Ctrl+Alt Combinations

```python
with VNCAgentBridge('localhost') as vnc:
    # System operations (varies by OS)
    vnc.keyboard.hotkey("ctrl", "alt", "delete")  # System menu / Task manager
    vnc.keyboard.hotkey("ctrl", "alt", "escape")  # Task manager
```

### Multi-Key Combinations

```python
with VNCAgentBridge('localhost') as vnc:
    # Three key combinations
    vnc.keyboard.hotkey("ctrl", "shift", "s")  # Save as
    vnc.keyboard.hotkey("ctrl", "shift", "n")  # New window
    vnc.keyboard.hotkey("alt", "shift", "tab") # Switch backward
```

## Key Events

### Hold and Release Key

```python
with VNCAgentBridge('localhost') as vnc:
    # Hold Shift while pressing arrow key
    vnc.keyboard.keydown("shift", delay=0.1)
    vnc.keyboard.press_key("right", delay=0.1)
    vnc.keyboard.press_key("right", delay=0.1)
    vnc.keyboard.keyup("shift", delay=0.1)
```

### Multiple Keys Held

```python
with VNCAgentBridge('localhost') as vnc:
    # Hold multiple modifiers
    vnc.keyboard.keydown("ctrl", delay=0.05)
    vnc.keyboard.keydown("shift", delay=0.05)
    vnc.keyboard.press_key("s", delay=0.1)
    vnc.keyboard.keyup("shift", delay=0.05)
    vnc.keyboard.keyup("ctrl", delay=0.05)
```

## Complete Text Input Workflows

### Fill Text Field

```python
with VNCAgentBridge('localhost') as vnc:
    # Click field
    vnc.mouse.left_click(100, 100, delay=0.2)
    
    # Clear existing content
    vnc.keyboard.hotkey("ctrl", "a", delay=0.1)
    vnc.keyboard.press_key("delete", delay=0.1)
    
    # Type new content
    vnc.keyboard.type_text("New content", delay=0.05)
    
    # Confirm
    vnc.keyboard.press_key("return", delay=0.2)
```

### Search and Navigate

```python
with VNCAgentBridge('localhost') as vnc:
    # Open search
    vnc.keyboard.hotkey("ctrl", "f", delay=0.3)
    
    # Type search term
    vnc.keyboard.type_text("search term", delay=0.05)
    
    # Find next
    vnc.keyboard.press_key("f3", delay=0.2)
    vnc.keyboard.press_key("f3", delay=0.2)
```

### Multi-line Text Entry

```python
with VNCAgentBridge('localhost') as vnc:
    # Type first line
    vnc.keyboard.type_text("Line 1", delay=0.05)
    
    # Press Enter for new line
    vnc.keyboard.press_key("return", delay=0.1)
    
    # Type second line
    vnc.keyboard.type_text("Line 2", delay=0.05)
    
    # Press Enter again
    vnc.keyboard.press_key("return", delay=0.1)
    
    # Type third line
    vnc.keyboard.type_text("Line 3", delay=0.05)
```

## Supported Keys

### Special Keys Reference

| Key Name | Action |
|----------|--------|
| `'return'` / `'enter'` | Return/Enter key |
| `'tab'` | Tab key |
| `'escape'` | Escape key |
| `'backspace'` | Backspace key |
| `'delete'` | Delete key |
| `'space'` | Spacebar |

### Function Keys

`'f1'` through `'f12'` - Function keys F1 through F12

### Navigation Keys

| Key | Action |
|-----|--------|
| `'up'` | Up arrow |
| `'down'` | Down arrow |
| `'left'` | Left arrow |
| `'right'` | Right arrow |
| `'home'` | Home key |
| `'end'` | End key |
| `'pageup'` | Page up |
| `'pagedown'` | Page down |

### Modifier Keys

| Key | Alternatives |
|-----|--------------|
| `'shift'` | `'lshift'` (left shift) |
| `'ctrl'` | `'lctrl'` (left control) |
| `'alt'` | `'lalt'` (left alt) |
| `'cmd'` | `'meta'` (Command key) |

### Character Keys

Any single character: `'a'`, `'A'`, `'1'`, `'!'`, etc.

## Error Handling

### Invalid Key

```python
from vnc_agent_bridge import VNCInputError

try:
    vnc.keyboard.press_key("invalid_key_name")
except VNCInputError as e:
    print(f"Unknown key: {e}")
```

### Not Connected

```python
from vnc_agent_bridge import VNCStateError

vnc = VNCAgentBridge('localhost')
try:
    vnc.keyboard.type_text("text")
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Performance Tips

### Typing Speed

```python
# Fast (for automated testing)
vnc.keyboard.type_text("text", delay=0)

# Human-like (for realistic interaction)
vnc.keyboard.type_text("text", delay=0.1)

# Slow (for visibility/debugging)
vnc.keyboard.type_text("text", delay=0.2)
```

### Batch Operations

```python
# Good: Group keyboard operations
with VNCAgentBridge('localhost') as vnc:
    vnc.keyboard.type_text("Search query", delay=0.05)
    vnc.keyboard.press_key("return", delay=0.2)
    vnc.keyboard.hotkey("ctrl", "a", delay=0.1)
```

## Application-Specific Examples

### Browser

```python
with VNCAgentBridge('localhost') as vnc:
    # Address bar
    vnc.keyboard.hotkey("ctrl", "l")
    
    # Type URL
    vnc.keyboard.type_text("example.com")
    
    # Navigate
    vnc.keyboard.press_key("return")
    
    # Refresh
    vnc.keyboard.press_key("f5")
```

### Text Editor

```python
with VNCAgentBridge('localhost') as vnc:
    # Find and replace
    vnc.keyboard.hotkey("ctrl", "h")
    
    # Type search term
    vnc.keyboard.type_text("old_text")
    
    # Tab to replace field
    vnc.keyboard.press_key("tab")
    
    # Type replacement
    vnc.keyboard.type_text("new_text")
    
    # Replace all
    vnc.keyboard.hotkey("alt", "a")
```

### Terminal/Console

```python
with VNCAgentBridge('localhost') as vnc:
    # Type command
    vnc.keyboard.type_text("ls -la", delay=0.05)
    
    # Execute
    vnc.keyboard.press_key("return")
```

## Related Guides

- **[Mouse Control Guide](mouse_control.md)** - Mouse operations
- **[Scrolling Guide](scrolling.md)** - Scroll wheel operations
- **[Advanced Guide](advanced.md)** - Complex workflows
- **[Getting Started](getting_started.md)** - Quick start guide
- **[Keyboard API Reference](../api/keyboard.md)** - Complete API

## Next Steps

1. Try the [Getting Started](getting_started.md) guide
2. Combine with [Mouse Control Guide](mouse_control.md)
3. Check [Advanced Guide](advanced.md) for complex patterns
4. Review [Keyboard API Reference](../api/keyboard.md) for all methods
