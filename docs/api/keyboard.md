# Keyboard Controller API Reference

The `KeyboardController` class provides comprehensive keyboard input control for remote VNC servers.

## Overview

The keyboard controller enables:
- Typing text strings
- Pressing individual keys
- Key combinations (hotkeys)
- Holding and releasing keys
- Support for special keys, function keys, and modifiers
- Optional timing control for each operation

## Class: KeyboardController

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    vnc.keyboard.type_text("Hello World")
    vnc.keyboard.press_key("return")
    vnc.keyboard.hotkey("ctrl", "a")
```

## Methods

### type_text(text, delay=0)

Type a text string character by character.

**Parameters:**
- `text` (str): Text to type
- `delay` (float): Delay in seconds after operation (default: 0)

**Returns:** None

**Raises:**
- `VNCStateError`: If not connected to VNC server
- `VNCInputError`: If text contains unsupported characters

**Example:**
```python
# Type simple text
vnc.keyboard.type_text("Hello World")

# Type with delay
vnc.keyboard.type_text("Important", delay=0.5)

# Type with special characters
vnc.keyboard.type_text("user@example.com")

# Type numbers
vnc.keyboard.type_text("12345")
```

### press_key(key, delay=0)

Press and release a single key.

**Parameters:**
- `key` (str or int): Key name or X11 key code
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If key name unknown or invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Press by name
vnc.keyboard.press_key("return")
vnc.keyboard.press_key("escape")
vnc.keyboard.press_key("tab")

# Press function key
vnc.keyboard.press_key("f1")

# Press arrow key
vnc.keyboard.press_key("up")

# Press by X11 key code
vnc.keyboard.press_key(0xFF0D)  # Return key
```

### hotkey(*keys, delay=0)

Press multiple keys simultaneously (key combination).

**Parameters:**
- `*keys` (str or int): Variable number of keys, typically modifiers first
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If any key invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Common hotkeys
vnc.keyboard.hotkey("ctrl", "a")  # Select all
vnc.keyboard.hotkey("ctrl", "c")  # Copy
vnc.keyboard.hotkey("ctrl", "v")  # Paste
vnc.keyboard.hotkey("ctrl", "x")  # Cut
vnc.keyboard.hotkey("ctrl", "z")  # Undo
vnc.keyboard.hotkey("ctrl", "y")  # Redo
vnc.keyboard.hotkey("ctrl", "s")  # Save

# Multiple modifiers
vnc.keyboard.hotkey("ctrl", "shift", "esc")  # Task manager
vnc.keyboard.hotkey("ctrl", "alt", "delete")  # System menu

# Alt combinations
vnc.keyboard.hotkey("alt", "tab")  # Switch window
vnc.keyboard.hotkey("alt", "f4")   # Close window

# Shift combinations
vnc.keyboard.hotkey("shift", "up")  # Select up
vnc.keyboard.hotkey("shift", "down")  # Select down
```

### keydown(key, delay=0)

Press and hold a key without releasing it.

**Parameters:**
- `key` (str or int): Key name or X11 key code
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If key invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Hold shift and press arrow keys
vnc.keyboard.keydown("shift")
vnc.keyboard.press_key("right")
vnc.keyboard.press_key("right")
vnc.keyboard.keyup("shift")

# Hold control while typing
vnc.keyboard.keydown("ctrl")
vnc.keyboard.type_text("l")
vnc.keyboard.keyup("ctrl")
```

### keyup(key, delay=0)

Release a held key.

**Parameters:**
- `key` (str or int): Key name or X11 key code
- `delay` (float): Delay in seconds (default: 0)

**Returns:** None

**Raises:**
- `VNCInputError`: If key invalid
- `VNCStateError`: If not connected

**Example:**
```python
# Release previously held key
vnc.keyboard.keyup("shift")
vnc.keyboard.keyup("ctrl")
```

## Supported Keys

### Special Keys

| Key Name | Action |
|----------|--------|
| `'return'` / `'enter'` | Return/Enter key |
| `'tab'` | Tab key |
| `'escape'` / `'esc'` | Escape key |
| `'backspace'` | Backspace key |
| `'delete'` / `'del'` | Delete key |
| `'space'` | Spacebar |

### Function Keys

- `'f1'` through `'f12'`: Function keys

### Arrow Keys

- `'up'`, `'down'`, `'left'`, `'right'`: Arrow keys
- `'home'`, `'end'`: Home and End keys
- `'pageup'`, `'pagedown'`: Page Up and Page Down keys

### Modifier Keys

| Key Name | Action |
|----------|--------|
| `'shift'` / `'lshift'` | Left Shift |
| `'rshift'` | Right Shift |
| `'ctrl'` / `'lctrl'` | Left Control |
| `'rctrl'` | Right Control |
| `'alt'` / `'lalt'` | Left Alt |
| `'ralt'` | Right Alt |
| `'cmd'` / `'meta'` | Command/Meta key |

### Character Keys

Any single character can be used as a key:
- Letters: `'a'`, `'B'`, etc. (case-sensitive)
- Numbers: `'0'`, `'1'`, etc.
- Symbols: `'!'`, `'@'`, `'#'`, etc.
- Unicode: Supported characters

### Lock Keys

- `'capslock'`: Caps Lock
- `'numlock'`: Num Lock
- `'scrolllock'`: Scroll Lock

## Common Patterns

### Text Input with Return

```python
vnc.keyboard.type_text("Search query")
vnc.keyboard.press_key("return")
```

### Select All and Copy

```python
vnc.keyboard.hotkey("ctrl", "a")  # Select all
vnc.keyboard.hotkey("ctrl", "c")  # Copy to clipboard
```

### Find and Replace

```python
vnc.keyboard.hotkey("ctrl", "h")  # Open Find & Replace
vnc.keyboard.type_text("old_text")
vnc.keyboard.press_key("tab")
vnc.keyboard.type_text("new_text")
vnc.keyboard.hotkey("alt", "a")  # Replace all (varies by app)
```

### Undo and Redo

```python
vnc.keyboard.hotkey("ctrl", "z")  # Undo
vnc.keyboard.hotkey("ctrl", "y")  # Redo
```

### Text Selection

```python
# Select line
vnc.keyboard.hotkey("shift", "end")

# Select word
vnc.keyboard.hotkey("ctrl", "shift", "right")

# Select paragraph
vnc.keyboard.hotkey("ctrl", "shift", "down")
```

### Navigation

```python
# Move to start of line
vnc.keyboard.press_key("home")

# Move to end of line
vnc.keyboard.press_key("end")

# Move to start of document
vnc.keyboard.hotkey("ctrl", "home")

# Move to end of document
vnc.keyboard.hotkey("ctrl", "end")
```

## Error Handling

```python
from vnc_agent_bridge import VNCInputError, VNCStateError

try:
    vnc.keyboard.press_key("unknown_key")
except VNCInputError as e:
    print(f"Invalid key: {e}")

try:
    vnc.keyboard.type_text("text")
except VNCStateError as e:
    print(f"Not connected: {e}")
```

## Timing Control

All methods support optional delay for timing:

```python
# No delay (fast typing)
vnc.keyboard.type_text("fast", delay=0)

# Quick typing (50ms between characters)
vnc.keyboard.type_text("medium", delay=0.05)

# Human-like typing (100-200ms)
vnc.keyboard.type_text("slow", delay=0.15)

# Deliberate typing (300ms+)
vnc.keyboard.type_text("very slow", delay=0.3)
```

## Related

- [MouseController API](mouse.md)
- [ScrollController API](scroll.md)
- [VNCConnection API](connection.md)
- [Main API Reference](../index.md)
