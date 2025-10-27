# Clipboard API Reference

## Overview

The `ClipboardController` class provides methods for managing clipboard operations on a remote VNC server. It allows AI agents to send text to the remote clipboard, retrieve clipboard content, and clear the clipboard.

## Class: ClipboardController

### Methods

#### `__init__(connection: VNCConnection) -> None`

Initialize the clipboard controller.

**Parameters:**
- `connection` (VNCConnection): VNC connection instance for protocol communication

**Example:**
```python
from vnc_agent_bridge.core.connection_tcp import TCPVNCConnection
from vnc_agent_bridge.core.clipboard import ClipboardController

connection = TCPVNCConnection('localhost', port=5900)
connection.connect()

clipboard = ClipboardController(connection)
```

---

#### `send_text(text: str, delay: float = 0) -> None`

Send text to the remote clipboard.

**Parameters:**
- `text` (str): Text to send to the remote clipboard. Cannot be empty.
- `delay` (float, optional): Wait time before sending in seconds (default: 0)

**Raises:**
- `VNCInputError`: If text is empty or contains unsupported characters
- `VNCStateError`: If not connected

**Example:**
```python
# Send simple text
clipboard.send_text("Hello, World!")

# Send text with delay
clipboard.send_text("Important data", delay=0.5)

# Send Unicode text (latin-1 compatible)
clipboard.send_text("Café")
```

**Encoding:**
- Text is encoded using latin-1 (ISO-8859-1) as per VNC protocol specification
- Characters outside the latin-1 range will raise an error

---

#### `get_text(timeout: float = 5.0) -> Optional[str]`

Retrieve text from the remote clipboard.

**Parameters:**
- `timeout` (float, optional): Maximum wait time for clipboard data in seconds (default: 5.0)

**Returns:**
- str or None: Clipboard text if available, None if no text available within timeout

**Raises:**
- `VNCInputError`: If timeout is negative
- `VNCStateError`: If not connected
- `VNCTimeoutError`: If timeout exceeded

**Example:**
```python
# Get clipboard content with default timeout
text = clipboard.get_text()
if text:
    print(f"Clipboard contains: {text}")

# Get with custom timeout
text = clipboard.get_text(timeout=2.0)

# Workflow: Copy and paste
clipboard.send_text("data to copy")
# ... user action to copy ...
content = clipboard.get_text()
print(f"Copied: {content}")
```

**Note:**
- The returned text is cached internally
- Call `get_text()` to refresh from server

---

#### `clear(delay: float = 0) -> None`

Clear the remote clipboard by sending an empty string.

**Parameters:**
- `delay` (float, optional): Wait time before clearing in seconds (default: 0)

**Raises:**
- `VNCStateError`: If not connected

**Example:**
```python
# Clear clipboard immediately
clipboard.clear()

# Clear with delay
clipboard.clear(delay=1.0)

# Security: Clear after use
clipboard.send_text("sensitive data")
# ... operations ...
clipboard.clear()  # Remove sensitive data
```

---

#### `has_text() -> bool`

Check if the clipboard contains text.

**Returns:**
- bool: True if clipboard has text, False otherwise

**Example:**
```python
if clipboard.has_text():
    print(f"Clipboard content: {clipboard.content}")
else:
    print("Clipboard is empty")
```

**Note:**
- This checks cached content
- Call `get_text()` first to refresh from server

---

### Properties

#### `content: str`

Get current clipboard content (cached).

**Returns:**
- str: Current clipboard text, empty string if no content

**Example:**
```python
# Get cached content
text = clipboard.content
if text:
    print(f"Cached: {text}")

# After sending
clipboard.send_text("new text")
print(clipboard.content)  # Output: "new text"
```

**Note:**
- Returns cached content from last `send_text()` or `get_text()` call
- Call `get_text()` to refresh from server

---

## Usage Patterns

### Pattern 1: Send Text to Clipboard

```python
with VNCAgentBridge('localhost') as vnc:
    # Send text that can be pasted
    vnc.clipboard.send_text("Hello, World!")
    
    # Paste with keyboard shortcut
    vnc.keyboard.hotkey('ctrl', 'v')
    
    # Wait for paste to complete
    vnc.keyboard.press_key('return', delay=0.5)
```

### Pattern 2: Copy and Get Text

```python
with VNCAgentBridge('localhost') as vnc:
    # User performs copy action
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.hotkey('ctrl', 'a')  # Select all
    vnc.keyboard.hotkey('ctrl', 'c')  # Copy
    
    # Retrieve clipboard content
    copied_text = vnc.clipboard.get_text(timeout=2.0)
    
    if copied_text:
        print(f"Copied: {copied_text}")
```

### Pattern 3: Clipboard-Based Data Transfer

```python
with VNCAgentBridge('localhost') as vnc:
    # Transfer data via clipboard
    data_chunks = ["chunk1", "chunk2", "chunk3"]
    
    for chunk in data_chunks:
        # Send chunk
        vnc.clipboard.send_text(chunk, delay=0.1)
        
        # User pastes the chunk
        vnc.keyboard.hotkey('ctrl', 'v')
        vnc.keyboard.press_key('return', delay=0.2)
        
        # Clear for next chunk
        vnc.clipboard.clear(delay=0.1)
```

