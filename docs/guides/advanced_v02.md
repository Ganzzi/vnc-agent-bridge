# Advanced v0.2.0 Patterns and Workflows

## Overview

This guide covers advanced patterns and workflows for using v0.2.0 features in complex automation scenarios. These patterns combine screenshot capture, video recording, and clipboard operations for sophisticated VNC automation.

---

## Pattern 1: Conditional Screenshot Capture

Capture screenshots only when specific conditions are met, useful for test reporting and debugging.

### Basic Conditional Capture

```python
from vnc_agent_bridge import VNCAgentBridge
import numpy as np

def has_error_dialog(screenshot):
    """Check if error dialog is visible by color analysis."""
    # Convert RGB to red channel
    red_channel = screenshot[:, :, 0]
    # Check if more than 5% of screen is bright red
    red_pixels = np.sum(red_channel > 200)
    total_pixels = screenshot.shape[0] * screenshot.shape[1]
    return (red_pixels / total_pixels) > 0.05

with VNCAgentBridge('test-server') as vnc:
    # Take action
    vnc.mouse.left_click(100, 100)
    
    # Capture only if error appears
    screenshot = vnc.screenshot.capture(delay=0.5)
    
    if has_error_dialog(screenshot):
        vnc.screenshot.save('error_condition.png')
        print("Error detected!")
```

### Advanced: Region-Based Detection

```python
def detect_button_state(vnc, button_region):
    """Detect if button is highlighted/active."""
    x, y, width, height = button_region
    region = vnc.screenshot.capture_region(x, y, width, height)
    
    # Highlight usually has more bright colors
    brightness = np.mean(np.max(region[:, :, :3], axis=2))
    is_highlighted = brightness > 200
    
    return is_highlighted

with VNCAgentBridge('localhost') as vnc:
    button_rect = (100, 150, 80, 40)
    
    if detect_button_state(vnc, button_rect):
        print("Button is highlighted")
        vnc.mouse.left_click(140, 170)
```

---

## Pattern 2: Sequential Screenshot Collection

Collect multiple screenshots during a workflow for later analysis or reporting.

### Simple Sequential Collection

```python
from vnc_agent_bridge import VNCAgentBridge
from datetime import datetime

def run_workflow_with_screenshots(vnc, output_dir):
    """Execute workflow and collect screenshots at each step."""
    screenshots = []
    step = 0
    
    # Step 1: Navigate
    vnc.mouse.left_click(50, 50)
    step += 1
    screenshot = vnc.screenshot.capture(delay=1.0)
    filename = f"{output_dir}/step_{step:02d}_navigate.png"
    vnc.screenshot.save(filename)
    screenshots.append(filename)
    
    # Step 2: Input data
    vnc.keyboard.type_text("test data")
    step += 1
    screenshot = vnc.screenshot.capture(delay=0.5)
    filename = f"{output_dir}/step_{step:02d}_input.png"
    vnc.screenshot.save(filename)
    screenshots.append(filename)
    
    # Step 3: Submit
    vnc.keyboard.press_key('return')
    step += 1
    screenshot = vnc.screenshot.capture(delay=2.0)
    filename = f"{output_dir}/step_{step:02d}_submit.png"
    vnc.screenshot.save(filename)
    screenshots.append(filename)
    
    return screenshots

with VNCAgentBridge('localhost') as vnc:
    screenshots = run_workflow_with_screenshots(vnc, 'workflow_steps')
    print(f"Collected {len(screenshots)} screenshots")
```

### With Timestamp Metadata

```python
import json
from datetime import datetime

with VNCAgentBridge('localhost') as vnc:
    metadata = {
        "workflow": "login_test",
        "start_time": datetime.now().isoformat(),
        "steps": []
    }
    
    # Step 1
    start_time = datetime.now()
    vnc.mouse.left_click(100, 100)
    vnc.screenshot.save('step_1.png', delay=1.0)
    
    metadata["steps"].append({
        "number": 1,
        "action": "click",
        "duration": (datetime.now() - start_time).total_seconds(),
        "screenshot": "step_1.png"
    })
    
    # Save metadata
    with open('workflow_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
```

---

## Pattern 3: Video Recording with Markers

Record video while performing actions and mark important moments.

### Recording with Event Markers

