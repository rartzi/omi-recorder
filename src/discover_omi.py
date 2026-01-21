#!/usr/bin/env python3
"""Omi Device Discovery - Finds your Omi device's Bluetooth UUID"""
import asyncio
from bleak import BleakScanner

print("=" * 70)
print("Omi Device Discovery")
print("=" * 70)
print()
print("Scanning for Bluetooth devices...")
print("(This takes about 10 seconds)")
print()

async def discover():
    devices = await BleakScanner.discover(timeout=10.0)
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
        print("1. Copy the UUID above")
        print("2. Edit src/omi_recorder.py")
        print("3. Set DEVICE_UUID = \"YOUR-UUID-HERE\"")
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
