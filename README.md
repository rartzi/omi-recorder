# Omi Audio Recorder

Record audio from your Omi wearable device to WAV files on your Mac via Bluetooth.

---

## ⚡ Quick Start (3 Steps)

### 1. Run Setup

```bash
# Make the setup script executable and run it
chmod +x setup_complete.sh
./setup_complete.sh
```

**What this does:**
- Creates all necessary files in `~/omi-recorder/`
- Installs Opus audio codec
- Creates Python virtual environment
- Installs dependencies (bleak)

### 2. Find Your Device UUID

```bash
cd ~/omi-recorder
source venv/bin/activate
python discover_omi.py
```

**Copy the UUID** that's displayed (format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`)

### 3. Update & Record

```bash
# Edit omi_recorder.py and set your UUID on line 10
nano omi_recorder.py
# Change: DEVICE_UUID = "YOUR-UUID-HERE"
# Save: Ctrl+X, then Y, then Enter

# Start recording!
python omi_recorder.py
```

**Recording steps:**
1. Press button on Omi to start recording
2. Press Enter when prompted
3. Speak into your Omi device
4. Press Ctrl+C when done
5. Audio saved to `omi_recordings/omi_YYYYMMDD_HHMMSS.wav`

---

## 📂 What Gets Installed

After running `setup_complete.sh`, you'll have:

```
~/omi-recorder/
├── venv/                    # Python virtual environment
├── omi_recordings/          # Your recordings go here
├── omi_recorder.py         # Main recorder script
└── discover_omi.py         # Device UUID finder
```

---

## 🎯 Daily Usage

Once set up, recording is simple:

```bash
# 1. Navigate and activate
cd ~/omi-recorder
source venv/bin/activate

# 2. Record (make sure Omi is recording first!)
python omi_recorder.py

# 3. Play your recording
open omi_recordings/omi_*.wav
```

---

## 🔧 Troubleshooting

### "No module named 'bleak'"

```bash
cd ~/omi-recorder
source venv/bin/activate
pip install bleak --break-system-packages
```

### "Opus library not found"

```bash
brew install opus
```

### "No audio captured"

**Check that:**
- ✅ Omi device is actively recording (button pressed, not just powered on)
- ✅ Device is within 10 meters
- ✅ You're speaking INTO the device (not just near it)
- ✅ Correct UUID is set in `omi_recorder.py`

### "Connection timeout"

```bash
# Turn Bluetooth off and on
# System Settings → Bluetooth → Toggle off/on

# Restart your Omi device
# Then try again
```

---

## 📊 Technical Details

- **Codec:** Opus (codec 21)
- **Sample Rate:** 16kHz
- **Channels:** Mono
- **Output:** WAV (PCM 16-bit)
- **Protocol:** BLE (Bluetooth Low Energy)

---

## 💡 Tips

### Create an Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias omi-record='cd ~/omi-recorder && source venv/bin/activate && python omi_recorder.py'
```

Then just type: `omi-record`

### Transcribe Recordings

Use Whisper for speech-to-text:

```bash
pip install openai-whisper
whisper omi_recordings/omi_20251025_123456.wav
```

---

## 📋 Requirements

- macOS (tested on Apple Silicon)
- Python 3.8+
- Homebrew
- Omi device (firmware 1.0.3+)

---

## 🆘 Support

- **Omi Docs:** https://docs.omi.me/
- **Omi GitHub:** https://github.com/BasedHardware/omi
- **Protocol Docs:** https://docs.omi.me/doc/developer/Protocol

---

## 📝 How It Works

1. **Connects** to Omi via Bluetooth (BLE)
2. **Receives** Opus-encoded audio packets
3. **Decodes** using libopus in real-time
4. **Saves** as standard WAV file

**Audio Characteristic:** `19B10001-E8F2-537E-4F6C-D104768A1214`

---

## ✅ Verification

After setup, test that everything works:

```bash
cd ~/omi-recorder
source venv/bin/activate

# Should show your device
python discover_omi.py

# Should record audio
python omi_recorder.py
```

---

**Questions?** All functionality is in 2 simple Python scripts - easy to read and modify!

---

Made with ❤️ for Omi users | October 2025
