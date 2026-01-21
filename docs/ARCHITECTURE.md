# Architecture

This document describes the technical architecture of the Omi Audio Recorder.

## Overview

```
┌─────────────────┐     BLE      ┌──────────────────┐
│   Omi Device    │─────────────▶│  Python Scripts  │
│  (Wearable)     │   Opus       │                  │
└─────────────────┘   Audio      └────────┬─────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │   libopus        │
                                 │   (Decoder)      │
                                 └────────┬─────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │   WAV Files      │
                                 │   (PCM 16-bit)   │
                                 └──────────────────┘
```

## Components

### 1. Omi Device

The Omi wearable device captures audio through its built-in microphone and streams it via Bluetooth Low Energy (BLE).

**Specifications:**
- Model: Omi CV 1
- Manufacturer: Based Hardware
- Audio Codec: Opus (16kHz mono)
- Protocol: BLE GATT notifications

### 2. BLE Communication Layer

Uses the `bleak` Python library for cross-platform BLE communication.

**Key UUIDs:**
| Service/Characteristic | UUID |
|------------------------|------|
| Audio Service | `19B10000-E8F2-537E-4F6C-D104768A1214` |
| Audio Data | `19B10001-E8F2-537E-4F6C-D104768A1214` |
| Codec Type | `19B10002-E8F2-537E-4F6C-D104768A1214` |
| Battery Service | `0000180F-0000-1000-8000-00805F9B34FB` |
| Device Info | `0000180A-0000-1000-8000-00805F9B34FB` |

### 3. Audio Pipeline

```
BLE Notification
       │
       ▼
┌─────────────────────────────────────────┐
│  Raw Packet (75-100 bytes typical)      │
│  ┌─────────┬─────────┬────────────────┐ │
│  │ Pkt Num │  Index  │   Opus Data    │ │
│  │ 2 bytes │ 1 byte  │   Variable     │ │
│  └─────────┴─────────┴────────────────┘ │
└─────────────────────────────────────────┘
       │
       │ Strip 3-byte header
       ▼
┌─────────────────────────────────────────┐
│  Opus Decoder (libopus via ctypes)      │
│  - Sample rate: 16000 Hz                │
│  - Channels: 1 (mono)                   │
│  - Frame size: 960 samples              │
└─────────────────────────────────────────┘
       │
       │ Decode to PCM
       ▼
┌─────────────────────────────────────────┐
│  PCM Buffer                             │
│  - 16-bit signed integers               │
│  - Little-endian byte order             │
│  - 960 samples per frame (~60ms)        │
└─────────────────────────────────────────┘
       │
       │ Accumulate frames
       ▼
┌─────────────────────────────────────────┐
│  WAV File Output                        │
│  - Format: PCM 16-bit mono              │
│  - Sample rate: 16000 Hz                │
│  - ~32 KB per second of audio           │
└─────────────────────────────────────────┘
```

### 4. Voice Activity Detection (Continuous Recorder)

The `src/omi_continuous_recorder.py` implements simple voice activity detection:

```
Audio Frame (PCM)
       │
       ▼
┌─────────────────────────────────────────┐
│  RMS Calculation                        │
│  rms = sqrt(sum(sample²) / n)           │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Threshold Comparison                   │
│  SILENCE_THRESHOLD = 500                │
│                                         │
│  if rms > threshold:                    │
│      state = SPEECH                     │
│  else:                                  │
│      state = SILENCE                    │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Session Management                     │
│                                         │
│  - Start recording on first speech      │
│  - Continue while speech or short       │
│    silence detected                     │
│  - Save file after SILENCE_DURATION     │
│    seconds of continuous silence        │
│  - Reset and wait for next speech       │
└─────────────────────────────────────────┘
```

## Script Architecture

### discover_omi.py
```
main()
  └── BleakScanner.discover()
        └── Filter devices by name "omi"
              └── Display UUID for configuration
```

### omi_recorder.py
```
main()
  ├── Load libopus via ctypes
  ├── Create Opus decoder
  └── asyncio.run(record())
        ├── BleakClient.connect()
        ├── start_notify(AUDIO_CHAR_UUID, callback)
        │     └── callback: decode Opus → append to buffer
        ├── Wait for Ctrl+C
        └── Save buffer to WAV file
```

### src/omi_continuous_recorder.py

**Features:**
- Auto-discovery of Omi devices (no hardcoded UUID needed)
- Optional command-line UUID argument: `python omi_continuous_recorder.py [device_uuid]`
- Dynamic device selection if multiple Omi devices found
- Real-time visual feedback with progress bar

