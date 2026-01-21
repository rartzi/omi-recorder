#!/usr/bin/env python3
"""
Transcription module for Omi Audio Recorder

Provides functions to transcribe WAV files using OpenAI Whisper
and generate markdown files with metadata and transcription text.

Features:
- Local transcription using Whisper base model
- Offline support with model caching
- Markdown generation with audio metadata
- Batch processing capabilities
"""

import os
import wave
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
import whisper


def get_audio_metadata(wav_path: str) -> Dict[str, Any]:
    """
    Extract metadata from WAV file.

    Args:
        wav_path: Path to WAV file

    Returns:
        Dict containing: duration, file_size, sample_rate, channels, recorded_at
    """
    wav_path = Path(wav_path)

    # Extract timestamp from filename
    # Format: omi_auto_YYYYMMDD_HHMMSS.wav
    filename = wav_path.stem
    parts = filename.split('_')

    recorded_at = None
    if len(parts) >= 4:
        try:
            date_str = parts[2]  # YYYYMMDD
            time_str = parts[3]  # HHMMSS
            datetime_str = f"{date_str} {time_str}"
            recorded_at = datetime.strptime(datetime_str, "%Y%m%d %H%M%S").isoformat()
        except (ValueError, IndexError):
            recorded_at = datetime.now().isoformat()
    else:
        recorded_at = datetime.now().isoformat()

    # Get duration and sample rate from WAV file
    try:
        with wave.open(wav_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            duration = frames / sample_rate
    except Exception as e:
        print(f"Warning: Could not read WAV metadata from {wav_path}: {e}")
        duration = 0
        sample_rate = 16000
        channels = 1

    # Get file size
    file_size = wav_path.stat().st_size

    return {
        'duration': duration,
        'file_size': file_size,
        'sample_rate': sample_rate,
        'channels': channels,
        'recorded_at': recorded_at,
    }


def transcribe_audio(wav_path: str, model: str = "base") -> str:
    """
    Transcribe a WAV file using OpenAI Whisper.

    Supports offline mode if model is already cached locally.
    Model cache location: ~/.cache/whisper/base.pt

    Args:
        wav_path: Path to WAV file to transcribe
        model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
               Default: 'base' (74M params, ~140MB)

    Returns:
        Transcribed text

    Raises:
        FileNotFoundError: If WAV file doesn't exist
        Exception: If transcription fails
    """
    wav_path = Path(wav_path)

    if not wav_path.exists():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    try:
        # Load Whisper model
        # Supports offline mode if ~/.cache/whisper/{model}.pt exists
        print(f"  Loading Whisper {model} model...")
        model_instance = whisper.load_model(model)

        # Transcribe
        print(f"  Transcribing {wav_path.name}...")
        result = model_instance.transcribe(str(wav_path))

        return result['text']

    except Exception as e:
        raise Exception(f"Transcription failed for {wav_path.name}: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "265.3 KB", "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "8.5 seconds", "1m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds:.0f}s"


def detect_rtl_text(text: str) -> bool:
    """
    Detect if text contains right-to-left characters (Arabic, Hebrew, etc).

    Args:
        text: Text to analyze

    Returns:
        True if RTL text detected, False otherwise
    """
    # Unicode ranges for common RTL languages
    rtl_ranges = [
        (0x0590, 0x05FF),    # Hebrew
        (0x0600, 0x06FF),    # Arabic
        (0x0750, 0x077F),    # Arabic Supplement
        (0x08A0, 0x08FF),    # Arabic Extended-A
    ]

    for char in text:
        code = ord(char)
        for start, end in rtl_ranges:
            if start <= code <= end:
                return True
    return False


def format_transcription_text(text: str) -> str:
    """
    Format transcription text, handling RTL languages properly.

    Args:
        text: Transcribed text

    Returns:
        Formatted text with RTL hints if needed
    """
    if not text.strip():
        return text

    if detect_rtl_text(text):
        # Wrap RTL text with HTML direction marker for proper alignment
        return f'<div dir="rtl">\n\n{text}\n\n</div>'

    return text


def generate_markdown(wav_path: str, transcription_text: str) -> str:
    """
    Generate markdown content with metadata and transcription.

    Args:
        wav_path: Path to WAV file
        transcription_text: Transcribed text from Whisper

    Returns:
        Markdown formatted string
    """
    wav_path = Path(wav_path)
    filename = wav_path.stem
    metadata = get_audio_metadata(str(wav_path))

    # Parse recorded_at for display
    recorded_at = metadata['recorded_at']
    try:
        dt = datetime.fromisoformat(recorded_at)
        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        formatted_date = recorded_at

    # Format metadata values
    duration_str = format_duration(metadata['duration'])
    file_size_str = format_file_size(metadata['file_size'])
    sample_rate = metadata['sample_rate']
    channels = metadata['channels']

    # Format transcription text (handles RTL languages)
    formatted_text = format_transcription_text(transcription_text)

    # Create markdown
    markdown = f"""# Recording: {filename}

## Metadata
- **Recorded:** {formatted_date}
- **Duration:** {duration_str}
- **File Size:** {file_size_str}
- **Sample Rate:** {sample_rate:,} Hz
- **Channels:** {'Mono' if channels == 1 else f'{channels}-channel'}
- **Format:** WAV (PCM 16-bit)
- **Transcription Model:** Whisper base

## Transcription

{formatted_text}

---
*Automatically transcribed using OpenAI Whisper*
"""

    return markdown


def save_markdown(wav_path: str, markdown_content: str) -> Path:
    """
    Save markdown file alongside WAV file.

    Example:
        Input:  omi_auto_20260120_143022.wav
        Output: omi_auto_20260120_143022.md

    Args:
        wav_path: Path to WAV file
        markdown_content: Markdown formatted string

    Returns:
        Path to saved markdown file

    Raises:
        IOError: If file write fails
    """
    wav_path = Path(wav_path)
    md_path = wav_path.with_suffix('.md')

    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        return md_path
    except IOError as e:
        raise IOError(f"Failed to save markdown file: {md_path}") from e


def should_transcribe(wav_path: str, force: bool = False) -> bool:
    """
    Determine if a WAV file should be transcribed.

    Checks if corresponding .md file already exists.

    Args:
        wav_path: Path to WAV file
        force: If True, always return True (force re-transcription)

    Returns:
        True if file should be transcribed, False otherwise
    """
    if force:
        return True

    wav_path = Path(wav_path)
    md_path = wav_path.with_suffix('.md')

    return not md_path.exists()


def transcribe_file(wav_path: str, model: str = "base", force: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Transcribe a single WAV file and save markdown.

    Args:
        wav_path: Path to WAV file
        model: Whisper model to use (default: 'base')
        force: If True, re-transcribe even if .md exists

    Returns:
        Tuple of (success: bool, message: Optional[str])
    """
    wav_path = Path(wav_path)

    # Check if should transcribe
    if not should_transcribe(str(wav_path), force):
        return True, f"Already transcribed: {wav_path.name}"

    try:
        # Transcribe
        transcription = transcribe_audio(str(wav_path), model)

        # Generate markdown
        markdown = generate_markdown(str(wav_path), transcription)

        # Save markdown
        md_path = save_markdown(str(wav_path), markdown)

        return True, f"Transcribed: {wav_path.name} → {md_path.name}"

    except Exception as e:
        return False, f"Failed: {wav_path.name} - {str(e)}"


def batch_transcribe(
    recordings_dir: str = "omi_recordings",
    model: str = "base",
    force: bool = False
) -> Dict[str, int]:
    """
    Batch transcribe all WAV files in a directory.

    Scans for WAV files and transcribes those without corresponding .md files.

    Args:
        recordings_dir: Directory containing WAV files (default: 'omi_recordings')
        model: Whisper model to use (default: 'base')
        force: If True, re-transcribe all files even if .md exists

    Returns:
        Dict with counts: {'total': int, 'succeeded': int, 'failed': int, 'skipped': int}
    """
    recordings_path = Path(recordings_dir)

    if not recordings_path.exists():
        raise FileNotFoundError(f"Recordings directory not found: {recordings_dir}")

    # Find all WAV files
    wav_files = sorted(recordings_path.glob("*.wav"))

    if not wav_files:
        return {'total': 0, 'succeeded': 0, 'failed': 0, 'skipped': 0}

    stats = {'total': len(wav_files), 'succeeded': 0, 'failed': 0, 'skipped': 0}

    print(f"\nBatch transcribing {len(wav_files)} file(s) from {recordings_dir}/\n")

    for i, wav_file in enumerate(wav_files, 1):
        print(f"[{i}/{len(wav_files)}] Processing: {wav_file.name}")

        success, message = transcribe_file(str(wav_file), model, force)

        if success:
            if "Already transcribed" in message:
                stats['skipped'] += 1
            else:
                stats['succeeded'] += 1
        else:
            stats['failed'] += 1

        if message:
            print(f"         {message}")

    return stats


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <wav_file>")
        print("       python transcribe.py --batch [recordings_dir] [--force]")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        recordings_dir = sys.argv[2] if len(sys.argv) > 2 else "omi_recordings"
        force = "--force" in sys.argv

        stats = batch_transcribe(recordings_dir, force=force)

        print(f"\n{'='*70}")
        print("Batch Transcription Complete")
        print(f"{'='*70}")
        print(f"Total:     {stats['total']}")
        print(f"Succeeded: {stats['succeeded']}")
        print(f"Failed:    {stats['failed']}")
        print(f"Skipped:   {stats['skipped']}")
        print(f"{'='*70}\n")
    else:
        wav_file = sys.argv[1]
        success, message = transcribe_file(wav_file)

        if message:
            print(message)

        sys.exit(0 if success else 1)
