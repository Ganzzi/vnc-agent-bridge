# VNC Agent Bridge - API Specification

## 1. Overview

The `vnc-agent-bridge` package provides a high-level Python API for AI agents to interact with VNC (Virtual Network Computing) servers. The API is designed for clarity, type safety, and ease of use.

---

## 2. Main Entry Point: VNCAgentBridge

### Class: `VNCAgentBridge`

**Module:** `vnc_agent_bridge.core.bridge`

The main facade class providing access to all VNC interaction capabilities.

#### Constructor

```python
VNCAgentBridge(
    host: str,
    port: int = 5900,
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: float = 10.0
) -> VNCAgentBridge
```

**Parameters:**
- `host` (str): Hostname or IP address of VNC server
- `port` (int): VNC server port (default: 5900, standard RFB port)
- `username` (Optional[str]): Username for authentication (if required)
- `password` (Optional[str]): Password for authentication (if required)
- `timeout` (float): Connection timeout in seconds (default: 10.0)

**Raises:**
- `ValueError`: If host is empty or port is invalid

**Example:**
```python
vnc = VNCAgentBridge('192.168.1.100', port=5900, password='secret')
```

#### Methods

##### `connect() -> None`

Establish connection to VNC server.

**Raises:**
- `VNCConnectionError`: If connection fails
- `VNCAuthenticationError`: If authentication fails
- `VNCTimeoutError`: If connection times out

**Example:**
```python
vnc.connect()
```

##### `disconnect() -> None`

Close connection to VNC server gracefully.

**Side Effects:**
- Closes network socket
- Releases resources
- Safe to call multiple times

**Example:**
```python
vnc.disconnect()
```

#### Properties

##### `mouse: MouseController`

Access mouse control operations.

**Returns:** MouseController instance

**Example:**
```python
vnc.mouse.left_click(100, 100)
```

##### `keyboard: KeyboardController`

Access keyboard input operations.

**Returns:** KeyboardController instance

**Example:**
```python
vnc.keyboard.type_text("Hello")
```

##### `scroll: ScrollController`

Access mouse wheel scrolling operations.

**Returns:** ScrollController instance

**Example:**
```python
vnc.scroll.scroll_down(5)
```

##### `is_connected: bool`

Check current connection status.

**Returns:** True if connected, False otherwise

**Example:**
```python
if vnc.is_connected:
    vnc.mouse.left_click()
```

#### Context Manager

##### `__enter__() -> VNCAgentBridge`
##### `__exit__(exc_type, exc_val, exc_tb) -> None`

Support for `with` statement (context manager protocol).

