# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.memory"""
import unittest
from rinnsal.memory.client import MemoryClient


class TestMemoryClient(unittest.TestCase):
    def setUp(self):
        self.client = MemoryClient(db_path=":memory:", agent_id="test")

    def test_add_and_get_fact(self):
        result = self.client.add_fact("system", "os", "Windows 11")
        self.assertTrue(result['merged'])
        facts = self.client.get_facts(category="system")
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]['key'], "os")
        self.assertEqual(facts[0]['value'], "Windows 11")

    def test_confidence_merge(self):
        self.client.add_fact("system", "os", "Linux", confidence=0.9)
        result = self.client.add_fact("system", "os", "Windows", confidence=0.5)
        self.assertFalse(result['merged'])
        facts = self.client.get_facts(category="system")
        self.assertEqual(facts[0]['value'], "Linux")

    def test_confidence_override(self):
        self.client.add_fact("system", "os", "Linux", confidence=0.5)
        result = self.client.add_fact("system", "os", "Windows", confidence=0.9)
        self.assertTrue(result['merged'])
        facts = self.client.get_facts(category="system")
        self.assertEqual(facts[0]['value'], "Windows")

    def test_invalid_category(self):
        with self.assertRaises(ValueError):
            self.client.add_fact("invalid", "key", "value")

    def test_add_and_get_working(self):
        result = self.client.add_working("Test-Notiz", type="note", priority=5)
        self.assertEqual(result['type'], 'note')
        notes = self.client.get_working()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['content'], "Test-Notiz")

    def test_clear_working(self):
        self.client.add_working("Notiz 1")
        self.client.add_working("Notiz 2")
        count = self.client.clear_working()
        self.assertEqual(count, 2)
        notes = self.client.get_working()
        self.assertEqual(len(notes), 0)

    def test_add_and_get_lesson(self):
        result = self.client.add_lesson(
            "UTF-8 Bug", "cp1252 Encoding", "PYTHONIOENCODING=utf-8",
            severity="high"
        )
        self.assertEqual(result['severity'], 'high')
        lessons = self.client.get_lessons()
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0]['title'], "UTF-8 Bug")

    def test_invalid_severity(self):
        with self.assertRaises(ValueError):
            self.client.add_lesson("Title", "Problem", "Solution", severity="unknown")

    def test_session(self):
        session = self.client.start_session(task="Test-Task")
        self.assertIn('id', session)
        success = self.client.end_session(session['id'], handoff_notes="Alles OK")
        self.assertTrue(success)

    def test_generate_context(self):
        self.client.add_fact("system", "os", "Windows 11", confidence=0.9)
        self.client.add_working("Aktueller Task")
        ctx = self.client.generate_context()
        self.assertIn("Windows 11", ctx)
        self.assertIn("Aktueller Task", ctx)

    def test_status(self):
        self.client.add_fact("system", "os", "Win")
        status = self.client.get_status()
        self.assertEqual(status['facts_count'], 1)

    def test_multi_agent(self):
        opus = MemoryClient(db_path=":memory:", agent_id="opus")
        opus.add_fact("project", "lang", "Python")
        facts = opus.get_facts(agent_id="opus")
        self.assertEqual(len(facts), 1)

    def test_changes_since(self):
        self.client.add_fact("system", "os", "Win")
        changes = self.client.get_changes_since("2000-01-01T00:00:00")
        self.assertEqual(len(changes['facts']), 1)


class TestMemoryAPI(unittest.TestCase):
    def setUp(self):
        from rinnsal.memory import api
        self.api = api
        self.api.init(db_path=":memory:", agent_id="test-api")

    def test_fact_and_facts(self):
        self.api.fact("system", "test", "value")
        facts = self.api.facts(category="system")
        self.assertEqual(len(facts), 1)

    def test_note_and_working(self):
        self.api.note("Test-Notiz")
        notes = self.api.working()
        self.assertEqual(len(notes), 1)

    def test_remember_and_forget(self):
        self.api.remember("key1", "value1")
        facts = self.api.facts(category="project")
        self.assertEqual(len(facts), 1)
        self.assertTrue(self.api.forget("key1"))
        facts = self.api.facts(category="project")
        self.assertEqual(len(facts), 0)

    def test_context(self):
        self.api.fact("system", "os", "Win", confidence=0.9)
        ctx = self.api.context()
        self.assertIn("os", ctx)

    def test_status(self):
        s = self.api.status()
        self.assertIn('facts_count', s)


if __name__ == '__main__':
    unittest.main()
