#!/usr/bin/env python3
"""
WebSocket VNC Connection Examples
=================================

Examples demonstrating how to use WebSocket-based VNC connections with
VNC Agent Bridge. WebSocket connections provide secure, real-time
communication with VNC servers over standard web protocols.

Requirements:
    - vnc-agent-bridge[websocket] installed (websocket-client library)
    - WebSocket-enabled VNC server running

Installation:
    pip install vnc-agent-bridge[websocket]

Examples:
    1. Basic WebSocket connection with URL template
    2. Proxmox VE WebSocket VNC connection
    3. SSL configuration and custom certificates
    4. Authentication methods (ticket/password)
    5. Error handling and troubleshooting
    6. Advanced usage with manual connection creation
"""

import time
from vnc_agent_bridge import (
    create_websocket_vnc,
    VNCAgentBridge,
    WebSocketVNCConnection,
    VNCConnectionError,
    VNCTimeoutError,
    VNCProtocolError,
)


def example_1_basic_websocket():
    """Example 1: Basic WebSocket connection with URL template."""
    print("Example 1: Basic WebSocket Connection")
    print("-" * 50)

    try:
        # Create WebSocket VNC connection using convenience function
        bridge = create_websocket_vnc(
            url_template="wss://${host}:${port}/websockify",
            host="localhost",  # Replace with your VNC server
            port=6080,  # Standard noVNC port
            timeout=10.0,
        )

        print("✓ Created WebSocket VNC connection")

        with bridge:
            print("✓ Connected to WebSocket VNC server")

            # Perform basic operations
            bridge.mouse.move_to(100, 100)
            print("✓ Moved mouse to (100, 100)")

            bridge.mouse.left_click()
            print("✓ Performed left click")

            bridge.keyboard.type_text("Hello WebSocket VNC!")
            print("✓ Typed greeting message")

            # Get current position
            position = bridge.mouse.get_position()
            print(f"✓ Current mouse position: {position}")

            time.sleep(1)  # Brief pause

    except VNCConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("  Make sure your WebSocket VNC server is running")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_2_proxmox_connection():
    """Example 2: Proxmox VE WebSocket VNC connection."""
    print("\nExample 2: Proxmox VE WebSocket Connection")
    print("-" * 50)

    # Proxmox VE WebSocket URL template
    proxmox_template = "wss://${host}:${port}/api2/json/nodes/pve/qemu/100/vncwebsocket?vncticket=${ticket}"

    try:
        bridge = create_websocket_vnc(
            url_template=proxmox_template,
            host="proxmox.example.com",  # Replace with your Proxmox host
            port=8006,  # Standard Proxmox port
            ticket="PVEVNC:your_ticket_here",  # Replace with actual ticket
            timeout=15.0,
        )

        print("✓ Created Proxmox WebSocket connection")

        with bridge:
            print("✓ Connected to Proxmox VM via WebSocket")

            # Simulate some VM management operations
            bridge.mouse.move_to(50, 50)
            bridge.keyboard.hotkey("ctrl", "alt", "delete")  # Send Ctrl+Alt+Delete
            print("✓ Sent Ctrl+Alt+Delete to VM")

            time.sleep(2)

            # Type a command
            bridge.keyboard.type_text("echo 'Hello from Proxmox VM!'")
            bridge.keyboard.press_key("enter")
            print("✓ Executed command in VM")

    except VNCConnectionError as e:
        print(f"✗ Proxmox connection failed: {e}")
        print("  Check your Proxmox host, port, and VNC ticket")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_3_ssl_configuration():
    """Example 3: SSL configuration and custom certificates."""
    print("\nExample 3: SSL Configuration")
    print("-" * 50)

    try:
        # Example with SSL verification disabled (development only)
        print("3a. Connection with SSL verification disabled:")
        bridge_no_ssl = create_websocket_vnc(
            url_template="wss://${host}:${port}/vnc/websocket",
            host="dev-vnc.example.com",
            port=8443,
            verify_ssl=False,  # WARNING: Only for development!
            timeout=10.0,
        )
        print("✓ Created connection with SSL disabled (dev mode)")

        # Note: Not actually connecting to avoid errors in example

    except Exception as e:
        print(f"✗ SSL configuration error: {e}")

    try:
        # Example with custom certificate (production)
        print("\n3b. Connection with custom SSL certificate:")
        # In real usage, load certificate from file:
        # with open("server.crt", "r") as f:
        #     cert_pem = f.read()

        cert_pem = (
            "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"  # Placeholder
        )

        bridge_custom_ssl = create_websocket_vnc(
            url_template="wss://${host}:${port}/secure/vnc",
            host="secure-vnc.example.com",
            port=8443,
            certificate_pem=cert_pem,
            verify_ssl=True,
            timeout=15.0,
        )
        print("✓ Created connection with custom SSL certificate")

        # Note: Not actually connecting to avoid errors in example

    except Exception as e:
        print(f"✗ Custom SSL configuration error: {e}")


