# -*- coding: utf-8 -*-
"""
Rinnsal Connectors -- Channel Abstraction
===========================================

Registry + Factory fuer Messaging-Connectors.

Usage:
    from rinnsal.connectors import load_connector
    tg = load_connector("telegram")
    tg.connect()
    tg.send_message("chat_id", "Hallo!")
"""
from typing import Optional

from .base import BaseConnector, ConnectorConfig, ConnectorStatus, Message

CONNECTOR_REGISTRY = {
    "telegram": "rinnsal.connectors.telegram.TelegramConnector",
    "discord": "rinnsal.connectors.discord.DiscordConnector",
    "homeassistant": "rinnsal.connectors.homeassistant.HomeAssistantConnector",
}


def load_connector(
    connector_type: str,
    config: Optional[ConnectorConfig] = None,
    name: Optional[str] = None,
) -> BaseConnector:
    """Factory: Erstellt einen Connector nach Typ.

    Args:
        connector_type: "telegram", "discord", "homeassistant"
        config: Optionale ConnectorConfig (sonst aus rinnsal.json + ENV)
        name: Optionaler Name fuer den Connector

    Returns:
        Initialisierte Connector-Instanz
    """
    if connector_type not in CONNECTOR_REGISTRY:
        raise ValueError(
            f"Unbekannter Connector-Typ: {connector_type}. "
            f"Verfuegbar: {list(CONNECTOR_REGISTRY.keys())}"
        )

    if config is None:
        from .config import connector_config_from_settings
        config = connector_config_from_settings(connector_type, name)

    # Lazy-Import des Connector-Moduls
    module_path, class_name = CONNECTOR_REGISTRY[connector_type].rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    connector_class = getattr(module, class_name)

    return connector_class(config)


def list_connectors() -> list[str]:
    """Gibt alle registrierten Connector-Typen zurueck."""
    return list(CONNECTOR_REGISTRY.keys())


__all__ = [
    "BaseConnector", "ConnectorConfig", "ConnectorStatus", "Message",
    "load_connector", "list_connectors",
]
