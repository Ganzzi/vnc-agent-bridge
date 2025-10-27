# VNC Agent Bridge - Technical Design Document

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────┐
│       VNCAgentBridge (Facade)           │
│   Main entry point for users            │
└────────────────────┬────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Mouse  │  │Keyboard│  │Scroll  │
    │Control-│  │Control-│  │Control-│
    │  ler   │  │  ler   │  │  ler   │
    └────────┘  └────────┘  └────────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────▼────────────┐
        │  VNCConnection          │
        │  (Low-level protocol)   │
        └─────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Network (TCP socket)   │
        │  to VNC Server          │
        └─────────────────────────┘
```

### 1.2 Module Organization

```
vnc_agent_bridge/
├── __init__.py                 # Package initialization, public API
├── core/
│   ├── __init__.py            # Core module exports
│   ├── bridge.py              # VNCAgentBridge main facade
│   ├── connection.py          # VNCConnection low-level protocol
│   ├── mouse.py               # MouseController
│   ├── keyboard.py            # KeyboardController
│   └── scroll.py              # ScrollController
├── types/
│   ├── __init__.py            # Type exports
│   └── common.py              # Common type definitions
└── exceptions/
    ├── __init__.py            # Exception exports
    └── __init__.py            # Exception classes

tests/
├── conftest.py                # Pytest fixtures
├── test_mouse.py              # Mouse tests
├── test_keyboard.py           # Keyboard tests
├── test_scroll.py             # Scroll tests
├── test_connection.py         # Connection tests
├── test_integration.py        # Integration tests
└── test_exceptions.py         # Exception tests

docs/
├── plan/
│   ├── PROJECT_PLAN.md        # This document
│   ├── IMPLEMENTATION_CHECKLIST.md
│   ├── TECHNICAL_DESIGN.md    # Technical deep dive
│   └── API_SPECIFICATION.md   # Detailed API spec
├── api/
│   ├── mouse.md               # MouseController API
│   ├── keyboard.md            # KeyboardController API
│   ├── scroll.md              # ScrollController API
│   └── connection.md          # Connection API
└── guides/
    ├── getting_started.md
    ├── mouse_control.md
    ├── keyboard_input.md
    ├── scrolling.md
    └── advanced.md
```

---

## 2. Type System Design

### 2.1 Type Definitions

**File:** `vnc_agent_bridge/types/common.py`

```python
# Position type
from typing import Tuple
Position = Tuple[int, int]  # (x, y)

# Button types
from enum import IntEnum

class MouseButton(IntEnum):
    """Mouse button constants for VNC protocol."""
    LEFT = 0      # Button 0 in VNC
    MIDDLE = 1    # Button 1 in VNC
    RIGHT = 2     # Button 2 in VNC

class ScrollDirection(IntEnum):
    """Scroll direction constants."""
    UP = 3         # Button 3 in VNC
    DOWN = 4       # Button 4 in VNC

# Key action types
class KeyAction(IntEnum):
    """Key action states."""
    RELEASE = 0   # Key up
    PRESS = 1     # Key down

# Delay type
DelayType = Union[int, float]  # In seconds

# Button mask type for VNC protocol
ButtonMask = int  # 8-bit mask for button states
```

### 2.2 Exception Hierarchy

**File:** `vnc_agent_bridge/exceptions/__init__.py`

```python
class VNCException(Exception):
    """Base exception for all VNC errors."""
    pass

class VNCConnectionError(VNCException):
    """Raised when connection to VNC server fails."""
    pass

class VNCAuthenticationError(VNCConnectionError):
    """Raised when authentication fails."""
    pass

class VNCTimeoutError(VNCException):
    """Raised when an operation times out."""
    pass

class VNCInputError(VNCException):
    """Raised when invalid input is provided."""
    pass

class VNCStateError(VNCException):
    """Raised when operation attempted in invalid state."""
    pass

class VNCProtocolError(VNCException):
    """Raised when VNC protocol violation occurs."""
    pass
```

---

## 3. Core Classes Design

### 3.1 VNCConnection Class

**Purpose:** Low-level VNC protocol handling and network communication.

```python
class VNCConnection:
    """Manages low-level VNC protocol communication."""
    
    def __init__(self, 
                 host: str, 
                 port: int = 5900,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: float = 10.0):
        """Initialize VNC connection parameters."""
    
    def connect(self) -> None:
        """Connect to VNC server and complete handshake."""
        # 1. Create TCP socket
        # 2. Perform version handshake
        # 3. Perform authentication
        # 4. Initialize framebuffer
    
    def disconnect(self) -> None:
        """Close connection gracefully."""
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
    
    def send_pointer_event(self, 
                          x: int, 
                          y: int, 
                          button_mask: int) -> None:
        """Send mouse pointer event to server."""
        # Format: [msg_type=5][button_mask][x][y]
    
    def send_key_event(self, 
                      keycode: int, 
                      pressed: bool) -> None:
        """Send keyboard event to server."""
        # Format: [msg_type=4][pressed][keycode]
    
    def _validate_connection(self) -> None:
        """Verify connection is active."""
        raise VNCStateError("Not connected") if not is_connected
    
    def _send_raw(self, data: bytes) -> None:
        """Send raw bytes to server."""
    
    def _recv_exact(self, count: int) -> bytes:
        """Receive exact number of bytes."""
