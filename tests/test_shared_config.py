# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.shared.config"""
import os
import unittest
from pathlib import Path
from unittest import mock

from rinnsal.shared import config as shared_config


class TestDefaultDbPath(unittest.TestCase):
    def test_env_var_wins(self):
        with mock.patch.dict(os.environ, {"RINNSAL_DB": "custom-env.db"}):
            self.assertTrue(
                shared_config.get_default_db_path().endswith("custom-env.db")
            )

    def test_config_value_used(self):
        cfg = {"memory": {"db_path": "from-config.db"}}
        with mock.patch.dict(os.environ, {"RINNSAL_DB": ""}), \
             mock.patch.object(shared_config, "load_config", return_value=cfg):
            self.assertTrue(
                shared_config.get_default_db_path().endswith("from-config.db")
            )

    def test_default_is_home_rinnsal(self):
        with mock.patch.dict(os.environ, {"RINNSAL_DB": ""}), \
             mock.patch.object(shared_config, "load_config", return_value={}):
            result = shared_config.get_default_db_path()
            expected = str(Path.home() / ".rinnsal" / "rinnsal.db")
            self.assertEqual(result, expected)

    def test_env_expands_user(self):
        with mock.patch.dict(os.environ, {"RINNSAL_DB": "~/somewhere/x.db"}):
            result = shared_config.get_default_db_path()
            self.assertNotIn("~", result)
            self.assertTrue(result.startswith(str(Path.home())))


if __name__ == '__main__':
    unittest.main()
