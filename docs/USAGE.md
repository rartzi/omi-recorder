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

**Note:** The recorder supports auto-discovery. No need to manually find or edit device UUIDs.

---

## Recording

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

Create a `config.yaml` file in the project root to customize settings:

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml`:

```yaml
recording:
  silence_threshold: 500   # Lower = more sensitive to quiet speech
  silence_duration: 3.0    # Seconds of silence before saving
  min_recording_duration: 1.0  # Ignore recordings shorter than this

directory:
  recordings_dir: omi_recordings    # Where WAV files are saved
  transcripts_dir: omi_recordings   # Where transcripts are saved
```

All settings are optional - the defaults work out of the box.

### Output Files

Files are saved to `omi_recordings/` with timestamps:
```
omi_recordings/
├── omi_auto_20260120_143022.wav
├── omi_auto_20260120_143035.wav
└── omi_auto_20260120_143048.wav
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

# Transcribe from a custom directory
uv run src/batch_transcribe.py --dir /path/to/recordings

# Save transcripts to a separate directory
uv run src/batch_transcribe.py --transcripts-dir /path/to/transcripts
```

**Tip:** Set `transcripts_dir` in `config.yaml` to always save transcripts to a separate folder.

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

Increase `silence_duration` in `config.yaml`:
```yaml
recording:
  silence_duration: 5.0  # Wait 5 seconds instead of 3
```

### Recordings not triggering on quiet speech

Lower `silence_threshold` in `config.yaml`:
```yaml
recording:
  silence_threshold: 300  # More sensitive to quiet audio
```
