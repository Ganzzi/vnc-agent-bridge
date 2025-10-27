#!/usr/bin/env python3
"""
Advanced Workflow Examples
==========================

Complex examples demonstrating sophisticated use cases and patterns.

Examples:
    1. Form filling workflow
    2. File operations (open, save, type)
    3. Multi-step automated task
    4. Timing-aware operations for realistic behavior

Requirements:
    - vnc-agent-bridge installed
    - VNC server running on localhost:5900
"""

from vnc_agent_bridge import VNCAgentBridge
import time


def example_1_form_filling():
    """Example: Fill out an online form."""
    print("Example 1: Form Filling Workflow")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Wait for page to load
        time.sleep(1)

        # Click on first name field
        vnc.mouse.left_click(200, 100, delay=0.3)
        vnc.keyboard.type_text("John Doe", delay=0.05)
        print("✓ Entered first name")

        # Click on email field
        vnc.mouse.left_click(200, 150, delay=0.3)
        vnc.keyboard.type_text("john.doe@example.com", delay=0.05)
        print("✓ Entered email")

        # Click on phone field
        vnc.mouse.left_click(200, 200, delay=0.3)
        vnc.keyboard.type_text("555-0123", delay=0.05)
        print("✓ Entered phone")

        # Select from dropdown
        vnc.mouse.left_click(200, 250, delay=0.2)
        print("✓ Clicked dropdown")
        time.sleep(0.3)
        vnc.mouse.left_click(200, 270, delay=0.2)
        print("✓ Selected option")

        # Check checkbox
        vnc.mouse.left_click(100, 300, delay=0.3)
        print("✓ Checked checkbox")

        # Submit form
        vnc.mouse.left_click(400, 400, delay=0.5)
        print("✓ Submitted form")


def example_2_file_operations():
    """Example: Open, edit, and save a file."""
    print("\nExample 2: File Operations")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Open File menu (Ctrl+O)
        vnc.keyboard.hotkey("ctrl", "o", delay=0.5)
        print("✓ Opened File dialog")

        time.sleep(0.5)

        # Type filename
        vnc.keyboard.type_text("document.txt", delay=0.05)
        print("✓ Typed filename")

        # Press Enter to open
        vnc.keyboard.press_key("return", delay=0.3)
        print("✓ File opened")

        time.sleep(1)

        # Click in text area and type content
        vnc.mouse.left_click(400, 300, delay=0.3)
        vnc.keyboard.type_text("This is the content of the document.", delay=0.05)
        print("✓ Typed content")

        time.sleep(0.5)

        # Save file (Ctrl+S)
        vnc.keyboard.hotkey("ctrl", "s", delay=0.3)
        print("✓ File saved")


def example_3_web_navigation():
    """Example: Navigate a website."""
    print("\nExample 3: Web Navigation")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Click on address bar (Ctrl+L)
        vnc.keyboard.hotkey("ctrl", "l", delay=0.3)
        print("✓ Selected address bar")

        # Type URL
        vnc.keyboard.type_text("example.com", delay=0.05)
        print("✓ Typed URL")

        # Navigate
        vnc.keyboard.press_key("return", delay=1.0)
        print("✓ Navigated to URL")

        time.sleep(2)  # Wait for page load

        # Scroll down to see content
        vnc.scroll.scroll_down(amount=5, delay=0.3)
        print("✓ Scrolled down")

        time.sleep(0.5)

        # Click on a link (approximate coordinates)
        vnc.mouse.left_click(250, 400, delay=0.3)
        print("✓ Clicked link")

        time.sleep(1)


def example_4_realistic_timing():
    """Example: Operations with realistic human-like timing."""
    print("\nExample 4: Realistic Timing")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Slow deliberate movements (like careful typing)
        print("Typing slowly and deliberately...")
        for char in "Careful input":
            vnc.keyboard.press_key(char, delay=0.1)
        print("✓ Slow deliberate typing")

        time.sleep(0.5)

        # Human-like pauses and movements
        positions = [(100, 100), (200, 150), (300, 200), (400, 250)]

        for i, (x, y) in enumerate(positions):
            vnc.mouse.move_to(x, y, delay=0.2)
            time.sleep(0.3)  # Human pause before clicking
            vnc.mouse.left_click(delay=0.3)
            print(f"✓ Clicked position {i+1}/{len(positions)}")

        print("✓ Realistic interaction pattern complete")


