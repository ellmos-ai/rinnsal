# -*- coding: utf-8 -*-
"""
Minimaler Event-Bus fuer komponentenuebergreifende Kommunikation.

Verwendung:
    from rinnsal.shared.events import bus

    def on_chain_complete(data):
        print(f"Chain fertig: {data['chain_name']}")

    bus.on("chain.complete", on_chain_complete)
    bus.emit("chain.complete", {"chain_name": "test"})
"""
from typing import Callable, Any


class EventBus:
    """Einfacher synchroner Event-Bus."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        """Registriert einen Handler fuer ein Event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable) -> None:
        """Entfernt einen Handler."""
        if event in self._handlers:
            self._handlers[event] = [h for h in self._handlers[event] if h != handler]

    def emit(self, event: str, data: Any = None) -> None:
        """Feuert ein Event und ruft alle Handler auf."""
        for handler in self._handlers.get(event, []):
            try:
                handler(data)
            except Exception:
                pass  # Event-Handler duerfen den Caller nicht blockieren

    def clear(self) -> None:
        """Entfernt alle Handler."""
        self._handlers.clear()


# Globale Instanz
bus = EventBus()
