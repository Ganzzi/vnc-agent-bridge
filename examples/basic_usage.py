#!/usr/bin/env python3
"""
Basic Usage Examples
====================

Simple examples demonstrating how to use VNC Agent Bridge for common tasks.

Examples:
    1. Connect and perform basic operations
    2. Use context manager for automatic cleanup
    3. Handle common exceptions

Requirements:
    - vnc-agent-bridge installed
    - VNC server running on localhost:5900 (or modify host/port)
"""

from vnc_agent_bridge import VNCAgentBridge, VNCException, VNCConnectionError


def example_1_basic_connection():
    """Example 1: Basic connection and operations."""
    print("Example 1: Basic Connection")
    print("-" * 50)

    # Create bridge connection
    vnc = VNCAgentBridge("localhost", port=5900)

    try:
        # Connect to VNC server
        vnc.connect()
        print("✓ Connected to VNC server")

        # Perform mouse click
        vnc.mouse.left_click(100, 100, delay=0.5)
        print("✓ Clicked at (100, 100)")

        # Get mouse position
        position = vnc.mouse.get_position()
        print(f"✓ Current mouse position: {position}")

        # Type some text
        vnc.keyboard.type_text("Hello from VNC Agent!")
        print("✓ Typed text")

        # Scroll down
        vnc.scroll.scroll_down(amount=3)
        print("✓ Scrolled down")

    finally:
        # Always disconnect
        vnc.disconnect()
        print("✓ Disconnected from VNC server")


def example_2_context_manager():
    """Example 2: Using context manager for automatic cleanup."""
    print("\nExample 2: Context Manager")
    print("-" * 50)

    # Use 'with' statement for automatic connection management
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("✓ Connected (automatic)")

        # Perform operations
        vnc.mouse.move_to(200, 200, delay=0.3)
        print("✓ Moved mouse to (200, 200)")

        # Click
        vnc.mouse.left_click()
        print("✓ Clicked at current position")

        # Disconnect happens automatically here
    print("✓ Disconnected (automatic)")


def example_3_keyboard_operations():
    """Example 3: Various keyboard operations."""
    print("\nExample 3: Keyboard Operations")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Type text
        vnc.keyboard.type_text("Important text", delay=0.1)
        print("✓ Typed: 'Important text'")

        # Press Enter
        vnc.keyboard.press_key("return")
        print("✓ Pressed Return")

        # Use hotkey: Ctrl+A (select all)
        vnc.keyboard.hotkey("ctrl", "a", delay=0.2)
        print("✓ Pressed Ctrl+A")

        # Use hotkey: Ctrl+C (copy)
        vnc.keyboard.hotkey("ctrl", "c")
        print("✓ Pressed Ctrl+C")

        # Hold and release key
        vnc.keyboard.keydown("shift")
        print("✓ Shift key down")
        vnc.keyboard.press_key("right")
        print("✓ Pressed Right arrow")
        vnc.keyboard.keyup("shift")
        print("✓ Shift key released")


def example_4_mouse_operations():
    """Example 4: Various mouse operations."""
    print("\nExample 4: Mouse Operations")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Move to position
        vnc.mouse.move_to(100, 100, delay=0.3)
        print("✓ Moved to (100, 100)")

        # Single click
        vnc.mouse.left_click()
        print("✓ Left click")

        # Right click (context menu)
        vnc.mouse.right_click(200, 200, delay=0.2)
        print("✓ Right clicked at (200, 200)")

        # Double click
        vnc.mouse.double_click(150, 150)
        print("✓ Double clicked at (150, 150)")

        # Drag to another position
        vnc.mouse.drag_to(300, 300, duration=2.0, delay=0.5)
        print("✓ Dragged to (300, 300) over 2 seconds")

        # Get current position
        x, y = vnc.mouse.get_position()
        print(f"✓ Current position: ({x}, {y})")


def example_5_scroll_operations():
    """Example 5: Scroll operations."""
    print("\nExample 5: Scroll Operations")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Scroll up
        vnc.scroll.scroll_up(amount=5, delay=0.2)
        print("✓ Scrolled up 5 ticks")

        # Scroll down
        vnc.scroll.scroll_down(amount=3)
        print("✓ Scrolled down 3 ticks")

        # Scroll at specific position
        vnc.scroll.scroll_to(500, 400)
        print("✓ Scrolled at (500, 400)")


def example_6_error_handling():
    """Example 6: Error handling."""
    print("\nExample 6: Error Handling")
    print("-" * 50)

    try:
        with VNCAgentBridge("invalid-host", port=5900) as vnc:
            vnc.mouse.left_click(100, 100)
    except VNCConnectionError as e:
        print(f"✓ Caught connection error: {e}")

    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        # Try to click without connecting
        vnc.mouse.left_click(100, 100)
    except Exception as e:
        print(f"✓ Caught error (not connected): {e}")

    try:
        with VNCAgentBridge("localhost", port=5900) as vnc:
            # Invalid coordinates
            vnc.mouse.left_click(-1, 100)
    except Exception as e:
        print(f"✓ Caught error (invalid coords): {e}")


if __name__ == "__main__":
    print("VNC Agent Bridge - Basic Usage Examples")
    print("=" * 50)
    print()

    # Note: These examples require a real VNC server running
    # In production, handle connection errors appropriately

    # Uncomment to run examples:
    # example_1_basic_connection()
    # example_2_context_manager()
    # example_3_keyboard_operations()
    # example_4_mouse_operations()
    # example_5_scroll_operations()
    # example_6_error_handling()

    print("\n" + "=" * 50)
    print("Examples are ready but commented out.")
    print("Uncomment at bottom to run with real VNC server.")
    print("=" * 50)
