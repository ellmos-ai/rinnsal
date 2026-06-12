# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.i18n"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rinnsal import i18n


def _reset_i18n():
    """Setzt den Modul-State zurueck, damit _load() erneut greift."""
    i18n._translations = {}
    i18n._loaded = False
    i18n._current_lang = i18n.DEFAULT_LANGUAGE


class TestI18nPackageMode(unittest.TestCase):
    """Laden aus den Paket-Daten (importlib.resources)."""

    def setUp(self):
        _reset_i18n()

    def tearDown(self):
        _reset_i18n()

    def test_package_data_found(self):
        raw = i18n._read_translations()
        self.assertIsNotNone(raw)
        data = json.loads(raw)
        self.assertIn("status.title", data)

    def test_t_returns_translation(self):
        i18n.set_language('de')
        self.assertEqual(i18n.t('status.title'), 'Rinnsal Status')

    def test_t_fallback_chain(self):
        # es ist leer im Katalog -> Fallback auf en
        i18n.set_language('es')
        self.assertEqual(i18n.t('status.title'), 'Rinnsal Status')

    def test_t_missing_key_returns_key(self):
        self.assertEqual(i18n.t('does.not.exist'), 'does.not.exist')

    def test_t_missing_key_with_kwargs_returns_key(self):
        # Auch mit Format-Argumenten darf ein fehlender Key nicht crashen.
        self.assertEqual(i18n.t('does.not.exist', name='x'), 'does.not.exist')

    def test_set_get_language(self):
        i18n.set_language('en')
        self.assertEqual(i18n.get_language(), 'en')
        i18n.set_language('xx')  # nicht unterstuetzt -> ignoriert
        self.assertEqual(i18n.get_language(), 'en')

    def test_supported_languages(self):
        self.assertEqual(
            i18n.get_supported_languages(),
            ['de', 'en', 'es', 'zh', 'ja', 'ru']
        )


class TestI18nLegacyMode(unittest.TestCase):
    """Fallback auf locales/ im Repo-Root (Entwicklungsmodus)."""

    def setUp(self):
        _reset_i18n()

    def tearDown(self):
        _reset_i18n()

    def test_legacy_repo_root_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            legacy_file = Path(tmp) / "translations.json"
            legacy_file.write_text(json.dumps({
                "legacy.key": {"de": "Alt", "en": "Legacy"}
            }), encoding="utf-8")

            class _NoFile:
                def joinpath(self, *a):
                    return self

                def is_file(self):
                    return False

            with mock.patch.object(i18n.resources, "files", return_value=_NoFile()), \
                 mock.patch.object(i18n, "_LEGACY_TRANSLATIONS_FILE", legacy_file):
                _reset_i18n()
                self.assertEqual(i18n.t('legacy.key'), 'Alt')

    def test_no_catalog_anywhere_falls_back_to_key(self):
        class _NoFile:
            def joinpath(self, *a):
                return self

            def is_file(self):
                return False

        missing = Path(tempfile.gettempdir()) / "rinnsal-i18n-does-not-exist.json"
        with mock.patch.object(i18n.resources, "files", return_value=_NoFile()), \
             mock.patch.object(i18n, "_LEGACY_TRANSLATIONS_FILE", missing):
            _reset_i18n()
            self.assertEqual(i18n.t('status.title'), 'status.title')


if __name__ == '__main__':
    unittest.main()