```

### 3.2 MouseController Class

**Purpose:** High-level mouse control operations.

```python
class MouseController:
    """Control mouse/pointer operations."""
    
    def __init__(self, connection: VNCConnection):
        """Initialize with VNC connection."""
        self._connection = connection
        self._current_position: Position = (0, 0)
        self._button_mask = 0
    
    def left_click(self, 
                   x: Optional[int] = None, 
                   y: Optional[int] = None,
                   delay: float = 0) -> None:
        """Click left mouse button."""
        # Move to position if specified
        # Press and release button 0
    
    def right_click(self, 
                    x: Optional[int] = None,
                    y: Optional[int] = None,
                    delay: float = 0) -> None:
        """Click right mouse button."""
    
    def double_click(self, 
                     x: Optional[int] = None,
                     y: Optional[int] = None,
                     delay: float = 0) -> None:
        """Double click left mouse button."""
        # Two left clicks with small interval
    
    def move_to(self, 
                x: int, 
                y: int,
                delay: float = 0) -> None:
        """Move mouse to absolute position."""
        # Send position without button press
    
    def drag_to(self, 
                x: int, 
                y: int,
                duration: float = 1.0,
                delay: float = 0) -> None:
        """Drag mouse from current to new position."""
        # 1. Calculate path
        # 2. Hold down button 0
        # 3. Move in steps over duration
        # 4. Release button 0
    
    def get_position(self) -> Position:
        """Get current mouse position."""
        return self._current_position
    
    def _apply_delay(self, delay: float) -> None:
        """Apply delay in seconds."""
        if delay > 0:
            time.sleep(delay)
    
    def _send_event(self, 
                    x: int, 
                    y: int,
                    button_mask: int) -> None:
        """Send pointer event to connection."""
```

### 3.3 KeyboardController Class

**Purpose:** High-level keyboard input operations.

```python
class KeyboardController:
    """Control keyboard input operations."""
    
    # X11 key code mappings
    KEY_CODES = {
        'return': 0xFF0D,
        'tab': 0xFF09,
        'escape': 0xFF1B,
        'backspace': 0xFF08,
        'delete': 0xFFFF,
        'space': 0x0020,
        # Special keys...
    }
    
    MODIFIER_KEYS = {
        'shift': 0xFFE1,
        'ctrl': 0xFFE3,
        'alt': 0xFFE9,
        'cmd': 0xFFEB,
    }
    
    def __init__(self, connection: VNCConnection):
        """Initialize with VNC connection."""
    
    def type_text(self, 
                  text: str,
                  delay: float = 0) -> None:
        """Type text character by character."""
        # For each character:
        # 1. Get key code
        # 2. Press key
        # 3. Release key
    
    def press_key(self, 
                  key: Union[str, int],
                  delay: float = 0) -> None:
        """Press and release single key."""
    
    def hotkey(self, 
               *keys: Union[str, int],
               delay: float = 0) -> None:
        """Press multiple keys simultaneously."""
        # 1. Press all modifier keys
        # 2. Press main key
        # 3. Release main key
        # 4. Release modifier keys
    
    def keydown(self, 
                key: Union[str, int],
                delay: float = 0) -> None:
        """Press and hold key."""
    
    def keyup(self, 
              key: Union[str, int],
              delay: float = 0) -> None:
        """Release held key."""
    
    def _get_keycode(self, 
                     key: Union[str, int]) -> int:
        """Convert key name or code to X11 keysym."""
        if isinstance(key, int):
            return key
        return self.KEY_CODES.get(key.lower())
    
    def _send_key_event(self, 
                       keycode: int,
                       pressed: bool) -> None:
        """Send key event to connection."""
```

### 3.4 ScrollController Class

**Purpose:** High-level mouse wheel scrolling operations.

```python
class ScrollController:
    """Control mouse wheel scrolling."""
    
    def __init__(self, connection: VNCConnection):
        """Initialize with VNC connection."""
    
    def scroll_up(self, 
                  amount: int = 3,
                  delay: float = 0) -> None:
        """Scroll up using mouse wheel."""
        # Press button 3 (scroll up) 'amount' times
    
    def scroll_down(self, 
                    amount: int = 3,
                    delay: float = 0) -> None:
        """Scroll down using mouse wheel."""
        # Press button 4 (scroll down) 'amount' times
    
    def scroll_to(self, 
                  x: int,
                  y: int,
                  delay: float = 0) -> None:
        """Scroll at specific position (scroll_down)."""
        # Move to position and scroll
    
    def _apply_delay(self, delay: float) -> None:
        """Apply delay in seconds."""
    
    def _send_scroll_event(self, button: int) -> None:
        """Send scroll button event."""
