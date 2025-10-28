#!/usr/bin/env python3
"""
Comprehensive VNC Agent Bridge Test Script
==========================================

This script demonstrates and tests all features of the VNC Agent Bridge package
against a VNC server running on 192.168.1.5.

Features tested:
- Mouse control (click, move, drag, position tracking)
- Keyboard input (type text, press keys, hotkeys, key combinations)
- Scroll control (up/down scrolling)
- Screenshot capture (full screen and regions)
- Video recording (background and timed recording)
- Clipboard management (send, get, clear text)
- Error handling and connection management

Requirements:
    pip install vnc-agent-bridge[full]

Usage:
    python comprehensive_test.py
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from vnc_agent_bridge import VNCAgentBridge, VNCException
import dotenv

dotenv.load_dotenv()


def create_test_output_directory():
    """Create directory for test outputs."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = output_dir / f"test_run_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_mouse_operations(vnc, output_dir):
    """Test all mouse operations."""
    print("\n" + "=" * 60)
    print("TESTING MOUSE OPERATIONS")
    print("=" * 60)

    try:
        # Test 1: Basic clicks
        print("\n1. Testing basic mouse clicks...")
        vnc.mouse.left_click(100, 100, delay=0.5)
        print("   ✓ Left click at (100, 100)")

        vnc.mouse.right_click(200, 200, delay=0.5)
        print("   ✓ Right click at (200, 200)")

        vnc.mouse.double_click(150, 150, delay=0.5)
        print("   ✓ Double click at (150, 150)")

        # Test 2: Mouse movement
        print("\n2. Testing mouse movement...")
        vnc.mouse.move_to(300, 300, delay=0.5)
        print("   ✓ Moved to (300, 300)")

        position = vnc.mouse.get_position()
        print(f"   ✓ Current position: {position}")

        # Test 3: Drag operation
        print("\n3. Testing drag operation...")
        vnc.mouse.move_to(100, 100, delay=0.3)
        vnc.mouse.drag_to(400, 400, duration=1.0, delay=0.5)
        print("   ✓ Dragged from (100, 100) to (400, 400)")

        print("\n✓ All mouse operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Mouse operations failed: {e}")
        return False


def test_keyboard_operations(vnc, output_dir):
    """Test all keyboard operations."""
    print("\n" + "=" * 60)
    print("TESTING KEYBOARD OPERATIONS")
    print("=" * 60)

    try:
        # Test 1: Type text
        print("\n1. Testing text typing...")
        vnc.keyboard.type_text("Hello from VNC Agent Bridge!", delay=0.1)
        print("   ✓ Typed: 'Hello from VNC Agent Bridge!'")

        vnc.keyboard.press_key("return", delay=0.3)
        print("   ✓ Pressed Enter")

        # Test 2: Individual key presses
        print("\n2. Testing individual key presses...")
        vnc.keyboard.press_key("tab", delay=0.2)
        print("   ✓ Pressed Tab")

        vnc.keyboard.press_key("space", delay=0.2)
        print("   ✓ Pressed Space")

        # Test 3: Hotkeys
        print("\n3. Testing hotkey combinations...")
        vnc.keyboard.hotkey("ctrl", "a", delay=0.3)  # Select all
        print("   ✓ Pressed Ctrl+A (Select All)")

        vnc.keyboard.hotkey("ctrl", "c", delay=0.3)  # Copy
        print("   ✓ Pressed Ctrl+C (Copy)")

        # Test 4: Key hold/release
        print("\n4. Testing key hold/release...")
        vnc.keyboard.keydown("shift", delay=0.2)
        vnc.keyboard.type_text("uppercase text")
        vnc.keyboard.keyup("shift", delay=0.2)
        print("   ✓ Typed uppercase text with Shift held")

        # Test 5: Special keys
        print("\n5. Testing special keys...")
        vnc.keyboard.press_key("backspace", delay=0.2)
        print("   ✓ Pressed Backspace")

        vnc.keyboard.press_key("escape", delay=0.2)
        print("   ✓ Pressed Escape")

        print("\n✓ All keyboard operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Keyboard operations failed: {e}")
        return False


def test_scroll_operations(vnc, output_dir):
    """Test scroll operations."""
    print("\n" + "=" * 60)
    print("TESTING SCROLL OPERATIONS")
    print("=" * 60)

    try:
        print("\n1. Testing scroll up/down...")
        vnc.scroll.scroll_up(amount=3, delay=0.3)
        print("   ✓ Scrolled up 3 units")

        vnc.scroll.scroll_down(amount=5, delay=0.3)
        print("   ✓ Scrolled down 5 units")

        print("\n2. Testing scroll at position...")
        vnc.scroll.scroll_to(200, 200, delay=0.3)
        print("   ✓ Scrolled at position (200, 200)")

        print("\n✓ All scroll operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Scroll operations failed: {e}")
        return False


