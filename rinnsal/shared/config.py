# -*- coding: utf-8 -*-
"""
Zentraler Config-Loader fuer Rinnsal.

Suchpfade:
    1. ./rinnsal.json  (aktuelles Verzeichnis)
    2. ~/.rinnsal/config.json  (User-Home)

Secrets: Ausschliesslich via ENV-Variablen.
"""
import json
import os
from pathlib import Path
from copy import deepcopy

DEFAULT_CONFIG = {
    "memory": {
        "db_path": "rinnsal.db",
        "default_agent_id": "default",
    },
    "connectors": {
        "telegram": {
            "bot_token_env": "RINNSAL_TELEGRAM_TOKEN",
            "owner_chat_id": "",
        },
        "discord": {
            "bot_token_env": "RINNSAL_DISCORD_TOKEN",
            "default_channel": "",
        },
        "homeassistant": {
            "access_token_env": "RINNSAL_HA_TOKEN",
            "endpoint": "",
        },
    },
    "auto": {
        "default_model": "claude-sonnet-4-6",
        "default_permission_mode": "dontAsk",
        "default_allowed_tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
        "default_timeout_seconds": 1800,
        "telegram": {
            "enabled": False,
            "bot_token_env": "RINNSAL_TELEGRAM_TOKEN",
            "chat_id": "",
        },
    },
}

_config_cache = None


def _find_config_file() -> Path | None:
    """Sucht die Config-Datei in den Standard-Pfaden."""
    candidates = [
        Path("rinnsal.json"),
        Path.home() / ".rinnsal" / "config.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def load_config(force_reload: bool = False) -> dict:
    """Laedt die Rinnsal-Konfiguration (mit Cache)."""
    global _config_cache
    if _config_cache is not None and not force_reload:
        return _config_cache

    config = deepcopy(DEFAULT_CONFIG)
    config_file = _find_config_file()

    if config_file:
        with open(config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        _deep_merge(config, user_config)

    _config_cache = config
    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Merged override rekursiv in base (in-place)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def get_rinnsal_dir() -> Path:
    """Gibt das Rinnsal-Arbeitsverzeichnis zurueck (~/.rinnsal/)."""
    rinnsal_dir = Path.home() / ".rinnsal"
    rinnsal_dir.mkdir(exist_ok=True)
    return rinnsal_dir


def save_config(config: dict, path: Path | None = None) -> Path:
    """Speichert Config in die angegebene oder Standard-Datei."""
    if path is None:
        path = get_rinnsal_dir() / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return path
