#!/usr/bin/env python3
"""
Omi Continuous Recorder - Session-based recording

Records continuously and auto-saves to separate files when silence
exceeds threshold. Each speaking session becomes its own WAV file.
Runs until killed with Ctrl+C.

Usage: python omi_continuous_recorder.py [device_uuid]
If no UUID provided, will auto-discover available Omi devices.
"""
import os, sys, glob, ctypes, asyncio, wave, struct
from datetime import datetime
from pathlib import Path
from collections import deque

# Accept device UUID as command line argument or auto-discover
DEVICE_UUID = sys.argv[1] if len(sys.argv) > 1 else None
AUDIO_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
SAMPLE_RATE = 16000

# Voice detection thresholds - hardcoded defaults that always work
SILENCE_THRESHOLD = 500      # Audio RMS below this = silence
SILENCE_DURATION = 3.0       # Seconds of silence before saving and starting new session
MIN_RECORDING_DURATION = 1.0 # Minimum seconds to save (ignore very short clips)
RECORDINGS_DIR = "omi_recordings"
DEVICE_DISCOVERY_TIMEOUT = 10.0

# Optionally load from config (failure uses defaults above)
try:
    sys.path.insert(0, str(Path(__file__).parent))
    import config
    SILENCE_THRESHOLD = config.get('recording', 'silence_threshold', SILENCE_THRESHOLD)
    SILENCE_DURATION = config.get('recording', 'silence_duration', SILENCE_DURATION)
    MIN_RECORDING_DURATION = config.get('recording', 'min_recording_duration', MIN_RECORDING_DURATION)
    RECORDINGS_DIR = config.get('directory', 'recordings_dir', RECORDINGS_DIR)
    DEVICE_DISCOVERY_TIMEOUT = config.get('device', 'discovery_timeout', DEVICE_DISCOVERY_TIMEOUT)
except Exception:
    pass  # Use defaults - config loading is optional

print("=" * 70)
print("Omi Continuous Recorder")
print("=" * 70)
print()

# Auto-discover device if UUID not provided
if not DEVICE_UUID:
    print("Scanning for Omi devices...")
    from bleak import BleakScanner

    async def discover_device():
        devices = await BleakScanner.discover(timeout=DEVICE_DISCOVERY_TIMEOUT)
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
        break

if not opus_path:
    print("Opus library not found! Install: brew install opus")
    sys.exit(1)

from bleak import BleakClient

# Setup Opus decoder
libopus = ctypes.CDLL(opus_path)
libopus.opus_decoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
libopus.opus_decoder_create.restype = ctypes.c_void_p
libopus.opus_decode.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int16), ctypes.c_int, ctypes.c_int]
libopus.opus_decode.restype = ctypes.c_int

error = ctypes.c_int()
opus_decoder = libopus.opus_decoder_create(SAMPLE_RATE, 1, ctypes.byref(error))
if error.value != 0:
    print("Failed to create Opus decoder")
    sys.exit(1)


