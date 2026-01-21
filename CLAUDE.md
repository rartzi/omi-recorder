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

# 1. Discover Omi device UUID
python discover_omi.py

# 2. Edit DEVICE_UUID in the script you want to use (line 7 or 13)

# 3. Recording options:
python omi_recorder.py              # Basic: Ctrl+C to stop
python omi_recorder_enhanced.py     # Interactive: r/s/q controls
python omi_continuous_recorder.py   # Voice-activated: auto-saves on silence
```

Note: `setup_complete.sh` only copies `discover_omi.py` and `omi_recorder.py` to `~/omi-recorder/`. Other scripts must be run from the repository.

## Architecture

**discover_omi.py**: BLE scanner using `BleakScanner.discover()` - filters devices by name containing "omi".

**omi_recorder.py**: Basic recorder - connects via `BleakClient`, subscribes to audio characteristic notifications, decodes Opus via ctypes, saves WAV on interrupt.

**omi_recorder_enhanced.py**: Adds `RecorderState` enum (IDLE/RECORDING/STOPPED), threaded keyboard input, and multi-file session support.

**omi_continuous_recorder.py**: Voice-activated continuous recording. Monitors audio stream, starts recording when speech detected, auto-saves to separate WAV files after configurable silence duration (default 3s). Ideal for capturing multiple ideas/notes in one session.

**Key constants** (in recorder scripts):
- `DEVICE_UUID`: Your Omi's Bluetooth UUID (from discover_omi.py)
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
