#!/usr/bin/env python3
"""
Example: Basic Screenshot Capture

This example demonstrates the basic screenshot capture functionality
introduced in v0.2.0. Shows how to capture the full screen and save
it to different image formats.

Requirements:
    pip install vnc-agent-bridge[capture]
"""

from vnc_agent_bridge import VNCAgentBridge
from pathlib import Path
import time


def example_basic_capture():
    """Capture full screen screenshot."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Connected to VNC server")

        # Capture full screen
        print("Capturing full screen...")
        vnc.screenshot.save("full_screen.png")
        print("Saved: full_screen.png")

        # Capture with delay
        print("Waiting 2 seconds before capture...")
        vnc.screenshot.save("delayed_screenshot.png", delay=2.0)
        print("Saved: delayed_screenshot.png")


def example_multiple_formats():
    """Capture and save in multiple formats."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Capturing in multiple formats...")

        # PNG format (lossless, recommended)
        vnc.screenshot.save("screenshot.png")
        print("Saved: screenshot.png")

        # JPEG format (lossy, smaller file)
        vnc.screenshot.save("screenshot.jpg")
        print("Saved: screenshot.jpg")

        # BMP format (uncompressed)
        vnc.screenshot.save("screenshot.bmp")
        print("Saved: screenshot.bmp")


def example_capture_to_array():
    """Capture as numpy array for analysis."""
    try:
        import numpy as np

        with VNCAgentBridge("localhost", port=5900) as vnc:
            # Capture to numpy array
            screenshot = vnc.screenshot.capture()

            print(f"Screenshot shape: {screenshot.shape}")
            print(f"Screenshot dtype: {screenshot.dtype}")
            print(f"Screenshot size: {screenshot.nbytes / 1024 / 1024:.1f} MB")

            # Analyze colors
            red_channel = screenshot[:, :, 0]
            red_mean = np.mean(red_channel)
            print(f"Average red intensity: {red_mean:.1f}")

            # Access specific pixel
            pixel = screenshot[100, 200]
            print(
                f"Pixel at (100, 200): R={pixel[0]}, G={pixel[1]}, B={pixel[2]}, A={pixel[3]}"
            )

    except ImportError:
        print("numpy not available, skipping array example")


def example_series_capture():
    """Capture a series of screenshots."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Capturing 5 screenshots with 1 second intervals...")

        for i in range(1, 6):
            filename = f"screenshot_{i:02d}.png"
            vnc.screenshot.save(filename, delay=1.0)
            print(f"  Saved: {filename}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("v0.2.0 Screenshot Capture Examples")
    print("=" * 60)

    # Note: These examples assume a VNC server is running on localhost:5900
    # Adjust host/port as needed

    try:
        print("\nExample 1: Basic Capture")
        print("-" * 60)
        example_basic_capture()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        print("\nExample 2: Multiple Formats")
        print("-" * 60)
        example_multiple_formats()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        print("\nExample 3: Capture to Array")
        print("-" * 60)
        example_capture_to_array()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        print("\nExample 4: Series Capture")
        print("-" * 60)
        example_series_capture()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