```python
from vnc_agent_bridge import VNCAgentBridge
import time

def record_with_markers(vnc, duration, events):
    """
    Record video and create event markers.
    
    Args:
        vnc: VNCAgentBridge instance
        duration: Recording duration in seconds
        events: List of (time, description) tuples
    """
    vnc.video.start_recording(fps=30.0)
    event_log = []
    start_time = time.time()
    
    for event_time, description in events:
        # Wait until event time
        wait_time = event_time - (time.time() - start_time)
        if wait_time > 0:
            time.sleep(wait_time)
        
        # Log event
        elapsed = time.time() - start_time
        event_log.append({
            "time": elapsed,
            "description": description,
            "screenshot": vnc.screenshot.capture()
        })
        
        print(f"[{elapsed:.1f}s] {description}")
    
    # Record until end
    remaining = duration - (time.time() - start_time)
    if remaining > 0:
        time.sleep(remaining)
    
    frames = vnc.video.stop_recording()
    return frames, event_log

with VNCAgentBridge('localhost') as vnc:
    events = [
        (1.0, "Click login button"),
        (3.0, "Enter username"),
        (5.0, "Enter password"),
        (6.0, "Submit login"),
    ]
    
    frames, log = record_with_markers(vnc, duration=10.0, events=events)
    vnc.video.save_frames(frames, 'recording/')
    
    # Save event log
    import json
    event_log_data = [
        {
            "time": e["time"],
            "description": e["description"]
        }
        for e in log
    ]
    with open('event_log.json', 'w') as f:
        json.dump(event_log_data, f, indent=2)
```

### Conditional Recording

```python
def record_until_success(vnc, max_duration=60):
    """Record until operation succeeds."""
    vnc.video.start_recording(fps=30.0)
    start_time = time.time()
    
    while time.time() - start_time < max_duration:
        screenshot = vnc.screenshot.capture()
        
        # Check for success (custom logic)
        if check_success_condition(screenshot):
            frames = vnc.video.stop_recording()
            return frames, True
        
        time.sleep(0.5)
    
    # Timeout - still stop recording
    frames = vnc.video.stop_recording()
    return frames, False

def check_success_condition(screenshot):
    """Check if operation succeeded."""
    # Look for specific text/color/pattern
    # This is simplified - real implementation would be more sophisticated
    green_channel = screenshot[:, :, 1]
    return np.mean(green_channel) > 150
```

---

## Pattern 4: Clipboard-Based Data Transfer

Use clipboard for efficient data transfer in workflows.

### Bidirectional Data Exchange

```python
from vnc_agent_bridge import VNCAgentBridge
import json

def send_config_via_clipboard(vnc, config_dict):
    """Send configuration dictionary via clipboard."""
    # Convert to JSON
    json_str = json.dumps(config_dict, indent=2)
    
    # Send to clipboard
    vnc.clipboard.send_text(json_str)
    print(f"Sent {len(json_str)} bytes to clipboard")
    
    # Paste into application
    vnc.mouse.left_click(300, 200)  # Click text area
    vnc.keyboard.hotkey('ctrl', 'v')  # Paste
    time.sleep(0.5)

def extract_result_via_clipboard(vnc, selection_action):
    """Extract result from application via clipboard."""
    # Clear clipboard
    vnc.clipboard.clear()
    
    # Perform action that copies result
    selection_action()
    
    # Wait for clipboard to be populated
    time.sleep(0.5)
    
    # Get result
    result_text = vnc.clipboard.get_text(timeout=2.0)
    
    if result_text:
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return result_text
    
    return None

with VNCAgentBridge('localhost') as vnc:
    # Send configuration
    config = {
        "username": "testuser",
        "password": "testpass",
        "server": "test.example.com"
    }
    send_config_via_clipboard(vnc, config)
    
    # Wait for processing
    time.sleep(2.0)
    
    # Extract result
    def copy_result():
        vnc.keyboard.hotkey('ctrl', 'a')  # Select all
        vnc.keyboard.hotkey('ctrl', 'c')  # Copy
    
    result = extract_result_via_clipboard(vnc, copy_result)
    print(f"Result: {result}")
```

### Large Data Transfer

```python
def transfer_large_data_chunked(vnc, data_str, chunk_size=1000):
    """Transfer large data via clipboard in chunks."""
    chunks = [data_str[i:i+chunk_size] for i in range(0, len(data_str), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        vnc.clipboard.send_text(chunk)
        print(f"Transferred chunk {i+1}/{len(chunks)}")
        
        # Paste chunk
        vnc.keyboard.hotkey('ctrl', 'v')
        time.sleep(0.1)

# Example: Transfer CSV data
with VNCAgentBridge('localhost') as vnc:
    csv_data = "id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n"
    transfer_large_data_chunked(vnc, csv_data)
```

---

## Pattern 5: Screenshot Comparison

Compare screenshots to detect changes or verify expected state.

### Simple Pixel Difference

