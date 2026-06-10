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
from pathlib import Path
from typing import Dict, List

SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'zh', 'ja', 'ru']
DEFAULT_LANGUAGE = 'de'
FALLBACK_CHAIN = ['en', 'de']

_current_lang: str = DEFAULT_LANGUAGE
_translations: Dict[str, Dict[str, str]] = {}
_translations_file: Path = Path(__file__).parent.parent.parent / "locales" / "translations.json"


def _load():
    global _translations
    if _translations_file.exists():
        try:
            with open(_translations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _translations = {k: v for k, v in data.items() if not k.startswith('_')}
        except Exception:
            _translations = {}


def t(key: str, **kwargs) -> str:
    """Übersetzt einen Key. Fallback: en -> de -> Key selbst."""
    if not _translations:
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
    if not _translations:
        _load()
    if lang and lang in SUPPORTED_LANGUAGES:
        return {lang: [k for k, v in _translations.items() if not v.get(lang)]}
    return {
        l: [k for k, v in _translations.items() if not v.get(l)]
        for l in SUPPORTED_LANGUAGES if l != 'de'
    }
