#!/usr/bin/env python3
"""
Video Recording Test Script
===========================

This script tests video recording operations for the VNC Agent Bridge package.

Features tested:
- Timed video recording
- Background video recording
- Frame saving and management
- Recording with different FPS settings

Requirements:
    pip install vnc-agent-bridge[full]

Usage:
    python test_video.py
"""

import time
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
    test_dir = output_dir / f"video_test_{timestamp}"
    test_dir.mkdir(exist_ok=True)
    return test_dir


def test_video_operations(vnc, output_dir):
    """Test video recording operations."""
    print("=" * 60)
    print("TESTING VIDEO OPERATIONS")
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
        video_dir = output_dir / "timed_recording"
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
        vnc.keyboard.type_text("Video recording test", delay=0.1)
        time.sleep(0.5)

        # Stop recording
        print("   Stopping background recording...")
        frames_bg = vnc.video.stop_recording()
        print(f"   ✓ Recorded {len(frames_bg)} frames in background")

        # Save background recording
        bg_video_dir = output_dir / "background_recording"
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

        print("\n✓ All video operations completed")
        results["overall_result"] = "PASSED"

    except Exception as e:
        print(f"\n✗ Video operations failed: {e}")
        results["overall_result"] = f"FAILED: {str(e)}"

    # Save results
    results["end_time"] = datetime.now().isoformat()
    results_file = output_dir / "video_test_results.json"
    with open(results_file, "w") as f:
        import json

        json.dump(results, f, indent=2)
    print(f"\n📄 Test results saved to: {results_file}")

    return results


def run_video_test():
    """Run the video test."""
    print("VNC Agent Bridge - Video Recording Test")
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

            # Run video tests
            results = test_video_operations(vnc, output_dir)

            # Summary
            print("\n" + "=" * 60)
            print("VIDEO TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Result: {results['overall_result']}")
            print(f"Output Directory: {output_dir}")

    except VNCException as e:
        print(f"\n❌ VNC Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

    print(
        f"\n🏁 Video test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    run_video_test()
