# -*- coding: utf-8 -*-
"""
Connector Base Interface
========================

Abstrakte Basisklasse fuer alle Rinnsal-Connectors.
Jeder Connector implementiert dieses Interface.

Based on BACH connector framework.

Author: Lukas Geiger
License: MIT
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ConnectorStatus(Enum):
    """Status eines Connectors."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class Message:
    """Einheitliches Nachrichtenformat fuer alle Channels."""
    channel: str            # "telegram", "discord", "homeassistant"
    sender: str             # Absender-ID
    content: str            # Nachrichtentext
    timestamp: str          # ISO-8601
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    direction: str = "in"   # "in" oder "out"
    message_id: str = ""    # Channel-spezifische ID


@dataclass
class ConnectorConfig:
    """Konfiguration fuer einen Connector."""
    name: str               # Eindeutiger Name (z.B. "telegram_main")
    connector_type: str     # "telegram", "discord", "homeassistant"
    endpoint: str = ""      # URL oder Pfad
    auth_type: str = "none" # "none", "api_key", "oauth", "token"
    auth_config: Dict[str, str] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstrakte Basisklasse fuer Rinnsal Connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self._status = ConnectorStatus.DISCONNECTED
        self._sender_tag = config.options.get("sender_tag", "")

    def _tag_content(self, content: str) -> str:
        """Fuegt Sender-Tag vor den Inhalt wenn konfiguriert."""
        if self._sender_tag and content:
            return f"[{self._sender_tag}] {content}"
        return content

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def connector_type(self) -> str:
        return self.config.connector_type

    @property
    def status(self) -> ConnectorStatus:
        return self._status

    @abstractmethod
    def connect(self) -> bool:
        """Verbindung herstellen. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def disconnect(self) -> bool:
        """Verbindung trennen. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht senden. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Nachrichten abrufen seit Zeitstempel (ISO-8601)."""
        ...

    def get_status(self) -> ConnectorStatus:
        """Aktuellen Status abfragen."""
        return self._status

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} status={self._status.value}>"
