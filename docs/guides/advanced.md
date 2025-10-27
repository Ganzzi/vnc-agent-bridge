# Advanced Guide

Advanced patterns and workflows for VNC Agent Bridge automation.

## Overview

This guide covers complex scenarios including:
- Multi-step workflows
- Error recovery strategies
- Performance optimization
- Robustness patterns
- Real-world automation examples

## Complex Workflows

### Multi-Window Coordination

```python
from vnc_agent_bridge import VNCAgentBridge

def coordinate_windows():
    """Interact with multiple windows in sequence."""
    with VNCAgentBridge('localhost') as vnc:
        # Open first application
        vnc.keyboard.hotkey("alt", "f2")  # Run dialog
        vnc.keyboard.type_text("firefox", delay=0.05)
        vnc.keyboard.press_key("return", delay=1)
        
        # Wait for it to open
        import time
        time.sleep(3)
        
        # Do work in first window
        vnc.keyboard.hotkey("ctrl", "l")  # Address bar
        vnc.keyboard.type_text("example.com", delay=0.05)
        vnc.keyboard.press_key("return", delay=2)
        
        # Switch to another window
        vnc.keyboard.hotkey("alt", "tab", delay=0.3)
        
        # Open another application
        vnc.keyboard.hotkey("alt", "f2")
        vnc.keyboard.type_text("gedit", delay=0.05)
        vnc.keyboard.press_key("return", delay=1)
        
        # Do work in second window
        vnc.keyboard.type_text("Note content", delay=0.05)
        
        # Switch back to first
        vnc.keyboard.hotkey("alt", "tab", delay=0.3)
```

### Form Completion with Validation

```python
def complete_form_with_checks():
    """Fill form and validate each field."""
    with VNCAgentBridge('localhost') as vnc:
        import time
        
        fields = [
            (100, 100, "John Doe"),
            (100, 150, "john@example.com"),
            (100, 200, "123 Main St"),
        ]
        
        for x, y, value in fields:
            # Click field
            vnc.mouse.left_click(x, y, delay=0.2)
            time.sleep(0.1)
            
            # Clear previous content
            vnc.keyboard.hotkey("ctrl", "a", delay=0.1)
            
            # Type new value
            vnc.keyboard.type_text(value, delay=0.05)
            time.sleep(0.1)
            
            # Move to next field
            vnc.keyboard.press_key("tab", delay=0.2)
```

### Scrollable List Navigation

```python
def find_and_select_item(target_item):
    """Scroll through list to find and select item."""
    with VNCAgentBridge('localhost') as vnc:
        import time
        
        max_scrolls = 20
        for scroll_count in range(max_scrolls):
            # Check if we can see the item
            # (In real scenario, would use vision/OCR)
            vnc.scroll.down(amount=3, delay=0.3)
            time.sleep(0.2)
            
            if scroll_count == 10:  # Pseudo-condition
                # Item found - click it
                vnc.mouse.left_click(200, 250, delay=0.2)
                return True
        
        return False
```

## Error Recovery Patterns

### Retry with Backoff

```python
from vnc_agent_bridge import VNCConnectionError
import time

def retry_operation(max_retries=3):
    """Retry operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            with VNCAgentBridge('localhost') as vnc:
                vnc.mouse.left_click(100, 100)
                return True
        except VNCConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"Retry attempt {attempt + 1} in {wait_time}s")
                time.sleep(wait_time)
            else:
                print("Failed after all retries")
                raise
```

### Try Alternative Actions

```python
def robust_click(primary_pos, fallback_pos):
    """Try primary click, fallback to alternative."""
    with VNCAgentBridge('localhost') as vnc:
        try:
            vnc.mouse.left_click(primary_pos[0], primary_pos[1], delay=0.2)
        except Exception as e:
            print(f"Primary click failed: {e}, trying fallback")
            vnc.mouse.left_click(fallback_pos[0], fallback_pos[1], delay=0.2)
```

### State-Based Recovery

```python
def navigate_with_recovery():
    """Navigate while handling different states."""
    with VNCAgentBridge('localhost') as vnc:
        import time
        
        # Try main navigation path
        vnc.keyboard.hotkey("ctrl", "n")  # New
        time.sleep(0.5)
        
        # Check if dialog appeared (simulated)
        try:
            # Attempt primary action
            vnc.keyboard.press_key("return", delay=0.2)
        except:
            # If dialog didn't appear, use alternative
            vnc.keyboard.press_key("escape", delay=0.2)
            # Try different approach
            vnc.keyboard.hotkey("alt", "f")  # File menu
            time.sleep(0.3)
```

## Performance Optimization

### Batch Operations

```python
def efficient_data_entry():
    """Group operations for better performance."""
    with VNCAgentBridge('localhost') as vnc:
        # Click once
        vnc.mouse.left_click(100, 100, delay=0.2)
        
        # Type all content in one operation
        content = "Line 1\nLine 2\nLine 3"
        for line in content.split('\n'):
            vnc.keyboard.type_text(line, delay=0.03)
            vnc.keyboard.press_key("return", delay=0.1)
```

