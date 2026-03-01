# -*- coding: utf-8 -*-
"""
Connector-Config aus JSON + ENV-Variablen.

Secrets werden ausschliesslich via ENV geladen.
"""
import os
from typing import Optional

from .base import ConnectorConfig
from ..shared.config import load_config


def connector_config_from_settings(
    connector_type: str,
    name: Optional[str] = None,
) -> ConnectorConfig:
    """Erstellt ConnectorConfig aus rinnsal.json + ENV-Variablen."""
    config = load_config()
    conn_settings = config.get("connectors", {}).get(connector_type, {})

    if connector_type == "telegram":
        token_env = conn_settings.get("bot_token_env", "RINNSAL_TELEGRAM_TOKEN")
        bot_token = os.environ.get(token_env, "")
        owner_chat_id = conn_settings.get("owner_chat_id", "")

        return ConnectorConfig(
            name=name or "telegram_main",
            connector_type="telegram",
            auth_type="api_key",
            auth_config={"bot_token": bot_token},
            options={"owner_chat_id": owner_chat_id},
        )

    elif connector_type == "discord":
        token_env = conn_settings.get("bot_token_env", "RINNSAL_DISCORD_TOKEN")
        bot_token = os.environ.get(token_env, "")
        endpoint = conn_settings.get("webhook_url", "")
        default_channel = conn_settings.get("default_channel", "")

        return ConnectorConfig(
            name=name or "discord_main",
            connector_type="discord",
            endpoint=endpoint,
            auth_type="api_key",
            auth_config={"bot_token": bot_token},
            options={"default_channel": default_channel},
        )

    elif connector_type == "homeassistant":
        token_env = conn_settings.get("access_token_env", "RINNSAL_HA_TOKEN")
        access_token = os.environ.get(token_env, "")
        endpoint = conn_settings.get("endpoint", "")

        return ConnectorConfig(
            name=name or "ha_main",
            connector_type="homeassistant",
            endpoint=endpoint,
            auth_type="token",
            auth_config={"access_token": access_token},
        )

    raise ValueError(f"Unbekannter Connector-Typ: {connector_type}")