**Behavior:**
- `__enter__`: Calls `connect()` and returns self
- `__exit__`: Calls `disconnect()` regardless of exceptions

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    vnc.mouse.left_click(100, 100)
# Automatically disconnects
```

---

## 3. Mouse Controller: MouseController

### Class: `MouseController`

**Module:** `vnc_agent_bridge.core.mouse`

Provides high-level mouse control operations.

#### Methods

##### `left_click(x: Optional[int] = None, y: Optional[int] = None, delay: float = 0) -> None`

Perform left mouse button click.

**Parameters:**
- `x` (Optional[int]): X coordinate (uses current position if None)
- `y` (Optional[int]): Y coordinate (uses current position if None)
- `delay` (float): Delay in seconds after click (default: 0)

**Raises:**
- `VNCInputError`: If coordinates are invalid
- `VNCStateError`: If not connected

**Example:**
```python
vnc.mouse.left_click(100, 200)           # Click at position
vnc.mouse.left_click(delay=0.1)          # Click at current position
vnc.mouse.left_click(100, 200, delay=0.5)
```

##### `right_click(x: Optional[int] = None, y: Optional[int] = None, delay: float = 0) -> None`

Perform right mouse button click (context menu).

**Parameters:**
- `x` (Optional[int]): X coordinate (uses current position if None)
- `y` (Optional[int]): Y coordinate (uses current position if None)
- `delay` (float): Delay in seconds after click (default: 0)

**Raises:**
- `VNCInputError`: If coordinates are invalid
- `VNCStateError`: If not connected

**Example:**
```python
vnc.mouse.right_click(150, 250)
vnc.mouse.right_click(delay=0.2)
```

##### `double_click(x: Optional[int] = None, y: Optional[int] = None, delay: float = 0) -> None`

Perform double left mouse button click.

**Parameters:**
- `x` (Optional[int]): X coordinate (uses current position if None)
- `y` (Optional[int]): Y coordinate (uses current position if None)
- `delay` (float): Delay in seconds after double-click (default: 0)

**Raises:**
- `VNCInputError`: If coordinates are invalid
- `VNCStateError`: If not connected

**Example:**
```python
vnc.mouse.double_click(100, 100)         # Double-click on file
vnc.mouse.double_click(delay=0.3)
```

##### `move_to(x: int, y: int, delay: float = 0) -> None`

Move mouse cursor to absolute position.

**Parameters:**
- `x` (int): X coordinate (required)
- `y` (int): Y coordinate (required)
- `delay` (float): Delay in seconds after move (default: 0)

**Raises:**
- `VNCInputError`: If coordinates are invalid or out of bounds
- `VNCStateError`: If not connected

**Example:**
```python
vnc.mouse.move_to(0, 0)                  # Move to top-left
vnc.mouse.move_to(640, 480, delay=0.1)  # Move and wait
```

##### `drag_to(x: int, y: int, duration: float = 1.0, delay: float = 0) -> None`

Drag mouse from current position to new position.

**Parameters:**
- `x` (int): Target X coordinate (required)
- `y` (int): Target Y coordinate (required)
- `duration` (float): Time to spend dragging in seconds (default: 1.0)
- `delay` (float): Delay in seconds after drag (default: 0)

**Behavior:**
- Moves mouse in smooth motion over specified duration
- Holds down left button during motion
- Releases button at end position

**Raises:**
- `VNCInputError`: If coordinates are invalid
- `VNCStateError`: If not connected

**Example:**
```python
vnc.mouse.drag_to(200, 300)              # Drag over 1 second
vnc.mouse.drag_to(100, 100, duration=2.0)
vnc.mouse.drag_to(300, 200, duration=0.5, delay=0.2)
```

##### `get_position() -> Tuple[int, int]`

Get current mouse cursor position.

**Returns:** Tuple of (x, y) coordinates

**Example:**
```python
x, y = vnc.mouse.get_position()
print(f"Mouse at ({x}, {y})")
```

---

## 4. Keyboard Controller: KeyboardController

### Class: `KeyboardController`

**Module:** `vnc_agent_bridge.core.keyboard`

Provides keyboard input operations.

#### Methods

##### `type_text(text: str, delay: float = 0) -> None`

Type text string character by character.

**Parameters:**
- `text` (str): Text to type (any Unicode string)
- `delay` (float): Delay in seconds after each character (default: 0)

**Behavior:**
- Types each character sequentially
- Uses key press/release events
- If delay > 0, waits after each character

**Raises:**
- `VNCInputError`: If text contains unsupported characters
- `VNCStateError`: If not connected

**Example:**
```python
vnc.keyboard.type_text("Hello, World!")
vnc.keyboard.type_text("password", delay=0.1)  # Type slowly
vnc.keyboard.type_text("test123")
```

##### `press_key(key: Union[str, int], delay: float = 0) -> None`

Press and release a single key.

**Parameters:**
- `key` (Union[str, int]): Key name (string) or key code (int)
- `delay` (float): Delay in seconds after key press (default: 0)

**Supported Key Names (string):**
- Special keys: 'return', 'tab', 'escape', 'backspace', 'delete', 'space'
- Function keys: 'f1', 'f2', ..., 'f12'
- Arrow keys: 'up', 'down', 'left', 'right'
- Home/End: 'home', 'end', 'pageup', 'pagedown'
- Character keys: Single characters like 'a', 'A', '1', etc.

**Raises:**
- `VNCInputError`: If key is not recognized
- `VNCStateError`: If not connected

**Example:**
```python
vnc.keyboard.press_key('return')         # Press Enter
vnc.keyboard.press_key('tab')            # Press Tab
vnc.keyboard.press_key('f5')             # Press F5
vnc.keyboard.press_key(0xFF0D)           # Press Enter by key code
vnc.keyboard.press_key('a', delay=0.2)   # Press 'a' with delay
```

##### `hotkey(*keys: Union[str, int], delay: float = 0) -> None`

Press multiple keys simultaneously (for key combinations).

**Parameters:**
- `*keys`: Variable number of key names or codes
- `delay` (float): Delay in seconds after hotkey (default: 0)

**Behavior:**
- Presses all keys in order
- Releases all keys in reverse order
- Supports modifier keys (shift, ctrl, alt, cmd)

**Raises:**
- `VNCInputError`: If any key is not recognized
- `VNCStateError`: If not connected

**Example:**
```python
vnc.keyboard.hotkey('ctrl', 'c')         # Ctrl+C
vnc.keyboard.hotkey('ctrl', 'a')         # Ctrl+A
vnc.keyboard.hotkey('shift', 'tab')      # Shift+Tab
vnc.keyboard.hotkey('alt', 'f4')         # Alt+F4
vnc.keyboard.hotkey('ctrl', 'shift', 'esc', delay=0.5)
```

##### `keydown(key: Union[str, int], delay: float = 0) -> None`

Press and hold a key (without releasing).

**Parameters:**
- `key` (Union[str, int]): Key name or code
- `delay` (float): Delay in seconds after pressing (default: 0)

**Raises:**
- `VNCInputError`: If key is not recognized
- `VNCStateError`: If not connected

**Example:**
```python
vnc.keyboard.keydown('shift')            # Hold Shift
vnc.keyboard.type_text("text")           # Type while holding
vnc.keyboard.keyup('shift')              # Release Shift
```

##### `keyup(key: Union[str, int], delay: float = 0) -> None`

Release a previously held key.

**Parameters:**
- `key` (Union[str, int]): Key name or code
- `delay` (float): Delay in seconds after releasing (default: 0)

**Raises:**
- `VNCInputError`: If key is not recognized
- `VNCStateError`: If not connected

**Example:**
```python
vnc.keyboard.keydown('shift')
vnc.keyboard.type_text("TEXT")
vnc.keyboard.keyup('shift')
```

---

## 5. Scroll Controller: ScrollController

### Class: `ScrollController`

**Module:** `vnc_agent_bridge.core.scroll`

Provides mouse wheel scrolling operations.

#### Methods

##### `scroll_up(amount: int = 3, delay: float = 0) -> None`

Scroll up using mouse wheel.

**Parameters:**
- `amount` (int): Number of scroll ticks (default: 3)
- `delay` (float): Delay in seconds after scrolling (default: 0)

**Raises:**
- `VNCInputError`: If amount is negative
- `VNCStateError`: If not connected

**Example:**
```python
vnc.scroll.scroll_up()                   # Scroll up 3 ticks
vnc.scroll.scroll_up(5)                  # Scroll up 5 ticks
vnc.scroll.scroll_up(amount=10, delay=0.1)
```

##### `scroll_down(amount: int = 3, delay: float = 0) -> None`

Scroll down using mouse wheel.

**Parameters:**
- `amount` (int): Number of scroll ticks (default: 3)
- `delay` (float): Delay in seconds after scrolling (default: 0)

**Raises:**
- `VNCInputError`: If amount is negative
- `VNCStateError`: If not connected

**Example:**
```python
vnc.scroll.scroll_down()                 # Scroll down 3 ticks
vnc.scroll.scroll_down(5)                # Scroll down 5 ticks
vnc.scroll.scroll_down(amount=10, delay=0.1)
```

##### `scroll_to(x: int, y: int, delay: float = 0) -> None`

Scroll down at specific mouse position.

**Parameters:**
- `x` (int): X coordinate for scroll position
- `y` (int): Y coordinate for scroll position
- `delay` (float): Delay in seconds after scrolling (default: 0)

**Behavior:**
- Moves mouse to position (x, y)
- Performs scroll_down operation

**Raises:**
- `VNCInputError`: If coordinates are invalid
- `VNCStateError`: If not connected

**Example:**
```python
vnc.scroll.scroll_to(400, 300)           # Scroll at this position
vnc.scroll.scroll_to(640, 480, delay=0.2)
```

---

## 6. Exception Classes

### Exception Hierarchy

```
VNCException (base)
├── VNCConnectionError
│   └── VNCAuthenticationError
├── VNCTimeoutError
├── VNCInputError
├── VNCStateError
└── VNCProtocolError
```

### Exception Classes

#### `VNCException`

**Base exception** for all VNC-related errors.

**Module:** `vnc_agent_bridge.exceptions`

```python
class VNCException(Exception):
    """Base exception for all VNC errors."""
    pass