def example_5_complex_sequence():
    """Example: Complex multi-step sequence."""
    print("\nExample 5: Complex Sequence")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Step 1: Select all text
        vnc.keyboard.hotkey("ctrl", "a", delay=0.2)
        print("✓ Step 1: Selected all")

        # Step 2: Copy selected text
        vnc.keyboard.hotkey("ctrl", "c", delay=0.2)
        print("✓ Step 2: Copied")

        # Step 3: Open new window or field
        vnc.keyboard.hotkey("ctrl", "n", delay=0.5)
        print("✓ Step 3: Opened new")

        time.sleep(0.5)

        # Step 4: Paste text
        vnc.keyboard.hotkey("ctrl", "v", delay=0.2)
        print("✓ Step 4: Pasted")

        # Step 5: Save
        vnc.keyboard.hotkey("ctrl", "s", delay=0.3)
        print("✓ Step 5: Saved")


def example_6_drag_and_drop():
    """Example: Drag and drop operations."""
    print("\nExample 6: Drag and Drop")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Move to source
        vnc.mouse.move_to(100, 100, delay=0.3)
        print("✓ Positioned at source")

        # Drag to destination
        vnc.mouse.drag_to(300, 300, duration=1.5, delay=0.3)
        print("✓ Dragged to destination")

        # Release (implicit in VNC protocol)
        print("✓ Item dropped")

        # Verify position
        x, y = vnc.mouse.get_position()
        print(f"✓ Final position: ({x}, {y})")


def example_7_keyboard_shortcuts():
    """Example: Common keyboard shortcuts."""
    print("\nExample 7: Keyboard Shortcuts")
    print("-" * 50)

    shortcuts = [
        ("Ctrl+Z", "ctrl", "z", "Undo"),
        ("Ctrl+Y", "ctrl", "y", "Redo"),
        ("Ctrl+X", "ctrl", "x", "Cut"),
        ("Ctrl+C", "ctrl", "c", "Copy"),
        ("Ctrl+V", "ctrl", "v", "Paste"),
        ("Ctrl+S", "ctrl", "s", "Save"),
        ("Ctrl+P", "ctrl", "p", "Print"),
        ("Ctrl+F", "ctrl", "f", "Find"),
        ("Alt+Tab", "alt", "tab", "Switch window"),
    ]

    with VNCAgentBridge("localhost", port=5900) as vnc:
        for shortcut_name, *keys in shortcuts:
            vnc.keyboard.hotkey(*keys, delay=0.2)
            print(f"✓ {shortcut_name}")


def example_8_scroll_operations():
    """Example: Scrolling with positioning."""
    print("\nExample 8: Scroll Operations")
    print("-" * 50)

    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Scroll at center of screen
        vnc.scroll.scroll_to(400, 300)
        print("✓ Scrolled at center (400, 300)")

        # Scroll up progressively
        for i in range(3):
            vnc.scroll.scroll_up(amount=2, delay=0.2)
            print(f"✓ Scroll up iteration {i+1}")

        # Scroll down progressively
        for i in range(3):
            vnc.scroll.scroll_down(amount=2, delay=0.2)
            print(f"✓ Scroll down iteration {i+1}")


if __name__ == "__main__":
    print("VNC Agent Bridge - Advanced Workflow Examples")
    print("=" * 50)
    print()

    # Note: These examples require a real VNC server running
    # and visible applications to interact with

    # Uncomment to run examples:
    # example_1_form_filling()
    # example_2_file_operations()
    # example_3_web_navigation()
    # example_4_realistic_timing()
    # example_5_complex_sequence()
    # example_6_drag_and_drop()
    # example_7_keyboard_shortcuts()
    # example_8_scroll_operations()

    print("\n" + "=" * 50)
    print("Advanced examples are ready but commented out.")
    print("Uncomment to run with real VNC server and applications.")
    print("=" * 50)
