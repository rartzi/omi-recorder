#!/usr/bin/env python3
"""Omi Audio Recorder Enhanced - Graceful start/stop controls with multiple recordings"""
import os, sys, glob, ctypes, asyncio, wave, threading
from datetime import datetime
from pathlib import Path
from enum import Enum

# Accept device UUID as command line argument or auto-discover
DEVICE_UUID = sys.argv[1] if len(sys.argv) > 1 else None
AUDIO_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
SAMPLE_RATE = 16000

class RecorderState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    STOPPED = "stopped"

class EnhancedRecorder:
    def __init__(self):
        self.state = RecorderState.IDLE
        self.decoded_pcm = []
        self.notification_count = 0
        self.recording_number = 0
        self.output_dir = Path("omi_recordings")
        self.output_dir.mkdir(exist_ok=True)
        self.session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_recording_start = None
        self.stop_event = asyncio.Event()
        self.start_event = asyncio.Event()
        self.quit_event = asyncio.Event()
        self.saved_files = []

        # Load Opus
        self.opus_decoder = self._load_opus()

    def _load_opus(self):
        """Load Opus library and create decoder"""
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

        self.libopus = libopus
        return opus_decoder

    def process_audio(self, sender, data: bytearray):
        """Process incoming audio data (only when recording)"""
        if self.state != RecorderState.RECORDING:
            return

        self.notification_count += 1
        data_bytes = bytes(data)
        if len(data_bytes) < 3:
            return
        audio_data = data_bytes[3:]

        try:
            input_buffer = ctypes.cast(audio_data, ctypes.POINTER(ctypes.c_ubyte))
            frame_size = 960
            pcm_buffer = (ctypes.c_int16 * frame_size)()
            samples = self.libopus.opus_decode(
                self.opus_decoder, input_buffer, len(audio_data),
                pcm_buffer, frame_size, 0
            )
            if samples > 0:
                self.decoded_pcm.append(ctypes.string_at(pcm_buffer, samples * 2))
        except:
            pass

        if self.notification_count % 100 == 0:
            duration = sum(len(p) for p in self.decoded_pcm) // 2 / SAMPLE_RATE
            print(f"\r🔴 Recording... ({duration:.1f}s)", end='', flush=True)

    def start_recording(self):
        """Start a new recording"""
        if self.state == RecorderState.RECORDING:
            print("\r⚠ Already recording!                                    ")
            return

        self.state = RecorderState.RECORDING
        self.decoded_pcm = []
        self.notification_count = 0
        self.current_recording_start = datetime.now()
        print("\r🔴 Recording... (0.0s)                                    ", flush=True)

    def stop_recording(self):
        """Stop current recording and save"""
        if self.state != RecorderState.RECORDING:
            print("\r⚠ Not recording!                                    ")
            return

        self.state = RecorderState.STOPPED
        print("\r                                                            ", end='')
        print("\r✓ Stopped. Saving...", flush=True)

        if self.decoded_pcm:
            self.recording_number += 1
            filename = f"omi_{self.session_timestamp}_{self.recording_number:03d}.wav"
            wav_file = self.output_dir / filename

            try:
                total_bytes = sum(len(p) for p in self.decoded_pcm)
                duration = (total_bytes // 2) / SAMPLE_RATE

                with wave.open(str(wav_file), 'wb') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(SAMPLE_RATE)
                    for pcm in self.decoded_pcm:
                        wav.writeframes(pcm)

                file_size = wav_file.stat().st_size
                self.saved_files.append((wav_file, duration, file_size))
                print(f"✓ Saved: {filename} ({duration:.1f}s, {file_size/1024:.1f} KB)")
            except Exception as e:
                print(f"✗ Error saving: {e}")
        else:
            print("⚠ No audio captured")

        self.state = RecorderState.IDLE
        self.show_prompt()

    def show_prompt(self):
        """Show command prompt"""
        print("\nCommands: [r]ecord | [s]top | [q]uit")
        print("> ", end='', flush=True)

    async def keyboard_listener(self):
        """Listen for keyboard commands in separate thread"""
        def input_thread():
            while not self.quit_event.is_set():
                try:
                    cmd = sys.stdin.read(1).lower()

                    if cmd == 'r':
                        asyncio.run_coroutine_threadsafe(
                            self._handle_start_command(),
                            self.loop
                        )
                    elif cmd == 's':
                        asyncio.run_coroutine_threadsafe(
                            self._handle_stop_command(),
                            self.loop
                        )
                    elif cmd == 'q':
                        asyncio.run_coroutine_threadsafe(
                            self._handle_quit_command(),
                            self.loop
                        )
                except:
                    break

        thread = threading.Thread(target=input_thread, daemon=True)
        thread.start()

    async def _handle_start_command(self):
        """Handle 'r' command"""
        self.start_recording()

    async def _handle_stop_command(self):
        """Handle 's' command"""
        self.stop_recording()

    async def _handle_quit_command(self):
        """Handle 'q' command"""
        print("\r                                                            ")
        print("\r👋 Quitting...", flush=True)

        # Auto-save if currently recording
        if self.state == RecorderState.RECORDING:
            self.stop_recording()

        self.quit_event.set()

    async def run(self):
        """Main recording loop"""
        from bleak import BleakClient

        print("=" * 70)
        print("🎤 Omi Audio Recorder Enhanced")
        print("=" * 70)
        print()
        print("Connecting to Omi...")

        try:
            async with BleakClient(DEVICE_UUID, timeout=20.0) as client:
                print("✓ Connected\n")

                # Start audio notifications
                await client.start_notify(AUDIO_CHAR_UUID, self.process_audio)

                # Store loop reference for keyboard thread
                self.loop = asyncio.get_event_loop()

                # Start keyboard listener
                await self.keyboard_listener()

                # Show initial prompt
                self.show_prompt()

                # Wait until quit
                while not self.quit_event.is_set():
                    await asyncio.sleep(0.1)

                # Stop notifications
                await client.stop_notify(AUDIO_CHAR_UUID)

                # Show summary
                print()
                print("=" * 70)
                print("✅ Session Ended")
                print("=" * 70)
                print()
                if self.saved_files:
                    print(f"Saved {len(self.saved_files)} recording(s):")
                    for wav_file, duration, file_size in self.saved_files:
                        print(f"  • {wav_file.name} ({duration:.1f}s, {file_size/1024:.1f} KB)")
                    print()
                    print("Play recordings:")
                    print(f"  open {self.output_dir}")
                else:
                    print("No recordings saved.")
                print()
                print("=" * 70)

        except Exception as e:
            print(f"\n✗ Error: {e}")

def main():
    global DEVICE_UUID

    print("=" * 70)
    print("🎤 Omi Audio Recorder Enhanced")
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

    recorder = EnhancedRecorder()

    try:
        asyncio.run(recorder.run())
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by Ctrl+C")
        print("💡 Tip: Use 'q' to quit gracefully next time!")

if __name__ == "__main__":
    main()
