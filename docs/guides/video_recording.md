# Video Recording Guide

This guide shows how to use the `VideoRecorder` class to capture and save screen recordings from VNC servers.

## Table of Contents

1. [Basic Recording](#basic-recording)
2. [Fixed Duration vs Conditional](#fixed-duration-vs-conditional)
3. [Background Recording](#background-recording)
4. [Frame Management](#frame-management)
5. [Advanced Patterns](#advanced-patterns)
6. [Performance Tuning](#performance-tuning)

---

## Basic Recording

### Simple Recording

The simplest way to record is to specify a duration and frame rate:

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost', port=5900) as vnc:
    # Record 10 seconds at 30 FPS
    frames = vnc.video.record(duration=10.0, fps=30.0)
    print(f"Recorded {len(frames)} frames")
```

### Recording with Initial Delay

Add a delay before recording starts:

```python
with VNCAgentBridge('server.example.com') as vnc:
    # Wait 2 seconds, then record 5 seconds
    frames = vnc.video.record(
        duration=5.0,
        fps=30.0,
        delay=2.0
    )
    print(f"Recorded {len(frames)} frames")
```

This is useful when you need to wait for the system to reach a specific state before starting the recording.

---

## Fixed Duration vs Conditional

### Fixed Duration Recording

Use `record()` when you know how long to record:

```python
with VNCAgentBridge('localhost') as vnc:
    # Perform setup action
    vnc.mouse.left_click(100, 100)
    
    # Record while something happens
    frames = vnc.video.record(duration=10.0, fps=24.0)
    
    # Process frames
    print(f"Recorded {len(frames)} frames")
```

### Conditional Recording

Use `record_until()` to stop when a condition is met:

```python
import time

with VNCAgentBridge('localhost') as vnc:
    # Trigger an action
    vnc.keyboard.press_key('return')
    
    # Record until dialog closes (or 30 second timeout)
    start = time.time()
    
    def dialog_closed():
        # Simple check - better to use image recognition
        elapsed = time.time() - start
        return elapsed > 5.0  # Assume dialog closes in 5 seconds
    
    frames = vnc.video.record_until(
        condition=dialog_closed,
        max_duration=30.0,
        fps=30.0
    )
    
    print(f"Stopped after {len(frames)} frames")
```

### More Advanced Condition

Check the screen content to decide when to stop:

```python
with VNCAgentBridge('localhost') as vnc:
    # Trigger action that loads data
    vnc.mouse.left_click(200, 200)
    
    def loading_complete():
        # Take a screenshot
        screenshot = vnc.screenshot.capture()
        
        # Check if loading indicator is gone
        # (e.g., specific region should be white/gray, not animated)
        loading_area = screenshot[450:470, 400:600, :3]  # RGB only
        
        # If loading spinner gone, mean pixel value will be > 200
        is_complete = loading_area.mean() > 200
        
        return is_complete
    
    frames = vnc.video.record_until(
        loading_complete,
        max_duration=60.0,
        fps=30.0
    )
    
    print(f"Recording stopped, duration: {len(frames) / 30:.1f}s")
```

---

## Background Recording

### Basic Background Recording

Start recording without blocking, perform actions, then stop:

```python
import time
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    # Start recording in background
    vnc.video.start_recording(fps=30.0)
    
    # Perform multiple actions
    vnc.mouse.left_click(100, 100)
    time.sleep(0.5)
    
    vnc.keyboard.type_text("Hello World")
    time.sleep(0.5)
    
    vnc.mouse.right_click(200, 200)
    time.sleep(0.5)
    
    # Stop recording and get frames
    frames = vnc.video.stop_recording()
    
    print(f"Recorded {len(frames)} frames")
```

### Background Recording with Progress Check

Monitor recording progress while it's running:

```python
import time

with VNCAgentBridge('localhost') as vnc:
    # Start recording
    vnc.video.start_recording(fps=30.0)
    
    # While recording, check progress
    for i in range(10):
        time.sleep(0.5)
        current_frames = vnc.video.frame_count
        print(f"Progress: {current_frames} frames")
    
    # Stop when done
    frames = vnc.video.stop_recording()
    print(f"Final: {len(frames)} frames")
```

### Background Recording with Cleanup

Ensure recording is stopped even if error occurs:

```python
try:
    vnc = VNCAgentBridge('localhost')
    vnc.connect()
    
    vnc.video.start_recording(fps=30.0)
    
    # Do something that might fail
    vnc.mouse.left_click(999, 999)  # May fail
    
    frames = vnc.video.stop_recording()
    
finally:
    if vnc.is_connected:
        vnc.disconnect()
```

---

## Frame Management

### Getting Frame Statistics

Calculate frame rate and duration after recording:

```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=10.0, fps=30.0)
    
    # Get actual frame rate
    actual_fps = vnc.video.get_frame_rate(frames)
    print(f"Actual FPS: {actual_fps:.2f}")
    
    # Get total duration
    duration = vnc.video.get_duration(frames)
    print(f"Duration: {duration:.2f}s")
    
    # Manual calculations
    print(f"Frame count: {len(frames)}")
    print(f"Expected FPS: {len(frames) / duration:.2f}")
```

### Examining Frame Data

Access individual frame information:

```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=1.0, fps=10.0)
    
    # Examine first frame
    first_frame = frames[0]
    print(f"Frame number: {first_frame.frame_number}")
    print(f"Timestamp: {first_frame.timestamp:.3f}s")
    print(f"Shape: {first_frame.data.shape}")  # (height, width, 4)
    print(f"Dtype: {first_frame.data.dtype}")  # uint8
    
    # Get specific pixels
    pixel_value = first_frame.data[100, 100, :]  # RGBA at (100, 100)
    print(f"Pixel at (100, 100): {pixel_value}")
```

### Selecting Frame Subsets

Process only certain frames:

```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=10.0, fps=30.0)
    
    # Get every other frame (15 FPS from 30 FPS)
    selected = frames[::2]
    print(f"Selected {len(selected)} frames (every other)")
    
    # Get frames from specific time range
    start_time = 2.0
    end_time = 5.0
    subset = [f for f in frames if start_time <= f.timestamp <= end_time]
    print(f"Frames from {start_time}s to {end_time}s: {len(subset)}")
    
    # Get last N frames
    last_30_frames = frames[-30:]
    print(f"Last 30 frames: {len(last_30_frames)}")
```

### Saving Frames

Save recorded frames as image files:

```python
from vnc_agent_bridge.types.common import ImageFormat

with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=5.0, fps=30.0)
    
    # Save as PNG (lossless, larger files)
    vnc.video.save_frames(
        frames,
        directory="output/recording_png",
        prefix="frame",
        format=ImageFormat.PNG
    )
    
    # Save as JPEG (lossy, smaller files)
    vnc.video.save_frames(
        frames,
        directory="output/recording_jpeg",
        prefix="screen",
        format=ImageFormat.JPEG
    )
    
    print("Frames saved successfully")
```

---

## Advanced Patterns

### Pattern 1: Record Before and After

Record system state changes:

```python
with VNCAgentBridge('localhost') as vnc:
    # Record initial state
    print("Recording initial state...")
    initial_frames = vnc.video.record(duration=2.0, fps=10.0)
    
    # Trigger change
    print("Triggering action...")
    vnc.keyboard.hotkey('alt', 'tab')
    
    # Record after state
    print("Recording after state...")
    final_frames = vnc.video.record(duration=2.0, fps=10.0)
    
    # Save both
    vnc.video.save_frames(initial_frames, "output/before", prefix="frame")
    vnc.video.save_frames(final_frames, "output/after", prefix="frame")
```

### Pattern 2: Multi-Step Action Recording

Record a complex workflow:

```python
import time

with VNCAgentBridge('localhost') as vnc:
    steps = []
    
    # Step 1: Open file
    vnc.keyboard.hotkey('ctrl', 'o')
    frames = vnc.video.record(duration=3.0, fps=24.0)
    steps.append(("open_file", frames))
    
    time.sleep(0.5)
    
    # Step 2: Type filename
    vnc.keyboard.type_text("document.txt")
    frames = vnc.video.record(duration=1.0, fps=24.0)
    steps.append(("type_filename", frames))
    
    time.sleep(0.5)
    
    # Step 3: Press enter
    vnc.keyboard.press_key('return')
    frames = vnc.video.record(duration=3.0, fps=24.0)
    steps.append(("open_document", frames))
    
    # Save each step
    for i, (step_name, step_frames) in enumerate(steps):
        vnc.video.save_frames(
            step_frames,
            directory=f"output/step_{i:02d}_{step_name}",
            prefix="frame"
        )
```

### Pattern 3: Continuous Monitoring

Periodically record and discard, keeping only recent frames:

```python
import collections
import time

with VNCAgentBridge('localhost') as vnc:
    frame_buffer = collections.deque(maxlen=300)  # Keep 10 seconds at 30 FPS
    
    # Record for 60 seconds, keeping only recent frames
    for minute in range(2):
        frames = vnc.video.record(duration=30.0, fps=30.0)
        frame_buffer.extend(frames)
        print(f"Buffer has {len(frame_buffer)} frames")
    
    # Save final buffer
    vnc.video.save_frames(
        list(frame_buffer),
        directory="output/recent",
        prefix="frame"
    )
```

### Pattern 4: Conditional Segment Recording

Record different segments based on conditions:

```python
def create_segments():
    segments = []
    
    with VNCAgentBridge('localhost') as vnc:
        for i in range(3):
            segment_name = f"segment_{i}"
            
            def segment_done():
                # Define per-segment completion
                return i > 0 and i > len(segments)
            
            frames = vnc.video.record_until(
                segment_done,
                max_duration=20.0,
                fps=30.0
            )
            
            segments.append((segment_name, frames))
            
            if frames:
                vnc.video.save_frames(
                    frames,
                    directory=f"output/{segment_name}",
                    prefix="frame"
                )
    
    return segments
```

---

## Performance Tuning

### Choosing Frame Rate

Different scenarios benefit from different FPS:

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    # Slow interactions (15 FPS)
    # Use for: menu navigation, dialog clicks, typing
    frames_slow = vnc.video.record(duration=10.0, fps=15.0)
    
    # Normal interactions (24-30 FPS)
    # Use for: mouse movement, button clicks, general workflow
    frames_normal = vnc.video.record(duration=10.0, fps=30.0)
    
    # Fast interactions (60 FPS)
    # Use for: smooth scrolling, drag operations, animations
    frames_fast = vnc.video.record(duration=10.0, fps=60.0)
    
    print(f"Slow: {len(frames_slow)} frames")
    print(f"Normal: {len(frames_normal)} frames")
    print(f"Fast: {len(frames_fast)} frames")
```

### Memory-Efficient Recording

For very long recordings, use background recording with periodic saves:

```python
import time

def record_long_session(duration_seconds: int = 3600):
    """Record a long session (e.g., 1 hour) with periodic saves."""
    with VNCAgentBridge('localhost') as vnc:
        segment_duration = 60.0  # Save every 60 seconds
        segments_saved = 0
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # Record segment
            frames = vnc.video.record(
                duration=segment_duration,
                fps=30.0
            )
            
            # Save immediately to free memory
            vnc.video.save_frames(
                frames,
                directory=f"output/segment_{segments_saved:04d}",
                prefix="frame"
            )
            
            segments_saved += 1
            print(f"Saved segment {segments_saved}")
            
        print(f"Total segments saved: {segments_saved}")
```

### Checking Performance

Verify you're achieving target frame rate:

```python
with VNCAgentBridge('localhost') as vnc:
    target_fps = 30.0
    
    frames = vnc.video.record(duration=10.0, fps=target_fps)
    
    actual_fps = vnc.video.get_frame_rate(frames)
    efficiency = (actual_fps / target_fps) * 100
    
    print(f"Target FPS: {target_fps:.1f}")
    print(f"Actual FPS: {actual_fps:.1f}")
    print(f"Efficiency: {efficiency:.1f}%")
    
    if efficiency < 90:
        print("Warning: System may be overloaded")
        print("Consider: reducing FPS, improving network, or reducing resolution")
```

---

## Common Issues and Solutions

### Issue: Low Frame Rate

**Problem:** Getting only 10 FPS when requesting 30 FPS

**Causes:**
- System CPU overloaded
- Network latency
- VNC server slow
- Recording at high resolution

**Solutions:**
```python
# 1. Reduce FPS
frames = vnc.video.record(duration=10.0, fps=15.0)

# 2. Use background recording (non-blocking)
vnc.video.start_recording(fps=30.0)
time.sleep(5)
frames = vnc.video.stop_recording()

# 3. Profile actual performance
actual_fps = vnc.video.get_frame_rate(frames)
print(f"Actual: {actual_fps:.1f} FPS")
```

### Issue: Out of Memory

**Problem:** Recording long sessions causes out of memory errors

**Solution:**
```python
# Save frames in segments instead of all at once
for i in range(5):
    frames = vnc.video.record(duration=5.0, fps=30.0)
    vnc.video.save_frames(
        frames,
        directory=f"output/segment_{i}",
        prefix="frame"
    )
    # Frames discarded after saving, memory freed
```

### Issue: Timing Inaccuracy

**Problem:** Recorded frames have inconsistent timestamps

**Solution:**
```python
# Verify actual timing
frames = vnc.video.record(duration=10.0, fps=30.0)
duration = vnc.video.get_duration(frames)
fps = vnc.video.get_frame_rate(frames)

print(f"Duration: {duration:.2f}s (expected 10.0s)")
print(f"FPS: {fps:.1f} (expected 30.0)")
print(f"Frames: {len(frames)}")
```

---

## See Also

- [VideoRecorder API Reference](../api/video.md)
- [Screenshot Capture Guide](screenshot_capture.md)
- [Getting Started](getting_started.md)
- [Advanced Usage Guide](advanced.md)
