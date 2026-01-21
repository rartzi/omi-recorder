#!/usr/bin/env python3
"""Omi Device Discovery - Finds your Omi device's Bluetooth UUID"""
import sys
import asyncio
from pathlib import Path
from bleak import BleakScanner

# Hardcoded default that always works
DEVICE_DISCOVERY_TIMEOUT = 10.0

# Optionally load from config (failure uses default above)
try:
    sys.path.insert(0, str(Path(__file__).parent))
    import config
    DEVICE_DISCOVERY_TIMEOUT = config.get('device', 'discovery_timeout', DEVICE_DISCOVERY_TIMEOUT)
except Exception:
    pass  # Use default - config loading is optional

print("=" * 70)
print("Omi Device Discovery")
print("=" * 70)
print()
print("Scanning for Bluetooth devices...")
print(f"(This takes about {DEVICE_DISCOVERY_TIMEOUT:.0f} seconds)")
print()

async def discover():
    devices = await BleakScanner.discover(timeout=DEVICE_DISCOVERY_TIMEOUT)
    omi_devices = [d for d in devices if d.name and "omi" in d.name.lower()]
    
    print("=" * 70)
    print("Results")
    print("=" * 70)
    print()
    
    if omi_devices:
        print("✅ Found Omi device(s):")
        print()
        for device in omi_devices:
            print(f"  Name: {device.name}")
            print(f"  UUID: {device.address}")
            if hasattr(device, 'rssi') and device.rssi:
                print(f"  Signal: {device.rssi} dBm")
            print()
        print("=" * 70)
        print("Next Steps")
        print("=" * 70)
        print()
        print("1. Run the recorder (auto-discovery enabled):")
        print("   uv run src/omi_continuous_recorder.py")
        print()
        print("2. (Optional) Pass UUID manually:")
        print("   uv run src/omi_continuous_recorder.py <UUID>")
        print()
    else:
        print("⚠️  No Omi devices found")
        print()
        print("Troubleshooting:")
        print("  - Make sure your Omi device is powered on")
        print("  - Check if Bluetooth is enabled on your Mac")
        print("  - Try moving the device closer")
        print()
    print("=" * 70)

try:
    asyncio.run(discover())
except KeyboardInterrupt:
    print("\n\nScan cancelled")
except Exception as e:
    print(f"\n✗ Error: {e}")