### Reduce Delay When Possible

```python
def fast_automation():
    """Fast automation when delay not needed."""
    with VNCAgentBridge('localhost') as vnc:
        import time
        
        # Fast keyboard input
        vnc.keyboard.type_text("content", delay=0)
        
        # Standard delay for mouse (safer)
        vnc.mouse.left_click(100, 100, delay=0.1)
        
        # Wait outside of operations
        time.sleep(1)
```

### Minimize Connection Operations

```python
def consolidated_workflow():
    """Keep connection open for multiple operations."""
    with VNCAgentBridge('localhost') as vnc:
        # Good: One connection for many operations
        vnc.mouse.left_click(100, 100, delay=0.2)
        vnc.keyboard.type_text("text", delay=0.05)
        vnc.scroll.down(amount=3, delay=0.2)
        vnc.mouse.left_click(200, 200, delay=0.2)
    
    # Bad would be: Creating connection for each operation
    # vnc1 = VNCAgentBridge('localhost')
    # vnc1.mouse.left_click(...)
    # vnc1.close()
    # vnc2 = VNCAgentBridge('localhost')
    # vnc2.keyboard.type_text(...)
```

## Robustness Patterns

### Explicit Timing Control

```python
def precise_timing_workflow():
    """Use explicit delays for critical operations."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Click button to open dialog
        vnc.mouse.left_click(100, 100, delay=0.2)
        
        # Wait for dialog to appear (explicit timing)
        time.sleep(1)
        
        # Now interact with dialog
        vnc.keyboard.type_text("input", delay=0.05)
        vnc.keyboard.press_key("return", delay=0.2)
        
        # Wait for result
        time.sleep(0.5)
```

### Position Validation

```python
def validate_screen_state():
    """Verify screen state before operations."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Ensure focused on right area
        vnc.mouse.left_click(400, 300, delay=0.2)
        time.sleep(0.2)
        
        # Now type (cursor is in right place)
        vnc.keyboard.type_text("text", delay=0.05)
```

### Sequence Validation

```python
def validated_sequence():
    """Execute sequence with checks between steps."""
    from vnc_agent_bridge import VNCStateError
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        steps = [
            ("Step 1", lambda v: v.keyboard.hotkey("ctrl", "n")),
            ("Step 2", lambda v: v.keyboard.type_text("filename")),
            ("Step 3", lambda v: v.keyboard.press_key("return")),
        ]
        
        for step_name, step_fn in steps:
            try:
                step_fn(vnc)
                print(f"{step_name}: OK")
                time.sleep(0.3)
            except VNCStateError as e:
                print(f"{step_name}: FAILED - {e}")
                break
```

## Real-World Scenarios

### Web Form Automation

```python
def automate_web_form():
    """Complete workflow: navigate, fill form, submit."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Navigate to form
        vnc.keyboard.hotkey("ctrl", "l")  # Address bar
        vnc.keyboard.type_text("example.com/form", delay=0.05)
        vnc.keyboard.press_key("return", delay=2)
        
        # Wait for page load
        time.sleep(2)
        
        # Fill form fields
        fields_data = [
            ("First Name", "John"),
            ("Last Name", "Doe"),
            ("Email", "john@example.com"),
        ]
        
        for label, value in fields_data:
            vnc.keyboard.type_text(value, delay=0.05)
            vnc.keyboard.press_key("tab", delay=0.2)
            time.sleep(0.1)
        
        # Scroll to submit button
        vnc.scroll.down(amount=3, delay=0.3)
        time.sleep(0.2)
        
        # Click submit
        vnc.mouse.left_click(400, 400, delay=0.2)
        
        # Wait for confirmation
        time.sleep(2)
```

### Document Processing

```python
def process_document():
    """Open, search, edit, and save document."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Open document
        vnc.keyboard.hotkey("ctrl", "o")
        time.sleep(0.5)
        
        # Type filename
        vnc.keyboard.type_text("document.txt", delay=0.05)
        vnc.keyboard.press_key("return", delay=1)
        
        # Wait for document to open
        time.sleep(1)
        
        # Find text
        vnc.keyboard.hotkey("ctrl", "f")
        time.sleep(0.3)
        vnc.keyboard.type_text("search_term", delay=0.05)
        vnc.keyboard.press_key("return", delay=0.5)
        
        # Close find dialog
        vnc.keyboard.press_key("escape", delay=0.2)
        
        # Select and delete found text
        vnc.keyboard.hotkey("ctrl", "x")
        
        # Type replacement
        vnc.keyboard.type_text("replacement", delay=0.05)
        
        # Save document
        vnc.keyboard.hotkey("ctrl", "s")
        time.sleep(1)
```

### Application Testing Workflow

