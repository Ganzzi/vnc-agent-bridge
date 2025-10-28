#!/usr/bin/env python3
"""
WebSocket Video Recording Test Script
=====================================

This script tests video recording operations for WebSocket-based VNC servers.

Features tested:
- Timed video recording
- Background video recording
- Frame saving and management
- Recording with different FPS settings

Requirements:
    pip install vnc-agent-bridge[websocket,full]

Usage:
    python websocket_test_video.py
"""

import time
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
    test_dir = output_dir / f"websocket_video_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_video_operations(vnc, output_dir):
    """Test video recording operations."""
    print("=" * 60)
    print("TESTING WEBSOCKET VIDEO OPERATIONS")
    print("=" * 60)

    results = {
        "start_time": datetime.now().isoformat(),
        "tests": {},
    }

    try:
        # Test 1: Timed recording
        print("\n1. Testing timed video recording...")
        print("   Recording 3 seconds at 5 FPS...")
        frames = vnc.video.record(duration=3.0, fps=5.0)
        print(f"   ✓ Recorded {len(frames)} frames")

        # Save the recording
        video_dir = output_dir / "websocket_timed_recording"
        vnc.video.save_frames(frames, str(video_dir))
        print(f"   ✓ Saved frames to: {video_dir}")
        results["tests"]["timed_recording"] = "PASSED"

        # Test 2: Background recording
        print("\n2. Testing background recording...")
        print("   Starting background recording at 10 FPS...")
        vnc.video.start_recording(fps=10.0)

        # Perform some actions while recording
        print("   Performing actions during recording...")
        time.sleep(0.5)
        vnc.mouse.move_to(100, 100, delay=0.2)
        vnc.mouse.left_click(delay=0.2)
        time.sleep(0.5)
        vnc.keyboard.type_text("WebSocket video recording test", delay=0.1)
        time.sleep(0.5)

        # Stop recording
        print("   Stopping background recording...")
        frames_bg = vnc.video.stop_recording()
        print(f"   ✓ Recorded {len(frames_bg)} frames in background")

        # Save background recording
        bg_video_dir = output_dir / "websocket_background_recording"
        vnc.video.save_frames(frames_bg, str(bg_video_dir))
        print(f"   ✓ Saved background frames to: {bg_video_dir}")
        results["tests"]["background_recording"] = "PASSED"

        # Test 3: Recording statistics
        print("\n3. Testing recording statistics...")
        if frames:
            fps_actual = vnc.video.get_frame_rate(frames)
            duration = vnc.video.get_duration(frames)
            print(
                f"   ✓ Timed recording: {len(frames)} frames, {duration:.2f}s, {fps_actual:.2f} FPS"
            )

        if frames_bg:
            fps_bg_actual = vnc.video.get_frame_rate(frames_bg)
            duration_bg = vnc.video.get_duration(frames_bg)
            print(
                f"   ✓ Background recording: {len(frames_bg)} frames, {duration_bg:.2f}s, {fps_bg_actual:.2f} FPS"
            )

        results["tests"]["recording_stats"] = "PASSED"

        print("\n✓ All WebSocket video operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ WebSocket video operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "websocket_video_test_results.json"
    with open(results_file, "w") as f:
        import json

        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_websocket_video_test():
    """Run the WebSocket video test."""
    print("WebSocket VNC Agent Bridge - Video Recording Test")
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

            # Run video tests
            results = test_video_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("WEBSOCKET VIDEO TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ WebSocket VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 WebSocket video test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_websocket_video_test()
