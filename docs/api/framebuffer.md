# FramebufferManager API Reference

## Overview

The `FramebufferManager` class manages the remote framebuffer state and coordinate updates. It maintains an in-memory copy of the remote screen and processes incremental updates from the VNC server. This class is the foundation for screenshot capture and video recording functionality.

## Class Signature

```python
class FramebufferManager:
    """Manages framebuffer state and updates."""
    
    def __init__(
        self,
        connection: VNCConnection,
        config: FramebufferConfig
    ) -> None:
        """Initialize framebuffer manager.
        
        Args:
            connection: VNC connection instance
            config: Framebuffer configuration from server
        """
```

## Properties

### width

```python
@property
def width(self) -> int:
    """Get framebuffer width in pixels."""
```

**Returns:**
- `int`: Width of the framebuffer

**Example:**
```python
width = framebuffer.width
print(f"Screen width: {width}px")
```

---

### height

```python
@property
def height(self) -> int:
    """Get framebuffer height in pixels."""
```

**Returns:**
- `int`: Height of the framebuffer

**Example:**
```python
height = framebuffer.height
print(f"Screen height: {height}px")
```

---

### is_dirty

```python
@property
def is_dirty(self) -> bool:
    """Check if buffer has been updated since last check."""
```

**Returns:**
- `bool`: True if framebuffer was updated, False otherwise

**Example:**
```python
if framebuffer.is_dirty:
    print("Screen was updated")
```

---

## Methods

### initialize_buffer()

```python
def initialize_buffer(self) -> None:
    """
    Create initial framebuffer array.
    
    Raises:
        VNCStateError: If connection not ready
        ValueError: If invalid framebuffer dimensions
    """
```

**Purpose:**
Allocate and initialize the numpy array that holds the framebuffer data. Called after receiving ServerInit message.

**Raises:**
- `VNCStateError`: If framebuffer manager not in valid state
- `ValueError`: If framebuffer dimensions are invalid

**Example:**
```python
framebuffer.initialize_buffer()
print(f"Framebuffer initialized: {framebuffer.width}x{framebuffer.height}")
```

---

### request_update()

```python
def request_update(
    self,
    incremental: bool = True,
    x: int = 0,
    y: int = 0,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> None:
    """
    Request framebuffer update from server.
    
    Args:
        incremental: If True, request only changed regions
        x: Top-left X coordinate (default: 0)
        y: Top-left Y coordinate (default: 0)
        width: Region width (default: full width)
        height: Region height (default: full height)
        
    Raises:
        VNCStateError: If not connected
        VNCInputError: If coordinates invalid
    """
```

**Purpose:**
Request the server to send framebuffer updates. Incremental updates are faster but may miss changes. Full updates guarantee fresh data.

**Parameters:**
- `incremental`: Use incremental updates (faster, may miss rapid changes)
- `x`, `y`: Top-left corner of region to update
- `width`, `height`: Region size (None = entire framebuffer)

**Raises:**
- `VNCStateError`: If not connected to server
- `VNCInputError`: If coordinates out of bounds

**Example:**
```python
# Request full screen update
framebuffer.request_update(incremental=False)

# Request specific region
framebuffer.request_update(
    incremental=True,
    x=100, y=100,
    width=400, height=300
)
```

---

### process_update()

```python
def process_update(
    self,
    rectangles: List[Tuple[int, int, int, int, bytes]]
) -> None:
    """
    Process received framebuffer update.
    
    Args:
        rectangles: List of (x, y, width, height, pixel_data) tuples
        
    Raises:
        VNCProtocolError: If update format invalid
        MemoryError: If update too large
    """
```

**Purpose:**
Apply framebuffer updates received from the server to the in-memory buffer.

**Parameters:**
- `rectangles`: List of update rectangles from server, each containing:
  - `x`: X coordinate
  - `y`: Y coordinate
  - `width`: Rectangle width
  - `height`: Rectangle height
  - `pixel_data`: Raw pixel bytes (encoding-dependent)

**Raises:**
- `VNCProtocolError`: If pixel data format doesn't match framebuffer format
- `MemoryError`: If update data corrupted or too large