```python
def test_application():
    """Test application functionality workflow."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Test case 1: New document
        vnc.keyboard.hotkey("ctrl", "n")
        time.sleep(0.5)
        assert_window_opened()  # Pseudo-code
        
        # Test case 2: Type content
        vnc.keyboard.type_text("Test content", delay=0.05)
        assert_text_visible()  # Pseudo-code
        
        # Test case 3: Save
        vnc.keyboard.hotkey("ctrl", "s")
        time.sleep(1)
        assert_saved()  # Pseudo-code
        
        # Test case 4: Close
        vnc.keyboard.hotkey("alt", "f4")
        time.sleep(0.5)
```

### Data Entry from List

```python
def batch_data_entry():
    """Enter multiple records from list."""
    import time
    
    records = [
        ("Alice", "25", "Engineer"),
        ("Bob", "30", "Manager"),
        ("Charlie", "28", "Designer"),
    ]
    
    with VNCAgentBridge('localhost') as vnc:
        for name, age, role in records:
            # New record
            vnc.keyboard.hotkey("ctrl", "n")
            time.sleep(0.5)
            
            # Fill fields
            vnc.keyboard.type_text(name, delay=0.05)
            vnc.keyboard.press_key("tab", delay=0.1)
            
            vnc.keyboard.type_text(age, delay=0.05)
            vnc.keyboard.press_key("tab", delay=0.1)
            
            vnc.keyboard.type_text(role, delay=0.05)
            
            # Save record
            vnc.keyboard.hotkey("ctrl", "s")
            time.sleep(0.5)
```

## Troubleshooting Complex Workflows

### Debugging Timeline

```python
def workflow_with_debugging():
    """Execute workflow with debug output."""
    import time
    from datetime import datetime
    
    def log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    with VNCAgentBridge('localhost') as vnc:
        log("Starting workflow")
        
        vnc.mouse.left_click(100, 100, delay=0.2)
        log("Clicked button")
        time.sleep(1)
        log("Waited 1 second")
        
        vnc.keyboard.type_text("input", delay=0.05)
        log("Typed input")
        
        vnc.keyboard.press_key("return", delay=0.2)
        log("Pressed return")
```

### State Logging

```python
def log_operations():
    """Log each operation for debugging."""
    import time
    
    operations = []
    
    with VNCAgentBridge('localhost') as vnc:
        def log_op(op_name, op_fn):
            try:
                op_fn()
                operations.append((op_name, "OK"))
                print(f"✓ {op_name}")
            except Exception as e:
                operations.append((op_name, f"ERROR: {e}"))
                print(f"✗ {op_name}: {e}")
        
        log_op("Click button", lambda: vnc.mouse.left_click(100, 100, delay=0.2))
        log_op("Type text", lambda: vnc.keyboard.type_text("input", delay=0.05))
        log_op("Press return", lambda: vnc.keyboard.press_key("return", delay=0.2))
    
    # Print summary
    print("\nSummary:")
    for op_name, status in operations:
        print(f"  {op_name}: {status}")
```

## Performance Metrics

### Measure Workflow Duration

```python
def measure_workflow_performance():
    """Measure time taken for workflow."""
    import time
    
    start_time = time.time()
    
    with VNCAgentBridge('localhost') as vnc:
        vnc.mouse.left_click(100, 100, delay=0.2)
        vnc.keyboard.type_text("data", delay=0.05)
        vnc.keyboard.press_key("return", delay=0.2)
    
    elapsed = time.time() - start_time
    print(f"Workflow completed in {elapsed:.2f} seconds")
```

### Optimize Slow Workflows

```python
def profile_workflow():
    """Profile workflow to identify slow parts."""
    import time
    
    with VNCAgentBridge('localhost') as vnc:
        # Measure mouse operation
        t1 = time.time()
        vnc.mouse.left_click(100, 100, delay=0.2)
        mouse_time = time.time() - t1
        
        # Measure keyboard operation
        t2 = time.time()
        vnc.keyboard.type_text("data", delay=0.05)
        keyboard_time = time.time() - t2
        
        # Measure scroll operation
        t3 = time.time()
        vnc.scroll.down(amount=3, delay=0.2)
        scroll_time = time.time() - t3
        
        print(f"Mouse: {mouse_time:.3f}s")
        print(f"Keyboard: {keyboard_time:.3f}s")
        print(f"Scroll: {scroll_time:.3f}s")
```

## Related Guides

- **[Getting Started](getting_started.md)** - Quick start guide
- **[Mouse Control Guide](mouse_control.md)** - Mouse operations
- **[Keyboard Input Guide](keyboard_input.md)** - Keyboard operations
- **[Scrolling Guide](scrolling.md)** - Scroll wheel operations
- **[Mouse API Reference](../api/mouse.md)** - Complete API
- **[Keyboard API Reference](../api/keyboard.md)** - Complete API
- **[Scroll API Reference](../api/scroll.md)** - Complete API

## Next Steps

1. Review all specific operation guides first
2. Combine patterns from multiple guides
3. Implement error handling for production use
4. Test workflows with timing validation
5. Optimize performance using profiling
6. Review API references for all available options
