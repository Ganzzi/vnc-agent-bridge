#!/usr/bin/env python3
"""
VNC Connection Diagnostic Script
===============================

This script helps diagnose VNC connection issues by testing different
connection parameters and providing detailed error information.
"""

import os
import time
from vnc_agent_bridge import VNCAgentBridge, VNCException


def test_connection(host, port, password=None, timeout=10.0):
    """Test VNC connection with detailed error reporting."""
    print(f"\n🔍 Testing connection to {host}:{port}")
    print(f"   Timeout: {timeout}s")
    print(f"   Password: {'Set' if password else 'Not set'}")

    start_time = time.time()
    try:
        with VNCAgentBridge(host, port=port, password=password, timeout=timeout) as vnc:
            elapsed = time.time() - start_time
            print(f"   ⏱️  Connected in {elapsed:.2f}s")
            print("   ✓ Connection successful!")
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


def run_diagnostics():
    """Run comprehensive connection diagnostics."""
    print("VNC Connection Diagnostics")
    print("=" * 50)

    # Test configurations
    configs = [
        {"host": "192.168.1.5", "port": 5900, "password": None, "timeout": 10.0},
        {
            "host": "192.168.1.5",
            "port": 5900,
            "password": os.getenv("TCP_VNC_PASSWORD"),
            "timeout": 10.0,
        },
        {
            "host": "192.168.1.5",
            "port": 5900,
            "password": os.getenv("TCP_VNC_PASSWORD"),
            "timeout": 30.0,
        },
        {"host": "192.168.1.8", "port": 5900, "password": None, "timeout": 10.0},
        {
            "host": "192.168.1.8",
            "port": 5900,
            "password": os.getenv("TCP_VNC_PASSWORD"),
            "timeout": 10.0,
        },
        {
            "host": "192.168.1.8",
            "port": 5900,
            "password": os.getenv("TCP_VNC_PASSWORD"),
            "timeout": 30.0,
        },
        {"host": "192.168.1.5", "port": 5901, "password": None, "timeout": 10.0},
        {"host": "192.168.1.5", "port": 5902, "password": None, "timeout": 10.0},
        {"host": "localhost", "port": 5900, "password": None, "timeout": 10.0},
    ]

    successful_configs = []

    for config in configs:
        success = test_connection(**config)
        if success:
            successful_configs.append(config)

    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)

    if successful_configs:
        print(f"✅ {len(successful_configs)} successful connection(s) found:")
        for config in successful_configs:
            pw_status = "with password" if config["password"] else "no password"
            print(f"   • {config['host']}:{config['port']} ({pw_status})")
    else:
        print("❌ No successful connections found")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Verify VNC server is running on 192.168.1.5")
        print("   2. Check the correct port number (try 5901, 5902, etc.)")
        print("   3. Ensure no firewall is blocking the connection")
        print("   4. Try setting VNC_PASSWORD environment variable")
        print("   5. Check if server requires specific authentication")
        print("   6. Verify server supports RFB protocol (standard VNC)")


if __name__ == "__main__":
    run_diagnostics()
