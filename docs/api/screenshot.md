# ScreenshotController API Reference

## Overview

The `ScreenshotController` class provides comprehensive screenshot capture capabilities for VNC sessions. It supports capturing full screen or specific regions, saving to multiple image formats, and converting between different image representations.

## Class Signature

```python
class ScreenshotController:
    """Handles screenshot capture operations."""
    
    def __init__(
        self,
        connection: VNCConnection,
        framebuffer: FramebufferManager
    ) -> None:
        """Initialize screenshot controller.
        
        Args:
            connection: VNC connection instance
            framebuffer: Framebuffer manager instance
        """
```

## Methods

### capture()

```python
def capture(
    self,
    incremental: bool = False,
    delay: float = 0
) -> np.ndarray:
    """
    Capture current screen as numpy array.
    
    Args:
        incremental: Use incremental update (faster) or full refresh
        delay: Wait time before capture (seconds)
        
    Returns:
        RGBA numpy array with shape (height, width, 4)
        
    Raises:
        VNCStateError: If not connected to VNC server
        VNCProtocolError: If framebuffer update fails
    """
```

**Example:**
```python
# Capture full screen
screenshot = vnc.screenshot.capture()
print(f"Shape: {screenshot.shape}")  # (height, width, 4)

# Capture with full refresh
screenshot = vnc.screenshot.capture(incremental=False)

# Capture after delay
screenshot = vnc.screenshot.capture(delay=1.0)
```

### capture_region()

```python
def capture_region(
    self,
    x: int,
    y: int,
    width: int,
    height: int,
    delay: float = 0
) -> np.ndarray:
    """
    Capture specific screen region.
    
    Args:
        x: Top-left X coordinate (must be >= 0)
        y: Top-left Y coordinate (must be >= 0)
        width: Region width (must be > 0)
        height: Region height (must be > 0)
        delay: Wait time before capture (seconds)
        
    Returns:
        RGBA numpy array with shape (height, width, 4)
        
    Raises:
        VNCInputError: If coordinates are invalid
        VNCStateError: If not connected to VNC server
    """
```

**Example:**
```python
# Capture 400x300 region starting at (100, 100)
region = vnc.screenshot.capture_region(100, 100, 400, 300)

# Capture with delay
region = vnc.screenshot.capture_region(50, 50, 200, 150, delay=0.5)
```

### save()

```python
def save(
    self,
    filepath: str,
    format: ImageFormat = ImageFormat.PNG,
    incremental: bool = False,
    delay: float = 0
) -> None:
    """
    Capture and save screenshot to file.
    
    Args:
        filepath: Output file path (will be created/overwritten)
        format: Image format (PNG, JPEG, BMP)
        incremental: Use incremental update
        delay: Wait time before capture (seconds)
        
    Raises:
        VNCInputError: If filepath is invalid
        VNCStateError: If not connected
        OSError: If file cannot be written
        ImportError: If Pillow not available for JPEG/BMP
    """
```

**Example:**
```python
# Save as PNG (default)
vnc.screenshot.save('screenshot.png')

# Save as JPEG
vnc.screenshot.save('screenshot.jpg', format=ImageFormat.JPEG)

# Save as BMP
vnc.screenshot.save('screenshot.bmp', format=ImageFormat.BMP)

# Save with delay
vnc.screenshot.save('delayed.png', delay=2.0)
```

### save_region()

```python
def save_region(
    self,
    filepath: str,
    x: int,
    y: int,
    width: int,
    height: int,
    format: ImageFormat = ImageFormat.PNG,
    delay: float = 0
) -> None:
    """
    Capture and save screen region to file.
    
    Args:
        filepath: Output file path
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Region width
        height: Region height
        format: Image format
        delay: Wait time before capture (seconds)
        
    Raises:
        VNCInputError: If coordinates or filepath invalid
        VNCStateError: If not connected
        OSError: If file cannot be written
    """
```

**Example:**
```python
# Save window region
vnc.screenshot.save_region('window.png', 100, 100, 400, 300)

# Save region as JPEG
vnc.screenshot.save_region(
    'region.jpg',
    x=50, y=50,
    width=200, height=150,
    format=ImageFormat.JPEG
)
```

### to_pil_image()

```python
def to_pil_image(self, array: np.ndarray) -> Image.Image:
    """
    Convert numpy array to PIL Image.
    
    Args:
        array: RGBA numpy array from capture() methods
        
    Returns:
        PIL Image object (mode RGBA)
        
    Raises:
        ImportError: If Pillow not available
        ValueError: If array format invalid
    """
```

**Example:**
```python
# Capture and convert to PIL
screenshot = vnc.screenshot.capture()
pil_image = vnc.screenshot.to_pil_image(screenshot)

# Use PIL operations
pil_image.rotate(90).save('rotated.png')
```

### to_bytes()

```python
def to_bytes(
    self,
    array: np.ndarray,
    format: ImageFormat = ImageFormat.PNG
) -> bytes:
    """
    Convert numpy array to image bytes.
    
    Args:
        array: RGBA numpy array from capture() methods
        format: Image format for encoding
        
    Returns:
        Image data as bytes
        
    Raises:
        ImportError: If Pillow not available
        ValueError: If array format or format invalid
    """
```

**Example:**
```python
# Get image bytes for API response
screenshot = vnc.screenshot.capture()
png_bytes = vnc.screenshot.to_bytes(screenshot, ImageFormat.PNG)

# Send over network
send_to_api(png_bytes)
```

## Image Formats

### PNG (Portable Network Graphics)
- **Best for:** Screenshots, lossless quality
- **Supports:** Full RGBA (transparency)
- **File size:** Larger than JPEG
- **Use case:** Documentation, archiving

### JPEG (Joint Photographic Experts Group)
- **Best for:** Photographs, smaller file size
- **Supports:** RGB only (converted from RGBA)
- **Compression:** Lossy, adjustable quality
- **Use case:** Web sharing, storage

### BMP (Bitmap)
- **Best for:** Simple images, no compression needed
- **Supports:** Full RGBA
- **File size:** Large, uncompressed
- **Use case:** Technical analysis, debugging

## Error Handling

### VNCInputError
- Invalid coordinates (negative values)
- Invalid region dimensions (zero or negative)
- Invalid file paths
- Unsupported image formats

### VNCStateError
- Operations when not connected to VNC server
- Framebuffer not available

### ImportError
- Pillow not installed for image operations
- Use `pip install vnc-agent-bridge[capture]` to install

### OSError
- File write permissions
- Disk space issues
- Invalid file paths

## Performance Notes

- **Incremental updates:** Faster for small changes
- **Full refresh:** More accurate but slower
- **Region capture:** More efficient than full screen + crop
- **Memory usage:** RGBA arrays use 4 bytes per pixel
- **File I/O:** PNG is fastest to save, JPEG slowest

## Dependencies

**Required for screenshot features:**
```bash
pip install vnc-agent-bridge[capture]
```

This installs:
- `numpy`: Array manipulation
- `Pillow`: Image processing and file I/O

**Optional:** Can be used without these dependencies for basic VNC control.