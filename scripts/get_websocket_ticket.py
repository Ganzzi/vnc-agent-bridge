#!/usr/bin/env python3
"""
Get a fresh WebSocket VNC ticket from Proxmox API.

Usage:
    python get_websocket_ticket.py
"""

import os
import requests
import json
from pathlib import Path
import dotenv

dotenv.load_dotenv()

# Configuration
PROXMOX_HOST = os.getenv("PROXMOX_HOST", "192.168.1.224")
PROXMOX_PORT = int(os.getenv("PROXMOX_PORT", "8006"))
PROXMOX_NODE = os.getenv("PROXMOX_NODE", "pve")
PROXMOX_VMID = os.getenv("PROXMOX_VMID", "100")
PROXMOX_TOKEN = os.getenv("PROXMOX_API_TOKEN")

if not PROXMOX_TOKEN:
    print("Error: PROXMOX_API_TOKEN not set in .env file")
    print("Expected format: test@pam!test=91eb1dff-12ba-4c53-9528-1a4d18883c98")
    exit(1)

# Construct API endpoint
url = f"https://{PROXMOX_HOST}:{PROXMOX_PORT}/api2/json/nodes/{PROXMOX_NODE}/qemu/{PROXMOX_VMID}/vncproxy"

headers = {
    "Authorization": f"PVEAPIToken={PROXMOX_TOKEN}",
    "Content-Type": "application/json",
}

payload = {
    "generate-password": 0,
    "websocket": 1,
}

print(f"Requesting WebSocket VNC ticket from Proxmox...")
print(f"Endpoint: {url}")

try:
    # Disable SSL verification for self-signed certificates
    response = requests.post(url, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        data = response.json()
        ticket = data.get("data", {}).get("ticket")
        port = data.get("data", {}).get("port")

        if ticket:
            print("\n✓ Successfully retrieved WebSocket ticket!")
            print(f"\nUpdate your .env file with:")
            print(f"VNC_WEBSOCKET_TICKET={ticket}")
            print(f"\nTicket details:")
            print(f"  Ticket: {ticket[:50]}...")
            print(f"  Port: {port}")
            print(f"  Expires in: ~30 seconds")

            # Also update .env file automatically
            env_file = Path(".env")
            if env_file.exists():
                content = env_file.read_text()
                # Replace or add the ticket
                if "VNC_WEBSOCKET_TICKET=" in content:
                    import re

                    content = re.sub(
                        r"VNC_WEBSOCKET_TICKET=.*",
                        f"VNC_WEBSOCKET_TICKET={ticket}",
                        content,
                    )
                else:
                    content += f"\nVNC_WEBSOCKET_TICKET={ticket}\n"

                env_file.write_text(content)
                print(f"\n✓ Updated .env file automatically")

        else:
            print(f"\n✗ Error: No ticket in response")
            print(f"Response: {data}")
    else:
        print(f"\n✗ Error: HTTP {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check PROXMOX_API_TOKEN is correct in .env")
    print("  2. Verify Proxmox server is accessible")
    print("  3. Ensure VM exists (PROXMOX_NODE and PROXMOX_VMID are correct)")
