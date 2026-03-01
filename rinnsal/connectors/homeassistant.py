# -*- coding: utf-8 -*-
"""
HomeAssistantConnector -- Home Assistant REST-API Connector
=============================================================

Geraete, Sensoren, Automationen steuern.
Based on BACH HomeAssistantConnector.

Author: Lukas Geiger
License: MIT
"""
import json
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any

from .base import BaseConnector, ConnectorConfig, ConnectorStatus, Message


class HomeAssistantConnector(BaseConnector):
    """Home Assistant REST-API Connector."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._token = config.auth_config.get("access_token", "")
        self._base_url = config.endpoint.rstrip("/")
        self._ha_version = None

    def connect(self) -> bool:
        """Verbindung via /api/ pruefen."""
        if not self._token or not self._base_url:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        result = self._api_call("GET", "/api/")
        if result and "message" in result:
            self._ha_version = result.get("message", "")
            self._status = ConnectorStatus.CONNECTED
            return True

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Notification an HA senden."""
        content = self._tag_content(content)
        return self.call_service("notify", recipient, {"message": content})

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """HA hat kein Message-System."""
        return []

    # --- HA-spezifische Methoden ---

    def get_states(self) -> List[Dict]:
        """Alle Entity-States abrufen."""
        result = self._api_call("GET", "/api/states")
        return result if isinstance(result, list) else []

    def get_state(self, entity_id: str) -> Optional[Dict]:
        """Status einer Entity abrufen."""
        return self._api_call("GET", f"/api/states/{entity_id}")

    def call_service(self, domain: str, service: str,
                     data: Dict[str, Any] = None) -> bool:
        """Service aufrufen (z.B. light.turn_on)."""
        result = self._api_call("POST", f"/api/services/{domain}/{service}", data)
        return result is not None

    def get_history(self, entity_id: str, hours: int = 24) -> List:
        """Historie einer Entity abrufen."""
        from datetime import datetime, timedelta
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
        result = self._api_call("GET",
                                f"/api/history/period/{since}?filter_entity_id={entity_id}")
        return result if isinstance(result, list) else []

    def fire_event(self, event_type: str, data: Dict = None) -> bool:
        """Event feuern."""
        result = self._api_call("POST", f"/api/events/{event_type}", data)
        return result is not None

    # --- Internal ---

    def _api_call(self, method: str, endpoint: str, data: dict = None):
        url = f"{self._base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError:
            return None
        except urllib.error.URLError:
            return None
