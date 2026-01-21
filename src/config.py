"""
Configuration loader for Omi Audio Recorder.

This module provides a simple, fail-safe configuration system.
If config loading fails for any reason, default values are used.

Usage:
    import config
    threshold = config.get('recording', 'silence_threshold', 500)
"""
from pathlib import Path
from typing import Any, Dict, Optional

# All defaults in one place
DEFAULTS = {
    'recording': {
        'silence_threshold': 500,
        'silence_duration': 3.0,
        'min_recording_duration': 1.0,
        'sample_rate': 16000,
    },
    'transcription': {
        'model': 'base',
        'language': '',
        'enable_rtl_support': True,
    },
    'directory': {
        'recordings_dir': 'omi_recordings',
        'transcripts_dir': 'omi_recordings',
    },
    'device': {
        'discovery_timeout': 10.0,
    },
}

_config_cache: Optional[Dict] = None


def _find_config_file() -> Optional[Path]:
    """Find config.yaml in project root."""
    src_dir = Path(__file__).parent
    project_root = src_dir.parent
    config_path = project_root / 'config.yaml'
    if config_path.exists():
        return config_path
    return None


def _load_yaml(path: Path) -> Dict:
    """Load YAML file. Returns empty dict if PyYAML not available or on error."""
    try:
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}
    except Exception:
        return {}


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Merge override into base, preserving nested structure."""
    result = {}
    for key in base:
        if key in override:
            if isinstance(base[key], dict) and isinstance(override[key], dict):
                result[key] = _deep_merge(base[key], override[key])
            else:
                result[key] = override[key]
        else:
            result[key] = base[key]
    return result


def load_config() -> Dict:
    """
    Load configuration with fallback to defaults.

    Priority: config.yaml > DEFAULTS

    This function NEVER raises exceptions - always returns valid config.
    """
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    config = {k: v.copy() if isinstance(v, dict) else v for k, v in DEFAULTS.items()}

    config_file = _find_config_file()
    if config_file:
        user_config = _load_yaml(config_file)
        if user_config:
            config = _deep_merge(DEFAULTS, user_config)

    _config_cache = config
    return config


def get(section: str, key: str, default: Any = None) -> Any:
    """
    Get a configuration value.

    Example: get('recording', 'silence_threshold')
    """
    config = load_config()
    return config.get(section, {}).get(key, default)


def get_recordings_dir() -> str:
    """Get recordings directory path (creates if needed)."""
    dir_path = get('directory', 'recordings_dir', 'omi_recordings')
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


def get_transcripts_dir() -> str:
    """Get transcripts directory path (creates if needed)."""
    dir_path = get('directory', 'transcripts_dir', 'omi_recordings')
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


def reset_cache() -> None:
    """Reset config cache (useful for testing)."""
    global _config_cache
    _config_cache = None
