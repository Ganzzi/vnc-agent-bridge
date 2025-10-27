# VideoRecorder API Reference

**Module:** `vnc_agent_bridge.core.video`

The `VideoRecorder` class provides screen recording capabilities for VNC Agent Bridge. It allows you to capture screen sessions as a sequence of frames with precise FPS control.

## Overview

`VideoRecorder` enables three recording patterns:

1. **Fixed-duration recording** - Record for a specified time at target FPS
2. **Condition-based recording** - Record until a condition is met
3. **Background recording** - Start/stop recording in a separate thread

## Class Reference

### VideoRecorder

Main class for screen recording operations.

```python
class VideoRecorder:
    """Records screen sessions as video frames."""
```

#### Constructor

```python
def __init__(
    self,
    connection: VNCConnection,
    framebuffer: FramebufferManager,
    screenshot: ScreenshotController
) -> None:
```

**Parameters:**
- `connection`: VNCConnection instance for server communication
- `framebuffer`: FramebufferManager instance for screen data
- `screenshot`: ScreenshotController instance for frame capture

**Raises:**
- `VNCStateError`: If framebuffer or screenshot is None

**Example:**
```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    recorder = vnc.video
    # recorder is ready to use
```

---

## Methods

### record()

Record screen for a fixed duration at specified FPS.

```python
def record(
    self,
    duration: float,
    fps: float = 30.0,
    delay: float = 0
) -> List[VideoFrame]
```

**Parameters:**
- `duration` (float, required): Recording duration in seconds
  - Must be positive
  - Example: `10.0` for 10 seconds
- `fps` (float, optional, default=30.0): Target frames per second
  - Must be positive
  - Typical values: 15.0, 24.0, 30.0, 60.0
- `delay` (float, optional, default=0): Wait time before starting
  - In seconds
  - Useful for timing actions

**Returns:**
- `List[VideoFrame]`: List of captured frames with timestamps

**Raises:**
- `VNCInputError`: If duration ≤ 0 or fps ≤ 0
- `VNCStateError`: If not connected to VNC server

**Frame Information:**
Each `VideoFrame` contains:
- `timestamp`: Seconds since recording start
- `data`: numpy array (height, width, 4) RGBA uint8
- `frame_number`: Zero-indexed frame number

**Example 1: Simple recording**
```python
with VNCAgentBridge('localhost') as vnc:
    # Record 10 seconds at 30 FPS
    frames = vnc.video.record(duration=10.0, fps=30.0)
    print(f"Recorded {len(frames)} frames")
```

**Example 2: Recording with delay**
```python
with VNCAgentBridge('localhost') as vnc:
    # Wait 2 seconds, then record 5 seconds
    frames = vnc.video.record(duration=5.0, fps=30.0, delay=2.0)
```

**Example 3: High-speed recording**
```python
with VNCAgentBridge('localhost') as vnc:
    # Record at 60 FPS for smooth motion
    frames = vnc.video.record(duration=10.0, fps=60.0)
    fps_actual = vnc.video.get_frame_rate(frames)
    print(f"Achieved {fps_actual:.1f} FPS")
```

**Performance Notes:**
- FPS may not be exactly achieved depending on system performance
- Use `get_frame_rate()` to check actual frame rate
- Higher FPS requires more processing power
- 30 FPS is recommended for most scenarios

---

### record_until()

Record screen until a condition is met or timeout reached.

```python
def record_until(
    self,
    condition: Callable[[], bool],
    max_duration: float = 60.0,
    fps: float = 30.0,
    delay: float = 0
) -> List[VideoFrame]
```

**Parameters:**
- `condition` (Callable, required): Function that returns True to stop
  - Called once per frame
  - Should return quickly (< 1 frame interval)
  - Exceptions caught and ignored
- `max_duration` (float, optional, default=60.0): Maximum recording time
  - In seconds
  - Prevents infinite recording if condition never met
- `fps` (float, optional, default=30.0): Target frames per second
- `delay` (float, optional, default=0): Wait time before starting

**Returns:**
- `List[VideoFrame]`: List of frames (may stop early if condition met)

