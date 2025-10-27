"""Core modules for VNC Agent Bridge.

This package contains the core implementation of the VNC Agent Bridge library,
including protocol handling, input controllers, and the main facade.

Modules:
    - bridge: Main VNCAgentBridge facade class
    - connection: VNCConnection for VNC protocol handling
    - mouse: MouseController for mouse/pointer operations
    - keyboard: KeyboardController for keyboard input
    - scroll: ScrollController for scroll wheel operations

Example:
    Basic usage with context manager:
        from vnc_agent_bridge import VNCAgentBridge

        with VNCAgentBridge('localhost', port=5900) as vnc:
            vnc.mouse.left_click(100, 100)
            vnc.keyboard.type_text("Hello World")
            vnc.scroll.scroll_down(3)
"""
