#!/usr/bin/env python3
"""
WebSocket VNC Connection Diagnostic Script
==========================================

This script helps diagnose WebSocket VNC connection issues by testing different
connection parameters and providing detailed error information.

WebSocket VNC servers include:
- Proxmox VE (Virtual Environment)
- noVNC servers
- Custom WebSocket VNC implementations

The script tests various URL templates, authentication methods, and SSL configurations.
"""

import os
import time
from vnc_agent_bridge import create_websocket_vnc, VNCException
import dotenv

dotenv.load_dotenv()


def test_websocket_connection(
    url_template,
    host,
    port,
    ticket=None,
    vnc_port=None,
    certificate_pem=None,
    verify_ssl=True,
    timeout=10.0,
):
    """Test WebSocket VNC connection with detailed error reporting."""
    print(f"\n🔍 Testing WebSocket connection to {host}:{port}")
    print(f"   URL Template: {url_template}")
    print(f"   Timeout: {timeout}s")
    print(f"   Ticket: {'Set' if ticket else 'Not set'}")
    print(f"   SSL Verification: {'Enabled' if verify_ssl else 'Disabled'}")

    start_time = time.time()
    try:
        with create_websocket_vnc(
            url_template=url_template,
            host=host,
            port=port,
            ticket=ticket,
            vnc_port=vnc_port,
            certificate_pem=certificate_pem,
            verify_ssl=verify_ssl,
            timeout=timeout,
        ) as vnc:
            elapsed = time.time() - start_time
            print(f"   ⏱️  Connected in {elapsed:.2f}s")
            print("   ✓ WebSocket VNC connection successful!")
            return True
    except VNCException as e:
        elapsed = time.time() - start_time
        print(f"   ⏱️  Failed after {elapsed:.2f}s")
        print(f"   ❌ VNC Error: {e}")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ⏱️  Failed after {elapsed:.2f}s")
        print(f"   💥 Unexpected Error: {e}")
        return False


