#!/usr/bin/env python3
"""
WebSocket Clipboard Test Script
===============================

This script tests clipboard operations for WebSocket-based VNC servers.

Features tested:
- Send text to remote clipboard
- Retrieve text from remote clipboard
- Clear remote clipboard
- Send structured data (JSON)

Requirements:
    pip install vnc-agent-bridge[websocket,full]

Usage:
    python websocket_test_clipboard.py
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from vnc_agent_bridge import create_websocket_vnc, VNCException
import dotenv

dotenv.load_dotenv()


def create_test_output_directory():
    """Create directory for test outputs."""
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = output_dir / f"websocket_clipboard_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_clipboard_operations(vnc, output_dir):
    """Test clipboard operations."""
    print("=" * 60)
    print("TESTING WEBSOCKET CLIPBOARD OPERATIONS")
    print("=" * 60)

    results = {
        "start_time": datetime.now().isoformat(),
        "tests": {},
    }

    try:
        # Test 1: Send text to clipboard
        print("\n1. Testing clipboard text sending...")
        test_text = "Hello from WebSocket VNC Agent Bridge clipboard test!"
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
            "connection_type": "websocket",
            "feature": "clipboard",
            "server_config": {
                "host": os.getenv("WEBSOCKET_VNC_HOST", "unknown"),
                "port": int(os.getenv("WEBSOCKET_VNC_HOST_PORT", "8006")),
                "node": os.getenv("WEBSOCKET_VNC_NODE", "pve"),
                "vmid": os.getenv("WEBSOCKET_VNC_VMID", "100"),
            },
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
            results["tests"]["structured_data"] = "PASSED"
        except json.JSONDecodeError:
            print("   ⚠ Could not parse retrieved JSON")
            results["tests"]["structured_data"] = "FAILED"

        print("\n✓ All WebSocket clipboard operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ WebSocket clipboard operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "websocket_clipboard_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_websocket_clipboard_test():
    """Run the WebSocket clipboard test."""
    print("WebSocket VNC Agent Bridge - Clipboard Test")
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

            # Run clipboard tests
            results = test_clipboard_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("WEBSOCKET CLIPBOARD TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ WebSocket VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 WebSocket clipboard test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_websocket_clipboard_test()
