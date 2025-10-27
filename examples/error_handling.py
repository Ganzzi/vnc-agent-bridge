#!/usr/bin/env python3
"""
Error Handling Examples
=======================

Comprehensive examples showing how to handle various error conditions.

Examples:
    1. Connection errors
    2. Input validation errors
    3. State errors
    4. Timeout errors
    5. Error recovery patterns

Requirements:
    - vnc-agent-bridge installed
"""

from vnc_agent_bridge import (
    VNCAgentBridge,
    VNCException,
    VNCConnectionError,
    VNCInputError,
    VNCStateError,
    VNCTimeoutError,
)


def example_1_connection_errors():
    """Example: Handle connection errors."""
    print("Example 1: Connection Errors")
    print("-" * 50)

    # Test 1: Invalid host
    print("Test 1: Connecting to invalid host...")
    try:
        vnc = VNCAgentBridge("invalid-host-xyz.local", port=5900, timeout=2)
        vnc.connect()
    except VNCConnectionError as e:
        print(f"✓ Caught connection error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")

    # Test 2: Invalid port
    print("\nTest 2: Connecting to invalid port...")
    try:
        vnc = VNCAgentBridge("localhost", port=54321, timeout=2)
        vnc.connect()
    except VNCConnectionError as e:
        print(f"✓ Caught connection error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")

    # Test 3: Context manager with connection error
    print("\nTest 3: Context manager with connection error...")
    try:
        with VNCAgentBridge("invalid-host", port=5900, timeout=1) as vnc:
            vnc.mouse.left_click(100, 100)
    except VNCConnectionError as e:
        print(f"✓ Caught connection error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")


def example_2_state_errors():
    """Example: Handle state errors (operations before connecting)."""
    print("\nExample 2: State Errors")
    print("-" * 50)

    # Test 1: Operation without connecting
    print("Test 1: Click without connecting...")
    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        # Don't call connect()
        vnc.mouse.left_click(100, 100)
    except VNCStateError as e:
        print(f"✓ Caught state error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")

    # Test 2: Multiple disconnects
    print("\nTest 2: Multiple disconnects...")
    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        vnc.disconnect()  # Disconnect without connecting
        print("✓ First disconnect ok (expected)")
        vnc.disconnect()  # Disconnect again
        print("✓ Second disconnect ok (idempotent)")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")


def example_3_input_validation():
    """Example: Handle input validation errors."""
    print("\nExample 3: Input Validation Errors")
    print("-" * 50)

    # Test 1: Negative coordinates
    print("Test 1: Negative coordinates...")
    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        vnc.mouse.left_click(-1, 100)
    except VNCInputError as e:
        print(f"✓ Caught input error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")

    # Test 2: Invalid key name
    print("\nTest 2: Invalid key name...")
    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        vnc.keyboard.press_key("invalid_key_xyz")
    except VNCInputError as e:
        print(f"✓ Caught input error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")

    # Test 3: Invalid scroll amount
    print("\nTest 3: Negative scroll amount...")
    try:
        vnc = VNCAgentBridge("localhost", port=5900)
        vnc.scroll.scroll_up(amount=-5)
    except VNCInputError as e:
        print(f"✓ Caught input error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")


def example_4_retry_pattern():
    """Example: Retry pattern for handling transient errors."""
    print("\nExample 4: Retry Pattern")
    print("-" * 50)

    max_retries = 3
    retry_delay = 1

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}/{max_retries}...")
        try:
            vnc = VNCAgentBridge("localhost", port=5900, timeout=2)
            vnc.connect()
            print("✓ Connection successful")
            vnc.disconnect()
            break
        except VNCConnectionError as e:
            if attempt < max_retries:
                print(f"  Connection failed, retrying... ({e})")
                # time.sleep(retry_delay)
            else:
                print(f"✓ All retries failed: {e}")


def example_5_error_recovery():
    """Example: Error recovery and cleanup."""
    print("\nExample 5: Error Recovery")
    print("-" * 50)

    print("Attempting operation with cleanup...")
    vnc = None
    try:
        vnc = VNCAgentBridge("localhost", port=5900, timeout=2)
        vnc.connect()
        print("✓ Connected")

        # Simulate an error
        vnc.mouse.left_click(-1, 100)  # This will raise an error

    except VNCInputError as e:
        print(f"✓ Input error caught, recovering: {e}")

    except VNCConnectionError as e:
        print(f"✓ Connection error caught, recovering: {e}")

    except Exception as e:
        print(f"✓ Unexpected error caught: {type(e).__name__}: {e}")

    finally:
        if vnc:
            try:
                vnc.disconnect()
                print("✓ Cleanup: disconnected")
            except Exception as cleanup_error:
                print(f"✓ Cleanup error: {cleanup_error}")