def run_websocket_diagnostics():
    """Run comprehensive WebSocket VNC connection diagnostics."""
    print("WebSocket VNC Connection Diagnostics")
    print("=" * 60)

    # Get environment variables
    vnc_ticket = os.getenv("VNC_WEBSOCKET_TICKET")
    certificate_pem = os.getenv("VNC_CERTIFICATE_PEM")
    # Note: WebSocket VNC uses ticket-based auth, password is not used
    proxmox_host = os.getenv("PROXMOX_HOST", "192.168.1.5")
    proxmox_port = int(os.getenv("PROXMOX_PORT", "8006"))
    proxmox_node = os.getenv("PROXMOX_NODE", "pve")
    proxmox_vmid = os.getenv("PROXMOX_VMID", "100")
    proxmox_vnc_port = int(os.getenv("VNC_PORT", "5900"))

    print(f"Environment variables:")
    print(f"  PROXMOX_HOST: {proxmox_host}")
    print(f"  PROXMOX_PORT: {proxmox_port}")
    print(f"  PROXMOX_NODE: {proxmox_node}")
    print(f"  PROXMOX_VMID: {proxmox_vmid}")
    print(f"  VNC_WEBSOCKET_TICKET: {'Set' if vnc_ticket else 'Not set'}")
    print(f"  VNC_CERTIFICATE_PEM: {'Set' if certificate_pem else 'Not set'}")
    print("  Note: WebSocket VNC uses ticket-based authentication")
    print()

    # Test configurations for different WebSocket VNC servers
    configs = [
        # Proxmox configurations
        {
            "name": "Proxmox VM (Standard)",
            "url_template": f"wss://${{host}}:${{port}}/api2/json/nodes/{proxmox_node}/qemu/{proxmox_vmid}/vncwebsocket?port=${{vnc_port}}&vncticket=${{ticket}}",
            "host": proxmox_host,
            "port": proxmox_port,
            "vnc_port": proxmox_vnc_port,  # Default VNC display port
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,  # Often self-signed certificates
            "timeout": 15.0,
        },
        # Note: WebSocket VNC typically uses ticket-based auth, password not used
        {
            "name": "Proxmox VM (SSL Enabled)",
            "url_template": f"wss://${{host}}:${{port}}/api2/json/nodes/{proxmox_node}/qemu/{proxmox_vmid}/vncwebsocket?port=${{vnc_port}}&vncticket=${{ticket}}",
            "host": proxmox_host,
            "port": proxmox_port,
            "vnc_port": proxmox_vnc_port,
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": True,
            "timeout": 15.0,
        },
        # Alternative ports and configurations
        {
            "name": "Proxmox Alternative Port (443)",
            "url_template": f"wss://${{host}}:${{port}}/api2/json/nodes/{proxmox_node}/qemu/{proxmox_vmid}/vncwebsocket?port=${{vnc_port}}&vncticket=${{ticket}}",
            "host": proxmox_host,
            "port": 443,
            "vnc_port": 5900,
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,
            "timeout": 15.0,
        },
        # noVNC-style configurations
        {
            "name": "noVNC Server (Standard)",
            "url_template": "wss://${host}:${port}/websockify",
            "host": proxmox_host,
            "port": 6080,
            "ticket": None,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,
            "timeout": 10.0,
        },
        {
            "name": "noVNC Server (With Token)",
            "url_template": "wss://${host}:${port}/websockify?token=${ticket}",
            "host": proxmox_host,
            "port": 6080,
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,
            "timeout": 10.0,
        },
        # Custom WebSocket configurations
        {
            "name": "Custom WebSocket VNC",
            "url_template": "wss://${host}:${port}/vnc/websocket?token=${ticket}",
            "host": proxmox_host,
            "port": 6900,
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,
            "timeout": 10.0,
        },
        {
            "name": "Custom WebSocket VNC with VNC Port",
            "url_template": "wss://${host}:${port}/vnc/${vnc_port}/websocket?token=${ticket}",
            "host": proxmox_host,
            "port": 6900,
            "vnc_port": 5901,
            "ticket": vnc_ticket,
            "certificate_pem": certificate_pem,
            "verify_ssl": False,
            "timeout": 10.0,
        },
        # Local development servers
        {
            "name": "Local Development Server",
            "url_template": "ws://${host}:${port}/vnc",
            "host": "localhost",
            "port": 8080,
            "ticket": None,
            "certificate_pem": None,
            "verify_ssl": False,
            "timeout": 5.0,
        },
    ]

    successful_configs = []

    for config in configs:
        print(f"\n🎯 Testing: {config['name']}")
        print("-" * 40)

        # Remove 'name' from config before passing to function
        test_config = {k: v for k, v in config.items() if k != "name"}
        success = test_websocket_connection(**test_config)
        if success:
            successful_configs.append(config)

    print("\n" + "=" * 60)
    print("WEBSOCKET VNC DIAGNOSTIC SUMMARY")
    print("=" * 60)

    if successful_configs:
        print(f"✅ {len(successful_configs)} successful WebSocket connection(s) found:")
        for config in successful_configs:
            auth_info = []
            if config["ticket"]:
                auth_info.append("ticket")
            auth_str = f" ({', '.join(auth_info)})" if auth_info else " (no auth)"

            ssl_str = " SSL" if config["verify_ssl"] else " no-SSL"
            print(
                f"   • {config['name']}: {config['host']}:{config['port']}{auth_str}{ssl_str}"
            )
    else:
        print("❌ No successful WebSocket VNC connections found")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Verify WebSocket VNC server is running and accessible")
        print("   2. Check the correct URL template for your VNC server type:")
        print(
            "      - Proxmox: wss://host:8006/api2/json/nodes/node/qemu/vmid/vncwebsocket?vncticket=ticket"
        )
        print("      - noVNC: wss://host:6080/websockify")
        print("      - Custom: wss://host:port/vnc/websocket?token=ticket")
        print("   3. Ensure authentication credentials are correct (ticket)")
        print(
            "   4. Try disabling SSL verification (verify_ssl=False) for self-signed certificates"
        )
        print("   5. Check firewall settings and port accessibility")
        print("   6. Verify the VNC server supports WebSocket connections")
        print("   7. Update environment variables in .env file:")
        print("      - PROXMOX_HOST=your.proxmox.host")
        print("      - PROXMOX_PORT=8006")
        print("      - PROXMOX_NODE=your-node-name")
        print("      - PROXMOX_VMID=vm-id")
        print("      - VNC_WEBSOCKET_TICKET=your-ticket")
        print("      - VNC_CERTIFICATE_PEM=your-certificate-pem-string")
        print("      Note: WebSocket VNC uses ticket-based authentication")


if __name__ == "__main__":
    run_websocket_diagnostics()