```python
import numpy as np

def calculate_difference(screenshot1, screenshot2):
    """Calculate pixel-level difference between screenshots."""
    if screenshot1.shape != screenshot2.shape:
        raise ValueError("Screenshots have different sizes")
    
    # Calculate absolute difference
    diff = np.abs(screenshot1.astype(int) - screenshot2.astype(int))
    
    # Overall difference percentage
    max_possible = 255 * np.prod(screenshot1.shape)
    diff_percentage = (np.sum(diff) / max_possible) * 100
    
    return diff_percentage, diff

def detect_state_change(vnc, threshold=5.0):
    """Detect if screen changed significantly."""
    screenshot1 = vnc.screenshot.capture()
    time.sleep(0.5)
    screenshot2 = vnc.screenshot.capture()
    
    diff_pct, _ = calculate_difference(screenshot1, screenshot2)
    
    print(f"Screen change: {diff_pct:.2f}%")
    return diff_pct > threshold

with VNCAgentBridge('localhost') as vnc:
    # Perform action
    vnc.mouse.left_click(100, 100)
    
    # Check if screen changed
    if detect_state_change(vnc, threshold=2.0):
        print("Application responded to click")
    else:
        print("No response to click")
```

### Region Verification

```python
def verify_region_content(vnc, x, y, width, height, expected_color):
    """Verify specific region matches expected color."""
    region = vnc.screenshot.capture_region(x, y, width, height)
    
    # Get average color
    avg_color = np.mean(region[:, :, :3], axis=(0, 1))
    
    # Compare with expected (with tolerance)
    tolerance = 20
    match = np.all(np.abs(avg_color - expected_color) < tolerance)
    
    return match, avg_color

with VNCAgentBridge('localhost') as vnc:
    # Check if button area is green (success state)
    button_region = (100, 150, 80, 40)
    is_green, actual = verify_region_content(
        vnc,
        *button_region,
        expected_color=np.array([0, 255, 0])  # Green
    )
    
    if is_green:
        print("Button is green (success)")
    else:
        print(f"Button is {actual} - not green")
```

---

## Pattern 6: Combined Workflow with All Features

Complex workflow using screenshots, video, and clipboard together.

```python
from vnc_agent_bridge import VNCAgentBridge
import json
import time
from datetime import datetime

def run_complex_automation(vnc, config):
    """
    Run complex automation workflow:
    1. Record entire session
    2. Take screenshots at key points
    3. Use clipboard for data transfer
    4. Collect all results
    """
    
    results = {
        "start_time": datetime.now().isoformat(),
        "config": config,
        "screenshots": [],
        "steps": []
    }
    
    # Start video recording
    vnc.video.start_recording(fps=30.0)
    
    try:
        # Step 1: Login
        step_start = time.time()
        vnc.mouse.left_click(100, 100)
        vnc.keyboard.type_text(config['username'])
        vnc.keyboard.press_key('tab')
        vnc.keyboard.type_text(config['password'])
        
        # Screenshot after login
        vnc.screenshot.save('step_1_login.png', delay=1.0)
        results["screenshots"].append("step_1_login.png")
        
        results["steps"].append({
            "number": 1,
            "name": "Login",
            "duration": time.time() - step_start,
            "status": "completed"
        })
        
        # Step 2: Fill form via clipboard
        step_start = time.time()
        form_data = config['form_data']
        vnc.clipboard.send_text(json.dumps(form_data))
        
        # Navigate to form field
        vnc.keyboard.hotkey('ctrl', 'tab')
        vnc.keyboard.hotkey('ctrl', 'v')  # Paste
        
        vnc.screenshot.save('step_2_form.png', delay=0.5)
        results["screenshots"].append("step_2_form.png")
        
        results["steps"].append({
            "number": 2,
            "name": "Fill Form",
            "duration": time.time() - step_start,
            "status": "completed"
        })
        
        # Step 3: Submit and wait for result
        step_start = time.time()
        vnc.keyboard.press_key('return')
        time.sleep(2.0)
        
        vnc.screenshot.save('step_3_result.png')
        results["screenshots"].append("step_3_result.png")
        
        # Extract result via clipboard
        vnc.keyboard.hotkey('ctrl', 'a')
        vnc.keyboard.hotkey('ctrl', 'c')
        result_text = vnc.clipboard.get_text(timeout=1.0)
        
        results["steps"].append({
            "number": 3,
            "name": "Submit",
            "duration": time.time() - step_start,
            "status": "completed",
            "result": result_text
        })
        
    finally:
        # Stop recording
        frames = vnc.video.stop_recording()
        vnc.video.save_frames(frames, 'recording/')
        
        results["end_time"] = datetime.now().isoformat()
        results["video_frames"] = len(frames)
    
    return results

# Usage
with VNCAgentBridge('localhost') as vnc:
    config = {
        "username": "testuser",
        "password": "testpass",
        "form_data": {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Test message"
        }
    }
    
    results = run_complex_automation(vnc, config)
    
    # Save results
    with open('automation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Automation completed")
    print(f"  Steps: {len(results['steps'])}")
    print(f"  Screenshots: {len(results['screenshots'])}")
    print(f"  Video frames: {results['video_frames']}")
```

