# Omi Audio Recorder

A macOS application for recording audio from Omi wearable devices via Bluetooth Low Energy (BLE). Captures Opus-encoded audio streams in real-time and saves them as WAV files.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

## Features

- **Real-time audio capture** from Omi wearable devices
- **Voice-activated recording** with automatic session segmentation
- **Multiple recording modes** (continuous, manual, interactive)
- **Opus to WAV conversion** with high-quality decoding
- **Simple setup** with minimal dependencies

## Quick Start

```bash
# Install dependencies
brew install opus
python3 -m venv venv && source venv/bin/activate
pip install bleak

# Find your device
python discover_omi.py

# Update DEVICE_UUID in your chosen script, then run:
python omi_continuous_recorder.py
```

## Installation

See [docs/INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

### Requirements

- macOS 11+ (Big Sur or later)
- Python 3.8+
- Homebrew
- Omi wearable device

### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd omi-clean

# Install Opus codec
brew install opus

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install bleak

# Discover your Omi device UUID
python discover_omi.py
```

## Usage

### Continuous Recorder (Recommended)

Automatically records and saves separate files based on voice activity:

```bash
python omi_continuous_recorder.py
```

- Starts recording when speech is detected
- Saves to a new file after 3 seconds of silence
- Creates separate files for each speech segment
- Press `Ctrl+C` to stop

### Basic Recorder

Simple recording that saves when you press `Ctrl+C`:

```bash
python omi_recorder.py
```

### Enhanced Recorder

Manual control with keyboard shortcuts:

```bash
python omi_recorder_enhanced.py
```

| Key | Action |
|-----|--------|
| `r` | Start recording |
| `s` | Stop and save |
| `q` | Quit |

See [docs/USAGE.md](docs/USAGE.md) for comprehensive usage guide.

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALL.md](docs/INSTALL.md) | Installation and setup guide |
| [USAGE.md](docs/USAGE.md) | Usage guide with examples |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture |
| [CLAUDE.md](CLAUDE.md) | AI assistant instructions |

## Project Structure

```
omi-clean/
├── discover_omi.py            # Device discovery utility
├── omi_recorder.py            # Basic recorder
├── omi_recorder_enhanced.py   # Interactive recorder
├── omi_continuous_recorder.py # Voice-activated recorder
├── setup_complete.sh          # User installation script
├── docs/
│   ├── ARCHITECTURE.md        # Technical documentation
│   ├── INSTALL.md             # Installation guide
│   └── USAGE.md               # Usage guide
└── omi_recordings/            # Output directory (created on first run)
```

## Configuration

Edit these values in `omi_continuous_recorder.py` to customize behavior:

```python
DEVICE_UUID = "YOUR-UUID-HERE"  # Your Omi's Bluetooth UUID
SILENCE_THRESHOLD = 500         # Voice detection sensitivity
SILENCE_DURATION = 3.0          # Seconds of silence before saving
MIN_RECORDING_DURATION = 1.0    # Minimum recording length to save
```

## Technical Specifications

| Specification | Value |
|---------------|-------|
| Audio Codec | Opus |
| Sample Rate | 16 kHz |
| Channels | Mono |
| Output Format | WAV (PCM 16-bit) |
| Protocol | Bluetooth Low Energy (BLE) |

## Transcription

Recorded files can be transcribed using OpenAI Whisper:

```bash
# Install Whisper
pip install openai-whisper

# Transcribe recordings
whisper omi_recordings/*.wav
```

## Troubleshooting

### Device not found

1. Ensure Omi is powered on
2. Check Bluetooth is enabled on Mac
3. Run `discover_omi.py` to verify UUID

### Opus library not found

```bash
brew install opus
```

### No audio captured

- Speak directly into the Omi device
- Check device battery level
- Verify correct UUID in script

See [docs/USAGE.md](docs/USAGE.md#troubleshooting) for more solutions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Omi Audio Recorder Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- [Based Hardware](https://github.com/BasedHardware/omi) - Omi device and SDK
- [Bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy library
- [Opus Codec](https://opus-codec.org/) - Audio codec

## Resources

- [Omi Documentation](https://docs.omi.me/)
- [Omi GitHub](https://github.com/BasedHardware/omi)
- [Omi Protocol Docs](https://docs.omi.me/doc/developer/Protocol)