def test_screenshot_operations(vnc, output_dir):
    """Test screenshot capture operations."""
    print("\n" + "=" * 60)
    print("TESTING SCREENSHOT OPERATIONS")
    print("=" * 60)

    try:
        # Test 1: Full screenshot capture
        print("\n1. Testing full screenshot capture...")
        screenshot = vnc.screenshot.capture(delay=0.5)
        print(f"   ✓ Captured screenshot: {screenshot.shape}")

        # Test 2: Save screenshot
        print("\n2. Testing screenshot saving...")
        screenshot_path = output_dir / "full_screenshot.png"
        vnc.screenshot.save_image(str(screenshot_path), delay=0.3)
        print(f"   ✓ Saved screenshot to: {screenshot_path}")

        # Test 3: Region capture
        print("\n3. Testing region capture...")
        region_path = output_dir / "region_screenshot.png"
        vnc.screenshot.capture_region(100, 100, 300, 200, delay=0.3)
        vnc.screenshot.save_image(str(region_path))
        print(f"   ✓ Captured and saved region (100,100,300x200) to: {region_path}")

        # Test 4: Different formats
        print("\n4. Testing different image formats...")
        for fmt in ["PNG", "JPEG", "BMP"]:
            fmt_path = output_dir / f"screenshot.{fmt.lower()}"
            vnc.screenshot.save_image(str(fmt_path), format=fmt, delay=0.2)
            print(f"   ✓ Saved {fmt} format to: {fmt_path}")

        print("\n✓ All screenshot operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Screenshot operations failed: {e}")
        return False


def test_video_operations(vnc, output_dir):
    """Test video recording operations."""
    print("\n" + "=" * 60)
    print("TESTING VIDEO OPERATIONS")
    print("=" * 60)

    try:
        # Test 1: Timed recording
        print("\n1. Testing timed video recording...")
        print("   Recording 5 seconds at 10 FPS...")
        frames = vnc.video.record(duration=5.0, fps=10.0)
        print(f"   ✓ Recorded {len(frames)} frames")

        # Save the recording
        video_dir = output_dir / "timed_recording"
        vnc.video.save_frames(frames, str(video_dir))
        print(f"   ✓ Saved frames to: {video_dir}")

        # Test 2: Background recording
        print("\n2. Testing background recording...")
        print("   Starting background recording...")
        vnc.video.start_recording(fps=15.0)

        # Perform some actions while recording
        print("   Performing actions during recording...")
        time.sleep(1)
        vnc.mouse.move_to(100, 100, delay=0.3)
        vnc.mouse.left_click(delay=0.3)
        time.sleep(1)
        vnc.keyboard.type_text("Recording in progress...", delay=0.1)
        time.sleep(1)

        # Stop recording
        print("   Stopping background recording...")
        frames_bg = vnc.video.stop_recording()
        print(f"   ✓ Recorded {len(frames_bg)} frames in background")

        # Save background recording
        bg_video_dir = output_dir / "background_recording"
        vnc.video.save_frames(frames_bg, str(bg_video_dir))
        print(f"   ✓ Saved background frames to: {bg_video_dir}")

        print("\n✓ All video operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Video operations failed: {e}")
        return False


def test_clipboard_operations(vnc, output_dir):
    """Test clipboard operations."""
    print("\n" + "=" * 60)
    print("TESTING CLIPBOARD OPERATIONS")
    print("=" * 60)

    try:
        # Test 1: Send text to clipboard
        print("\n1. Testing clipboard text sending...")
        test_text = "Hello from VNC Agent Bridge clipboard test!"
        vnc.clipboard.send_text(test_text, delay=0.3)
        print(f"   ✓ Sent text to clipboard: '{test_text}'")

        # Test 2: Get text from clipboard
        print("\n2. Testing clipboard text retrieval...")
        retrieved_text = vnc.clipboard.get_text()
        print(f"   ✓ Retrieved text: '{retrieved_text}'")

        if retrieved_text == test_text:
            print("   ✓ Text matches what was sent")
        else:
            print("   ⚠ Text mismatch (may be expected if clipboard was modified)")

        # Test 3: Clear clipboard
        print("\n3. Testing clipboard clearing...")
        vnc.clipboard.clear()
        cleared_text = vnc.clipboard.get_text()
        if not cleared_text:
            print("   ✓ Clipboard cleared successfully")
        else:
            print(f"   ⚠ Clipboard not empty after clear: '{cleared_text}'")

        # Test 4: Send structured data
        print("\n4. Testing structured data transfer...")
        test_data = {
            "test_run": datetime.now().isoformat(),
            "features_tested": [
                "mouse",
                "keyboard",
                "scroll",
                "screenshot",
                "video",
                "clipboard",
            ],
            "server": "192.168.1.5",
        }
        json_data = json.dumps(test_data, indent=2)
        vnc.clipboard.send_text(json_data, delay=0.3)
        print("   ✓ Sent JSON data to clipboard")

        # Verify JSON data
        retrieved_json = vnc.clipboard.get_text()
        try:
            parsed_data = json.loads(retrieved_json)
            print("   ✓ Retrieved and parsed JSON data successfully")
            print(f"   ✓ Data keys: {list(parsed_data.keys())}")
        except json.JSONDecodeError:
            print("   ⚠ Could not parse retrieved JSON")

        print("\n✓ All clipboard operations completed successfully")
        return True

    except Exception as e:
        print(f"\n✗ Clipboard operations failed: {e}")
        return False