**Raises:**
- `VNCInputError`: If max_duration ≤ 0 or fps ≤ 0
- `VNCStateError`: If not connected

**Example 1: Stop on window appearance**
```python
with VNCAgentBridge('localhost') as vnc:
    def window_loaded():
        # Take screenshot and check for success indicator
        screenshot = vnc.screenshot.capture()
        # Check if loading spinner is gone (simplified)
        return screenshot[100:110, 100:110].mean() > 200
    
    frames = vnc.video.record_until(
        condition=window_loaded,
        max_duration=30.0,
        fps=30.0
    )
    print(f"Recording stopped after {len(frames)} frames")
```

**Example 2: Stop on user action**
```python
import time

with VNCAgentBridge('localhost') as vnc:
    start_time = time.time()
    
    def timeout_reached():
        return time.time() - start_time >= 5.0
    
    frames = vnc.video.record_until(timeout_reached)
```

**Example 3: Stop on pattern detection**
```python
with VNCAgentBridge('localhost') as vnc:
    def dialog_closed():
        try:
            screenshot = vnc.screenshot.capture()
            # Check if dialog window is visible
            # (simple pixel check - use image processing for real apps)
            return screenshot[200, 200, 3] < 50  # Alpha channel
        except:
            return False
    
    frames = vnc.video.record_until(dialog_closed, max_duration=10.0)
```

**Important Notes:**
- Condition is called frequently - keep it efficient
- Exceptions in condition are silently caught
- Recording stops on condition True OR max_duration reached
- Max duration acts as safety mechanism

---

### start_recording()

Start recording in a background thread (non-blocking).

```python
def start_recording(
    self,
    fps: float = 30.0,
    delay: float = 0
) -> None
```

**Parameters:**
- `fps` (float, optional, default=30.0): Target frames per second
- `delay` (float, optional, default=0): Wait before starting

**Returns:**
- None

**Raises:**
- `VNCInputError`: If fps ≤ 0
- `VNCStateError`: If already recording or not connected

**Example 1: Simple background recording**
```python
with VNCAgentBridge('localhost') as vnc:
    # Start recording
    vnc.video.start_recording(fps=30.0)
    
    # Perform actions while recording
    vnc.mouse.left_click(100, 100)
    vnc.keyboard.type_text("test data")
    
    # Stop and get frames
    frames = vnc.video.stop_recording()
    print(f"Recorded {len(frames)} frames")
```

**Example 2: Record action sequence**
```python
with VNCAgentBridge('localhost') as vnc:
    vnc.video.start_recording(fps=24.0)
    
    # Open menu
    vnc.mouse.right_click(200, 200)
    time.sleep(0.5)
    
    # Click option
    vnc.mouse.left_click(250, 300)
    time.sleep(1.0)
    
    # Stop recording
    frames = vnc.video.stop_recording()
```

**Thread Safety:**
- Runs in separate daemon thread
- Non-blocking call returns immediately
- Call `stop_recording()` to retrieve frames
- Only one recording session at a time

---

### stop_recording()

Stop background recording and return frames.

```python
def stop_recording(self) -> List[VideoFrame]
```

**Parameters:**
- None

**Returns:**
- `List[VideoFrame]`: Frames captured since `start_recording()`

**Raises:**
- `VNCStateError`: If not currently recording

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    # Start and do actions
    vnc.video.start_recording()
    vnc.mouse.left_click(100, 100)
    time.sleep(2.0)
    
    # Stop and process
    frames = vnc.video.stop_recording()
    print(f"Duration: {vnc.video.get_duration(frames):.1f}s")
```

**Important:**
- Blocks until recording thread completes
- Must call `start_recording()` first
- Call only once per recording session

---

### is_recording()

Check if currently recording in background.

```python
def is_recording(self) -> bool
```

**Returns:**
- `bool`: True if recording, False otherwise

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    vnc.video.start_recording()
    
    if vnc.video.is_recording():
        print("Recording in progress")
    
    vnc.video.stop_recording()
```

---

### save_frames()

