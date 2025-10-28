#!/usr/bin/env python3
"""
Screenshot Test Script
======================

This script tests screenshot capture operations for the VNC Agent Bridge package.

Features tested:
- Full screen screenshot capture
- Region screenshot capture
- Screenshot saving in different formats (PNG, JPEG, BMP)
- Incremental vs full refresh capture

Requirements:
    pip install vnc-agent-bridge[full]

Usage:
    python test_screenshot.py
"""

import time
import os
from pathlib import Path
from datetime import datetime
from vnc_agent_bridge import VNCAgentBridge, VNCException
from vnc_agent_bridge.types.common import ImageFormat
import dotenv

dotenv.load_dotenv()


def create_test_output_directory():
    """Create directory for test outputs."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = output_dir / f"screenshot_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_screenshot_operations(vnc, output_dir):
    """Test screenshot operations."""
    print("=" * 60)
    print("TESTING SCREENSHOT OPERATIONS")
    print("=" * 60)

    results = {
        "start_time": datetime.now().isoformat(),
        "tests": {},
    }

    try:
        # Test 1: Full screenshot capture
        print("\n1. Testing full screenshot capture...")
        screenshot = vnc.screenshot.capture(delay=0.5)
        print(f"   ✓ Captured screenshot: {screenshot.shape}")
        results["tests"]["full_capture"] = "PASSED"

        # Test 2: Save screenshot
        print("\n2. Testing screenshot saving...")
        screenshot_path = output_dir / "full_screenshot.png"
        vnc.screenshot.save(str(screenshot_path), delay=0.3)
        print(f"   ✓ Saved screenshot to: {screenshot_path}")
        results["tests"]["save_screenshot"] = "PASSED"

        # Test 3: Region capture
        print("\n3. Testing region capture...")
        region_path = output_dir / "region_screenshot.png"
        vnc.screenshot.save_region(str(region_path), 100, 100, 300, 200, delay=0.3)
        print(f"   ✓ Captured and saved region (100,100,300x200) to: {region_path}")
        results["tests"]["region_capture"] = "PASSED"

        # Test 4: Different formats
        print("\n4. Testing different image formats...")
        format_tests = [
            (ImageFormat.PNG, "png"),
            (ImageFormat.JPEG, "jpeg"),
            (ImageFormat.BMP, "bmp"),
        ]
        for fmt_enum, fmt_name in format_tests:
            fmt_path = output_dir / f"screenshot.{fmt_name}"
            vnc.screenshot.save(str(fmt_path), format=fmt_enum, delay=0.2)
            print(f"   ✓ Saved {fmt_name.upper()} format to: {fmt_path}")
        results["tests"]["format_save"] = "PASSED"

        # Test 5: Incremental capture
        print("\n5. Testing incremental capture...")
        incremental_screenshot = vnc.screenshot.capture(incremental=True, delay=0.3)
        print(f"   ✓ Captured incremental screenshot: {incremental_screenshot.shape}")
        results["tests"]["incremental_capture"] = "PASSED"

        print("\n✓ All screenshot operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ Screenshot operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "screenshot_test_results.json"
    with open(results_file, "w") as f:
        import json

        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_screenshot_test():
    """Run the screenshot test."""
    print("VNC Agent Bridge - Screenshot Test")
    print("=" * 50)

    # Get connection parameters from environment
    vnc_host = os.getenv("TCP_VNC_HOST", "192.168.1.5")
    vnc_port = int(os.getenv("TCP_VNC_PORT", "5900"))
    vnc_password = os.getenv("TCP_VNC_PASSWORD", "")

    print(f"Target VNC Server: {vnc_host}:{vnc_port}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directory
    output_dir = create_test_output_directory()
    print(f"Test outputs will be saved to: {output_dir}")

    try:
        # Connect to VNC server
        print("\n🔌 Connecting to VNC server...")
        with VNCAgentBridge(
            vnc_host,
            port=vnc_port,
            timeout=30.0,
            password=vnc_password,
        ) as vnc:
            print("✓ Connected successfully")

            # Run screenshot tests
            results = test_screenshot_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("SCREENSHOT TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 Screenshot test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_screenshot_test()
