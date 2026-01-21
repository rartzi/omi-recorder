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

The `omi_continuous_recorder.py` implements simple voice activity detection:

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

### omi_continuous_recorder.py
```
main()
  └── AutoRecorder.run()
        ├── Load libopus via ctypes
        ├── Create Opus decoder
        ├── BleakClient.connect()
        ├── start_notify(AUDIO_CHAR_UUID, handle_audio)
        │     └── handle_audio:
        │           ├── Decode Opus to PCM
        │           ├── Calculate RMS level
        │           ├── Detect speech/silence
        │           ├── Manage recording state
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

The `omi_recorder_enhanced.py` additionally uses a background thread for keyboard input to allow non-blocking user interaction.

## Error Handling

- **BLE disconnection**: Scripts exit gracefully, saving any recorded audio
- **Opus decode errors**: Silent failures (logged), frame skipped
- **File write errors**: Exception raised, user notified

## Limitations

1. **macOS only**: Uses CoreBluetooth via pyobjc (bleak backend)
2. **Single device**: One Omi connection at a time
3. **No offline storage**: Consumer Omi devices don't expose storage service
4. **Real-time only**: Audio must be captured while connected
