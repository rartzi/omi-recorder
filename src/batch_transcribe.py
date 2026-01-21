#!/usr/bin/env python3
"""
Batch Transcription Script for Omi Audio Recorder

Standalone script to transcribe all WAV files in the omi_recordings/
directory without corresponding markdown files.

Usage:
    python batch_transcribe.py                    # Transcribe all new files
    python batch_transcribe.py --force           # Re-transcribe all files
    python batch_transcribe.py --dir path/to/dir # Use custom directory
    python batch_transcribe.py --model small     # Use different model size

Supported Whisper models:
    - tiny   (39M params, ~75MB)   - Fastest
    - base   (74M params, ~140MB)  - Recommended
    - small  (244M params, ~461MB)
    - medium (769M params, ~1.4GB)
    - large  (1550M params, ~2.9GB) - Most accurate
"""

import sys
import argparse
from pathlib import Path
from transcribe import batch_transcribe as transcribe_batch

def main():
    """Main entry point for batch transcription."""
    parser = argparse.ArgumentParser(
        description="Batch transcribe WAV files in omi_recordings directory"
    )

    parser.add_argument(
        "--dir",
        default="omi_recordings",
        help="Directory containing WAV files (default: omi_recordings)"
    )

    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-transcribe files even if .md already exists"
    )

    args = parser.parse_args()

    # Print header
    print("\n" + "=" * 70)
    print("Omi Audio Recorder - Batch Transcription")
    print("=" * 70)
    print(f"\nDirectory: {args.dir}")
    print(f"Model: Whisper {args.model}")
    if args.force:
        print("Mode: Force re-transcription of all files")
    else:
        print("Mode: Transcribe new files only (skip if .md exists)")
    print()

    # Check if directory exists
    recordings_path = Path(args.dir)
    if not recordings_path.exists():
        print(f"❌ Error: Directory not found: {args.dir}\n")
        return 1

    # Count WAV files
    wav_files = list(recordings_path.glob("*.wav"))
    if not wav_files:
        print(f"⚠️  No WAV files found in {args.dir}\n")
        return 0

    print(f"Found {len(wav_files)} WAV file(s)\n")

    try:
        # Run batch transcription
        stats = transcribe_batch(args.dir, model=args.model, force=args.force)

        # Print summary
        print(f"\n{'='*70}")
        print("Batch Transcription Complete")
        print(f"{'='*70}")
        print(f"Total:     {stats['total']}")
        print(f"Succeeded: {stats['succeeded']}")
        print(f"Failed:    {stats['failed']}")
        print(f"Skipped:   {stats['skipped']}")
        print(f"{'='*70}\n")

        # Return appropriate exit code
        return 0 if stats['failed'] == 0 else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Transcription interrupted by user\n")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