```

#### `VNCConnectionError`

**Raised when** connection to VNC server cannot be established.

```python
raise VNCConnectionError("Failed to connect to 192.168.1.100:5900")
```

#### `VNCAuthenticationError`

**Raised when** authentication with VNC server fails.

**Inherits from:** `VNCConnectionError`

```python
raise VNCAuthenticationError("Authentication failed: Invalid password")
```

#### `VNCTimeoutError`

**Raised when** an operation times out.

```python
raise VNCTimeoutError("Connection timed out after 10 seconds")
```

#### `VNCInputError`

**Raised when** invalid input is provided to a method.

```python
raise VNCInputError("Invalid coordinates: (-10, 200)")
```

#### `VNCStateError`

**Raised when** operation is attempted in invalid state.

```python
raise VNCStateError("Not connected to VNC server")
```

#### `VNCProtocolError`

**Raised when** VNC protocol violation occurs.

```python
raise VNCProtocolError("Invalid server response: malformed packet")
```

---

## 7. Type Definitions

### Common Types

**Module:** `vnc_agent_bridge.types.common`

```python
from typing import Tuple, Union

# Position coordinates
Position = Tuple[int, int]  # (x, y)

# Delay type
DelayType = Union[int, float]  # Seconds

# Button types
class MouseButton(IntEnum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2

class ScrollDirection(IntEnum):
    UP = 3
    DOWN = 4

class KeyAction(IntEnum):
    RELEASE = 0
    PRESS = 1
```

---

## 8. Complete Usage Examples

### Example 1: Basic Click and Type

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost', password='secret') as vnc:
    # Click on a text field
    vnc.mouse.left_click(100, 100)
    
    # Type some text
    vnc.keyboard.type_text("Hello, VNC!")
    
    # Press Enter
    vnc.keyboard.press_key('return')
```

### Example 2: Complex Workflow with Delays

```python
from vnc_agent_bridge import VNCAgentBridge
import time

with VNCAgentBridge('192.168.1.100', password='mypassword') as vnc:
    # Wait for screen to stabilize
    time.sleep(1)
    
    # Move to button and click (with delay)
    vnc.mouse.move_to(150, 200, delay=0.5)
    vnc.mouse.left_click(delay=0.3)
    
    # Fill login form
    vnc.keyboard.type_text("admin", delay=0.05)
    vnc.keyboard.press_key('tab', delay=0.2)
    vnc.keyboard.type_text("password123", delay=0.05)
    
    # Submit form
    vnc.keyboard.press_key('return', delay=1.0)
```

### Example 3: Keyboard Shortcuts

```python
with VNCAgentBridge('localhost') as vnc:
    # Select all with Ctrl+A
    vnc.keyboard.hotkey('ctrl', 'a')
    
    # Copy with Ctrl+C
    vnc.keyboard.hotkey('ctrl', 'c', delay=0.2)
    
    # Click elsewhere
    vnc.mouse.left_click(300, 300, delay=0.3)
    
    # Paste with Ctrl+V
    vnc.keyboard.hotkey('ctrl', 'v')
```

### Example 4: Drag and Drop

```python
with VNCAgentBridge('localhost') as vnc:
    # Move to source and drag to destination
    vnc.mouse.move_to(100, 100)
    vnc.mouse.drag_to(300, 300, duration=1.5)
    
    # Alternative: click, move, release
    vnc.mouse.left_click(100, 100)
    vnc.mouse.move_to(300, 300, delay=0.5)
```

### Example 5: Scrolling

```python
with VNCAgentBridge('localhost') as vnc:
    # Click on scrollable area
    vnc.mouse.left_click(400, 400, delay=0.2)
    
    # Scroll down
    vnc.scroll.scroll_down(5, delay=0.1)
    
    # Scroll at specific position
    vnc.scroll.scroll_to(400, 300)
    
    # Scroll up
    vnc.scroll.scroll_up(3, delay=0.1)
```

### Example 6: Error Handling

```python
from vnc_agent_bridge import VNCAgentBridge, VNCException

try:
    with VNCAgentBridge('192.168.1.100', password='secret') as vnc:
        vnc.mouse.left_click(100, 100)
except VNCConnectionError as e:
    print(f"Connection failed: {e}")
except VNCInputError as e:
    print(f"Invalid input: {e}")
except VNCException as e:
    print(f"VNC error: {e}")
```

---

## 9. Best Practices

### Connection Management

```python
# ✓ Good: Use context manager
with VNCAgentBridge('localhost') as vnc:
    vnc.mouse.left_click(100, 100)

# ✗ Avoid: Manual connection handling
vnc = VNCAgentBridge('localhost')
vnc.connect()
vnc.mouse.left_click(100, 100)
# Forget to disconnect!
```

### Delay Usage

```python
# ✓ Good: Use appropriate delays
vnc.mouse.left_click(delay=0.1)      # Short delay
vnc.keyboard.type_text("text", delay=0.05)  # Per character

# ✗ Bad: No delays (unrealistic)
vnc.mouse.left_click()
vnc.keyboard.type_text("text")
```

### Error Handling

```python
# ✓ Good: Handle specific exceptions
from vnc_agent_bridge import VNCException, VNCInputError

try:
    vnc.mouse.left_click(-10, -10)
except VNCInputError:
    print("Invalid coordinates")

# ✗ Bad: Generic exception
try:
    vnc.mouse.left_click(-10, -10)
except Exception:
    pass
```

### Key Specifications

```python
# ✓ Good: Use key names (more readable)
vnc.keyboard.press_key('return')
vnc.keyboard.hotkey('ctrl', 'a')

# ✗ Avoid: Use key codes (less readable)
vnc.keyboard.press_key(0xFF0D)
```

---

## 10. Performance Characteristics

### Operation Timing

| Operation | Time (typical) |
|-----------|----------------|
| Mouse click | <1ms |
| Mouse move | <1ms |
| Key press | <1ms |
| Drag (1s duration) | ~1000ms |
| Type (per character) | <1ms + delay |
| Scroll | <1ms |

### Network Latency

Add expected VNC server latency to all operations (typically 10-100ms).

---

## 11. Compatibility

### Python Versions

- **Minimum:** Python 3.8
- **Tested:** Python 3.8, 3.9, 3.10, 3.11, 3.12

### Operating Systems

- **Linux:** Full support
- **Windows:** Full support (with VNC client)
- **macOS:** Full support

### VNC Servers

- **TightVNC:** ✓ Tested
- **RealVNC:** ✓ Tested
- **x11vnc:** ✓ Tested
- **vncserver:** ✓ Tested
- **LibVNC:** ✓ Tested

---

## 12. Deprecated Methods

(None at this version)

---

## 13. Migration Guide

### From Version 0.0.x to 0.1.0

(Initial release - no migration needed)

---

## References

- **VNC Protocol:** RFB 3.8 Specification
- **X11 Key Codes:** X11 keysym database
- **Python typing:** PEP 484, PEP 586