**Example:**
```python
# After receiving framebuffer update from server
rectangles = [(100, 100, 50, 50, b'\xff\x00\x00\xff...')]
framebuffer.process_update(rectangles)
```

---

### update_rectangle()

```python
def update_rectangle(
    self,
    x: int,
    y: int,
    width: int,
    height: int,
    pixel_data: bytes
) -> None:
    """
    Update specific rectangle in framebuffer.
    
    Args:
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Rectangle width
        height: Rectangle height
        pixel_data: Raw pixel bytes
        
    Raises:
        VNCInputError: If coordinates out of bounds
        VNCProtocolError: If pixel data format invalid
    """
```

**Purpose:**
Update a single rectangular region of the framebuffer. Used internally by `process_update()` for each rectangle.

**Parameters:**
- `x`, `y`: Top-left corner coordinates
- `width`, `height`: Rectangle dimensions
- `pixel_data`: Raw pixel data in framebuffer's pixel format

**Raises:**
- `VNCInputError`: If rectangle coordinates outside framebuffer bounds
- `VNCProtocolError`: If pixel data wrong size for rectangle

**Example:**
```python
# Update a 100x100 pixel region
pixel_data = b'\xff' * (100 * 100 * 4)  # RGBA, 4 bytes per pixel
framebuffer.update_rectangle(50, 50, 100, 100, pixel_data)
```

---

### get_buffer()

```python
def get_buffer(self) -> np.ndarray:
    """
    Get current framebuffer as numpy array.
    
    Returns:
        Numpy array with shape (height, width, 4) - RGBA format
    """
```

**Purpose:**
Retrieve the entire framebuffer as a numpy array. Useful for screenshot capture or analysis.

**Returns:**
- `np.ndarray`: Framebuffer as RGBA numpy array
  - Shape: `(height, width, 4)`
  - Dtype: `uint8`
  - Channel order: RGBA

**Example:**
```python
buffer = framebuffer.get_buffer()
print(f"Framebuffer shape: {buffer.shape}")  # (1080, 1920, 4)
print(f"Framebuffer dtype: {buffer.dtype}")  # uint8

# Access pixel at (100, 200)
pixel = buffer[100, 200]  # (R, G, B, A)
```

---

### get_region()

```python
def get_region(
    self,
    x: int,
    y: int,
    width: int,
    height: int
) -> np.ndarray:
    """
    Get specific region of framebuffer.
    
    Args:
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Region width
        height: Region height
        
    Returns:
        Numpy array with shape (height, width, 4) - RGBA format
        
    Raises:
        VNCInputError: If coordinates out of bounds
    """
```

**Purpose:**
Extract a rectangular region from the framebuffer. More efficient than extracting manually from the full buffer.

**Parameters:**
- `x`, `y`: Top-left corner of region
- `width`, `height`: Region dimensions

**Returns:**
- `np.ndarray`: Region as RGBA numpy array with shape `(height, width, 4)`

**Raises:**
- `VNCInputError`: If region extends outside framebuffer bounds

**Example:**
```python
# Get a 400x300 region starting at (100, 100)
region = framebuffer.get_region(100, 100, 400, 300)
print(f"Region shape: {region.shape}")  # (300, 400, 4)

# Compare with full buffer extraction (slower)
full_buffer = framebuffer.get_buffer()
region_manual = full_buffer[100:400, 100:500]  # Note: row then col
```

---

### reset()

```python
def reset(self) -> None:
    """
    Reset framebuffer state.
    
    Clears the buffer and resets dirty flags. Call after reconnection
    or when you want to force a full framebuffer refresh.
    """
```

**Purpose:**
Clear and reset the framebuffer. Used after server reconnection or to force a full refresh on next update.

**Example:**
```python
# After server reconnection
framebuffer.reset()
framebuffer.initialize_buffer()
framebuffer.request_update(incremental=False)
```

---

## Usage Examples

### Example 1: Basic Framebuffer Initialization

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    # Framebuffer is initialized automatically
    fb = vnc._framebuffer
    
    print(f"Screen: {fb.width}x{fb.height}")
    
    # Request full update
    fb.request_update(incremental=False)
    
    # Get full buffer
    buffer = fb.get_buffer()
    print(f"Buffer shape: {buffer.shape}")
