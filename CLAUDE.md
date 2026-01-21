# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Omi Audio Recorder - A macOS tool to record audio from Omi wearable devices via Bluetooth Low Energy (BLE). Captures Opus-encoded audio packets from the device, decodes them in real-time, and saves as WAV files.

## Setup and Installation

```bash
# Run the setup script (installs to ~/omi-recorder/)
chmod +x setup_complete.sh
./setup_complete.sh
```

The setup script:
- Copies Python scripts to `~/omi-recorder/`
- Installs Opus codec via Homebrew
- Creates Python virtual environment with `bleak` dependency

## Running the Scripts

```bash
cd ~/omi-recorder
source venv/bin/activate

# Discover Omi device UUID
python discover_omi.py

# Record audio (set DEVICE_UUID first)
python omi_recorder.py

# Enhanced recorder with start/stop controls
python omi_recorder_enhanced.py
```

## Architecture

**discover_omi.py**: BLE scanner that finds Omi devices and displays their UUIDs using `bleak.BleakScanner`.

**omi_recorder.py**: Basic recorder - connects to device, receives Opus packets, decodes via libopus (ctypes), saves to WAV on Ctrl+C.

**omi_recorder_enhanced.py**: Interactive version with state machine (IDLE/RECORDING/STOPPED), keyboard controls (r/s/q), and multi-recording sessions.

**Key constants** (must be configured):
- `DEVICE_UUID`: Set to your Omi device's Bluetooth UUID
- `AUDIO_CHAR_UUID`: `19B10001-E8F2-537E-4F6C-D104768A1214` (Omi audio characteristic)
- `SAMPLE_RATE`: 16kHz

**Audio pipeline**: BLE notification -> Skip 3-byte header -> Opus decode (960 samples/frame) -> Accumulate PCM -> Write WAV

## Dependencies

- Python 3.8+
- `bleak` (BLE library)
- `opus` (Homebrew: `brew install opus`)
- macOS with Bluetooth