class AutoRecorder:
    def __init__(self):
        self.is_recording = False
        self.decoded_pcm = []
        self.recording_count = 0
        self.output_dir = Path(RECORDINGS_DIR)
        self.output_dir.mkdir(exist_ok=True)
        self.running = True

        # Voice activity detection
        self.last_speech_time = 0
        self.recording_start_time = 0
        self.pre_buffer = deque(maxlen=10)  # Keep ~0.5s of audio before speech

        # Stats
        self.total_packets = 0

    def decode_opus(self, data: bytes) -> bytes:
        """Decode Opus packet to PCM"""
        if len(data) <= 3:
            return b''
        audio_data = data[3:]
        try:
            input_buffer = ctypes.cast(audio_data, ctypes.POINTER(ctypes.c_ubyte))
            pcm_buffer = (ctypes.c_int16 * 960)()
            samples = libopus.opus_decode(opus_decoder, input_buffer, len(audio_data),
                                          pcm_buffer, 960, 0)
            if samples > 0:
                return ctypes.string_at(pcm_buffer, samples * 2)
        except:
            pass
        return b''

    def get_audio_level(self, pcm_data: bytes) -> float:
        """Calculate RMS audio level from PCM data"""
        if len(pcm_data) < 2:
            return 0

        # Convert bytes to 16-bit samples
        samples = struct.unpack(f'<{len(pcm_data)//2}h', pcm_data)

        # Calculate RMS
        sum_squares = sum(s * s for s in samples)
        rms = (sum_squares / len(samples)) ** 0.5
        return rms

    def handle_audio(self, sender, data: bytearray):
        """Handle incoming audio packet"""
        self.total_packets += 1
        now = asyncio.get_event_loop().time()

        pcm = self.decode_opus(bytes(data))
        if not pcm:
            return

        level = self.get_audio_level(pcm)
        is_speech = level > SILENCE_THRESHOLD

        if is_speech:
            self.last_speech_time = now

        if not self.is_recording:
            # Keep pre-buffer
            self.pre_buffer.append(pcm)

            # Start recording on speech
            if is_speech:
                self.is_recording = True
                self.recording_start_time = now
                # Add pre-buffer to recording
                self.decoded_pcm = list(self.pre_buffer)
                self.pre_buffer.clear()
                print("\r" + " " * 70, end="\r")
                print("Recording started (speech detected)...", flush=True)

        else:
            # Currently recording
            self.decoded_pcm.append(pcm)

            # Check for silence timeout
            silence_duration = now - self.last_speech_time
            duration = now - self.recording_start_time

            if silence_duration > SILENCE_DURATION:
                # End recording session, save file
                print()
                self.save_recording()
                self.is_recording = False
                self.decoded_pcm = []
                print()
                print("Session saved. Waiting for next speech...", flush=True)
            else:
                # Show progress
                bar_len = min(int(level / 200), 30)
                bar = "" * bar_len
                status = "SPEECH" if is_speech else "silent"
                print(f"\r  Recording: {duration:.1f}s | {status:6} | {bar:<30} |", end="", flush=True)

    def save_recording(self):
        """Save the current recording to a WAV file"""
        if not self.decoded_pcm:
            return None

        total_bytes = sum(len(p) for p in self.decoded_pcm)
        duration = (total_bytes // 2) / SAMPLE_RATE

        if duration < MIN_RECORDING_DURATION:
            print(f"  Recording too short ({duration:.1f}s), discarding")
            return None

        self.recording_count += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        wav_file = self.output_dir / f"omi_auto_{timestamp}.wav"

        with wave.open(str(wav_file), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            for pcm in self.decoded_pcm:
                wav.writeframes(pcm)

        file_size = wav_file.stat().st_size
        print(f"  Saved: {wav_file.name} ({duration:.1f}s, {file_size/1024:.1f}KB)")
        return wav_file

    async def run(self):
        """Main loop"""
        print(f"Connecting to {DEVICE_UUID}...")

        try:
            async with BleakClient(DEVICE_UUID, timeout=20.0) as client:
                print("Connected!")
                print()
                print("=" * 70)
                print("CONTINUOUS RECORDING MODE")
                print("=" * 70)
                print()
                print("  - Recording starts when you speak")
                print(f"  - Auto-saves after {SILENCE_DURATION:.0f}s of silence")
                print("  - Then continues recording next session")
                print("  - Press Ctrl+C to stop")
                print()
                print("Waiting for speech...")

                await client.start_notify(AUDIO_CHAR_UUID, self.handle_audio)

                try:
                    while self.running:
                        await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    pass

                await client.stop_notify(AUDIO_CHAR_UUID)

                # Save any remaining recording
                if self.is_recording and self.decoded_pcm:
                    print()
                    self.save_recording()

                print()
                print("=" * 70)
                print(f"Session ended. {self.recording_count} recording(s) saved.")
                print(f"Total packets received: {self.total_packets}")
                print(f"Files in: {self.output_dir}/")
                print("=" * 70)

        except Exception as e:
            print(f"\nError: {e}")


async def main():
    recorder = AutoRecorder()
    await recorder.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nQuitting...")