def example_6_context_manager_cleanup():
    """Example: Context manager ensures cleanup even on error."""
    print("\nExample 6: Context Manager Cleanup")
    print("-" * 50)

    print("Using context manager (automatic cleanup)...")
    try:
        with VNCAgentBridge("localhost", port=5900, timeout=2) as vnc:
            print("✓ Connected (via context manager)")

            # Simulate an error
            # vnc.mouse.left_click(-1, 100)  # This would raise an error

            print("✓ Operations performed")

            # Cleanup happens automatically here, even if there's an error
    except VNCException as e:
        print(f"✓ Error handled, context manager cleaned up: {e}")

    print("✓ Context manager cleanup complete")


def example_7_timeout_handling():
    """Example: Handle timeout errors."""
    print("\nExample 7: Timeout Handling")
    print("-" * 50)

    print("Connecting with short timeout...")
    try:
        # Use very short timeout to simulate timeout
        vnc = VNCAgentBridge("localhost", port=5900, timeout=0.001)
        vnc.connect()
    except VNCTimeoutError as e:
        print(f"✓ Caught timeout error: {e}")
    except VNCConnectionError as e:
        print(f"✓ Caught connection error (might be timeout): {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")


def example_8_exception_hierarchy():
    """Example: Understanding exception hierarchy."""
    print("\nExample 8: Exception Hierarchy")
    print("-" * 50)

    print("Exception hierarchy:")
    print("  VNCException (base)")
    print("    ├─ VNCConnectionError")
    print("    ├─ VNCInputError")
    print("    ├─ VNCStateError")
    print("    ├─ VNCTimeoutError")
    print("    └─ VNCProtocolError")

    print("\nCatch all VNC exceptions:")

    try:
        # Simulate a generic VNC error
        raise VNCInputError("Test error")
    except VNCException as e:
        print(f"✓ Caught generic VNCException: {e}")

    print("\nCatch specific exceptions:")

    try:
        raise VNCConnectionError("Connection failed")
    except VNCConnectionError as e:
        print(f"✓ Caught VNCConnectionError: {e}")

    try:
        raise VNCInputError("Invalid input")
    except VNCInputError as e:
        print(f"✓ Caught VNCInputError: {e}")


def example_9_best_practices():
    """Example: Best practices for error handling."""
    print("\nExample 9: Best Practices")
    print("-" * 50)

    print("Best Practice 1: Use context manager")
    print("  with VNCAgentBridge(...) as vnc:")
    print("      vnc.mouse.left_click(100, 100)")
    print("  # Automatic cleanup")

    print("\nBest Practice 2: Catch specific exceptions")
    print("  try:")
    print("      vnc.mouse.left_click(-1, 100)")
    print("  except VNCInputError as e:")
    print("      # Handle validation error")

    print("\nBest Practice 3: Log and recover")
    print("  try:")
    print("      vnc.connect()")
    print("  except VNCConnectionError as e:")
    print("      logger.error(f'Connection failed: {e}')")
    print("      # Implement retry logic")

    print("\nBest Practice 4: Cleanup in finally")
    print("  try:")
    print("      vnc.connect()")
    print("  finally:")
    print("      vnc.disconnect()  # Always cleanup")

    print("\nBest Practice 5: Use timeout")
    print("  vnc = VNCAgentBridge('host', timeout=30)")
    print("  # Prevents hanging on network issues")

    print("\n✓ Best practices documented")


if __name__ == "__main__":
    print("VNC Agent Bridge - Error Handling Examples")
    print("=" * 50)
    print()

    # Run all examples
    example_1_connection_errors()
    example_2_state_errors()
    example_3_input_validation()
    example_4_retry_pattern()
    example_5_error_recovery()
    example_6_context_manager_cleanup()
    example_7_timeout_handling()
    example_8_exception_hierarchy()
    example_9_best_practices()

    print("\n" + "=" * 50)
    print("All error handling examples completed!")
    print("=" * 50)
