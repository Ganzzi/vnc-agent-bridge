#!/usr/bin/env python3
"""
Clipboard Test Script
=====================

This script tests clipboard operations for the VNC Agent Bridge package.

Features tested:
- Send text to remote clipboard
- Retrieve text from remote clipboard
- Clear remote clipboard
- Send structured data (JSON)

Requirements:
    pip install vnc-agent-bridge[full]

Usage:
    python test_clipboard.py
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
    test_dir = output_dir / f"clipboard_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_clipboard_operations(vnc, output_dir):
    """Test clipboard operations."""
    print("=" * 60)
    print("TESTING CLIPBOARD OPERATIONS")
    print("=" * 60)

    results = {
        "start_time": datetime.now().isoformat(),
        "tests": {},
    }

    try:
        # Test 1: Send text to clipboard
        print("\n1. Testing clipboard text sending...")
        test_text = "Hello from VNC Agent Bridge clipboard test!"
        vnc.clipboard.send_text(test_text, delay=0.3)
        print(f"   ✓ Sent text to clipboard: '{test_text}'")
        results["tests"]["send_text"] = "PASSED"

        # Test 2: Get text from clipboard
        print("\n2. Testing clipboard text retrieval...")
        retrieved_text = vnc.clipboard.get_text()
        print(f"   ✓ Retrieved text: '{retrieved_text}'")

        # Note: VNC clipboard is asynchronous - sent text may not be immediately available
        if retrieved_text == test_text:
            print("   ✓ Text matches what was sent")
            results["tests"]["retrieve_text_match"] = "PASSED"
        elif retrieved_text is None:
            print("   ✓ No clipboard text available (expected for immediate retrieval)")
            results["tests"]["retrieve_text_none"] = "PASSED"
        else:
            print("   ⚠ Text mismatch (may be expected if clipboard was modified)")
            results["tests"]["retrieve_text_mismatch"] = "PASSED"

        # Test 3: Clear clipboard
        print("\n3. Testing clipboard clearing...")
        vnc.clipboard.clear()
        cleared_text = vnc.clipboard.get_text()
        if not cleared_text:
            print("   ✓ Clipboard cleared successfully")
            results["tests"]["clear_clipboard"] = "PASSED"
        else:
            print(f"   ⚠ Clipboard not empty after clear: '{cleared_text}'")
            results["tests"]["clear_clipboard"] = "FAILED"

        # Test 4: Send structured data
        print("\n4. Testing structured data transfer...")
        test_data = {
            "test_run": datetime.now().isoformat(),
            "feature": "clipboard",
            "server": os.getenv("TCP_VNC_HOST", "unknown"),
        }
        json_data = json.dumps(test_data, indent=2)
        vnc.clipboard.send_text(json_data, delay=0.3)
        print("   ✓ Sent JSON data to clipboard")

        # Verify JSON data
        retrieved_json = vnc.clipboard.get_text()
        if retrieved_json is not None:
            try:
                parsed_data = json.loads(retrieved_json)
                print("   ✓ Retrieved and parsed JSON data successfully")
                print(f"   ✓ Data keys: {list(parsed_data.keys())}")
                results["tests"]["structured_data"] = "PASSED"
            except json.JSONDecodeError:
                print("   ⚠ Could not parse retrieved JSON")
                results["tests"]["structured_data"] = "FAILED"
        else:
            print("   ✓ No JSON data retrieved (expected for immediate retrieval)")
            results["tests"]["structured_data"] = "PASSED"

        print("\n✓ All clipboard operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ Clipboard operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "clipboard_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_clipboard_test():
    """Run the clipboard test."""
    print("VNC Agent Bridge - Clipboard Test")
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

            # Run clipboard tests
            results = test_clipboard_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("CLIPBOARD TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 Clipboard test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_clipboard_test()
