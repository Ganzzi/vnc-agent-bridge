# VNC Agent Bridge Test Scripts

This directory contains specialized test scripts for testing individual features of the VNC Agent Bridge package.

## Available Test Scripts

### TCP Connection Tests
- `test_clipboard.py` - Tests clipboard operations (send, receive, clear)
- `test_screenshot.py` - Tests screenshot capture operations
- `test_video.py` - Tests video recording operations

### WebSocket Connection Tests
- `websocket_test_clipboard.py` - Tests clipboard operations over WebSocket
- `websocket_test_screenshot.py` - Tests screenshot capture over WebSocket
- `websocket_test_video.py` - Tests video recording over WebSocket

### Comprehensive Tests
- `tcp_comprehensive_test.py` - Tests all features over TCP
- `websocket_comprehensive_test.py` - Tests all features over WebSocket

## Environment Variables

### TCP Tests
```bash
VNC_HOST=192.168.1.5          # VNC server hostname/IP
WEBSOCKET_VNC_PORT=5900                 # VNC server port
VNC_PASSWORD=password         # VNC server password (optional)
```

### WebSocket Tests
```bash
WEBSOCKET_VNC_HOST=192.168.1.5      # Proxmox server hostname/IP
WEBSOCKET_VNC_HOST_PORT=8006             # Proxmox API port
WEBSOCKET_VNC_NODE=pve              # Proxmox node name
WEBSOCKET_VNC_VMID=100              # VM ID
WEBSOCKET_VNC_PORT=5900                 # VNC display port
WEBSOCKET_VNC_TICKET=...      # WebSocket authentication ticket
WEBSOCKET_VNC_API_TOKEN=...         # Proxmox API token
WEBSOCKET_VNC_CERTIFICATE_PEM=...       # SSL certificate (optional)
```

## Usage

### Running Individual Tests
```bash
# Test clipboard operations
python test_clipboard.py

# Test screenshot operations
python test_screenshot.py

# Test video recording
python test_video.py

# WebSocket versions
python websocket_test_clipboard.py
python websocket_test_screenshot.py
python websocket_test_video.py
```

### Running Comprehensive Tests
```bash
# Test all TCP features
python tcp_comprehensive_test.py

# Test all WebSocket features
python websocket_comprehensive_test.py
```

## Test Output

Each test creates a timestamped output directory in `test_output/` containing:
- Test results in JSON format
- Screenshots, video frames, and other generated files
- Detailed logs of test operations

## Requirements

```bash
pip install vnc-agent-bridge[full]           # For TCP tests
pip install vnc-agent-bridge[websocket,full] # For WebSocket tests
```

## Notes

- WebSocket tests require a Proxmox server with VNC WebSocket support
- Clipboard operations are asynchronous - immediate retrieval may return None
- Screenshot and video operations require framebuffer initialization
- All tests include proper error handling and detailed result reporting