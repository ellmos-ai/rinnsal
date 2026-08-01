# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.i18n"""
import contextlib
import io
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
        # Fehlt eine Sprache bei einem Key, greift die Kette en -> de.
        i18n._load()  # erst laden, sonst ueberschreibt der Lazy-Load den Probe-Key
        i18n._translations['fallback.probe'] = {'de': 'Deutsch', 'en': 'English'}
        i18n.set_language('es')
        self.assertEqual(i18n.t('fallback.probe'), 'English')

    def test_catalog_complete_in_all_languages(self):
        """Kein Key darf in einer der sechs Sprachen leer bleiben.

        Ohne diesen Test faellt eine fehlende Uebersetzung im Betrieb nicht auf:
        `t()` weicht still auf die Leitsprache aus.
        """
        raw = i18n._read_translations()
        data = json.loads(raw)
        missing = {
            key: [lang for lang in i18n.SUPPORTED_LANGUAGES if not entry.get(lang)]
            for key, entry in data.items()
            if not key.startswith('_')
        }
        missing = {k: v for k, v in missing.items() if v}
        self.assertEqual(missing, {}, f"Unuebersetzte Eintraege: {missing}")

    def test_status_keys_present(self):
        """Der status-Befehl darf keinen Key ausgeben, den es nicht gibt."""
        raw = json.loads(i18n._read_translations())
        for key in ('status.title', 'status.memory', 'status.tasks',
                    'status.chains', 'status.connectors', 'status.unavailable'):
            self.assertIn(key, raw)

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


class TestLanguageResolution(unittest.TestCase):
    """Sprachwahl muss fuer Nutzer erreichbar sein -- ENV, Flag, Systemsprache."""

    def setUp(self):
        _reset_i18n()

    def tearDown(self):
        _reset_i18n()

    def test_explicit_wins_over_env(self):
        with mock.patch.dict(i18n.os.environ, {i18n.LANG_ENV_VAR: 'ru'}, clear=False):
            self.assertEqual(i18n.resolve_language('ja'), 'ja')

    def test_env_var_is_used(self):
        with mock.patch.dict(i18n.os.environ, {i18n.LANG_ENV_VAR: 'es'}, clear=False):
            self.assertEqual(i18n.resolve_language(), 'es')

    def test_system_language_is_detected(self):
        env = {'LC_ALL': '', 'LC_MESSAGES': '', 'LANGUAGE': '', 'LANG': 'zh_CN.UTF-8'}
        with mock.patch.dict(i18n.os.environ, env, clear=True):
            self.assertEqual(i18n.resolve_language(), 'zh')

    def test_unsupported_values_are_skipped_not_fatal(self):
        env = {i18n.LANG_ENV_VAR: 'klingon', 'LC_ALL': '', 'LC_MESSAGES': '',
               'LANGUAGE': '', 'LANG': ''}
        with mock.patch.dict(i18n.os.environ, env, clear=True), \
             mock.patch.object(i18n.locale, 'getlocale', return_value=(None, None)):
            self.assertEqual(i18n.resolve_language(), i18n.DEFAULT_LANGUAGE)

    def test_apply_language_activates(self):
        i18n.apply_language('ja')
        self.assertEqual(i18n.get_language(), 'ja')
        self.assertEqual(i18n.t('status.title'), 'Rinnsal ステータス')

    def test_cli_lang_flag_switches_output(self):
        from rinnsal import cli
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cli.main(['--lang', 'ru', 'status'])
        self.assertIn('Статус Rinnsal', buf.getvalue())


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
