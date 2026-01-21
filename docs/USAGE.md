# Usage Guide

This guide explains how to use the Omi Audio Recorder scripts.

## Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run the continuous recorder (auto-discovers your device)
uv run src/omi_continuous_recorder.py

# That's it! No configuration needed.
```

**Note:** All recorders now support auto-discovery. No need to manually find or edit device UUIDs.

## Available Scripts

| Script | Best For |
|--------|----------|
| `src/omi_continuous_recorder.py` | Recording multiple ideas/notes automatically |
| `src/omi_recorder.py` | Simple one-shot recordings |
| `src/omi_recorder_enhanced.py` | Manual control with keyboard shortcuts |

---

## Continuous Recorder (Recommended)

**Purpose:** Automatically records and saves separate audio files based on voice activity. Perfect for capturing multiple ideas or notes in one session.

### How It Works

1. Connects to your Omi device
2. Listens for speech
3. Starts recording when you speak
4. Saves to a new file after 3 seconds of silence
5. Waits for the next speech
6. Repeats until you press Ctrl+C

### Usage

```bash
uv run src/omi_continuous_recorder.py
```

### Example Session

```
======================================================================
Omi Continuous Recorder
======================================================================

Connecting to 93826AE8-AE8C-2AE4-D717-0978E4817739...
Connected!

======================================================================
CONTINUOUS RECORDING MODE
======================================================================

  - Recording starts when you speak
  - Auto-saves after 3s of silence
  - Then continues recording next session
  - Press Ctrl+C to stop

Waiting for speech...
Recording started (speech detected)...
  Recording: 5.2s | SPEECH |

  Saved: omi_auto_20260120_143022.wav (8.5s, 265.3KB)

Session saved. Waiting for next speech...
Recording started (speech detected)...
  Recording: 3.1s | SPEECH |

  Saved: omi_auto_20260120_143035.wav (6.4s, 199.8KB)

Session saved. Waiting for next speech...
^C

Quitting...
```

### Configuration

Edit these values at the top of `src/omi_continuous_recorder.py`:

```python
SILENCE_THRESHOLD = 500   # Lower = more sensitive to quiet speech
SILENCE_DURATION = 3.0    # Seconds of silence before saving
MIN_RECORDING_DURATION = 1.0  # Ignore recordings shorter than this
```

### Output Files

Files are saved to `omi_recordings/` with timestamps:
```
omi_recordings/
├── omi_auto_20260120_143022.wav
├── omi_auto_20260120_143035.wav
└── omi_auto_20260120_143048.wav
```

---

## Basic Recorder

**Purpose:** Simple recording that saves when you press Ctrl+C.

### Usage

```bash
uv run src/omi_recorder.py
```

### Workflow

1. Start the script
2. Press Enter when prompted
3. Speak into your Omi
4. Press Ctrl+C to stop and save

### Example

```
======================================================================
Omi Audio Recorder
======================================================================

Ready to record
  Output: omi_recordings/omi_20260120_143500.wav

Instructions:
  1. Start recording on your Omi device
  2. Press Enter to begin capture
  3. Speak into your Omi
  4. Press Ctrl+C when done

Press Enter to start...

Connecting to Omi...
Connected

Recording... (Press Ctrl+C to stop)

^C

Stopped

Saving audio...

======================================================================
Recording saved successfully!
======================================================================

  File: omi_recordings/omi_20260120_143500.wav
  Duration: 12.5 seconds
  Size: 390.2 KB

Play it:
  open omi_recordings/omi_20260120_143500.wav
```

---

## Enhanced Recorder

**Purpose:** Manual control with keyboard shortcuts for multiple recordings in one session.

### Usage

```bash
uv run src/omi_recorder_enhanced.py
```

### Controls

| Key | Action |
|-----|--------|
| `r` | Start recording |
| `s` | Stop recording and save |
| `q` | Quit the application |

### Example

```
======================================================================
Omi Audio Recorder Enhanced
======================================================================

Connecting to Omi...
Connected

Commands: [r]ecord | [s]top | [q]uit
> r
Recording... (0.0s)
Recording... (5.2s)
> s
Saved: omi_20260120_143600_001.wav (5.2s, 162.5KB)

Commands: [r]ecord | [s]top | [q]uit
> r
Recording... (0.0s)
Recording... (3.8s)
> s
Saved: omi_20260120_143600_002.wav (3.8s, 118.6KB)

Commands: [r]ecord | [s]top | [q]uit
> q

======================================================================
Session Ended
======================================================================

Saved 2 recording(s):
  • omi_20260120_143600_001.wav (5.2s, 162.5KB)
  • omi_20260120_143600_002.wav (3.8s, 118.6KB)

Play recordings:
  open omi_recordings
```

---

## Device Discovery (Optional)

**Purpose:** Manually find your Omi device's Bluetooth UUID (useful for manual recording or troubleshooting).

### Usage

```bash
uv run src/discover_omi.py
```

### Example Output

```
======================================================================
Omi Device Discovery
======================================================================

Scanning for Bluetooth devices...
(This takes about 10 seconds)

======================================================================
Results
======================================================================

Found Omi device(s):

  Name: Omi
  UUID: 93826AE8-AE8C-2AE4-D717-0978E4817739
  Signal: -50 dBm

======================================================================
Next Steps
======================================================================

1. Run the recorder (auto-discovery enabled):
   uv run src/omi_continuous_recorder.py

