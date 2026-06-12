"""
rinnsal.i18n - Internationalisierung für Rinnsal
=================================================
Referenz: .SOFTWARE/_LANG/LANGUAGE_CODES.md

Verwendung:
    from rinnsal.i18n import t, set_language, get_language

    print(t('status.running'))
    set_language('en')
"""

import json
import sys
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional

SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'zh', 'ja', 'ru']
DEFAULT_LANGUAGE = 'de'
FALLBACK_CHAIN = ['en', 'de']

_current_lang: str = DEFAULT_LANGUAGE
_translations: Dict[str, Dict[str, str]] = {}
_loaded: bool = False

# Legacy-Pfad (Repo-Root locales/) als Fallback fuer aeltere Checkouts.
_LEGACY_TRANSLATIONS_FILE: Path = (
    Path(__file__).resolve().parent.parent.parent / "locales" / "translations.json"
)


def _read_translations() -> Optional[str]:
    """Liest translations.json als Text.

    Suchreihenfolge:
    1. PyInstaller-Bundle (sys._MEIPASS)
    2. Paket-Daten via importlib.resources (pip install + Source-Checkout)
    3. Legacy: locales/ im Repo-Root (Entwicklungsmodus, alte Checkouts)
    """
    if getattr(sys, "frozen", False):
        bundled = (
            Path(getattr(sys, "_MEIPASS", ""))
            / "rinnsal" / "i18n" / "locales" / "translations.json"
        )
        if bundled.exists():
            return bundled.read_text(encoding="utf-8")
    try:
        res = resources.files(__package__).joinpath("locales/translations.json")
        if res.is_file():
            return res.read_text(encoding="utf-8")
    except Exception:
        pass
    if _LEGACY_TRANSLATIONS_FILE.exists():
        return _LEGACY_TRANSLATIONS_FILE.read_text(encoding="utf-8")
    return None


def _load():
    global _translations, _loaded
    _loaded = True
    try:
        raw = _read_translations()
        if raw is None:
            _translations = {}
            return
        data = json.loads(raw)
        _translations = {k: v for k, v in data.items() if not k.startswith('_')}
    except Exception:
        _translations = {}


def t(key: str, **kwargs) -> str:
    """Übersetzt einen Key. Fallback: en -> de -> Key selbst."""
    if not _loaded:
        _load()

    entry = _translations.get(key)
    if entry:
        value = entry.get(_current_lang)
        if value:
            return value.format(**kwargs) if kwargs else value
        for fb in FALLBACK_CHAIN:
            value = entry.get(fb)
            if value:
                return value.format(**kwargs) if kwargs else value
    return key


def set_language(lang: str):
    global _current_lang
    if lang in SUPPORTED_LANGUAGES:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def get_supported_languages() -> List[str]:
    return list(SUPPORTED_LANGUAGES)


def get_missing(lang: str = None) -> Dict[str, List[str]]:
    """Gibt Keys ohne Übersetzung zurück."""
    if not _loaded:
        _load()
    if lang and lang in SUPPORTED_LANGUAGES:
        return {lang: [k for k, v in _translations.items() if not v.get(lang)]}
    return {
        l: [k for k, v in _translations.items() if not v.get(l)]
        for l in SUPPORTED_LANGUAGES if l != 'de'
    }
