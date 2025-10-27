# Screenshot Capture Guide

This guide covers how to use the screenshot capture features of the VNC Agent Bridge package.

## Installation

Install with screenshot support:

```bash
pip install vnc-agent-bridge[capture]
```

This adds the required dependencies:
- `numpy` for array manipulation
- `Pillow` for image processing

## Basic Usage

### Connecting and Taking Screenshots

```python
from vnc_agent_bridge import VNCAgentBridge

# Connect to VNC server
with VNCAgentBridge('localhost', port=5900) as vnc:
    # Take screenshot
    screenshot = vnc.screenshot.capture()
    print(f"Screen size: {screenshot.shape}")  # (height, width, 4)
```

### Saving Screenshots

```python
with VNCAgentBridge('localhost') as vnc:
    # Save as PNG (default)
    vnc.screenshot.save('screen.png')
    
    # Save as JPEG
    vnc.screenshot.save('screen.jpg', format=ImageFormat.JPEG)
    
    # Save as BMP
    vnc.screenshot.save('screen.bmp', format=ImageFormat.BMP)
```

## Advanced Usage

### Region Capture

Capture specific areas of the screen:

```python
with VNCAgentBridge('localhost') as vnc:
    # Capture window area (400x300 pixels starting at 100,100)
    region = vnc.screenshot.capture_region(100, 100, 400, 300)
    
    # Save the region
    vnc.screenshot.save_region('window.png', 100, 100, 400, 300)
```

### Timing Control

Add delays for dynamic content:

```python
with VNCAgentBridge('localhost') as vnc:
    # Wait 2 seconds before capturing (let page load)
    vnc.screenshot.save('after_load.png', delay=2.0)
    
    # Take multiple screenshots with delays
    for i in range(3):
        vnc.screenshot.save(f'animation_{i}.png', delay=1.0)
```

### Working with Image Data

```python
import numpy as np
from PIL import Image

with VNCAgentBridge('localhost') as vnc:
    # Capture screenshot
    screenshot = vnc.screenshot.capture()
    
    # Convert to PIL Image
    pil_image = vnc.screenshot.to_pil_image(screenshot)
    
    # Apply PIL operations
    rotated = pil_image.rotate(90)
    cropped = pil_image.crop((100, 100, 300, 300))
    
    # Save processed image
    rotated.save('rotated.png')
    cropped.save('cropped.png')
```

## Image Formats

### PNG Format
Best for screenshots and lossless quality:

```python
# PNG preserves transparency and quality
vnc.screenshot.save('screenshot.png')  # Default format
vnc.screenshot.save('screenshot.png', format=ImageFormat.PNG)
```

### JPEG Format
Best for smaller file sizes:

```python
# JPEG converts RGBA to RGB (no transparency)
vnc.screenshot.save('photo.jpg', format=ImageFormat.JPEG)
vnc.screenshot.save_region('region.jpg', 0, 0, 800, 600, format=ImageFormat.JPEG)
```

### BMP Format
Uncompressed bitmap format:

```python
# BMP preserves all data, largest file size
vnc.screenshot.save('debug.bmp', format=ImageFormat.BMP)
```

## Integration with Other Features

### Mouse and Screenshot

```python
with VNCAgentBridge('localhost') as vnc:
    # Click a button
    vnc.mouse.left_click(500, 300)
    
    # Wait for UI to update and capture
    vnc.screenshot.save('after_click.png', delay=0.5)
```

### Keyboard and Screenshot

```python
with VNCAgentBridge('localhost') as vnc:
    # Type some text
    vnc.keyboard.type_text("Hello World")
    
    # Capture the result
    vnc.screenshot.save('typed_text.png')
```

### Scroll and Screenshot

```python
with VNCAgentBridge('localhost') as vnc:
    # Scroll down
    vnc.scroll.scroll_down(5)
    
    # Capture scrolled content
    vnc.screenshot.save('scrolled.png', delay=0.3)
```

## Error Handling

### Connection Errors

```python
from vnc_agent_bridge import VNCStateError

try:
    with VNCAgentBridge('localhost') as vnc:
        screenshot = vnc.screenshot.capture()
except VNCStateError as e:
    print(f"Not connected: {e}")
```

### Invalid Coordinates

```python
from vnc_agent_bridge import VNCInputError

try:
    region = vnc.screenshot.capture_region(-10, -10, 100, 100)
except VNCInputError as e:
    print(f"Invalid coordinates: {e}")
```

### Missing Dependencies

```python
try:
    vnc.screenshot.save('test.jpg', format=ImageFormat.JPEG)
except ImportError as e:
    print(f"Install Pillow: pip install vnc-agent-bridge[capture]")
```

## Performance Optimization

### Incremental Updates

```python
# Faster for small changes
vnc.screenshot.save('quick.png', incremental=True)

# More accurate for full state
vnc.screenshot.save('accurate.png', incremental=False)
```

### Region vs Full Screen

```python
# More efficient for small areas
region = vnc.screenshot.capture_region(100, 100, 200, 200)

# Less efficient (capture all, then crop)
full = vnc.screenshot.capture()
region = full[100:300, 100:300, :]  # Manual crop
```

## Real-World Examples

### Automated Testing

```python
def test_login_flow():
    with VNCAgentBridge('test-server') as vnc:
        # Navigate to login
        vnc.mouse.left_click(400, 200)
        vnc.keyboard.type_text("testuser")
        vnc.keyboard.press_key('tab')
        vnc.keyboard.type_text("password")
        vnc.keyboard.press_key('return')
        
        # Capture result
        vnc.screenshot.save('login_result.png', delay=1.0)
        
        # Could analyze image for success/failure indicators
```

### Documentation Generation

```python
def document_workflow(name: str):
    screenshots = []
    
    with VNCAgentBridge('demo-server') as vnc:
        # Step 1
        vnc.screenshot.save(f'{name}_step1.png')
        screenshots.append('step1.png')
        
        # Perform actions...
        vnc.mouse.left_click(100, 100)
        
        # Step 2
        vnc.screenshot.save(f'{name}_step2.png', delay=0.5)
        screenshots.append('step2.png')
    
    return screenshots
```

### Monitoring Application

```python
def monitor_application(interval: float = 5.0):
    with VNCAgentBridge('monitor-server') as vnc:
        while True:
            timestamp = time.strftime('%H%M%S')
            vnc.screenshot.save(f'monitor_{timestamp}.png')
            time.sleep(interval)
```

## API Reference

For complete API details, see: `docs/api/screenshot.md`

## Troubleshooting

### Common Issues

1. **"Pillow not available"**
   - Install: `pip install vnc-agent-bridge[capture]`

2. **"Not connected" errors**
   - Ensure VNCAgentBridge context manager is used
   - Check VNC server is running

3. **"Invalid coordinates"**
   - Coordinates must be >= 0
   - Width/height must be > 0
   - Check screen bounds

4. **Large file sizes**
   - Use JPEG for smaller files
   - Use region capture for smaller areas

5. **Slow captures**
   - Use incremental=True for faster updates
   - Use region capture when possible