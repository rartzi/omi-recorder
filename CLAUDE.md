# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Omi Audio Recorder - A macOS tool to record audio from Omi wearable devices via Bluetooth Low Energy (BLE). Captures Opus-encoded audio packets from the device, decodes them in real-time, and saves as WAV files.

## Development Setup

**Option 1: Run from repository (for development)**
```bash
brew install opus
python3 -m venv venv && source venv/bin/activate
pip install bleak
```

**Option 2: Install to ~/omi-recorder/ (for end users)**
```bash
./setup_complete.sh
```

## Running the Scripts

```bash
source venv/bin/activate

# 1. Auto-discovery mode (Recommended)
# Continuous recorder will auto-discover your Omi device:
uv run src/omi_continuous_recorder.py

# 2. Manual device UUID mode (Optional)
# First discover your device:
uv run src/discover_omi.py

# Then run with the UUID:
uv run src/omi_continuous_recorder.py B6B3A95D-FAC4-E984-0E50-8924A6F36529

# 3. Other recording options:
uv run src/omi_recorder.py              # Basic: Ctrl+C to stop
uv run src/omi_recorder_enhanced.py     # Interactive: r/s/q controls
uv run src/omi_continuous_recorder.py   # Voice-activated: auto-saves on silence
```

**Key improvements:**
- No need to edit DEVICE_UUID in scripts anymore
- Auto-discovery scans for Omi devices at runtime
- Optional UUID can be passed as command-line argument
- All scripts in `src/` directory using `uv run`

Note: `setup_complete.sh` only copies `discover_omi.py` and `omi_recorder.py` to `~/omi-recorder/`. Other scripts must be run from the repository.

## Architecture

**discover_omi.py**: BLE scanner using `BleakScanner.discover()` - filters devices by name containing "omi".

**omi_recorder.py**: Basic recorder - connects via `BleakClient`, subscribes to audio characteristic notifications, decodes Opus via ctypes, saves WAV on interrupt.

**omi_recorder_enhanced.py**: Adds `RecorderState` enum (IDLE/RECORDING/STOPPED), threaded keyboard input, and multi-file session support.

**src/omi_continuous_recorder.py**: Voice-activated continuous recording with auto-discovery. Features:
- Auto-discovers Omi devices via BLE scan if no UUID provided
- Accepts optional UUID as command-line argument: `python omi_continuous_recorder.py [device_uuid]`
- Monitors audio stream, starts recording when speech detected
- Auto-saves to separate WAV files after configurable silence duration (default 3s)
- Ideal for capturing multiple ideas/notes in one session
- Real-time visual feedback showing recording progress and audio levels

**Key constants** (configurable in src/omi_continuous_recorder.py):
- `SILENCE_THRESHOLD`: 500 (RMS level below this = silence)
- `SILENCE_DURATION`: 3.0 seconds (silence before auto-save)
- `MIN_RECORDING_DURATION`: 1.0 second (minimum recording to save)
- `AUDIO_CHAR_UUID`: `19B10001-E8F2-537E-4F6C-D104768A1214`
- `SAMPLE_RATE`: 16000 Hz

## Audio Pipeline

```
BLE notification (bytearray)
  -> Skip 3-byte header (data[3:])
  -> opus_decode() via ctypes (960 samples/frame)
  -> Accumulate PCM bytes in list
  -> wave.open() write as 16-bit mono WAV
```

The Opus library is loaded dynamically from `/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib` or `/opt/homebrew/lib/libopus.0.dylib`.

## Dependencies

- macOS with Bluetooth (tested on Apple Silicon)
- Python 3.8+
- `bleak` - async BLE library
- `opus` - Homebrew package (`brew install opus`)

## BLE Protocol Reference

**Audio Streaming Service:** `19B10000-E8F2-537E-4F6C-D104768A1214`
- Audio Data: `19B10001-...` (notifications with 3-byte header + Opus)
- Codec Type: `19B10002-...` (read to get codec: 0=PCM16k, 20=Opus)

**Other Services:**
- Battery: `0000180F-...` (standard BLE battery service)
- Device Info: `0000180A-...` (manufacturer, model, firmware version)