def example_4_authentication_methods():
    """Example 4: Different authentication methods."""
    print("\nExample 4: Authentication Methods")
    print("-" * 50)

    try:
        # Ticket-based authentication
        print("4a. Ticket-based authentication:")
        bridge_ticket = create_websocket_vnc(
            url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
            host="vnc.example.com",
            port=6900,
            ticket="session_ticket_12345",
        )
        print("✓ Created connection with ticket authentication")

    except Exception as e:
        print(f"✗ Ticket authentication error: {e}")

    try:
        # Password-based authentication
        print("\n4b. Password-based authentication:")
        bridge_password = create_websocket_vnc(
            url_template="wss://${host}:${port}/vnc/websocket?password=${password}",
            host="vnc.example.com",
            port=6900,
            password="my_secure_password",
        )
        print("✓ Created connection with password authentication")

    except Exception as e:
        print(f"✗ Password authentication error: {e}")

    try:
        # Combined authentication
        print("\n4c. Combined ticket and password authentication:")
        bridge_combined = create_websocket_vnc(
            url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}&password=${password}",
            host="vnc.example.com",
            port=6900,
            ticket="session_token",
            password="user_password",
        )
        print("✓ Created connection with combined authentication")

    except Exception as e:
        print(f"✗ Combined authentication error: {e}")


def example_5_error_handling():
    """Example 5: Error handling and troubleshooting."""
    print("\nExample 5: Error Handling")
    print("-" * 50)

    # Test different error scenarios
    error_scenarios = [
        {
            "name": "Invalid host",
            "config": {
                "url_template": "wss://${host}:${port}/websockify",
                "host": "invalid.host.that.does.not.exist",
                "port": 6080,
                "timeout": 5.0,
            },
        },
        {
            "name": "Connection timeout",
            "config": {
                "url_template": "wss://${host}:${port}/websockify",
                "host": "10.255.255.1",  # Unreachable IP
                "port": 6080,
                "timeout": 2.0,
            },
        },
        {
            "name": "Invalid port",
            "config": {
                "url_template": "wss://${host}:${port}/websockify",
                "host": "localhost",
                "port": 12345,  # Closed port
                "timeout": 3.0,
            },
        },
    ]

    for scenario in error_scenarios:
        print(f"\nTesting: {scenario['name']}")
        try:
            bridge = create_websocket_vnc(**scenario["config"])
            with bridge:
                print("✓ Unexpected success - connection worked!")
        except VNCConnectionError as e:
            print(f"✓ Expected connection error: {e}")
        except VNCTimeoutError as e:
            print(f"✓ Expected timeout error: {e}")
        except VNCProtocolError as e:
            print(f"✓ Expected protocol error: {e}")
        except Exception as e:
            print(f"? Unexpected error type: {type(e).__name__}: {e}")


def example_6_advanced_usage():
    """Example 6: Advanced usage with manual connection creation."""
    print("\nExample 6: Advanced Usage")
    print("-" * 50)

    try:
        # Manual connection creation for full control
        connection = WebSocketVNCConnection(
            url_template="wss://${host}:${port}/vnc/websocket?token=${ticket}",
            host="advanced-vnc.example.com",
            port=6900,
            ticket="advanced_session_token",
            timeout=20.0,
            verify_ssl=True,
        )

        print("✓ Created WebSocketVNCConnection manually")

        # Create bridge with custom connection
        bridge = VNCAgentBridge(connection=connection)
        print("✓ Created VNCAgentBridge with custom connection")

        # Demonstrate connection reuse
        print("\nDemonstrating connection reuse:")
        operations = [
            ("Move mouse", lambda: bridge.mouse.move_to(200, 200)),
            ("Click", lambda: bridge.mouse.left_click()),
            ("Type text", lambda: bridge.keyboard.type_text("Advanced WebSocket demo")),
            ("Scroll", lambda: bridge.scroll.scroll_down(2)),
        ]

        # Note: Not actually connecting to avoid errors in example
        for op_name, op_func in operations:
            print(f"  - Would perform: {op_name}")
            # op_func()  # Uncomment when you have a real server

        print("✓ Connection reuse demonstration complete")

    except Exception as e:
        print(f"✗ Advanced usage error: {e}")


def main():
    """Run all WebSocket examples."""
    print("VNC Agent Bridge - WebSocket Connection Examples")
    print("=" * 60)
    print("Note: These examples require a WebSocket-enabled VNC server.")
    print("Modify host/port/ticket values to match your environment.\n")

    # Run examples (comment out ones you don't want to test)
    example_1_basic_websocket()
    example_2_proxmox_connection()
    example_3_ssl_configuration()
    example_4_authentication_methods()
    example_5_error_handling()
    example_6_advanced_usage()

    print("\n" + "=" * 60)
    print("Examples completed. Check output above for results.")
    print("\nTo run specific examples, comment out the ones you don't need.")
    print("Make sure your WebSocket VNC server is running and accessible!")


if __name__ == "__main__":
    main()