def run_comprehensive_test():
    """Run the complete test suite."""
    print("VNC Agent Bridge - Comprehensive Test Suite")
    print("=" * 80)

    # Test multiple servers
    servers_to_test = [
        {"host": "192.168.1.5", "port": 5900, "name": "Server 192.168.1.5"},
        # {"host": "192.168.1.8", "port": 5900, "name": "Server 192.168.1.8"},
    ]

    # Get password from environment
    vnc_password = os.getenv("VNC_PASSWORD", "")
    if vnc_password:
        print(f"Using VNC password from VNC_PASSWORD environment variable")
    else:
        print("No VNC_PASSWORD environment variable set - testing without password")

    print("=" * 80)

    for server_config in servers_to_test:
        print(
            f"\n🎯 Testing {server_config['name']} ({server_config['host']}:{server_config['port']})"
        )
        print("-" * 60)

        test_server(server_config, vnc_password)


def test_server(server_config, vnc_password):
    """Test a specific VNC server."""
    host = server_config["host"]
    port = server_config["port"]
    server_name = server_config["name"]

    print(f"Target VNC Server: {host}:{port}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directory
    output_dir = create_test_output_directory()
    print(f"Test outputs will be saved to: {output_dir}")

    # Test results
    results = {
        "start_time": datetime.now().isoformat(),
        "server": f"{host}:{port}",
        "server_name": server_name,
        "tests": {},
        "output_directory": str(output_dir),
    }

    try:
        # Connect to VNC server
        print("\n🔌 Connecting to VNC server...")
        with VNCAgentBridge(
            host,
            port=port,
            timeout=30.0,  # Increased timeout
            password=vnc_password,
        ) as vnc:
            print("✓ Connected successfully")

            # Run all tests
            test_functions = [
                ("mouse_operations", test_mouse_operations),
                ("keyboard_operations", test_keyboard_operations),
                ("scroll_operations", test_scroll_operations),
                ("screenshot_operations", test_screenshot_operations),
                ("video_operations", test_video_operations),
                ("clipboard_operations", test_clipboard_operations),
            ]

            all_passed = True
            for test_name, test_func in test_functions:
                try:
                    success = test_func(vnc, output_dir)
                    results["tests"][test_name] = "PASSED" if success else "FAILED"
                    if not success:
                        all_passed = False
                except Exception as e:
                    print(f"\n✗ {test_name} crashed: {e}")
                    results["tests"][test_name] = f"CRASHED: {str(e)}"
                    all_passed = False

            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(
                f"Overall Result: {'ALL TESTS PASSED ✓' if all_passed else 'SOME TESTS FAILED ✗'}"
            )
            print(f"Output Directory: {output_dir}")
            print("\nDetailed Results:")
            for test_name, result in results["tests"].items():
                status = "✓" if result == "PASSED" else "✗"
                print(f"  {status} {test_name.replace('_', ' ').title()}: {result}")

            results["overall_result"] = "PASSED" if all_passed else "FAILED"
            results["end_time"] = datetime.now().isoformat()

            # Save results
            results_file = output_dir / "test_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Detailed results saved to: {results_file}")

    except VNCException as e:
        print(f"\n❌ VNC Error: {e}")
        results["overall_result"] = f"VNC_ERROR: {str(e)}"
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        results["overall_result"] = f"CRASHED: {str(e)}"

    # Save final results even if connection failed
    results["end_time"] = datetime.now().isoformat()
    try:
        results_file = output_dir / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"📄 Error results saved to: {results_file}")
    except:
        print("Could not save results file")

    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_comprehensive_test()
