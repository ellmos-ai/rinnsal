# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.auto"""
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest import mock

from rinnsal.auto.runner import ClaudeRunner
from rinnsal.auto.state import ChainState
from rinnsal.auto import config as auto_config
from rinnsal.auto.config import DEFAULT_CHAIN_CONFIG, DEFAULT_LINK, new_link


class TestClaudeRunner(unittest.TestCase):
    def test_init_defaults(self):
        runner = ClaudeRunner()
        self.assertEqual(runner.model, "claude-sonnet-4-6")
        self.assertEqual(runner.timeout, 1800)
        self.assertIn("Read", runner.allowed_tools)

    def test_build_cmd(self):
        runner = ClaudeRunner(model="claude-opus-4-6")
        cmd = runner._build_cmd("Test prompt")
        self.assertIn("claude", cmd)
        self.assertIn("claude-opus-4-6", cmd)
        self.assertIn("Test prompt", cmd)

    def test_build_cmd_continue(self):
        runner = ClaudeRunner()
        cmd = runner._build_cmd("prompt", continue_conversation=True)
        self.assertIn("--continue", cmd)

    def test_build_cmd_fallback(self):
        runner = ClaudeRunner(fallback_model="claude-haiku-4-5-20251001")
        cmd = runner._build_cmd("prompt")
        self.assertIn("--fallback-model", cmd)
        self.assertIn("claude-haiku-4-5-20251001", cmd)

    def test_build_env(self):
        runner = ClaudeRunner()
        env = runner._build_env()
        self.assertEqual(env["PYTHONIOENCODING"], "utf-8")
        self.assertNotIn("CLAUDECODE", env)