```
main()
  ├── Check command-line args for UUID
  │     └── if not provided: auto-discover
  │           ├── BleakScanner.discover()
  │           ├── Filter devices by "omi" name
  │           ├── If single device: connect to it
  │           └── If multiple devices: prompt user to select
  ├── Load libopus via ctypes
  ├── Create Opus decoder
  └── AutoRecorder.run()
        ├── BleakClient.connect(DEVICE_UUID)
        ├── start_notify(AUDIO_CHAR_UUID, handle_audio)
        │     └── handle_audio:
        │           ├── Decode Opus to PCM
        │           ├── Calculate RMS level
        │           ├── Detect speech/silence
        │           ├── Manage recording state
        │           ├── Show real-time progress bar
        │           └── Auto-save on silence timeout
        └── Wait for Ctrl+C
              └── Save any remaining audio
```

## Data Flow Rates

| Stage | Data Rate |
|-------|-----------|
| BLE Packets | ~50 packets/sec |
| Raw Opus | ~4-5 KB/sec |
| Decoded PCM | ~32 KB/sec |
| WAV File | ~32 KB/sec + 44 byte header |

## Threading Model

All scripts use Python's `asyncio` for concurrent operations:

- **Main thread**: asyncio event loop
- **BLE callbacks**: Executed in event loop context
- **File I/O**: Synchronous (acceptable for WAV writes)

The `src/omi_recorder_enhanced.py` additionally uses a background thread for keyboard input to allow non-blocking user interaction.

## Error Handling

- **BLE disconnection**: Scripts exit gracefully, saving any recorded audio
- **Opus decode errors**: Silent failures (logged), frame skipped
- **File write errors**: Exception raised, user notified

## Transcription Pipeline

```
WAV File
       │
       ▼
┌─────────────────────────────────────────┐
│  Audio Metadata Extraction              │
│  - Extract timestamp from filename      │
│  - Read duration & sample rate          │
│  - Get file size                        │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Whisper Transcription                  │
│  - Load model from cache or download    │
│  - Convert WAV to text                  │
│  - Supports offline after first run     │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Markdown Generation                    │
│  - Combine metadata + transcription     │
│  - Format as markdown                   │
│  - Add footer and timestamps            │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Output: .md File                       │
│  Example: omi_auto_20260120_143022.md   │
│  - Metadata section (YAML-like)         │
│  - Transcription text                   │
└─────────────────────────────────────────┘
```

### Transcription Scripts

**src/transcribe.py** - Core transcription module

```
Main Functions:
  transcribe_audio()      - Whisper transcription
  generate_markdown()     - Create markdown with metadata
  save_markdown()         - Write .md file
  batch_transcribe()      - Process all WAV files
  transcribe_file()       - Single file wrapper
  get_audio_metadata()    - Extract WAV metadata
```

**src/batch_transcribe.py** - Standalone CLI script

```
Features:
  - CLI argument parsing (--dir, --model, --force)
  - Directory scanning for WAV files
  - Progress reporting
  - Error handling
  - Summary statistics
```

### Whisper Model Caching

```
First Run (with internet):
  1. User runs: uv run src/batch_transcribe.py
  2. Script checks ~/.cache/whisper/base.pt
  3. Model not found, downloads from Hugging Face (~140MB)
  4. Model cached for future use
  5. Transcription begins

Subsequent Runs (with or without internet):
  1. User runs: uv run src/batch_transcribe.py
  2. Script finds model at ~/.cache/whisper/base.pt
  3. Loads from cache (offline capable)
  4. Transcription begins immediately
```

### Batch Processing Flow

```
uv run src/batch_transcribe.py [--options]
       │
       ├─ Parse arguments
       │
       ├─ Scan omi_recordings/ for *.wav files
       │
       ├─ For each WAV file:
       │   ├─ Check if .md exists (skip if exists, unless --force)
       │   ├─ Transcribe using Whisper
       │   ├─ Generate markdown with metadata
       │   ├─ Save .md file
       │   └─ Update statistics
       │
       └─ Print summary report
```

### Performance Characteristics

| Stage | Time | Model Dependency |
|-------|------|------------------|
| Model Load | ~2-5s | First run: download, subsequent: cache |
| Per Minute Audio | ~5-10s | base model on Apple Silicon |
| Metadata Extraction | <100ms | None |
| Markdown Generation | <100ms | None |
| File I/O | <100ms | None |

**Notes:**
- Larger models are slower but more accurate
- Apple Silicon (M1/M2/M3) faster than Intel
- First run includes model download (~140MB base model)
- Subsequent runs use cached model (offline capable)

## Limitations

1. **macOS only**: Uses CoreBluetooth via pyobjc (bleak backend)
2. **Single device**: One Omi connection at a time
3. **No offline storage**: Consumer Omi devices don't expose storage service
4. **Real-time only**: Audio must be captured while connected
5. **Transcription**: Requires internet for first model download (then offline-capable)
