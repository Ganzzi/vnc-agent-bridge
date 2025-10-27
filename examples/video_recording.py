#!/usr/bin/env python3
"""
Example: Video Recording

This example demonstrates the video recording functionality introduced
in v0.2.0. Shows how to record screen sessions and save frame sequences.

Requirements:
    pip install vnc-agent-bridge[video]
"""

from vnc_agent_bridge import VNCAgentBridge
import time


def example_record_for_duration():
    """Record screen for a fixed duration."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Recording 10 seconds at 30 FPS...")

        frames = vnc.video.record(duration=10.0, fps=30.0)

        print(f"Recorded {len(frames)} frames")
        print(f"Duration: {vnc.video.get_duration(frames):.2f} seconds")
        print(f"FPS: {vnc.video.get_frame_rate(frames):.2f}")

        # Save frames
        vnc.video.save_frames(frames, "recording_duration/")
        print("Frames saved to: recording_duration/")


def example_background_recording():
    """Record in background while performing actions."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Starting background recording...")
        vnc.video.start_recording(fps=30.0)

        try:
            # Perform actions
            print("Performing actions...")
            vnc.mouse.left_click(100, 100)
            time.sleep(1.0)

            vnc.keyboard.type_text("Background Recording Test")
            time.sleep(1.0)

            vnc.keyboard.press_key("return")
            time.sleep(1.0)

        finally:
            # Stop recording
            print("Stopping recording...")
            frames = vnc.video.stop_recording()

            print(f"Recorded {len(frames)} frames")
            print(f"Duration: {vnc.video.get_duration(frames):.2f} seconds")

            # Save frames
            vnc.video.save_frames(frames, "recording_background/")
            print("Frames saved to: recording_background/")


def example_record_until_completion():
    """Record until a condition is met."""
    try:
        import numpy as np

        def condition_met():
            """Check if operation completed."""
            # This is a simplified check - in real scenarios would be more sophisticated
            # For now, always return False to demonstrate the pattern
            return False

        with VNCAgentBridge("localhost", port=5900) as vnc:
            print("Recording until condition met (max 20 seconds)...")

            frames = vnc.video.record_until(
                condition=condition_met, max_duration=20.0, fps=30.0
            )

            print(f"Recorded {len(frames)} frames")
            print(f"Duration: {vnc.video.get_duration(frames):.2f} seconds")

            # Save frames
            vnc.video.save_frames(frames, "recording_conditional/")
            print("Frames saved to: recording_conditional/")

    except ImportError:
        print("numpy not available, skipping conditional recording")


def example_frame_statistics():
    """Record and analyze frame statistics."""
    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("Recording 5 seconds for statistics...")

        frames = vnc.video.record(duration=5.0, fps=30.0)

        # Get statistics
        num_frames = len(frames)
        duration = vnc.video.get_duration(frames)
        actual_fps = vnc.video.get_frame_rate(frames)

        print(f"Statistics:")
        print(f"  Total frames: {num_frames}")
        print(f"  Total duration: {duration:.2f} seconds")
        print(f"  Target FPS: 30")
        print(f"  Actual FPS: {actual_fps:.2f}")
        print(f"  FPS accuracy: {(actual_fps / 30.0) * 100:.1f}%")

        # Time per frame
        if num_frames > 1:
            time_per_frame = duration / (num_frames - 1)
            print(f"  Time per frame: {time_per_frame * 1000:.2f} ms")


def example_multiple_fps_rates():
    """Record at different FPS rates."""
    fps_rates = [15.0, 30.0, 60.0]

    for fps in fps_rates:
        print(f"Recording 5 seconds at {fps} FPS...")

        with VNCAgentBridge("localhost", port=5900) as vnc:
            frames = vnc.video.record(duration=5.0, fps=fps)

            actual_fps = vnc.video.get_frame_rate(frames)
            duration = vnc.video.get_duration(frames)

            print(f"  Frames: {len(frames)}")
            print(f"  Actual FPS: {actual_fps:.2f}")
            print(f"  Duration: {duration:.2f}s")

            # Save frames
            vnc.video.save_frames(frames, f"recording_fps_{fps}/", prefix="frame")
            print(f"  Saved to: recording_fps_{fps}/")


def main():
    """Run all video recording examples."""
    print("=" * 60)
    print("v0.2.0 Video Recording Examples")
    print("=" * 60)

    try:
        print("\nExample 1: Record for Duration")
        print("-" * 60)
        example_record_for_duration()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        print("\nExample 2: Background Recording")
        print("-" * 60)
        example_background_recording()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        print("\nExample 3: Record Until Condition")
        print("-" * 60)
        example_record_until_completion()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        print("\nExample 4: Frame Statistics")
        print("-" * 60)
        example_frame_statistics()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        print("\nExample 5: Multiple FPS Rates")
        print("-" * 60)
        example_multiple_fps_rates()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