```

### 3.5 VNCAgentBridge Class (Facade)

**Purpose:** Main public API, unifying all controllers.

```python
class VNCAgentBridge:
    """Main facade for VNC agent interaction."""
    
    def __init__(self,
                 host: str,
                 port: int = 5900,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """Initialize VNC bridge."""
        self._connection = VNCConnection(host, port, username, password)
        self._mouse = MouseController(self._connection)
        self._keyboard = KeyboardController(self._connection)
        self._scroll = ScrollController(self._connection)
    
    def connect(self) -> None:
        """Connect to VNC server."""
        self._connection.connect()
    
    def disconnect(self) -> None:
        """Disconnect from VNC server."""
        self._connection.disconnect()
    
    @property
    def mouse(self) -> MouseController:
        """Access mouse controller."""
        return self._mouse
    
    @property
    def keyboard(self) -> KeyboardController:
        """Access keyboard controller."""
        return self._keyboard
    
    @property
    def scroll(self) -> ScrollController:
        """Access scroll controller."""
        return self._scroll
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connection.is_connected
    
    def __enter__(self) -> 'VNCAgentBridge':
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()
```

---

## 4. Usage Patterns

### 4.1 Basic Usage Pattern

```python
from vnc_agent_bridge import VNCAgentBridge

# Initialize bridge
bridge = VNCAgentBridge('192.168.1.100', port=5900, password='secret')

# Connect
bridge.connect()

try:
    # Use controllers
    bridge.mouse.move_to(100, 100)
    bridge.mouse.left_click()
    bridge.keyboard.type_text("Hello, VNC!")
    bridge.scroll.scroll_down(3)
finally:
    bridge.disconnect()
```

### 4.2 Context Manager Pattern (Recommended)

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('192.168.1.100', password='secret') as vnc:
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.type_text("Text input")
    vnc.scroll.scroll_up(5)
# Automatically disconnects
```

### 4.3 Complex Workflow

```python
with VNCAgentBridge(host='localhost') as vnc:
    # Move to button and click
    vnc.mouse.move_to(150, 200, delay=0.5)
    vnc.mouse.left_click(delay=0.2)
    
    # Type with delay between characters
    vnc.keyboard.type_text("username", delay=0.1)
    
    # Press Tab and Enter
    vnc.keyboard.press_key('tab', delay=0.2)
    vnc.keyboard.press_key('return', delay=0.2)
    
    # Complex hotkey
    vnc.keyboard.hotkey('ctrl', 'shift', 'escape', delay=0.5)
    
    # Drag operation
    vnc.mouse.drag_to(400, 300, duration=2.0, delay=0.1)
    
    # Scroll with delay
    vnc.scroll.scroll_down(amount=5, delay=0.3)
```

---

## 5. Delay Mechanism

### 5.1 Delay Strategy

- **Optional parameter on all methods:** `delay: float = 0`
- **Unit:** Seconds (float for precision)
- **Implementation:** `time.sleep(delay)` after operation
- **Purpose:** Allow AI agents to throttle operations for realism

### 5.2 Delay Levels

```python
# No delay (fast execution)
vnc.mouse.left_click()

# Minimal delay (50ms)
vnc.mouse.left_click(delay=0.05)

# Human-like delay (200-500ms)
vnc.mouse.left_click(delay=0.3)

# Realistic interaction (500ms+)
vnc.keyboard.type_text("text", delay=0.5)  # Per character
```

---

## 6. Error Handling Strategy

### 6.1 Error Hierarchy

```
VNCException
├── VNCConnectionError
│   └── VNCAuthenticationError
├── VNCTimeoutError
├── VNCInputError
├── VNCStateError
└── VNCProtocolError
```

### 6.2 Validation Points

```python
# Connection validation
if not connection.is_connected:
    raise VNCStateError("Not connected to VNC server")

# Coordinate validation
if x < 0 or y < 0 or x > screen_width or y > screen_height:
    raise VNCInputError(f"Invalid coordinates: ({x}, {y})")

# Key code validation
if keycode not in valid_keycodes:
    raise VNCInputError(f"Invalid key code: {keycode}")

# Delay validation
if delay < 0:
    raise VNCInputError("Delay must be non-negative")
```

---

## 7. Testing Strategy

### 7.1 Mock Architecture

```python
# Mock VNC Connection
class MockVNCConnection:
    def __init__(self):
        self.events = []  # Track all events sent
        self._connected = True
    
    def send_pointer_event(self, x, y, button_mask):
        self.events.append(('pointer', x, y, button_mask))
    
    def send_key_event(self, keycode, pressed):
        self.events.append(('key', keycode, pressed))
    
    def connect(self):
        self._connected = True
    
    def disconnect(self):
        self._connected = False
```

### 7.2 Test Organization

- **Unit tests:** Test individual classes in isolation with mocks
- **Integration tests:** Test facade with all components
- **Fixture-based:** Use conftest.py for shared setup
- **Parametrized tests:** Use pytest.mark.parametrize for multiple scenarios

---

## 8. Type Checking Configuration

### 8.1 MyPy Settings

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_calls = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_optional = True
```

### 8.2 Type Stub Files

- Consider creating `py.typed` marker for PEP 561 compliance
- No separate `.pyi` files needed if inline annotations complete

---

## 9. Dependencies Analysis

### 9.1 Core Dependencies

**Minimal approach** (to keep it lightweight):

- **No external dependencies for core functionality**
  - Use only standard library (socket, struct, time, enum)
  - Implement VNC protocol directly

**Optional dependencies for enhanced features:**
- `numpy` (if image processing needed)
- `cryptography` (for advanced authentication)

### 9.2 Development Dependencies

```
pytest >= 7.0
pytest-cov >= 3.0
mypy >= 0.950
black >= 22.0
flake8 >= 4.0
pylint >= 2.10
tox >= 3.20
```

---

## 10. Performance Considerations

### 10.1 Event Generation

- **Mouse events:** Throttled as needed by delay parameter
- **Drag operations:** Multiple pointer events with smooth interpolation
- **Keyboard:** Sequential key events (no buffering)

### 10.2 Memory Management

- Keep internal state minimal
- Don't buffer screen captures (unless explicitly requested)
- Clean up on disconnect

### 10.3 Network Efficiency

- Send events immediately (no batching)
- Use VNC protocol efficiently
- Implement timeout handling

---

## 11. Security Considerations

### 11.1 Password Handling

- Accept password parameter but never log it
- Don't store password in memory longer than needed
- Consider supporting keyfile authentication in future

### 11.2 Input Validation

- Validate all coordinates
- Validate key codes
- Sanitize text input (if needed)

### 11.3 Connection Security

- Implement timeout to prevent hanging
- Validate server responses
- Handle closed connections gracefully

---

## 12. Future Enhancements

### Phase 2 Features

- Async/await support for concurrent operations
- Framebuffer capture and analysis
- Screen region recognition
- Multi-monitor support
- Event recording/playback
- Advanced authentication (ARD, SSH)
- Screen dimension detection
- VNC server discovery

### Phase 3 Optimizations

- Connection pooling
- Event buffering/compression
- Performance profiling
- GPU acceleration for rendering
- Distributed agent coordination

---

## 13. Documentation Structure

### Generated Files

```
docs/
├── api/
│   ├── mouse.md              # Auto-generated from docstrings
│   ├── keyboard.md
│   ├── scroll.md
│   └── connection.md
├── guides/
│   ├── getting_started.md    # Installation, quick start
│   ├── mouse_control.md      # Examples and patterns
│   ├── keyboard_input.md
│   ├── scrolling.md
│   └── advanced.md           # Error handling, custom delays
└── plan/
    ├── PROJECT_PLAN.md
    ├── IMPLEMENTATION_CHECKLIST.md
    └── TECHNICAL_DESIGN.md   # This document
```

---

## 14. Version Management

### 14.1 Semantic Versioning

- **0.1.0** - Initial release with core features
- **0.2.0** - Additional features (async, screen capture)
- **1.0.0** - Stable API, production ready

### 14.2 Version Locations

- `vnc_agent_bridge/__init__.py` - `__version__ = "0.1.0"`
- `pyproject.toml` - version field
- `setup.py` - version parameter
- `CHANGELOG.md` - All versions documented

---

## 15. Deployment Strategy

### 15.1 Local Development

```bash
pip install -e .  # Editable install
pytest            # Run tests
mypy vnc_agent_bridge  # Type check
```

### 15.2 Testing Before Release

```bash
tox               # Test on multiple Python versions
pytest --cov      # Coverage check (85%+ required)
mypy --strict     # Strict type checking
```

### 15.3 PyPI Release

```bash
python -m build   # Build wheel and sdist
twine upload dist/ # Upload to PyPI
```

---

## References

1. **VNC Protocol:** RFB (Remote Framebuffer) Protocol v3.8
2. **Python Packaging:** https://packaging.python.org/
3. **Type Hints:** PEP 484, PEP 526, PEP 544
4. **Testing:** pytest documentation
5. **X11 Key Codes:** X11 keysym definitions
6. **Socket Programming:** Python socket module documentation