### Pattern 4: Secure Clipboard Handling

```python
with VNCAgentBridge('localhost') as vnc:
    # Handle sensitive data
    sensitive_password = "SuperSecret123!"
    
    try:
        # Send password
        vnc.clipboard.send_text(sensitive_password)
        
        # Use password (paste it)
        vnc.keyboard.hotkey('ctrl', 'v')
        vnc.keyboard.press_key('return')
        
    finally:
        # Always clear sensitive data
        vnc.clipboard.clear()
```

### Pattern 5: Check Before Access

```python
with VNCAgentBridge('localhost') as vnc:
    # Check clipboard status
    if vnc.clipboard.has_text():
        content = vnc.clipboard.content
        print(f"Current clipboard: {content}")
    else:
        print("Clipboard is empty")
        vnc.clipboard.send_text("default text")
```

---

## Exceptions

### VNCInputError

Raised when input validation fails.

**Common causes:**
- Empty text string
- Characters outside latin-1 encoding range
- Negative timeout value

**Example:**
```python
try:
    clipboard.send_text("")  # Empty
except VNCInputError as e:
    print(f"Invalid input: {e}")
```

### VNCStateError

Raised when operation fails due to connection state.

**Common causes:**
- Not connected to VNC server
- Connection lost during operation

**Example:**
```python
try:
    clipboard.send_text("text")
except VNCStateError as e:
    print(f"State error: {e}")
    vnc.connect()  # Reconnect
```

### VNCTimeoutError

Raised when operation times out.

**Common causes:**
- Server not responding to clipboard requests
- Timeout too short for network latency

**Example:**
```python
try:
    text = clipboard.get_text(timeout=1.0)
except VNCTimeoutError as e:
    print(f"Timeout: {e}")
    text = clipboard.get_text(timeout=5.0)  # Retry with longer timeout
```

---

## Text Encoding

### Latin-1 Support

The clipboard controller uses **latin-1 (ISO-8859-1)** encoding as specified by the VNC protocol.

**Supported characters:**
- ASCII characters (a-z, A-Z, 0-9, symbols)
- Extended Latin characters (é, ñ, ü, etc.)
- Accented characters in Western European languages

**Unsupported characters:**
- Emoji and symbols outside latin-1: ❌ 😀, 🎉
- CJK characters: ❌ 中文, 日本語, 한글
- Greek, Cyrillic, Hebrew: ❌ (requires extended encoding)

**Example:**
```python
# Works - Latin-1 characters
clipboard.send_text("Café résumé")  # ✓

# Fails - Emoji not in latin-1
try:
    clipboard.send_text("Hello 😀")  # ✗
except VNCInputError:
    print("Emoji not supported")
```

---

## Performance Considerations

### Caching

Text is cached after `send_text()` or `get_text()` calls:

```python
# Cache is updated
clipboard.send_text("text1")
print(clipboard.content)  # Output: "text1" (from cache)

# Cache is updated
clipboard.send_text("text2")
print(clipboard.content)  # Output: "text2" (from cache)

# Cache refreshed
text = clipboard.get_text()
print(clipboard.content)  # Output: retrieved text
```

### Delay Handling

Use delay parameter for synchronization:

```python
# Fast operation (no delay)
clipboard.send_text("text", delay=0)

# Realistic human speed (medium delay)
clipboard.send_text("text", delay=0.3)

# Very deliberate (large delay)
clipboard.send_text("text", delay=1.0)
```

---

## Best Practices

### 1. Always Handle Empty Content

```python
# Good
text = clipboard.get_text()
if text:
    process(text)
else:
    print("Clipboard empty")

# Avoid
text = clipboard.get_text()
process(text)  # May receive None
```

### 2. Clear Sensitive Data

```python
# Good
try:
    clipboard.send_text(password)
    use_password()
finally:
    clipboard.clear()

# Avoid
clipboard.send_text(password)
use_password()
# Password remains in clipboard!
```

### 3. Use Appropriate Timeouts

```python
# Fast network - short timeout
text = clipboard.get_text(timeout=1.0)

# Slow network - longer timeout
text = clipboard.get_text(timeout=5.0)

# Unknown network - reasonable default
text = clipboard.get_text(timeout=3.0)
```

### 4. Validate Text Before Sending

```python
# Good
text = user_input
if len(text) > 0:
    clipboard.send_text(text)

# Avoid
clipboard.send_text("")  # Raises error
```

### 5. Check Compatibility

```python
# Good - check if text can be encoded
try:
    clipboard.send_text(user_text)
except VNCInputError:
    print("Text contains unsupported characters")
    # Handle alternative encoding or filtering

# Avoid
clipboard.send_text(any_text)  # May fail with non-latin-1
```

---

## See Also

- `VNCAgentBridge`: Main facade for VNC operations
- `KeyboardController`: Keyboard input operations
- `MouseController`: Mouse/pointer operations
- `VNCConnection`: Low-level protocol communication