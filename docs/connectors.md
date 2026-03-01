# Connectors

Channel-Abstraktion fuer Messaging-Plattformen. Alle Connectors implementieren `BaseConnector`.

## Verfuegbare Connectors

| Connector | Protokoll | Features |
|---|---|---|
| Telegram | Bot API (urllib) | Polling, Send, File-Upload |
| Discord | REST API v10 | Bot + Webhook Dual-Modus |
| Home Assistant | REST API | States, Services, Events, History |

## Quick Start

```python
from rinnsal.connectors import load_connector

# Token via ENV setzen: export RINNSAL_TELEGRAM_TOKEN=...
tg = load_connector("telegram")
tg.connect()
tg.send_message("chat_id", "Hallo!")
```

## Manuelle Config

```python
from rinnsal.connectors.base import ConnectorConfig
from rinnsal.connectors.telegram import TelegramConnector

config = ConnectorConfig(
    name="mein_bot",
    connector_type="telegram",
    auth_type="api_key",
    auth_config={"bot_token": "123:ABC..."},
    options={"owner_chat_id": "123456789"}
)
bot = TelegramConnector(config)
bot.connect()
```

## Secrets

Alle Secrets werden via ENV-Variablen geladen:

| Variable | Connector |
|---|---|
| `RINNSAL_TELEGRAM_TOKEN` | Telegram |
| `RINNSAL_DISCORD_TOKEN` | Discord |
| `RINNSAL_HA_TOKEN` | Home Assistant |

## Eigenen Connector schreiben

```python
from rinnsal.connectors.base import BaseConnector, ConnectorConfig, Message

class MeinConnector(BaseConnector):
    def connect(self) -> bool: ...
    def disconnect(self) -> bool: ...
    def send_message(self, recipient, content, attachments=None) -> bool: ...
    def get_messages(self, since=None, limit=50) -> list[Message]: ...
```