Save recorded frames to individual image files.

```python
def save_frames(
    self,
    frames: List[VideoFrame],
    directory: str,
    prefix: str = "frame",
    format: ImageFormat = ImageFormat.PNG
) -> None
```

**Parameters:**
- `frames` (List[VideoFrame], required): Frames to save
- `directory` (str, required): Output directory path
  - Created if doesn't exist
  - Example: "output/video_frames"
- `prefix` (str, optional, default="frame"): Filename prefix
  - Files named: `{prefix}_000000.{format}`
  - Example: "scene_000000.png", "scene_000001.png"
- `format` (ImageFormat, optional, default=PNG): Image format
  - Options: ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.BMP

**Raises:**
- `VNCInputError`: If frames list empty
- `OSError`: If directory creation or file write fails

**Example 1: Save as PNG**
```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=5.0, fps=30.0)
    
    # Save all frames
    vnc.video.save_frames(
        frames,
        directory="output/video",
        prefix="frame",
        format=ImageFormat.PNG
    )
```

**Example 2: Save with custom prefix**
```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=2.0, fps=24.0)
    
    vnc.video.save_frames(
        frames,
        directory="/tmp/recording",
        prefix="action_sequence",
        format=ImageFormat.PNG
    )
    
    # Creates: action_sequence_000000.png, action_sequence_000001.png, ...
```

**Example 3: Save as JPEG for smaller files**
```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=30.0, fps=30.0)
    
    # ~900 frames, JPEG is smaller than PNG
    vnc.video.save_frames(
        frames,
        directory="video_output",
        prefix="screen",
        format=ImageFormat.JPEG
    )
```

**Format Details:**
- **PNG**: Lossless, larger files, preserves quality
- **JPEG**: Lossy, smaller files, good for motion
- **BMP**: Uncompressed, very large files, rarely used

---

### get_frame_rate()

Calculate actual frame rate from recorded frames.

```python
def get_frame_rate(self, frames: List[VideoFrame]) -> float
```

**Parameters:**
- `frames` (List[VideoFrame], required): Recorded frames

**Returns:**
- `float`: Actual frames per second achieved

**Raises:**
- `VNCInputError`: If frames list empty or < 2 frames

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=10.0, fps=30.0)
    
    actual_fps = vnc.video.get_frame_rate(frames)
    target_fps = 30.0
    efficiency = (actual_fps / target_fps) * 100
    
    print(f"Target: {target_fps:.1f} FPS")
    print(f"Actual: {actual_fps:.1f} FPS")
    print(f"Efficiency: {efficiency:.1f}%")
```

**Calculation:**
```
FPS = (number_of_frames) / (time_of_last_frame - time_of_first_frame)
```

**Returns 0.0 if:**
- Frames list has < 2 items
- All frames have same timestamp

---

### get_duration()

Calculate total duration of recorded frames.

```python
def get_duration(self, frames: List[VideoFrame]) -> float
```

**Parameters:**
- `frames` (List[VideoFrame], required): Recorded frames

**Returns:**
- `float`: Total duration in seconds

**Raises:**
- `VNCInputError`: If frames list empty

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    frames = vnc.video.record(duration=10.0, fps=30.0)
    
    actual_duration = vnc.video.get_duration(frames)
    frame_count = len(frames)
    
    print(f"Frames: {frame_count}")
    print(f"Duration: {actual_duration:.2f}s")
    print(f"Average FPS: {frame_count/actual_duration:.1f}")
```

**Calculation:**
```
Duration = timestamp_of_last_frame - timestamp_of_first_frame
```

---

### frame_count

Property: Get number of frames from background recording.

```python
@property
def frame_count(self) -> int
```

**Returns:**
- `int`: Number of frames recorded

**Example:**
```python
with VNCAgentBridge('localhost') as vnc:
    vnc.video.start_recording(fps=30.0)
    time.sleep(1.0)
    
    # Check progress
    print(f"Frames so far: {vnc.video.frame_count}")
    
    frames = vnc.video.stop_recording()
    print(f"Total frames: {vnc.video.frame_count}")
```

