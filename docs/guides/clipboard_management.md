# Clipboard Management Guide

## Overview

This guide covers how to use the clipboard features in VNC Agent Bridge to transfer text data to and from a remote system through the VNC connection.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Operations](#basic-operations)
3. [Advanced Workflows](#advanced-workflows)
4. [Handling Special Cases](#handling-special-cases)
5. [Performance Tips](#performance-tips)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

Make sure you have VNC Agent Bridge installed:

```bash
pip install vnc-agent-bridge
```

### Basic Example

```python
from vnc_agent_bridge import VNCAgentBridge

# Connect to VNC server
with VNCAgentBridge('192.168.1.100') as vnc:
    # Send text to clipboard
    vnc.clipboard.send_text("Hello, Remote System!")
    
    # Paste it with keyboard
    vnc.keyboard.hotkey('ctrl', 'v')
    
    # Retrieve clipboard content
    content = vnc.clipboard.get_text()
    print(f"Clipboard contains: {content}")
```

---

## Basic Operations

### Sending Text to Clipboard

Send text that can be pasted on the remote system:

```python
with VNCAgentBridge('localhost') as vnc:
    # Simple send
    vnc.clipboard.send_text("Copy this text")
    
    # User can now paste with Ctrl+V
```

**With Delay:**

```python
# Wait 500ms before sending
vnc.clipboard.send_text("text", delay=0.5)
```

**For Different Content Types:**

```python
# Plain text
vnc.clipboard.send_text("Hello World")

# Numbers as text
vnc.clipboard.send_text("1234567890")

# Paths
vnc.clipboard.send_text("/path/to/file.txt")

# URLs
vnc.clipboard.send_text("https://example.com/page?param=value")

# JSON
vnc.clipboard.send_text('{"key": "value"}')
```

### Retrieving Clipboard Content

Get text from the remote system's clipboard:

```python
with VNCAgentBridge('localhost') as vnc:
    # Get clipboard content
    text = vnc.clipboard.get_text()
    
    if text:
        print(f"Retrieved: {text}")
    else:
        print("Clipboard is empty")
```

**With Custom Timeout:**

```python
# Wait up to 10 seconds for clipboard data
text = vnc.clipboard.get_text(timeout=10.0)

# Quick check (1 second timeout)
text = vnc.clipboard.get_text(timeout=1.0)
```

### Clearing Clipboard

Remove content from the remote clipboard:

```python
with VNCAgentBridge('localhost') as vnc:
    # Clear immediately
    vnc.clipboard.clear()
    
    # Clear with delay
    vnc.clipboard.clear(delay=0.5)
```

### Checking Clipboard Status

Check if clipboard has content:

```python
with VNCAgentBridge('localhost') as vnc:
    if vnc.clipboard.has_text():
        print(f"Content: {vnc.clipboard.content}")
    else:
        print("Clipboard is empty")
```

---

## Advanced Workflows

### Workflow 1: Copy Text from Remote System

Copy selected text from the remote display:

```python
with VNCAgentBridge('localhost') as vnc:
    # Click on text area
    vnc.mouse.left_click(200, 300)
    
    # Select all text
    vnc.keyboard.hotkey('ctrl', 'a')
    
    # Copy to clipboard
    vnc.keyboard.hotkey('ctrl', 'c')
    
    # Wait for clipboard update
    import time
    time.sleep(0.5)
    
    # Get the copied text
    copied_text = vnc.clipboard.get_text()
    print(f"Copied: {copied_text}")
```

### Workflow 2: Paste Multiple Items

Paste multiple pieces of text sequentially:

```python
with VNCAgentBridge('localhost') as vnc:
    items_to_paste = [
        "First line of text",
        "Second line of text",
        "Third line of text"
    ]
    
    for item in items_to_paste:
        # Send to clipboard
        vnc.clipboard.send_text(item)
        
        # Paste it
        vnc.keyboard.hotkey('ctrl', 'v')
        
        # Press Enter to go to next line
        vnc.keyboard.press_key('return', delay=0.2)
```

### Workflow 3: Fill Form with Data

Use clipboard to fill web forms:

```python
with VNCAgentBridge('localhost') as vnc:
    form_data = {
        'name_field': 'John Doe',
        'email_field': 'john@example.com',
        'address_field': '123 Main St, City, State 12345',
        'phone_field': '555-1234567'
    }
    
    for field_name, field_value in form_data.items():
        # Click on field
        vnc.mouse.left_click(field_positions[field_name][0], 
                             field_positions[field_name][1])
        
        # Send value via clipboard
        vnc.clipboard.send_text(field_value)
        
        # Paste
        vnc.keyboard.hotkey('ctrl', 'v')
        
        # Move to next field
        vnc.keyboard.press_key('tab', delay=0.3)
```

### Workflow 4: Configuration Management

Transfer configuration data:

```python
with VNCAgentBridge('localhost') as vnc:
    config_content = """
    [Settings]
    debug=true
    log_level=INFO
    max_connections=100
    """
    
    # Open text editor
    vnc.keyboard.hotkey('alt', 'tab')
    
    # Send configuration via clipboard
    vnc.clipboard.send_text(config_content.strip())
    
    # Paste into editor
    vnc.keyboard.hotkey('ctrl', 'v')
    
    # Save file
    vnc.keyboard.hotkey('ctrl', 's')
```

### Workflow 5: Extract and Process Data

Copy data and process it locally:

```python
with VNCAgentBridge('localhost') as vnc:
    # Click on data area
    vnc.mouse.left_click(100, 100)
    
    # Select data
    vnc.keyboard.hotkey('ctrl', 'a')
    vnc.keyboard.hotkey('ctrl', 'c')
    
    # Wait for clipboard
    import time
    time.sleep(0.3)
    
    # Get data
    data = vnc.clipboard.get_text()
    
    # Process locally
    lines = data.split('\n')
    for line in lines:
        if line.strip():
            print(f"Processing: {line}")
```

---

## Handling Special Cases

### Empty Clipboard

Handle when clipboard is empty:

```python
with VNCAgentBridge('localhost') as vnc:
    text = vnc.clipboard.get_text()
    
    if text is None:
        print("Clipboard is empty or inaccessible")
        # Provide default or retry
        vnc.clipboard.send_text("default value")
    else:
        print(f"Got: {text}")
```

### Timeout Scenarios

Handle timeouts gracefully:

```python
with VNCAgentBridge('localhost') as vnc:
    # Try with short timeout first
    text = vnc.clipboard.get_text(timeout=1.0)
    
    if text is None:
        print("No immediate clipboard data, retrying...")
        # Retry with longer timeout
        text = vnc.clipboard.get_text(timeout=5.0)
    
    if text is not None:
        print(f"Retrieved: {text}")
    else:
        print("Failed to get clipboard data")
```

### Non-ASCII Characters

Handle international characters:

```python
with VNCAgentBridge('localhost') as vnc:
    # These work (Latin-1 compatible)
    vnc.clipboard.send_text("Café")
    vnc.clipboard.send_text("Münchën")
    vnc.clipboard.send_text("España")
    
    # These don't work (outside Latin-1)
    try:
        vnc.clipboard.send_text("中文")  # Chinese
    except Exception as e:
        print(f"Cannot send: {e}")
        # Convert to Latin-1 or use alternative
```

### Large Text Chunks

Handle large text efficiently:

```python
with VNCAgentBridge('localhost') as vnc:
    # For large text, consider chunking
    large_text = "..." * 10000  # 30KB of text
    
    # Option 1: Send all at once
    vnc.clipboard.send_text(large_text)
    vnc.keyboard.hotkey('ctrl', 'v')
    
    # Option 2: Send in chunks
    chunk_size = 1000
    for i in range(0, len(large_text), chunk_size):
        chunk = large_text[i:i+chunk_size]
        vnc.clipboard.send_text(chunk)
        vnc.keyboard.hotkey('ctrl', 'v')
        vnc.keyboard.press_key('return', delay=0.1)
```

### Security: Clearing Sensitive Data

Always clear sensitive data after use:

```python
with VNCAgentBridge('localhost') as vnc:
    password = "SecretPassword123!"
    api_key = "sk-proj-abc123xyz..."
    
    try:
        # Send sensitive data
        vnc.clipboard.send_text(password)
        vnc.keyboard.hotkey('ctrl', 'v')
        
        # Use it
        vnc.keyboard.press_key('return')
        
    finally:
        # Always clear
        vnc.clipboard.clear()
        print("Sensitive data cleared")
```

---

## Performance Tips

### 1. Optimal Delay Timing

```python
# Fast (instant, good for testing)
vnc.clipboard.send_text(text, delay=0)

# Recommended (allows system processing)
vnc.clipboard.send_text(text, delay=0.1)

# Human-like (slower for realism)
vnc.clipboard.send_text(text, delay=0.5)
```

### 2. Batch Operations

```python
# Good: Batch related operations
with VNCAgentBridge('localhost') as vnc:
    for item in items:
        vnc.clipboard.send_text(item)
        vnc.keyboard.hotkey('ctrl', 'v')

# Avoid: Reconnect for each item
for item in items:
    with VNCAgentBridge('localhost') as vnc:
        vnc.clipboard.send_text(item)
```

### 3. Check Cache First

```python
# Efficient: Use cached content if available
if vnc.clipboard.has_text():
    text = vnc.clipboard.content  # Instant, no network call
else:
    text = vnc.clipboard.get_text()  # Network call
```

### 4. Timeout Tuning

```python
# Network speed consideration
if is_local_network():
    timeout = 1.0  # Fast local network
elif is_corporate_network():
    timeout = 3.0  # Medium corporate network
else:
    timeout = 5.0  # Slower remote connection
    
text = vnc.clipboard.get_text(timeout=timeout)
```

---

## Troubleshooting

### Issue: Text Not Appearing After Paste

**Problem:** Text sent to clipboard doesn't appear after `Ctrl+V`

**Solutions:**
1. Add delay to allow clipboard update:
   ```python
   vnc.clipboard.send_text("text")
   import time
   time.sleep(0.2)
   vnc.keyboard.hotkey('ctrl', 'v')
   ```

2. Check if target window is focused:
   ```python
   vnc.mouse.left_click(target_x, target_y)
   vnc.keyboard.hotkey('ctrl', 'v')
   ```

3. Verify connection is active:
   ```python
   if vnc.is_connected:
       vnc.clipboard.send_text("text")
   ```

### Issue: Can't Retrieve Clipboard Data

**Problem:** `get_text()` returns None

**Solutions:**
1. Increase timeout:
   ```python
   text = vnc.clipboard.get_text(timeout=5.0)
   ```

2. Ensure data was copied:
   ```python
   vnc.keyboard.hotkey('ctrl', 'a')  # Select all first
   vnc.keyboard.hotkey('ctrl', 'c')  # Then copy
   import time
   time.sleep(0.5)
   text = vnc.clipboard.get_text()
   ```

3. Check if server supports clipboard:
   ```python
   try:
       vnc.clipboard.send_text("test")
   except Exception as e:
       print(f"Clipboard not supported: {e}")
   ```

### Issue: Character Encoding Problems

**Problem:** Special characters cause errors

**Solutions:**
1. Use only Latin-1 compatible characters:
   ```python
   # Good
   text = "Café"  # Works
   
   # Bad
   text = "中文"  # Raises error
   ```

2. Filter or escape characters:
   ```python
   def sanitize_for_clipboard(text):
       return text.encode('latin-1', errors='ignore').decode('latin-1')
   
   sanitized = sanitize_for_clipboard(user_input)
   vnc.clipboard.send_text(sanitized)
   ```

### Issue: Clipboard Clear Not Working

**Problem:** `clear()` doesn't empty clipboard

**Solution:**
```python
# Explicitly send empty string
vnc.clipboard.send_text("")

# Or use clear method
vnc.clipboard.clear()

# Verify
if not vnc.clipboard.has_text():
    print("Clipboard cleared successfully")
```

---

## Examples

### Example 1: Password Entry

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('target.server.com') as vnc:
    password = "MySecurePassword123"
    
    try:
        # Click on password field
        vnc.mouse.left_click(400, 300)
        
        # Send via clipboard (secure, no keylogging)
        vnc.clipboard.send_text(password)
        
        # Paste
        vnc.keyboard.hotkey('ctrl', 'v')
        
        # Submit form
        vnc.keyboard.press_key('return')
        
    finally:
        # Always clear sensitive data
        vnc.clipboard.clear()
```

### Example 2: Data Export

```python
with VNCAgentBridge('database.server.com') as vnc:
    # Select data in database client
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.hotkey('ctrl', 'a')
    vnc.keyboard.hotkey('ctrl', 'c')
    
    # Wait for clipboard
    import time
    time.sleep(0.5)
    
    # Export data
    exported_data = vnc.clipboard.get_text()
    
    # Process and save
    with open('exported_data.txt', 'w') as f:
        f.write(exported_data)
    
    print(f"Exported {len(exported_data)} characters")
```

### Example 3: Configuration Update

```python
def update_remote_config():
    config_lines = [
        "log_level=DEBUG",
        "timeout=30",
        "max_retries=5"
    ]
    
    with VNCAgentBridge('config.server.com') as vnc:
        for line in config_lines:
            vnc.clipboard.send_text(line)
            vnc.keyboard.hotkey('ctrl', 'v')
            vnc.keyboard.press_key('return', delay=0.1)

update_remote_config()
```

---

## See Also

- [Keyboard Control Guide](keyboard_input.md)
- [Mouse Control Guide](mouse_control.md)
- [API Reference](../api/clipboard.md)
- [Getting Started](getting_started.md)