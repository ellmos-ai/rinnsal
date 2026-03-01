# -*- coding: utf-8 -*-
"""
TelegramConnector -- Telegram Bot API Connector
=================================================

Implementiert BaseConnector fuer Telegram Bot API.
Benoetigt: Bot-Token von @BotFather (via ENV: RINNSAL_TELEGRAM_TOKEN)

Based on BACH TelegramConnector. BACH-spezifische Abhaengigkeiten entfernt:
- _load_from_secrets_table() entfernt (bach.db)
- _get_stt() / Voice-Transkription entfernt (BACH-Service)
- Secrets via ENV statt DB

Author: Lukas Geiger
License: MIT
"""
import json
import os
import sys
import socket
import tempfile
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Tuple

from .base import BaseConnector, ConnectorConfig, ConnectorStatus, Message


class TelegramConnector(BaseConnector):
    """Telegram Bot API Connector mit Polling-Runtime."""

    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._bot_token = config.auth_config.get("bot_token", "")
        self._owner_chat_id = str(config.options.get("owner_chat_id", ""))
        self._last_update_id = int(config.auth_config.get("last_update_id", 0))
        self._bot_info = None
        self._polling = False

    def connect(self) -> bool:
        """Verbindung pruefen via getMe."""
        if not self._bot_token:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        try:
            result = self._api_call("getMe")
            if result:
                self._bot_info = result
                self._status = ConnectorStatus.CONNECTED
                return True
        except Exception:
            pass

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        """Telegram benoetigt keinen expliziten Disconnect."""
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht an chat_id senden."""
        try:
            content = self._tag_content(content)
            params = {
                "chat_id": recipient or self._owner_chat_id,
                "text": content,
                "parse_mode": "Markdown"
            }
            result = self._api_call("sendMessage", params, retries=1)

            if result is None:
                params = {
                    "chat_id": recipient or self._owner_chat_id,
                    "text": content
                }
                result = self._api_call("sendMessage", params)

            return result is not None
        except Exception as e:
            print(f"[Telegram send_message Error] {type(e).__name__}: {e}", file=sys.stderr)
            return False

    def send_file(self, recipient: str, file_path: str, caption: str = "") -> bool:
        """Datei (Dokument) an chat_id senden via sendDocument."""
        try:
            import mimetypes

            chat_id = recipient or self._owner_chat_id
            if not os.path.exists(file_path):
                print(f"[Telegram send_file Error] Datei nicht gefunden: {file_path}", file=sys.stderr)
                return False

            boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
            url = self.API_BASE.format(token=self._bot_token, method="sendDocument")

            body = []
            body.append(f'--{boundary}'.encode())
            body.append(b'Content-Disposition: form-data; name="chat_id"')
            body.append(b'')
            body.append(str(chat_id).encode())

            if caption:
                body.append(f'--{boundary}'.encode())
                body.append(b'Content-Disposition: form-data; name="caption"')
                body.append(b'')
                body.append(caption.encode('utf-8'))

            filename = os.path.basename(file_path)
            try:
                filename.encode('ascii')
                filename_header = f'filename="{filename}"'
            except UnicodeEncodeError:
                import urllib.parse
                filename_ascii = filename.encode('ascii', 'replace').decode('ascii').replace('?', '_')
                filename_utf8 = urllib.parse.quote(filename, safe='')
                filename_header = f'filename="{filename_ascii}"; filename*=UTF-8\'\'{filename_utf8}'
            mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            body.append(f'--{boundary}'.encode())
            body.append(f'Content-Disposition: form-data; name="document"; {filename_header}'.encode())
            body.append(f'Content-Type: {mime}'.encode())
            body.append(b'')
            with open(file_path, 'rb') as f:
                body.append(f.read())

            body.append(f'--{boundary}--'.encode())
            body.append(b'')

            data = b'\r\n'.join(body)

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("ok", False)

        except Exception as e:
            print(f"[Telegram send_file Error] {type(e).__name__}: {e}", file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Neue Nachrichten via getUpdates abrufen."""
        try:
            params = {
                "offset": self._last_update_id + 1,
                "limit": min(limit, 100),
                "timeout": 30
            }
            result = self._api_call("getUpdates", params, timeout=40)
            if not result:
                return []

            messages = []
            for update in result:
                self._last_update_id = max(self._last_update_id, update.get("update_id", 0))

                msg = update.get("message")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                sender_id = str(chat.get("id", ""))

                if self._owner_chat_id and sender_id != self._owner_chat_id:
                    continue

                from_user = msg.get("from", {})
                sender_name = from_user.get("first_name", "") + " " + from_user.get("last_name", "")

                content = msg.get("text", "")
                msg_type = "text"

                if not content:
                    voice = msg.get("voice") or msg.get("audio")
                    if voice and voice.get("file_id"):
                        msg_type = "voice"
                        duration = voice.get("duration", 0)
                        content = f"[Sprachnachricht ({duration}s)]"

                    if not content:
                        content = msg.get("caption", "")
                        if content:
                            msg_type = "caption"

                if not content:
                    continue

                messages.append(Message(
                    channel="telegram",
                    sender=sender_id,
                    content=content,
                    timestamp=datetime.fromtimestamp(
                        msg.get("date", 0)).isoformat(),
                    direction="in",
                    message_id=str(msg.get("message_id", "")),
                    metadata={
                        "chat_type": chat.get("type", ""),
                        "sender_name": sender_name.strip(),
                        "update_id": update.get("update_id", 0),
                        "message_type": msg_type,
                    }
                ))

            return messages
        except Exception as e:
            print(f"[Telegram get_messages Error] {type(e).__name__}: {e}", file=sys.stderr)
            return []

    # --- Polling Runtime ---

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 5.0, stop_event: threading.Event = None):
        """Blockierender Polling-Loop."""
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                messages = self.get_messages()
                for msg in messages:
                    try:
                        on_message(msg)
                    except Exception as e:
                        print(f"[Telegram on_message callback Error] {type(e).__name__}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"[Telegram poll_loop Error] {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(interval)

    def poll_threaded(self, on_message: Callable[[Message], None],
                      interval: float = 5.0) -> Tuple[threading.Thread, threading.Event]:
        """Startet Polling in eigenem Thread. Gibt (Thread, StopEvent) zurueck."""
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True, name="rinnsal-telegram-poll")
        thread.start()
        return thread, stop_event

    # --- Internal ---

    def _api_call(self, method: str, params: dict = None, retries: int = 3, timeout: int = 15) -> any:
        """Telegram Bot API aufrufen (stdlib urllib, mit Retry)."""
        url = self.API_BASE.format(token=self._bot_token, method=method)

        for attempt in range(retries):
            if params:
                data = json.dumps(params, ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json; charset=utf-8"})
            else:
                req = urllib.request.Request(url)

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("ok"):
                        return body.get("result")
                    error_msg = body.get("description", "Unknown error")
                    if attempt == retries - 1:
                        print(f"[Telegram API Error] {method}: {error_msg}", file=sys.stderr)
                    return None
            except urllib.error.HTTPError as e:
                if attempt == retries - 1:
                    print(f"[Telegram HTTP Error] {method}: HTTP {e.code}", file=sys.stderr)
                return None
            except urllib.error.URLError as e:
                if attempt == retries - 1:
                    print(f"[Telegram Network Error] {method}: {e.reason}", file=sys.stderr)
                return None
            except socket.timeout:
                if method == "getUpdates":
                    return []
                if attempt == retries - 1:
                    print(f"[Telegram Timeout] {method}", file=sys.stderr)
                return None
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                print(f"[Telegram Exception] {method}: {type(e).__name__}: {e}", file=sys.stderr)
                return None