---

## Pattern 7: Error Recovery with Capture

Detect errors and capture context for debugging.

```python
from vnc_agent_bridge import VNCAgentBridge

class AutomationWithErrorCapture:
    """Automation with automatic error capture."""
    
    def __init__(self, vnc, error_dir='errors'):
        self.vnc = vnc
        self.error_dir = error_dir
        self.error_count = 0
    
    def capture_error(self, error_name, context=''):
        """Capture error context."""
        self.error_count += 1
        
        # Screenshot
        filename = f"{self.error_dir}/error_{self.error_count}_{error_name}.png"
        self.vnc.screenshot.save(filename)
        
        # Log
        log_file = f"{self.error_dir}/error_{self.error_count}_{error_name}.txt"
        with open(log_file, 'w') as f:
            f.write(f"Error: {error_name}\n")
            f.write(f"Context: {context}\n")
            f.write(f"Screenshot: {filename}\n")
        
        print(f"Error captured: {error_name}")
        return filename
    
    def run_action_with_recovery(self, action, max_retries=3):
        """Run action with error capture and retry."""
        for attempt in range(max_retries):
            try:
                action()
                return True
            except Exception as e:
                self.capture_error(
                    f"attempt_{attempt+1}",
                    f"Failed with: {str(e)}"
                )
                
                if attempt < max_retries - 1:
                    # Try recovery (example: click OK on error dialog)
                    try:
                        self.vnc.mouse.left_click(200, 250)  # OK button
                        time.sleep(0.5)
                    except:
                        pass
        
        return False

# Usage
with VNCAgentBridge('localhost') as vnc:
    automation = AutomationWithErrorCapture(vnc)
    
    def risky_action():
        vnc.mouse.left_click(100, 100)
        vnc.keyboard.type_text("data")
        vnc.keyboard.press_key('return')
    
    if automation.run_action_with_recovery(risky_action):
        print("Action succeeded")
    else:
        print("Action failed after retries")
```

---

## Performance Tips

### 1. Optimize Screenshot Capture

```python
# ❌ Slow: Full screenshot each time
for i in range(100):
    screenshot = vnc.screenshot.capture()
    process(screenshot)

# ✅ Fast: Capture region of interest
roi = (100, 100, 500, 500)
for i in range(100):
    region = vnc.screenshot.capture_region(*roi)
    process(region)
```

### 2. Use Incremental Updates

```python
# ❌ Slower: Full refresh each time
for i in range(10):
    vnc.screenshot.capture(incremental=False)

# ✅ Faster: Use incremental updates
for i in range(10):
    vnc.screenshot.capture(incremental=True)
```

### 3. Batch Operations

```python
# ❌ Inefficient: Separate operations
for item in items:
    vnc.keyboard.type_text(item)
    vnc.keyboard.press_key('return')

# ✅ More efficient: Combine with delays
for item in items:
    vnc.keyboard.type_text(item + '\n')
    time.sleep(0.1)  # Single delay between items
```

### 4. Memory Management

```python
# ❌ Memory leak: Hold all screenshots
screenshots = []
for i in range(1000):
    screenshots.append(vnc.screenshot.capture())

# ✅ Process and discard
for i in range(1000):
    screenshot = vnc.screenshot.capture()
    process_and_discard(screenshot)
```

---

## Common Gotchas

### 1. Timing Issues

```python
# ❌ Wrong: No delay for application processing
vnc.keyboard.press_key('return')
vnc.screenshot.capture()  # May capture before response

# ✅ Correct: Add delay for processing
vnc.keyboard.press_key('return')
vnc.screenshot.capture(delay=1.0)  # Wait for response
```

### 2. Clipboard Encoding

```python
# ❌ May fail: Special characters
vnc.clipboard.send_text("Data with\ttabs\n newlines")

# ✅ Better: Ensure proper encoding
import json
data = {"field": "Value with\ttabs"}
vnc.clipboard.send_text(json.dumps(data))
```

### 3. Region Out of Bounds

```python
# ❌ Will raise error
region = vnc.screenshot.capture_region(1900, 1900, 400, 400)

# ✅ Check bounds first
max_x = vnc._framebuffer.width
max_y = vnc._framebuffer.height
if x + width <= max_x and y + height <= max_y:
    region = vnc.screenshot.capture_region(x, y, width, height)
```

---

## See Also

- [Screenshot Capture Guide](screenshot_capture.md)
- [Video Recording Guide](video_recording.md)
- [Clipboard Management Guide](clipboard_management.md)
- [Getting Started Guide](getting_started.md)

---

**Last Updated:** October 27, 2025  
**Version:** v0.2.0  
**Status:** Complete ✅