```

### Example 2: Region Capture and Analysis

```python
from vnc_agent_bridge import VNCAgentBridge
import numpy as np

with VNCAgentBridge('localhost') as vnc:
    fb = vnc._framebuffer
    
    # Capture specific region
    region = fb.get_region(100, 100, 400, 300)
    
    # Analyze colors
    red_channel = region[:, :, 0]
    red_avg = np.mean(red_channel)
    print(f"Average red in region: {red_avg:.1f}")
    
    # Check for specific color (e.g., red warning indicator)
    is_red = np.any(red_channel > 200)
    print(f"Has bright red: {is_red}")
```

### Example 3: Continuous Monitoring

```python
from vnc_agent_bridge import VNCAgentBridge
import time

with VNCAgentBridge('localhost') as vnc:
    fb = vnc._framebuffer
    
    # Monitor for changes
    update_count = 0
    for i in range(10):
        fb.request_update(incremental=True)
        time.sleep(0.1)
        
        if fb.is_dirty:
            update_count += 1
            print(f"Update #{update_count}")
    
    print(f"Total updates: {update_count}")
```

### Example 4: Framebuffer Reset After Reconnection

```python
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('localhost') as vnc:
    fb = vnc._framebuffer
    
    # Do some work...
    
    # Connection lost and reconnected
    # Reset framebuffer state
    fb.reset()
    fb.initialize_buffer()
    
    # Get fresh full screen
    fb.request_update(incremental=False)
    buffer = fb.get_buffer()
```

---

## Type Definitions

### FramebufferConfig

```python
@dataclass
class FramebufferConfig:
    """Framebuffer configuration from VNC server."""
    
    width: int              # Screen width in pixels
    height: int             # Screen height in pixels
    pixel_format: bytes     # Pixel format specification
    name: str               # Server name/identifier
```

---

## Common Patterns

### Pattern: Update Request Loop

```python
fb = vnc._framebuffer
while True:
    # Request incremental updates
    fb.request_update(incremental=True)
    
    # Check if there were updates
    if fb.is_dirty:
        buffer = fb.get_buffer()
        # Process buffer...
    
    time.sleep(0.1)
```

### Pattern: Region Monitoring

```python
def monitor_region(x, y, width, height, check_fn):
    """Monitor specific region for changes."""
    fb = vnc._framebuffer
    
    while True:
        region = fb.get_region(x, y, width, height)
        
        if check_fn(region):
            return region
        
        time.sleep(0.5)
```

---

## Performance Considerations

1. **Incremental Updates**: Faster but may miss rapid changes. Use for continuous monitoring.
2. **Full Updates**: Slower but guaranteed fresh data. Use after important state transitions.
3. **Region Extraction**: More efficient than manual numpy slicing for repeated operations.
4. **Buffer Size**: Framebuffer size depends on screen resolution (e.g., 1920×1080×4 ≈ 8MB)
5. **Memory Usage**: Consider memory when accessing full buffer repeatedly

---

## Error Handling

```python
from vnc_agent_bridge import VNCAgentBridge, VNCInputError, VNCProtocolError

with VNCAgentBridge('localhost') as vnc:
    fb = vnc._framebuffer
    
    try:
        # Try to get region outside bounds
        region = fb.get_region(9000, 9000, 100, 100)
    except VNCInputError as e:
        print(f"Invalid coordinates: {e}")
    
    try:
        # Try to process invalid update
        fb.process_update([(0, 0, 100, 100, b'invalid')])
    except VNCProtocolError as e:
        print(f"Invalid protocol data: {e}")
```

---

## See Also

- [ScreenshotController API](screenshot.md) - Screenshot capture using framebuffer
- [VideoRecorder API](video.md) - Video recording using framebuffer
- [ClipboardController API](clipboard.md) - Clipboard management
- [VNCAgentBridge API](connection.md) - Main facade

---

**Last Updated:** October 27, 2025  
**Version:** v0.2.0  
**Status:** Complete ✅
