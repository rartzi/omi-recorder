# Installation & Build Guide

This guide covers how to install and set up the Omi Audio Recorder.

## Requirements

### Hardware
- Mac with Bluetooth (tested on Apple Silicon)
- Omi wearable device (firmware 1.0.3+)

### Software
- macOS 11+ (Big Sur or later)
- Python 3.8+
- Homebrew (for installing Opus)

---

## Quick Installation

### Option 1: Development Setup (Recommended)

For development or running from the repository:

```bash
# 1. Clone the repository
git clone <repository-url>
cd omi-clean

# 2. Install Opus codec
brew install opus

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install Python dependencies
pip install bleak

# 6. Find your Omi device UUID
python discover_omi.py

# 7. Update DEVICE_UUID in your chosen script
# Edit line 7 or 13 in the script you want to use
```

### Option 2: User Installation

For end-users who just want to record:

```bash
# Run the setup script
chmod +x setup_complete.sh
./setup_complete.sh
```

This installs to `~/omi-recorder/` with all dependencies.

---

## Detailed Installation Steps

### Step 1: Install Homebrew (if needed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Opus Codec

```bash
brew install opus
```

Verify installation:
```bash
ls /opt/homebrew/lib/libopus*
# Should show: libopus.0.dylib, libopus.a, libopus.dylib
```

### Step 3: Install Python 3

macOS usually includes Python 3. Verify:
```bash
python3 --version
# Should show: Python 3.x.x
```

If not installed:
```bash
brew install python
```

### Step 4: Create Virtual Environment

```bash
# Navigate to project directory
cd /path/to/omi-clean

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 5: Install Python Dependencies

```bash
pip install bleak
```

This installs:
- `bleak` - Bluetooth Low Energy library
- `pyobjc-framework-CoreBluetooth` - macOS Bluetooth bindings (auto-installed)

### Step 6: Configure Device UUID

1. Power on your Omi device
2. Run discovery:
   ```bash
   python discover_omi.py
   ```
3. Copy the UUID shown (e.g., `93826AE8-AE8C-2AE4-D717-0978E4817739`)
4. Edit your chosen recorder script and update `DEVICE_UUID`

---

## Project Structure

```
omi-clean/
├── discover_omi.py           # Device discovery
├── omi_recorder.py           # Basic recorder
├── omi_recorder_enhanced.py  # Interactive recorder
├── omi_continuous_recorder.py # Voice-activated recorder
├── setup_complete.sh         # User installation script
├── CLAUDE.md                 # AI assistant instructions
├── README.md                 # Project overview
├── .gitignore                # Git ignore rules
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   ├── USAGE.md
│   └── INSTALL.md
├── venv/                     # Virtual environment (not in git)
└── omi_recordings/           # Output directory (not in git)
```

---

## Verifying Installation

### Test 1: Check Opus

```bash
python3 -c "
import ctypes
import glob
for p in ['/opt/homebrew/lib/libopus.0.dylib', '/opt/homebrew/Cellar/opus/*/lib/libopus.0.dylib']:
    for m in glob.glob(p):
        try:
            ctypes.CDLL(m)
            print(f'Opus OK: {m}')
            exit(0)
        except: pass
print('Opus NOT FOUND')
"
```

### Test 2: Check Bleak

```bash
python3 -c "from bleak import BleakScanner; print('Bleak OK')"
```

### Test 3: Scan for Devices

```bash
source venv/bin/activate
python discover_omi.py
```

### Test 4: Test Recording

```bash
source venv/bin/activate
python omi_continuous_recorder.py
# Speak into Omi, wait for recording, press Ctrl+C
```

---

## Updating

### Update Python Dependencies

```bash
source venv/bin/activate
pip install --upgrade bleak
```

### Update Opus

```bash
brew upgrade opus
```

---

## Uninstallation

### Remove Development Setup

```bash
# Remove virtual environment
rm -rf venv/

# Remove recordings
rm -rf omi_recordings/

# Optionally remove Opus
brew uninstall opus
```

### Remove User Installation

```bash
rm -rf ~/omi-recorder/
```

---

## Platform Notes

### Apple Silicon (M1/M2/M3)

Opus is installed to `/opt/homebrew/lib/`. The scripts automatically detect this path.

### Intel Mac

Opus may be installed to `/usr/local/lib/`. If you encounter issues, check:
```bash
brew --prefix opus
```

And update the glob patterns in the scripts if needed.

### Bluetooth Permissions

On first run, macOS may ask for Bluetooth permissions. Grant access to Terminal (or your IDE) to allow BLE scanning and connection.

---

## Building from Source (Advanced)

The project is pure Python and doesn't require building. However, if you want to create a standalone distribution:

### Create Distribution Package

```bash
# Install build tools
pip install build

# Create wheel
python -m build
```

### Create Standalone App (PyInstaller)

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile omi_continuous_recorder.py
```

Note: Standalone builds require bundling libopus, which adds complexity.

---

## Troubleshooting Installation

### "brew: command not found"

Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### "No module named 'bleak'"

Activate virtual environment first:
```bash
source venv/bin/activate
pip install bleak
```

### "Opus library not found"

```bash
brew install opus
# or reinstall if corrupted
brew reinstall opus
```

### "Permission denied" on Bluetooth

1. Open System Preferences → Security & Privacy → Privacy
2. Select Bluetooth
3. Add Terminal (or your IDE) to the allowed list

### Python version issues

Ensure you're using Python 3.8+:
```bash
python3 --version
```

If multiple versions exist, specify explicitly:
```bash
python3.11 -m venv venv
```
