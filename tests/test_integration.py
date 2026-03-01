# -*- coding: utf-8 -*-
"""Integrationstests fuer rinnsal"""
import unittest
from rinnsal.shared.events import EventBus
from rinnsal.shared.config import DEFAULT_CONFIG, _deep_merge


class TestEventBus(unittest.TestCase):
    def test_emit_and_receive(self):
        bus = EventBus()
        received = []
        bus.on("test", lambda data: received.append(data))
        bus.emit("test", {"key": "value"})
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['key'], 'value')

    def test_multiple_handlers(self):
        bus = EventBus()
        results = []
        bus.on("evt", lambda d: results.append("a"))
        bus.on("evt", lambda d: results.append("b"))
        bus.emit("evt")
        self.assertEqual(results, ["a", "b"])

    def test_off(self):
        bus = EventBus()
        results = []
        handler = lambda d: results.append(1)
        bus.on("evt", handler)
        bus.off("evt", handler)
        bus.emit("evt")
        self.assertEqual(len(results), 0)

    def test_clear(self):
        bus = EventBus()
        bus.on("evt", lambda d: None)
        bus.clear()
        self.assertEqual(len(bus._handlers), 0)

    def test_handler_error_ignored(self):
        bus = EventBus()
        bus.on("evt", lambda d: 1/0)
        bus.on("evt", lambda d: None)
        bus.emit("evt")  # Sollte nicht crashen


class TestConfigMerge(unittest.TestCase):
    def test_deep_merge(self):
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 99}, "e": 4}
        result = _deep_merge(base, override)
        self.assertEqual(result['a']['b'], 99)
        self.assertEqual(result['a']['c'], 2)
        self.assertEqual(result['e'], 4)

    def test_default_config_structure(self):
        self.assertIn('memory', DEFAULT_CONFIG)
        self.assertIn('connectors', DEFAULT_CONFIG)
        self.assertIn('auto', DEFAULT_CONFIG)


class TestPackageImports(unittest.TestCase):
    def test_import_rinnsal(self):
        import rinnsal
        self.assertEqual(rinnsal.__version__, "0.1.0")

    def test_import_memory(self):
        from rinnsal.memory import MemoryClient, api
        self.assertIsNotNone(MemoryClient)

    def test_import_connectors(self):
        from rinnsal.connectors import load_connector, list_connectors
        self.assertIsNotNone(load_connector)

    def test_import_auto(self):
        from rinnsal.auto.runner import ClaudeRunner
        from rinnsal.auto.state import ChainState
        self.assertIsNotNone(ClaudeRunner)
        self.assertIsNotNone(ChainState)


if __name__ == '__main__':
    unittest.main()
