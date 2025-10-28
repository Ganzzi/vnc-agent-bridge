#!/usr/bin/env python3
"""
WebSocket Screenshot Test Script
=================================

This script tests screenshot capture operations for WebSocket-based VNC servers.

Features tested:
- Full screen screenshot capture
- Region screenshot capture
- Screenshot saving in different formats (PNG, JPEG, BMP)
- Incremental vs full refresh capture

Requirements:
    pip install vnc-agent-bridge[websocket,full]

Usage:
    python websocket_test_screenshot.py
"""

import time
import os
from pathlib import Path
from datetime import datetime
from vnc_agent_bridge import create_websocket_vnc, VNCException
from vnc_agent_bridge.types.common import ImageFormat
import dotenv

dotenv.load_dotenv()


def create_test_output_directory():
    """Create directory for test outputs."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = output_dir / f"websocket_screenshot_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_screenshot_operations(vnc, output_dir):
    """Test screenshot operations."""
    print("=" * 60)
    print("TESTING WEBSOCKET SCREENSHOT OPERATIONS")
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
        screenshot_path = output_dir / "websocket_full_screenshot.png"
        vnc.screenshot.save(str(screenshot_path), delay=0.3)
        print(f"   ✓ Saved screenshot to: {screenshot_path}")
        results["tests"]["save_screenshot"] = "PASSED"

        # Test 3: Region capture
        print("\n3. Testing region capture...")
        region_path = output_dir / "websocket_region_screenshot.png"
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
            fmt_path = output_dir / f"websocket_screenshot.{fmt_name}"
            vnc.screenshot.save(str(fmt_path), format=fmt_enum, delay=0.2)
            print(f"   ✓ Saved {fmt_name.upper()} format to: {fmt_path}")
        results["tests"]["format_save"] = "PASSED"

        # Test 5: Incremental capture
        print("\n5. Testing incremental capture...")
        incremental_screenshot = vnc.screenshot.capture(incremental=True, delay=0.3)
        print(f"   ✓ Captured incremental screenshot: {incremental_screenshot.shape}")
        results["tests"]["incremental_capture"] = "PASSED"

        print("\n✓ All WebSocket screenshot operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ WebSocket screenshot operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "websocket_screenshot_test_results.json"
    with open(results_file, "w") as f:
        import json

        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_websocket_screenshot_test():
    """Run the WebSocket screenshot test."""
    print("WebSocket VNC Agent Bridge - Screenshot Test")
    print("=" * 55)

    # Get WebSocket configuration from environment
    proxmox_host = os.getenv("WEBSOCKET_VNC_HOST", "192.168.1.5")
    proxmox_port = int(os.getenv("WEBSOCKET_VNC_HOST_PORT", "8006"))
    vnc_port = int(os.getenv("WEBSOCKET_VNC_PORT", "5900"))
    proxmox_node = os.getenv("WEBSOCKET_VNC_NODE", "pve")
    proxmox_vmid = os.getenv("WEBSOCKET_VNC_VMID", "100")
    vnc_ticket = os.getenv("WEBSOCKET_VNC_TICKET")
    proxmox_api_token = os.getenv("WEBSOCKET_VNC_API_TOKEN")
    certificate_pem = os.getenv("WEBSOCKET_VNC_CERTIFICATE_PEM")

    print("WebSocket VNC Configuration:")
    print(f"  Host: {proxmox_host}")
    print(f"  Port: {proxmox_port}")
    print(f"  Node: {proxmox_node}")
    print(f"  VM ID: {proxmox_vmid}")
    print(f"  VNC Ticket: {'Set' if vnc_ticket else 'Not set'}")
    print(f"  Proxmox API Token: {'Set' if proxmox_api_token else 'Not set'}")
    print(f"  Certificate PEM: {'Set' if certificate_pem else 'Not set'}")

    if not vnc_ticket:
        print(
            "\n⚠️  Warning: WEBSOCKET_VNC_TICKET not set. WebSocket authentication may fail."
        )
        print("   Please update your .env file with the appropriate ticket.")

    # URL template for Proxmox
    url_template = f"wss://${{host}}:${{host_port}}/api2/json/nodes/{proxmox_node}/qemu/{proxmox_vmid}/vncwebsocket?port=${{vnc_port}}&vncticket=${{ticket}}"

    print(f"  URL Template: {url_template}")
    print("=" * 55)

    # Create output directory
    output_dir = create_test_output_directory()
    print(f"Test outputs will be saved to: {output_dir}")

    headers = {
        "Authorization": f"PVEAPIToken={proxmox_api_token}",
    }

    try:
        # Connect to WebSocket VNC server
        print("\n🔌 Connecting to WebSocket VNC server...")
        with create_websocket_vnc(
            url_template=url_template,
            host=proxmox_host,
            host_port=proxmox_port,
            vnc_port=vnc_port,
            ticket=vnc_ticket,
            certificate_pem=certificate_pem,
            verify_ssl=False,  # Often self-signed certificates
            timeout=30.0,
            headers=headers,
        ) as vnc:
            print("✓ WebSocket VNC connected successfully")

            # Run screenshot tests
            results = test_screenshot_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("WEBSOCKET SCREENSHOT TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ WebSocket VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 WebSocket screenshot test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_websocket_screenshot_test()