class TestChainState(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.state = ChainState("test-chain", base_dir=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_initial_status(self):
        self.assertEqual(self.state.get_status(), "UNKNOWN")

    def test_set_get_status(self):
        self.state.set_status("RUNNING")
        self.assertEqual(self.state.get_status(), "RUNNING")

    def test_round_counter(self):
        self.assertEqual(self.state.get_round(), 0)
        self.state.increment_round()
        self.assertEqual(self.state.get_round(), 1)
        self.state.increment_round()
        self.assertEqual(self.state.get_round(), 2)

    def test_handoff(self):
        self.state.write_handoff("Test Handoff Content")
        self.assertEqual(self.state.get_handoff(), "Test Handoff Content")

    def test_stop_request(self):
        self.assertFalse(self.state.is_stop_requested())
        self.state.request_stop("Test Stop")
        self.assertTrue(self.state.is_stop_requested())
        self.assertEqual(self.state.get_stop_reason(), "Test Stop")

    def test_check_shutdown_manual(self):
        self.state.request_stop("Manual")
        stop, reason = self.state.check_shutdown({})
        self.assertTrue(stop)
        self.assertIn("MANUAL_STOP", reason)

    def test_check_shutdown_max_rounds(self):
        for _ in range(5):
            self.state.increment_round()
        stop, reason = self.state.check_shutdown({"max_rounds": 5})
        self.assertTrue(stop)
        self.assertIn("MAX_ROUNDS", reason)

    def test_check_shutdown_no_stop(self):
        self.state.set_status("RUNNING")
        stop, reason = self.state.check_shutdown({"max_rounds": 100})
        self.assertFalse(stop)

    def test_skip_protection(self):
        self.state.write_handoff("Langer originaler Handoff mit vielen Details " * 20)
        original = self.state.get_handoff()
        self.state.write_handoff("SKIPPED - nichts zu tun")
        restored = self.state.protect_handoff_from_skip("worker-1", original)
        self.assertTrue(restored)
        self.assertEqual(self.state.get_handoff(), original)

    def test_reset(self):
        self.state.set_status("RUNNING")
        self.state.increment_round()
        self.state.increment_round()
        self.state.reset()
        self.assertEqual(self.state.get_status(), "READY")
        self.assertEqual(self.state.get_round(), 0)


class TestAutoConfig(unittest.TestCase):
    def test_default_chain_config(self):
        self.assertEqual(DEFAULT_CHAIN_CONFIG['mode'], 'loop')
        self.assertEqual(DEFAULT_CHAIN_CONFIG['max_rounds'], 100)

    def test_default_link(self):
        self.assertEqual(DEFAULT_LINK['role'], 'worker')

    def test_new_link(self):
        link = new_link(name="test", role="reviewer", model="claude-opus-4-6")
        self.assertEqual(link['name'], 'test')
        self.assertEqual(link['role'], 'reviewer')
        self.assertEqual(link['model'], 'claude-opus-4-6')
        self.assertFalse(link['until_full'])


class TestHomePlaceholders(unittest.TestCase):
    def test_windows_home(self):
        from rinnsal.auto.chain import _home_placeholders
        native, bash = _home_placeholders("C:\\Users\\Foo\\")
        self.assertEqual(native, "C:\\Users\\Foo")
        self.assertEqual(bash, "/c/Users/Foo")

    def test_windows_home_uppercase_drive(self):
        from rinnsal.auto.chain import _home_placeholders
        native, bash = _home_placeholders("D:\\Home\\Bar")
        self.assertEqual(native, "D:\\Home\\Bar")
        self.assertEqual(bash, "/d/Home/Bar")

    def test_posix_home(self):
        from rinnsal.auto.chain import _home_placeholders
        native, bash = _home_placeholders("/home/foo/")
        self.assertEqual(native, "/home/foo")
        self.assertEqual(bash, "/home/foo")

    def test_macos_home(self):
        from rinnsal.auto.chain import _home_placeholders
        native, bash = _home_placeholders("/Users/lukas")
        self.assertEqual(native, "/Users/lukas")
        self.assertEqual(bash, "/Users/lukas")

    def test_posix_path_with_colon_not_treated_as_drive(self):
        from rinnsal.auto.chain import _home_placeholders
        native, bash = _home_placeholders("/home/we:ird")
        self.assertEqual(native, "/home/we:ird")
        self.assertEqual(bash, "/home/we:ird")


class TestPathNormalization(unittest.TestCase):
    def test_no_hardcoded_homes(self):
        # Ohne Config/ENV duerfen keine Home-Pfade bekannt sein (Privacy).
        with mock.patch.object(auto_config, "load_config", return_value={}), \
             mock.patch.dict(os.environ, {"RINNSAL_KNOWN_HOMES": ""}):
            self.assertEqual(auto_config._get_known_user_homes(), [])

    def test_known_homes_from_env(self):
        with mock.patch.object(auto_config, "load_config", return_value={}), \
             mock.patch.dict(os.environ, {"RINNSAL_KNOWN_HOMES": "C:\\Users\\Alice\\"}):
            self.assertEqual(auto_config._get_known_user_homes(), ["C:\\Users\\Alice\\"])

    def test_known_homes_from_config(self):
        cfg = {"auto": {"known_user_homes": ["/home/alice/"]}}
        with mock.patch.object(auto_config, "load_config", return_value=cfg), \
             mock.patch.dict(os.environ, {"RINNSAL_KNOWN_HOMES": ""}):
            self.assertEqual(auto_config._get_known_user_homes(), ["/home/alice/"])

    def test_normalize_replaces_known_home(self):
        obj = {"path": "C:\\Users\\Alice\\project\\x.txt", "n": 1}
        result = auto_config._normalize_paths(obj, known_homes=["C:\\Users\\Alice\\"])
        self.assertEqual(result["path"], auto_config._ACTUAL_HOME + "project\\x.txt")
        self.assertEqual(result["n"], 1)

    def test_normalize_without_known_homes_is_noop(self):
        obj = "C:\\Users\\Somebody\\foo"
        self.assertEqual(auto_config._normalize_paths(obj, known_homes=[]), obj)


if __name__ == '__main__':
    unittest.main()