**Note:**
- Only updated during background recording
- Returns 0 if not recording

---

## Data Types

### VideoFrame

Represents a single captured frame.

```python
@dataclass
class VideoFrame:
    timestamp: float        # Seconds since recording start
    data: np.ndarray       # Frame image (height, width, 4) RGBA
    frame_number: int      # Zero-indexed frame number
```

**Fields:**
- `timestamp`: Time in seconds from recording start
  - First frame always 0.0
  - Use for FPS calculations
- `data`: NumPy array with shape (height, width, 4)
  - Data type: uint8 (0-255 values)
  - Channels: RGBA (Red, Green, Blue, Alpha)
  - Use with PIL.Image or OpenCV for processing
- `frame_number`: Index of frame in sequence
  - Starts at 0
  - Increments for each frame

**Example:**
```python
frames = vnc.video.record(duration=1.0, fps=30.0)

for frame in frames[:5]:  # First 5 frames
    print(f"Frame {frame.frame_number}")
    print(f"  Timestamp: {frame.timestamp:.3f}s")
    print(f"  Shape: {frame.data.shape}")
    print(f"  Dtype: {frame.data.dtype}")
```

### ImageFormat

Enumeration for image export formats.

```python
class ImageFormat(str, Enum):
    PNG = "png"           # PNG format
    JPEG = "jpeg"         # JPEG format
    BMP = "bmp"           # BMP format
```

---

## Common Patterns

### Pattern 1: Record action and verify

```python
with VNCAgentBridge('target_server') as vnc:
    # Start recording
    vnc.video.start_recording(fps=30.0)
    
    # Perform action
    vnc.mouse.left_click(100, 100)
    time.sleep(1.0)
    
    # Stop and analyze
    frames = vnc.video.stop_recording()
    print(f"Recorded {len(frames)} frames in {vnc.video.get_duration(frames):.1f}s")
```

### Pattern 2: Record until completion

```python
with VNCAgentBridge('server') as vnc:
    def task_complete():
        screenshot = vnc.screenshot.capture()
        # Check for "Done" button or similar
        return True  # Simple example
    
    frames = vnc.video.record_until(
        task_complete,
        max_duration=60.0,
        fps=24.0
    )
    
    print(f"Task completed in {vnc.video.get_duration(frames):.1f}s")
```

### Pattern 3: Save recording for analysis

```python
with VNCAgentBridge('server') as vnc:
    # Record session
    frames = vnc.video.record(duration=30.0, fps=30.0)
    
    # Save frames
    vnc.video.save_frames(
        frames,
        directory="recordings/session_001",
        prefix="frame"
    )
    
    # Print statistics
    print(f"Saved {len(frames)} frames")
    print(f"FPS: {vnc.video.get_frame_rate(frames):.1f}")
    print(f"Duration: {vnc.video.get_duration(frames):.2f}s")
```

---

## Error Handling

```python
from vnc_agent_bridge.exceptions import VNCInputError, VNCStateError

with VNCAgentBridge('localhost') as vnc:
    try:
        frames = vnc.video.record(duration=-1)  # Invalid
    except VNCInputError as e:
        print(f"Invalid parameter: {e}")
    
    try:
        frames = vnc.video.record(duration=5.0)
    except VNCStateError as e:
        print(f"State error: {e}")
```

---

## Performance Considerations

- **FPS Target vs Actual**: Actual FPS depends on:
  - System CPU performance
  - Network latency
  - Screen resolution
  - Use `get_frame_rate()` to verify
  
- **Memory Usage**: Recording at high FPS uses memory:
  - 1080p at 30 FPS: ~250MB per 10 seconds
  - Limit recording duration or reduce FPS for long sessions
  
- **Threading**: Background recording runs in separate thread:
  - Non-blocking: `start_recording()` returns immediately
  - Thread-safe: Frames collected safely
  - Cleanup: `stop_recording()` waits for thread completion

---

## See Also

- `ScreenshotController` - Single screenshot capture
- `VNCAgentBridge` - Main facade
- `VNCConnection` - Low-level protocol handling
