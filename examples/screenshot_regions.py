#!/usr/bin/env python3
"""
Example: Screenshot Regional Capture

This example demonstrates capturing specific regions of the screen.
Useful for monitoring specific UI elements or reducing data transfer
when you only care about a portion of the screen.

Requirements:
    pip install vnc-agent-bridge[capture]
"""

from vnc_agent_bridge import VNCAgentBridge
import time


def example_capture_window():
    """Capture a specific window region."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Capturing window at (100, 100) size 800x600...")

        # Capture window region
        vnc.screenshot.save_region(
            "window_screenshot.png", x=100, y=100, width=800, height=600
        )
        print("Saved: window_screenshot.png")


def example_capture_multiple_regions():
    """Capture multiple regions of interest."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        regions = {
            "top_left": (0, 0, 400, 300),
            "top_right": (400, 0, 400, 300),
            "bottom_left": (0, 300, 400, 300),
            "bottom_right": (400, 300, 400, 300),
        }

        print("Capturing 4 regions of screen...")
        for name, (x, y, w, h) in regions.items():
            filename = f"region_{name}.png"
            vnc.screenshot.save_region(filename, x=x, y=y, width=w, height=h)
            print(f"  Saved: {filename}")


def example_monitor_button():
    """Monitor a specific button area for changes."""
    try:
        import numpy as np

        with VNCAgentBridge("localhost", port=5900) as vnc:
            # Define button area (example coordinates)
            button_x, button_y = 100, 150
            button_w, button_h = 80, 40

            print(f"Monitoring button at ({button_x}, {button_y})...")

            # Take initial screenshot
            initial = vnc.screenshot.capture_region(
                button_x, button_y, button_w, button_h
            )
            print(f"Initial button region shape: {initial.shape}")

            # Simulate action (in real scenario, this would be user interaction)
            print("Waiting 2 seconds...")
            time.sleep(2.0)

            # Take follow-up screenshot
            follow_up = vnc.screenshot.capture_region(
                button_x, button_y, button_w, button_h
            )

            # Compare
            diff = np.abs(initial.astype(int) - follow_up.astype(int))
            change_percentage = (np.sum(diff) / (button_w * button_h * 4)) * 100

            print(f"Button area changed by: {change_percentage:.2f}%")

            if change_percentage > 5:
                print("Button was highlighted/changed!")
                follow_up_np = follow_up.astype(np.uint8)
                # Could save this for debugging
            else:
                print("Button state unchanged")

    except ImportError:
        print("numpy not available, skipping monitoring example")


def example_grid_capture():
    """Capture screen in a grid pattern."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        # Get screen dimensions (assuming standard sizes)
        grid_cols = 4
        grid_rows = 3
        cell_width = 480  # 1920 / 4
        cell_height = 360  # 1080 / 3

        print(f"Capturing {grid_rows}x{grid_cols} grid of screen regions...")

        for row in range(grid_rows):
            for col in range(grid_cols):
                x = col * cell_width
                y = row * cell_height
                filename = f"grid_{row}_{col}.png"

                vnc.screenshot.save_region(
                    filename, x=x, y=y, width=cell_width, height=cell_height
                )
                print(f"  Saved: {filename}")


def example_progressive_capture():
    """Capture progressively larger regions."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Capturing progressively larger regions from center...")

        center_x, center_y = 960, 540  # Assuming 1920x1080 center

        sizes = [
            (100, 100),
            (200, 200),
            (400, 400),
            (800, 600),
        ]

        for i, (w, h) in enumerate(sizes, 1):
            x = center_x - w // 2
            y = center_y - h // 2
            filename = f"progressive_{i}.png"

            try:
                vnc.screenshot.save_region(filename, x=x, y=y, width=w, height=h)
                print(f"  Saved: {filename} ({w}x{h})")
            except Exception as e:
                print(f"  Failed to capture {w}x{h}: {e}")


def main():
    """Run all region capture examples."""
    print("=" * 60)
    print("v0.2.0 Regional Screenshot Capture Examples")
    print("=" * 60)

    try:
        print("\nExample 1: Capture Window")
        print("-" * 60)
        example_capture_window()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        print("\nExample 2: Capture Multiple Regions")
        print("-" * 60)
        example_capture_multiple_regions()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        print("\nExample 3: Monitor Button Area")
        print("-" * 60)
        example_monitor_button()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        print("\nExample 4: Grid Capture")
        print("-" * 60)
        example_grid_capture()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        print("\nExample 5: Progressive Capture")
        print("-" * 60)
        example_progressive_capture()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
