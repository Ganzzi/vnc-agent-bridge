#!/usr/bin/env python3
"""
Example: Complete v0.2.0 Workflow

This example demonstrates a complete workflow combining all v0.2.0 features:
- Screenshot capture for verification
- Clipboard management for data transfer
- Video recording for documentation

This simulates a realistic test automation scenario where we:
1. Record the entire session
2. Take screenshots at key points
3. Transfer data via clipboard
4. Verify results

Requirements:
    pip install vnc-agent-bridge[full]
"""

from vnc_agent_bridge import VNCAgentBridge
import json
import time
from datetime import datetime
from pathlib import Path


def create_output_directory():
    """Create output directory for results."""
    output_dir = Path("workflow_output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def run_complete_workflow():
    """Run a complete workflow combining all v0.2.0 features."""

    output_dir = create_output_directory()

    # Initialize results tracking
    results = {
        "start_time": datetime.now().isoformat(),
        "steps": [],
        "screenshots": [],
        "video_recorded": False,
        "status": "running",
    }

    with VNCAgentBridge("localhost", port=5900) as vnc:
        print("=" * 70)
        print("Complete v0.2.0 Workflow Example")
        print("=" * 70)

        try:
            # ============================================================
            # Phase 1: Start Recording
            # ============================================================
            print("\nPhase 1: Starting video recording...")
            vnc.video.start_recording(fps=30.0)
            results["video_recorded"] = True

            step_num = 1
            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Setup",
                    "action": "Started video recording",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            print("  ✓ Video recording started")

            # ============================================================
            # Phase 2: Application Setup
            # ============================================================
            print("\nPhase 2: Application setup...")
            step_num += 1

            # Take screenshot of initial state
            vnc.screenshot.save(str(output_dir / "01_initial_state.png"))
            results["screenshots"].append("01_initial_state.png")
            print("  ✓ Captured initial state")

            # Simulate navigation
            print("  ✓ Navigating to login page")
            vnc.mouse.left_click(100, 100)
            time.sleep(1.0)

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Application Setup",
                    "action": "Navigated to application",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Phase 3: Data Transfer via Clipboard
            # ============================================================
            print("\nPhase 3: Data transfer via clipboard...")
            step_num += 1

            credentials = {
                "username": "demo_user",
                "email": "demo@example.com",
                "timestamp": datetime.now().isoformat(),
            }

            json_credentials = json.dumps(credentials)
            vnc.clipboard.send_text(json_credentials)
            print(f"  ✓ Sent credentials ({len(json_credentials)} bytes)")

            # Paste credentials
            vnc.keyboard.hotkey("ctrl", "v")
            time.sleep(0.5)

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Data Transfer",
                    "action": "Transferred credentials via clipboard",
                    "data_size": len(json_credentials),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Phase 4: Interaction and Verification
            # ============================================================
            print("\nPhase 4: Application interaction...")
            step_num += 1

            # Simulate form filling
            vnc.keyboard.press_key("tab")
            vnc.keyboard.type_text("demo_password")
            vnc.keyboard.press_key("return")

            time.sleep(2.0)

            # Take screenshot of result
            vnc.screenshot.save(str(output_dir / "02_after_login.png"))
            results["screenshots"].append("02_after_login.png")
            print("  ✓ Captured post-login state")

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Interaction",
                    "action": "Logged in and captured result",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Phase 5: Data Extraction
            # ============================================================
            print("\nPhase 5: Data extraction...")
            step_num += 1

            # Clear clipboard to ensure fresh data
            vnc.clipboard.clear()
            time.sleep(0.3)

            # Copy result (simulated)
            vnc.keyboard.hotkey("ctrl", "a")
            vnc.keyboard.hotkey("ctrl", "c")

            time.sleep(0.5)

            # Get extracted data
            extracted_data = vnc.clipboard.get_text(timeout=2.0)

            if extracted_data:
                print(f"  ✓ Extracted data ({len(extracted_data)} bytes)")
            else:
                print("  ⚠ No data extracted")

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Data Extraction",
                    "action": "Extracted result from application",
                    "data_size": len(extracted_data) if extracted_data else 0,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Phase 6: Verification Screenshots
            # ============================================================
            print("\nPhase 6: Capturing verification screenshots...")
            step_num += 1

            # Capture multiple regions for verification
            regions = {
                "header": (0, 0, 1920, 100),
                "content": (100, 150, 1720, 700),
                "footer": (0, 980, 1920, 100),
            }

            for region_name, (x, y, w, h) in regions.items():
                filename = f"03_region_{region_name}.png"
                vnc.screenshot.save_region(
                    str(output_dir / filename), x=x, y=y, width=w, height=h
                )
                results["screenshots"].append(filename)

            print(f"  ✓ Captured {len(regions)} region screenshots")

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Verification",
                    "action": f"Captured {len(regions)} region screenshots",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Phase 7: Recording Completion
            # ============================================================
            print("\nPhase 7: Stopping video recording...")
            step_num += 1

            frames = vnc.video.stop_recording()

            print(f"  ✓ Recorded {len(frames)} frames")
            print(f"  ✓ Duration: {vnc.video.get_duration(frames):.2f} seconds")
            print(f"  ✓ FPS: {vnc.video.get_frame_rate(frames):.2f}")

            # Save frames
            vnc.video.save_frames(frames, str(output_dir / "recording"))

            results["steps"].append(
                {
                    "number": step_num,
                    "phase": "Recording",
                    "action": "Stopped and saved recording",
                    "total_frames": len(frames),
                    "duration": vnc.video.get_duration(frames),
                    "fps": vnc.video.get_frame_rate(frames),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ============================================================
            # Summary
            # ============================================================
            print("\nWorkflow completed successfully!")

            results["status"] = "completed"
            results["end_time"] = datetime.now().isoformat()

        except Exception as e:
            print(f"\nError during workflow: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

            # Make sure to stop recording
            if vnc.video.is_recording():
                frames = vnc.video.stop_recording()
                vnc.video.save_frames(frames, str(output_dir / "recording"))

        finally:
            # Save results to JSON
            results_file = output_dir / "workflow_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)

            print(f"\nResults saved to: {results_file}")

    # ====================================================================
    # Print Summary
    # ====================================================================
    print("\n" + "=" * 70)
    print("Workflow Summary")
    print("=" * 70)
    print(f"Status: {results['status'].upper()}")
    print(f"Steps completed: {len(results['steps'])}")
    print(f"Screenshots captured: {len(results['screenshots'])}")
    print(f"Video recorded: {results['video_recorded']}")
    print(f"Output directory: {output_dir}")
    print("=" * 70)

    return results


def main():
    """Run the complete workflow."""
    try:
        results = run_complete_workflow()

        if results["status"] == "completed":
            print("\n✓ Workflow completed successfully!")
        else:
            print("\n✗ Workflow encountered errors")

    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
