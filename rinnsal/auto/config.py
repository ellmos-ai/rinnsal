# -*- coding: utf-8 -*-
"""
Chain-Konfigurationsmanagement
================================

Laedt, validiert und speichert Chain-Configs.
Based on llmauto.core.config. Angepasst fuer Rinnsal-Struktur.

Author: Lukas Geiger
License: MIT
"""
import json
import os
from pathlib import Path
from copy import deepcopy

from ..shared.config import get_rinnsal_dir, load_config

# Bekannte User-Home-Pfade fuer Cross-Machine Normalisierung.
_KNOWN_USER_HOMES = [
    "C:\\Users\\User\\",
]
_ACTUAL_HOME = str(Path.home()) + os.sep


DEFAULT_CHAIN_CONFIG = {
    "chain_name": "",
    "description": "",
    "mode": "loop",
    "max_rounds": 100,
    "runtime_hours": 0,
    "deadline": "",
    "max_consecutive_blocks": 5,
    "links": [],
    "prompts": {},
    "task_pools": {},
}


DEFAULT_LINK = {
    "name": "",
    "role": "worker",
    "model": None,
    "fallback_model": None,
    "prompt": "",
    "task_pool": "",
    "telegram_update": False,
    "until_full": False,
    "description": "",
}


def _get_chains_dir() -> Path:
    """Gibt das Chains-Verzeichnis zurueck. Sucht in CWD und ~/.rinnsal/."""
    local = Path("chains")
    if local.exists():
        return local
    rinnsal_dir = get_rinnsal_dir()
    chains_dir = rinnsal_dir / "chains"
    chains_dir.mkdir(exist_ok=True)
    return chains_dir


def _get_prompts_dir() -> Path:
    """Gibt das Prompts-Verzeichnis zurueck."""
    local = Path("prompts")
    if local.exists():
        return local
    rinnsal_dir = get_rinnsal_dir()
    prompts_dir = rinnsal_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    return prompts_dir


def load_auto_config() -> dict:
    """Laedt die Auto-Konfiguration aus rinnsal.json."""
    config = load_config()
    auto = config.get("auto", {})
    defaults = {
        "default_model": "claude-sonnet-4-6",
        "default_permission_mode": "dontAsk",
        "default_allowed_tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
        "default_timeout_seconds": 1800,
    }
    for k, v in defaults.items():
        auto.setdefault(k, v)
    return auto


def _normalize_paths(obj):
    """Ersetzt bekannte User-Home-Pfade durch den aktuellen."""
    if isinstance(obj, str):
        for known in _KNOWN_USER_HOMES:
            if known in obj and known != _ACTUAL_HOME:
                obj = obj.replace(known, _ACTUAL_HOME)
        return obj
    elif isinstance(obj, dict):
        return {k: _normalize_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_paths(item) for item in obj]
    return obj


def load_chain(name) -> dict:
    """Laedt eine gespeicherte Chain-Config."""
    chains_dir = _get_chains_dir()
    chain_file = chains_dir / f"{name}.json"
    if not chain_file.exists():
        raise FileNotFoundError(f"Kette '{name}' nicht gefunden: {chain_file}")
    with open(chain_file, "r", encoding="utf-8") as f:
        chain = json.load(f)
    chain = _normalize_paths(chain)
    config = deepcopy(DEFAULT_CHAIN_CONFIG)
    config.update(chain)
    return config


def save_chain(name, config):
    """Speichert eine Chain-Config."""
    chains_dir = _get_chains_dir()
    chains_dir.mkdir(exist_ok=True)
    chain_file = chains_dir / f"{name}.json"
    with open(chain_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def list_chains() -> list[str]:
    """Listet alle gespeicherten Ketten."""
    chains_dir = _get_chains_dir()
    if not chains_dir.exists():
        return []
    return [f.stem for f in chains_dir.glob("*.json")]


def new_link(**kwargs) -> dict:
    """Erstellt ein neues Kettenglied mit Defaults."""
    link = deepcopy(DEFAULT_LINK)
    link.update(kwargs)
    return link
