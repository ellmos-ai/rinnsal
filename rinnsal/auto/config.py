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

from ..shared.config import DEFAULT_MODEL, get_rinnsal_dir, load_config

_ACTUAL_HOME = str(Path.home()) + os.sep


def _get_known_user_homes() -> list:
    """Bekannte User-Home-Pfade fuer Cross-Machine Normalisierung.

    Es sind bewusst KEINE Pfade hart kodiert. Quellen:
    1. Config-Key "auto" -> "known_user_homes" (Liste von Strings,
       rinnsal.json ist gitignored)
    2. ENV-Variable RINNSAL_KNOWN_HOMES (mehrere Pfade via ";" getrennt;
       NICHT os.pathsep, da dieser auf POSIX ":" ist und Windows-
       Laufwerksbuchstaben wie "C:\\..." zerschneiden wuerde)

    Eintraege sollten den abschliessenden Pfadtrenner enthalten,
    z. B. "C:\\Users\\Alice\\" oder "/home/alice/".
    """
    homes = []
    try:
        auto = load_config().get("auto", {})
        for entry in auto.get("known_user_homes", []) or []:
            if isinstance(entry, str) and entry:
                homes.append(entry)
    except Exception:
        pass
    for entry in os.environ.get("RINNSAL_KNOWN_HOMES", "").split(";"):
        if entry:
            homes.append(entry)
    return homes


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
        "default_model": DEFAULT_MODEL,
        "default_permission_mode": "dontAsk",
        "default_allowed_tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
        "default_timeout_seconds": 1800,
    }
    for k, v in defaults.items():
        auto.setdefault(k, v)
    return auto


def _normalize_paths(obj, known_homes=None):
    """Ersetzt bekannte User-Home-Pfade durch den aktuellen."""
    if known_homes is None:
        known_homes = _get_known_user_homes()
    if isinstance(obj, str):
        for known in known_homes:
            if known in obj and known != _ACTUAL_HOME:
                obj = obj.replace(known, _ACTUAL_HOME)
        return obj
    elif isinstance(obj, dict):
        return {k: _normalize_paths(v, known_homes) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_paths(item, known_homes) for item in obj]
    return obj


def validate_chain_name(name) -> str:
    """Validiert einen Chain-Namen fuer die Verwendung in Dateipfaden.

    Chain-Namen werden in chains/-, logs/- und state/-Pfade eingesetzt.
    Ohne Validierung erlauben Pfadtrenner und '..' Path Traversal (CWE-22),
    z. B. `rinnsal chain start "../../../../andere_datei"`.
    """
    name = str(name)
    if (
        not name
        or name != name.strip()
        or name.startswith(".")
        or any(sep in name for sep in ("/", "\\", ":"))
    ):
        raise ValueError(
            f"Ungueltiger Chain-Name {name!r}: Pfadtrenner (/ \\ :), "
            "fuehrende Punkte und Leerraum am Rand sind nicht erlaubt."
        )
    return name


def load_chain(name) -> dict:
    """Laedt eine gespeicherte Chain-Config."""
    name = validate_chain_name(name)
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
    name = validate_chain_name(name)
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
