# -*- coding: utf-8 -*-
"""
DiscordConnector -- Discord Bot/Webhook Connector
===================================================

Dual-Modus: Bot-API (bidirektional) oder Webhook (nur senden).
Based on BACH DiscordConnector.

Author: Lukas Geiger
License: MIT
"""
import json
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Callable, Tuple

from .base import BaseConnector, ConnectorConfig, ConnectorStatus, Message


class DiscordConnector(BaseConnector):
    """Discord Bot/Webhook Connector mit Polling-Runtime."""

    API_BASE = "https://discord.com/api/v10"

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._bot_token = config.auth_config.get("bot_token", "")
        self._webhook_url = config.endpoint
        self._bot_info = None
        self._last_message_id = config.options.get("last_message_id", "")
        self._polling = False

    def connect(self) -> bool:
        """Verbindung pruefen via /users/@me."""
        if not self._bot_token and not self._webhook_url:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING

        if self._bot_token:
            try:
                result = self._api_call("GET", "/users/@me")
                if result:
                    self._bot_info = result
                    self._status = ConnectorStatus.CONNECTED
                    return True
            except Exception:
                pass
        elif self._webhook_url:
            self._status = ConnectorStatus.CONNECTED
            return True

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht an Channel senden (via Bot oder Webhook)."""
        content = self._tag_content(content)
        if self._webhook_url:
            return self._send_webhook(content)
        if self._bot_token:
            return self._send_bot(recipient, content)
        return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Nachrichten aus einem Channel abrufen (nur Bot-Modus)."""
        if not self._bot_token:
            return []

        channel_id = self.config.options.get("default_channel", "")
        if not channel_id:
            return []

        try:
            params = f"?limit={min(limit, 100)}"
            if since:
                params += f"&after={since}"

            result = self._api_call("GET", f"/channels/{channel_id}/messages{params}")
            if not result or not isinstance(result, list):
                return []

            messages = []
            for msg in result:
                author = msg.get("author", {})
                if self._bot_info and author.get("id") == self._bot_info.get("id"):
                    continue
                msg_id = msg.get("id", "")
                messages.append(Message(
                    channel="discord",
                    sender=author.get("username", "unknown"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", ""),
                    direction="in",
                    message_id=msg_id,
                    metadata={
                        "channel_id": msg.get("channel_id", ""),
                        "author_id": author.get("id", ""),
                        "guild_id": msg.get("guild_id", ""),
                    }
                ))
                if msg_id:
                    self._last_message_id = msg_id

            return messages
        except Exception:
            return []

    def get_new_messages(self) -> List[Message]:
        """Nur neue Nachrichten seit letztem Poll abrufen (inkrementell)."""
        if not self._bot_token:
            return []

        channel_id = self.config.options.get("default_channel", "")
        if not channel_id:
            return []

        try:
            params = "?limit=50"
            if self._last_message_id:
                params += f"&after={self._last_message_id}"

            result = self._api_call("GET", f"/channels/{channel_id}/messages{params}")
            if not result or not isinstance(result, list):
                return []

            messages = []
            for msg in result:
                author = msg.get("author", {})
                if self._bot_info and author.get("id") == self._bot_info.get("id"):
                    continue
                msg_id = msg.get("id", "")
                messages.append(Message(
                    channel="discord",
                    sender=author.get("username", "unknown"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", ""),
                    direction="in",
                    message_id=msg_id,
                    metadata={
                        "channel_id": msg.get("channel_id", ""),
                        "author_id": author.get("id", ""),
                        "guild_id": msg.get("guild_id", ""),
                    }
                ))
                if msg_id:
                    self._last_message_id = msg_id

            return messages
        except Exception:
            return []

    # --- Polling Runtime ---

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 10.0, stop_event: threading.Event = None):
        """Blockierender Polling-Loop fuer eingehende Nachrichten."""
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                messages = self.get_new_messages()
                for msg in messages:
                    on_message(msg)
            except Exception:
                pass
            time.sleep(interval)

    def poll_threaded(self, on_message: Callable[[Message], None],
                      interval: float = 10.0) -> Tuple[threading.Thread, threading.Event]:
        """Startet Polling in eigenem Thread."""
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True, name="rinnsal-discord-poll")
        thread.start()
        return thread, stop_event

    # --- Internal ---

    def _api_call(self, method: str, endpoint: str, data: dict = None):
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bot {self._bot_token}",
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

    def _send_bot(self, channel_id: str, content: str) -> bool:
        result = self._api_call("POST", f"/channels/{channel_id}/messages",
                                {"content": content})
        return result is not None

    def _send_webhook(self, content: str) -> bool:
        data = json.dumps({"content": content}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self._webhook_url, data=data,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status < 400
        except Exception:
            return False
