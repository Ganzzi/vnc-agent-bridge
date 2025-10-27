#!/usr/bin/env python3
"""
Example: Clipboard Management

This example demonstrates clipboard operations introduced in v0.2.0.
Shows how to send and receive text via the remote clipboard.

Requirements:
    pip install vnc-agent-bridge
"""

from vnc_agent_bridge import VNCAgentBridge
import time
import json


def example_send_text():
    """Send text to remote clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Sending text to clipboard...")

        text = "Hello from VNC Agent Bridge!"
        vnc.clipboard.send_text(text)

        print(f"Sent to clipboard: {text}")

        # Paste it
        vnc.mouse.left_click(500, 300)  # Click in text area
        vnc.keyboard.hotkey("ctrl", "v")  # Paste

        print("Text pasted into application")


def example_get_text():
    """Get text from remote clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Getting text from clipboard...")

        # Copy text from application
        vnc.keyboard.hotkey("ctrl", "a")  # Select all
        vnc.keyboard.hotkey("ctrl", "c")  # Copy

        # Small delay for clipboard to update
        time.sleep(0.5)

        # Retrieve text
        text = vnc.clipboard.get_text(timeout=2.0)

        if text:
            print(f"Retrieved from clipboard: {text[:100]}...")
        else:
            print("No text in clipboard")


def example_clipboard_check():
    """Check if clipboard has text."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Checking clipboard status...")

        # Clear clipboard
        vnc.clipboard.clear()
        print("Clipboard cleared")

        # Check
        has_text = vnc.clipboard.has_text()
        print(f"Clipboard has text: {has_text}")

        # Send text
        vnc.clipboard.send_text("New content")

        # Check again
        has_text = vnc.clipboard.has_text()
        print(f"Clipboard has text: {has_text}")


def example_json_transfer():
    """Transfer structured data via clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Transferring JSON data via clipboard...")

        # Prepare data
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "roles": ["admin", "user"],
            "settings": {"theme": "dark", "notifications": True},
        }

        # Convert to JSON
        json_text = json.dumps(data, indent=2)

        # Send to clipboard
        vnc.clipboard.send_text(json_text)
        print(f"Sent JSON ({len(json_text)} bytes) to clipboard")

        # Paste into application
        vnc.mouse.left_click(500, 300)
        vnc.keyboard.hotkey("ctrl", "v")

        print("JSON pasted into application")


def example_multiline_text():
    """Send multiline text via clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Sending multiline text...")

        text = """Line 1: First line of text
Line 2: Second line of text
Line 3: Third line of text
Line 4: Fourth line of text"""

        vnc.clipboard.send_text(text)
        print(f"Sent {len(text)} character text to clipboard")

        # Paste
        vnc.mouse.left_click(500, 300)
        vnc.keyboard.hotkey("ctrl", "v")

        print("Multiline text pasted")


def example_csv_transfer():
    """Transfer CSV data via clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Transferring CSV data...")

        csv_data = """Name,Email,Department,Salary
Alice Johnson,alice@example.com,Engineering,120000
Bob Smith,bob@example.com,Sales,90000
Carol Williams,carol@example.com,Marketing,95000
Dave Brown,dave@example.com,Engineering,125000"""

        vnc.clipboard.send_text(csv_data)
        print(f"Sent CSV data ({len(csv_data)} bytes) to clipboard")

        # Paste into spreadsheet or text editor
        vnc.mouse.left_click(500, 300)
        vnc.keyboard.hotkey("ctrl", "v")

        print("CSV data pasted")


def example_clear_clipboard():
    """Clear clipboard."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Clearing clipboard...")

        # Send some text first
        vnc.clipboard.send_text("Text to clear")

        # Verify
        text = vnc.clipboard.get_text()
        print(f"Before clear: {text}")

        # Clear
        vnc.clipboard.clear()
        print("Clipboard cleared")

        # Verify
        text = vnc.clipboard.get_text()
        print(f"After clear: {text}")


def example_content_property():
    """Use clipboard content property."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Using clipboard content property...")

        # Send text
        vnc.clipboard.send_text("Property test content")

        # Wait a moment
        time.sleep(0.5)

        # Access content property
        content = vnc.clipboard.content

        if content:
            print(f"Clipboard content: {content}")
        else:
            print("Clipboard empty")


def main():
    """Run all clipboard examples."""
    print("=" * 60)
    print("v0.2.0 Clipboard Management Examples")
    print("=" * 60)

    try:
        print("\nExample 1: Send Text")
        print("-" * 60)
        example_send_text()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        print("\nExample 2: Get Text")
        print("-" * 60)
        example_get_text()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        print("\nExample 3: Clipboard Check")
        print("-" * 60)
        example_clipboard_check()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        print("\nExample 4: JSON Transfer")
        print("-" * 60)
        example_json_transfer()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        print("\nExample 5: Multiline Text")
        print("-" * 60)
        example_multiline_text()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    try:
        print("\nExample 6: CSV Transfer")
        print("-" * 60)
        example_csv_transfer()
    except Exception as e:
        print(f"Example 6 failed: {e}")

    try:
        print("\nExample 7: Clear Clipboard")
        print("-" * 60)
        example_clear_clipboard()
    except Exception as e:
        print(f"Example 7 failed: {e}")

    try:
        print("\nExample 8: Content Property")
        print("-" * 60)
        example_content_property()
    except Exception as e:
        print(f"Example 8 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
