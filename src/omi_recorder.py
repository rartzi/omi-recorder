#!/usr/bin/env python3
"""Omi Audio Recorder - Records audio from Omi device to WAV files"""
import os, sys, glob, ctypes, asyncio, wave, struct
from datetime import datetime
from pathlib import Path

# Accept device UUID as command line argument or auto-discover
DEVICE_UUID = sys.argv[1] if len(sys.argv) > 1 else None
AUDIO_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
SAMPLE_RATE = 16000

print("=" * 70)
print("🎤 Omi Audio Recorder")
print("=" * 70)
print()

# Auto-discover device if UUID not provided
if not DEVICE_UUID:
    print("Scanning for Omi devices...")
    from bleak import BleakScanner

    async def discover_device():
        devices = await BleakScanner.discover(timeout=10.0)
        omi_devices = [d for d in devices if d.name and "omi" in d.name.lower()]
        if not omi_devices:
            print("✗ No Omi devices found")
            print("Make sure your Omi is powered on and Bluetooth is enabled")
            sys.exit(1)
        if len(omi_devices) == 1:
            print(f"✓ Found Omi device: {omi_devices[0].name}")
            return omi_devices[0].address
        else:
            print(f"✓ Found {len(omi_devices)} Omi device(s):")
            for i, d in enumerate(omi_devices, 1):
                print(f"  {i}. {d.name} ({d.address})")
            choice = input("Select device (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(omi_devices):
                    return omi_devices[idx].address
            except:
                pass
            print("Invalid selection")
            sys.exit(1)

    DEVICE_UUID = asyncio.run(discover_device())
    print()

# Load Opus
opus_path = None
for pattern in ["/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib",
                "/opt/homebrew/lib/libopus.0.dylib"]:
    matches = glob.glob(pattern)
    if matches:
        opus_path = matches[0]
        ctypes.CDLL(opus_path)
        os.environ['OPUS_LIBRARY'] = opus_path
        break

if not opus_path:
    print("✗ Opus library not found!")
    print("  Install: brew install opus")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bleak import BleakClient

libopus = ctypes.CDLL(opus_path)
libopus.opus_decoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
libopus.opus_decoder_create.restype = ctypes.c_void_p
libopus.opus_decode.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.c_int]
libopus.opus_decode.restype = ctypes.c_int

error = ctypes.c_int()
opus_decoder = libopus.opus_decoder_create(SAMPLE_RATE, 1, ctypes.byref(error))
if error.value != 0:
    print(f"✗ Failed to create Opus decoder")
    sys.exit(1)

output_dir = Path("omi_recordings")
output_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
wav_file = output_dir / f"omi_{timestamp}.wav"

print(f"✓ Ready to record")
print(f"  Output: {wav_file}")
print()
print("Instructions:")
print("  1. Start recording on your Omi device")
print("  2. Press Enter to begin capture")
print("  3. Speak into your Omi")
print("  4. Press Ctrl+C when done")
print()
input("Press Enter to start...")

decoded_pcm = []
notification_count = 0

def process_audio(sender, data: bytearray):
    global notification_count
    notification_count += 1
    data_bytes = bytes(data)
    if len(data_bytes) < 3:
        return
    audio_data = data_bytes[3:]
    try:
        input_buffer = ctypes.cast(audio_data, ctypes.POINTER(ctypes.c_ubyte))
        frame_size = 960
        pcm_buffer = (ctypes.c_int16 * frame_size)()
        samples = libopus.opus_decode(opus_decoder, input_buffer, len(audio_data),
                                       pcm_buffer, frame_size, 0)
        if samples > 0:
            decoded_pcm.append(ctypes.string_at(pcm_buffer, samples * 2))
    except:
        pass
    if notification_count % 100 == 0:
        duration = sum(len(p) for p in decoded_pcm) // 2 / SAMPLE_RATE
        print(f"  Recording: {duration:.1f}s | {len(decoded_pcm)} packets", end='\r')

async def record():
    print("\nConnecting to Omi...")
    try:
        async with BleakClient(DEVICE_UUID, timeout=20.0) as client:
            print("✓ Connected\n")
            await client.start_notify(AUDIO_CHAR_UUID, process_audio)
            print("🔴 Recording... (Press Ctrl+C to stop)\n")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\n✓ Stopped")
            await client.stop_notify(AUDIO_CHAR_UUID)
    except Exception as e:
        print(f"\n✗ Error: {e}")

try:
    asyncio.run(record())
except KeyboardInterrupt:
    pass

print("\nSaving audio...")
if decoded_pcm:
    try:
        total_bytes = sum(len(p) for p in decoded_pcm)
        duration = (total_bytes // 2) / SAMPLE_RATE
        with wave.open(str(wav_file), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            for pcm in decoded_pcm:
                wav.writeframes(pcm)
        file_size = wav_file.stat().st_size
        print()
        print("=" * 70)
        print("✅ Recording saved successfully!")
        print("=" * 70)
        print()
        print(f"  File: {wav_file}")
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Size: {file_size/1024:.1f} KB")
        print()
        print("Play it:")
        print(f"  open {wav_file}")
        print()
    except Exception as e:
        print(f"✗ Error saving: {e}")
else:
    print("⚠ No audio captured")
print("=" * 70)