2. (Optional) Pass UUID manually:
   uv run src/omi_continuous_recorder.py 93826AE8-AE8C-2AE4-D717-0978E4817739
```

**Note:** You don't need to run discovery unless you want to manually specify a device or if auto-discovery fails.

---

## Playing Recordings

### macOS Quick Play

```bash
# Play a specific file
open omi_recordings/omi_auto_20260120_143022.wav

# Open folder in Finder
open omi_recordings/

# Play with afplay (command line)
afplay omi_recordings/omi_auto_20260120_143022.wav
```

### Get Recording Info

```bash
# File details
file omi_recordings/*.wav

# Duration (requires ffprobe)
ffprobe -i omi_recordings/omi_auto_20260120_143022.wav 2>&1 | grep Duration
```

---

## Transcription

Automatically transcribe recordings to markdown files with metadata and full transcription text.

### Batch Transcription (Recommended)

```bash
# Transcribe all new recordings
uv run src/batch_transcribe.py

# Re-transcribe all files (ignore existing .md files)
uv run src/batch_transcribe.py --force

# Use a different Whisper model size
uv run src/batch_transcribe.py --model small

# Transcribe a custom directory
uv run src/batch_transcribe.py --dir /path/to/recordings
```

**Supported Models:**
- `tiny` (39M params, ~75MB) - Fastest, lowest quality
- `base` (74M params, ~140MB) - **Recommended** - Good balance
- `small` (244M params, ~461MB) - Better accuracy
- `medium` (769M params, ~1.4GB) - High accuracy
- `large` (1550M params, ~2.9GB) - Best accuracy

### Batch Transcription Output

For each WAV file, a markdown file is created with metadata and transcription:

```markdown
# Recording: omi_auto_20260120_143022

## Metadata
- **Recorded:** 2026-01-20 14:30:22
- **Duration:** 8.5s
- **File Size:** 265.3 KB
- **Sample Rate:** 16,000 Hz
- **Channels:** Mono
- **Format:** WAV (PCM 16-bit)
- **Transcription Model:** Whisper base

## Transcription

[Full transcribed text from Whisper]

---
*Automatically transcribed using OpenAI Whisper*
```

### Offline Transcription

The Whisper model is cached locally at `~/.cache/whisper/base.pt` (~140MB):

```bash
# First run downloads the model
uv run src/batch_transcribe.py
# This may take a few minutes on first run

# Subsequent runs use cached model
# Works completely offline after first download
uv run src/batch_transcribe.py
```

### Example Session

```
$ uv run src/batch_transcribe.py

======================================================================
Omi Audio Recorder - Batch Transcription
======================================================================

Directory: omi_recordings
Model: Whisper base
Mode: Transcribe new files only (skip if .md exists)

Found 3 WAV file(s)

[1/3] Processing: omi_auto_20260120_143022.wav
         Loading Whisper base model...
         Transcribing omi_auto_20260120_143022.wav...
         Transcribed: omi_auto_20260120_143022.wav → omi_auto_20260120_143022.md

[2/3] Processing: omi_auto_20260120_143035.wav
         Already transcribed: omi_auto_20260120_143035.wav

[3/3] Processing: omi_auto_20260120_143048.wav
         Loading Whisper base model...
         Transcribing omi_auto_20260120_143048.wav...
         Transcribed: omi_auto_20260120_143048.wav → omi_auto_20260120_143048.md

======================================================================
Batch Transcription Complete
======================================================================
Total:     3
Succeeded: 2
Failed:    0
Skipped:   1
======================================================================
```

### Viewing Transcriptions

```bash
# Open all markdown files
open omi_recordings/*.md

# View a single transcription
cat omi_recordings/omi_auto_20260120_143022.md

# Search all transcriptions
grep -r "important topic" omi_recordings/*.md
```

### Transcription Troubleshooting

**"Model download failed":**
- Ensure you have internet on first run
- Model will be cached for offline use afterward
- Check `~/.cache/whisper/base.pt` exists

**"Transcription quality is poor":**
- Ensure audio was clear (speak directly into Omi)
- Try a larger model: `--model medium` or `--model large`
- Check that microphone was working during recording

**"Very slow transcription":**
- Use smaller model: `--model tiny` (faster but less accurate)
- Larger models require more compute time
- Apple Silicon (M1/M2) typically faster than Intel

### Advanced: Transcribe Individual Files

```bash
# Transcribe a single file
uv run src/transcribe.py omi_recordings/omi_auto_20260120_143022.wav

# Uses Python import:
from src.transcribe import transcribe_file

wav_file = "omi_recordings/omi_auto_20260120_143022.wav"
success, message = transcribe_file(wav_file, model="base", force=False)
print(message)
```

---

## Troubleshooting

### "Device not found"

1. Ensure Omi is powered on
2. Check Bluetooth is enabled on Mac
3. Move Omi closer to your Mac
4. Run `src/discover_omi.py` to verify UUID

### "No audio captured"

1. Speak directly into the Omi device
2. Check Omi battery level
3. Ensure no other app is connected to Omi

### "Opus library not found"

```bash
brew install opus
```

### Recordings are splitting too often

Increase `SILENCE_DURATION` in `src/omi_continuous_recorder.py`:
```python
SILENCE_DURATION = 5.0  # Wait 5 seconds instead of 3
```

### Recordings not triggering on quiet speech

Lower `SILENCE_THRESHOLD` in `src/omi_continuous_recorder.py`:
```python
SILENCE_THRESHOLD = 300  # More sensitive to quiet audio
```
