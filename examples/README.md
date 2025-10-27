"""
VNC Agent Bridge - Examples

This directory contains comprehensive examples demonstrating how to use
VNC Agent Bridge for various tasks and use cases.

Examples Overview
=================

1. **basic_usage.py**
   - Simple connection and operations
   - Context manager usage
   - Basic mouse, keyboard, and scroll operations
   - Error handling patterns

2. **advanced_workflow.py**
   - Complex multi-step workflows
   - Form filling
   - File operations
   - Web navigation
   - Realistic timing patterns
   - Keyboard shortcuts
   - Drag and drop operations

3. **error_handling.py**
   - Connection error handling
   - Input validation errors
   - State errors
   - Retry patterns
   - Error recovery
   - Exception hierarchy
   - Best practices

4. **ai_agent_example.py**
   - AI agent workflow pattern
   - Perception -> Planning -> Execution -> Verification
   - Goal-based planning
   - Complex workflows
   - Error recovery

Quick Start
===========

Installation:
    pip install vnc-agent-bridge

Basic Usage:
    from vnc_agent_bridge import VNCAgentBridge

    with VNCAgentBridge('localhost', port=5900) as vnc:
        vnc.mouse.left_click(100, 100)
        vnc.keyboard.type_text("Hello")
        vnc.scroll.scroll_down(3)

Common Patterns
===============

Pattern 1: Context Manager (Recommended)
-----------------------------------------
from vnc_agent_bridge import VNCAgentBridge

with VNCAgentBridge('host', port=5900) as vnc:
    # Automatic connection
    vnc.mouse.left_click(100, 100)
    # Automatic disconnection


Pattern 2: Manual Connection
-----------------------------
from vnc_agent_bridge import VNCAgentBridge

vnc = VNCAgentBridge('host', port=5900)
try:
    vnc.connect()
    vnc.mouse.left_click(100, 100)
finally:
    vnc.disconnect()


Pattern 3: Error Handling
-------------------------
from vnc_agent_bridge import (
    VNCAgentBridge,
    VNCConnectionError,
    VNCInputError
)

try:
    with VNCAgentBridge('host') as vnc:
        vnc.mouse.left_click(x, y)
except VNCConnectionError as e:
    print(f"Connection failed: {e}")
except VNCInputError as e:
    print(f"Invalid input: {e}")


Pattern 4: Timing Control
--------------------------
with VNCAgentBridge('host') as vnc:
    # No delay (fast)
    vnc.mouse.left_click(100, 100, delay=0)
    
    # Quick operation (100ms)
    vnc.mouse.left_click(100, 100, delay=0.1)
    
    # Human-like timing (500ms)
    vnc.mouse.left_click(100, 100, delay=0.5)
    
    # Deliberate action (1+ second)
    vnc.mouse.left_click(100, 100, delay=1.0)


Running Examples
================

Navigate to the examples directory:
    cd examples

Run basic usage:
    python basic_usage.py

Run advanced workflows:
    python advanced_workflow.py

Run error handling (no VNC server needed):
    python error_handling.py

Run AI agent examples:
    python ai_agent_example.py


API Overview
============

Mouse Controller
----------------
vnc.mouse.left_click(x, y, delay=0)      # Left click
vnc.mouse.right_click(x, y, delay=0)     # Right click
vnc.mouse.double_click(x, y, delay=0)    # Double click
vnc.mouse.move_to(x, y, delay=0)         # Move cursor
vnc.mouse.drag_to(x, y, duration=1.0, delay=0)  # Drag
vnc.mouse.get_position()                 # Get position

Keyboard Controller
-------------------
vnc.keyboard.type_text(text, delay=0)    # Type text
vnc.keyboard.press_key(key, delay=0)     # Press key
vnc.keyboard.hotkey(*keys, delay=0)      # Hotkey combo
vnc.keyboard.keydown(key, delay=0)       # Hold key
vnc.keyboard.keyup(key, delay=0)         # Release key

Scroll Controller
-----------------
vnc.scroll.scroll_up(amount=3, delay=0)  # Scroll up
vnc.scroll.scroll_down(amount=3, delay=0)  # Scroll down
vnc.scroll.scroll_to(x, y, delay=0)      # Scroll at position


Key Names
=========

Special Keys
  'return', 'tab', 'escape', 'backspace', 'delete', 'space'

Function Keys
  'f1', 'f2', ..., 'f12'

Arrow Keys
  'up', 'down', 'left', 'right'

Modifiers
  'shift', 'ctrl', 'alt', 'cmd'

Character Keys
  Single characters: 'a', 'A', '1', '!', etc.


Connection Parameters
=====================

host (required)
    - Hostname or IP address of VNC server
    - Example: 'localhost', '192.168.1.100', 'vnc.example.com'

port (default: 5900)
    - VNC server port
    - Example: 5900 (default), 5901, 5902

username (optional)
    - Authentication username
    - Only needed if VNC server requires authentication

password (optional)
    - Authentication password
    - Only needed if VNC server requires authentication

timeout (default: 10.0)
    - Connection timeout in seconds
    - Example: 10.0 (default), 30.0 (longer)


Exception Types
===============

VNCException
    - Base exception for all VNC errors

VNCConnectionError
    - Connection to VNC server failed

VNCInputError
    - Invalid input provided (e.g., negative coordinates)

VNCStateError
    - Operation attempted in invalid state (e.g., before connecting)

VNCTimeoutError
    - Operation timed out

VNCProtocolError
    - VNC protocol violation


Requirements
=============

- Python 3.8+
- VNC server (for running examples)
- Network access to VNC server


Troubleshooting
================

Connection Refused
    - Ensure VNC server is running
    - Check host and port are correct
    - Verify no firewall blocking port

Timeout
    - Check network connectivity
    - Increase timeout parameter
    - Verify VNC server is responding

Invalid Coordinates
    - Coordinates must be non-negative
    - Coordinates must be within screen bounds
    - Use get_position() to verify current position

Key Not Found
    - Check key name spelling
    - Refer to "Key Names" section
    - Use single character for alphanumeric


Additional Resources
====================

- Full API Documentation: docs/api/
- Usage Guides: docs/guides/
- GitHub Repository: https://github.com/Ganzzi/vnc-agent-bridge
- Issue Tracker: https://github.com/Ganzzi/vnc-agent-bridge/issues


Support
=======

- Issues: GitHub Issues
- Questions: GitHub Discussions
- Bugs: GitHub Issues with detailed reproduction steps
"""

# Examples can be imported and run programmatically:
#
# from examples.basic_usage import example_1_basic_connection
# example_1_basic_connection()
