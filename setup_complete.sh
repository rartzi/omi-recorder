#!/bin/bash
# Omi Recorder - All-in-One Setup Script
# This script copies necessary files and installs dependencies

echo "========================================================================"
echo "Omi Audio Recorder - Complete Setup"
echo "========================================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create directory
INSTALL_DIR="$HOME/omi-recorder"
mkdir -p "$INSTALL_DIR"

echo "✓ Created directory: $INSTALL_DIR"
echo ""

# ============================================================================
# Copy omi_recorder.py
# ============================================================================
echo "Copying omi_recorder.py..."

if [ ! -f "$SCRIPT_DIR/omi_recorder.py" ]; then
    echo "✗ Error: omi_recorder.py not found in $SCRIPT_DIR"
    exit 1
fi

cp "$SCRIPT_DIR/omi_recorder.py" "$INSTALL_DIR/omi_recorder.py"
chmod +x "$INSTALL_DIR/omi_recorder.py"
echo "✓ Copied omi_recorder.py"

# ============================================================================
# Copy discover_omi.py
# ============================================================================
echo "Copying discover_omi.py..."

if [ ! -f "$SCRIPT_DIR/discover_omi.py" ]; then
    echo "✗ Error: discover_omi.py not found in $SCRIPT_DIR"
    exit 1
fi

cp "$SCRIPT_DIR/discover_omi.py" "$INSTALL_DIR/discover_omi.py"
chmod +x "$INSTALL_DIR/discover_omi.py"
echo "✓ Copied discover_omi.py"

# ============================================================================
# Install dependencies
# ============================================================================
echo ""
echo "========================================================================"
echo "Installing Dependencies"
echo "========================================================================"
echo ""

# Check Homebrew
if ! command -v brew &> /dev/null; then
    echo "✗ Homebrew not found"
    echo ""
    echo "Install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi
echo "✓ Homebrew found"

# Install Opus
echo "Installing Opus..."
brew install opus
echo "✓ Opus installed"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    exit 1
fi
echo "✓ Python 3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install bleak --break-system-packages
echo "✓ Dependencies installed"

# Create output directory
mkdir -p "$INSTALL_DIR/omi_recordings"

echo ""
echo "========================================================================"
echo "✅ Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Find your Omi device UUID:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python discover_omi.py"
echo ""
echo "2. Edit omi_recorder.py and set DEVICE_UUID"
echo "   nano $INSTALL_DIR/omi_recorder.py"
echo ""
echo "3. Start recording:"
echo "   python omi_recorder.py"
echo ""
echo "Files are in: $INSTALL_DIR"
echo ""
echo "========================================================================"
