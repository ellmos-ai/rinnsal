# -*- coding: utf-8 -*-
"""Tests fuer rinnsal.connectors"""
import unittest
from rinnsal.connectors.base import (
    BaseConnector, ConnectorConfig, ConnectorStatus, Message
)
from rinnsal.connectors import list_connectors, CONNECTOR_REGISTRY


class TestConnectorBase(unittest.TestCase):
    def test_message_creation(self):
        msg = Message(
            channel="telegram",
            sender="123",
            content="Hallo",
            timestamp="2026-03-01T12:00:00"
        )
        self.assertEqual(msg.channel, "telegram")
        self.assertEqual(msg.direction, "in")
        self.assertEqual(msg.attachments, [])

    def test_connector_config(self):
        config = ConnectorConfig(
            name="test",
            connector_type="telegram",
            auth_type="api_key",
            auth_config={"bot_token": "123:ABC"}
        )
        self.assertEqual(config.name, "test")
        self.assertEqual(config.connector_type, "telegram")

    def test_connector_status_enum(self):
        self.assertEqual(ConnectorStatus.CONNECTED.value, "connected")
        self.assertEqual(ConnectorStatus.ERROR.value, "error")


class TestTelegramConnector(unittest.TestCase):
    def test_init_without_token(self):
        from rinnsal.connectors.telegram import TelegramConnector
        config = ConnectorConfig(
            name="test_tg",
            connector_type="telegram",
            auth_type="api_key",
            auth_config={}
        )
        tg = TelegramConnector(config)
        self.assertEqual(tg._bot_token, "")
        result = tg.connect()
        self.assertFalse(result)
        self.assertEqual(tg.status, ConnectorStatus.ERROR)

    def test_disconnect(self):
        from rinnsal.connectors.telegram import TelegramConnector
        config = ConnectorConfig(name="test", connector_type="telegram")
        tg = TelegramConnector(config)
        self.assertTrue(tg.disconnect())
        self.assertEqual(tg.status, ConnectorStatus.DISCONNECTED)

    def test_tag_content(self):
        from rinnsal.connectors.telegram import TelegramConnector
        config = ConnectorConfig(
            name="test", connector_type="telegram",
            options={"sender_tag": "BOT"}
        )
        tg = TelegramConnector(config)
        self.assertEqual(tg._tag_content("Hallo"), "[BOT] Hallo")
        self.assertEqual(tg._tag_content(""), "")


class TestDiscordConnector(unittest.TestCase):
    def test_init_without_credentials(self):
        from rinnsal.connectors.discord import DiscordConnector
        config = ConnectorConfig(name="test", connector_type="discord")
        dc = DiscordConnector(config)
        result = dc.connect()
        self.assertFalse(result)

    def test_webhook_mode_connect(self):
        from rinnsal.connectors.discord import DiscordConnector
        config = ConnectorConfig(
            name="test", connector_type="discord",
            endpoint="https://discord.com/api/webhooks/test"
        )
        dc = DiscordConnector(config)
        result = dc.connect()
        self.assertTrue(result)
        self.assertEqual(dc.status, ConnectorStatus.CONNECTED)


class TestHomeAssistantConnector(unittest.TestCase):
    def test_init_without_credentials(self):
        from rinnsal.connectors.homeassistant import HomeAssistantConnector
        config = ConnectorConfig(name="test", connector_type="homeassistant")
        ha = HomeAssistantConnector(config)
        result = ha.connect()
        self.assertFalse(result)

    def test_get_messages_empty(self):
        from rinnsal.connectors.homeassistant import HomeAssistantConnector
        config = ConnectorConfig(
            name="test", connector_type="homeassistant",
            endpoint="http://localhost:8123",
            auth_config={"access_token": "fake"}
        )
        ha = HomeAssistantConnector(config)
        self.assertEqual(ha.get_messages(), [])


class TestConnectorRegistry(unittest.TestCase):
    def test_list_connectors(self):
        connectors = list_connectors()
        self.assertIn("telegram", connectors)
        self.assertIn("discord", connectors)
        self.assertIn("homeassistant", connectors)

    def test_registry_has_all(self):
        self.assertEqual(len(CONNECTOR_REGISTRY), 3)


if __name__ == '__main__':
    unittest.main()
