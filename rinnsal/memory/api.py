# -*- coding: utf-8 -*-
"""
Rinnsal Memory High-Level API
===============================

Convenience-Funktionen fuer schnellen Zugriff ohne explizite Client-Instanz.
Singleton-Pattern mit globaler Default-DB.

Verwendung:
    from rinnsal.memory import api

    api.init(agent_id="opus")
    api.fact("system", "os", "Windows 11")
    api.note("Aktueller Task: Feature X implementieren")
    api.lesson("Encoding-Bug", "cp1252", "PYTHONIOENCODING=utf-8")

    print(api.context())
    print(api.status())

Author: Lukas Geiger
License: MIT
"""
from pathlib import Path
from typing import Optional, List, Dict

from .client import MemoryClient

_client: Optional[MemoryClient] = None
_default_db = "rinnsal.db"


def init(
    db_path: Optional[str] = None,
    agent_id: str = "default"
) -> MemoryClient:
    """Initialisiert die globale Memory-Instanz."""
    global _client
    _client = MemoryClient(
        db_path=db_path or _default_db,
        agent_id=agent_id
    )
    return _client


def get_client() -> MemoryClient:
    """Gibt die globale Client-Instanz zurueck (lazy init)."""
    global _client
    if _client is None:
        _client = MemoryClient(db_path=_default_db, agent_id="default")
    return _client


def set_agent(agent_id: str) -> None:
    """Setzt die Agent-ID fuer neue Eintraege."""
    client = get_client()
    client.agent_id = agent_id


# === Facts ===

def fact(category: str, key: str, value: str, confidence: float = 1.0) -> Dict:
    """Speichert einen Fakt."""
    return get_client().add_fact(category, key, value, confidence)


def facts(category: Optional[str] = None, min_confidence: float = 0.0) -> List[Dict]:
    """Holt alle Fakten (optional gefiltert)."""
    return get_client().get_facts(category=category, min_confidence=min_confidence)


# === Working Memory ===

def note(content: str, priority: int = 0, tags: Optional[str] = None) -> Dict:
    """Speichert eine Notiz im Working Memory."""
    return get_client().add_working(content, type='note', priority=priority, tags=tags)


def scratch(content: str) -> Dict:
    """Speichert einen Scratchpad-Eintrag (temporaer)."""
    return get_client().add_working(content, type='scratchpad', priority=-1)


def loop(content: str) -> Dict:
    """Speichert einen Loop-Eintrag (fuer Iterationen)."""
    return get_client().add_working(content, type='loop', priority=0)


def working(limit: int = 10) -> List[Dict]:
    """Holt aktive Working-Memory-Eintraege."""
    return get_client().get_working(limit=limit)


def clear() -> int:
    """Loescht alle Working-Memory-Eintraege des aktuellen Agents."""
    return get_client().clear_working(agent_only=True)


# === Lessons ===

def lesson(title: str, problem: str, solution: str, severity: str = 'medium') -> Dict:
    """Speichert eine Lesson Learned."""
    return get_client().add_lesson(
        title=title, problem=problem, solution=solution, severity=severity
    )


def lessons(severity: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Holt Lessons Learned."""
    return get_client().get_lessons(limit=limit, severity=severity)


# === Sessions ===

def start(task: Optional[str] = None) -> Dict:
    """Startet eine neue Session."""
    return get_client().start_session(task=task)


def end(session_id: int, notes: Optional[str] = None) -> bool:
    """Beendet eine Session mit optionalen Handoff-Notes."""
    return get_client().end_session(session_id, handoff_notes=notes)


# === Context & Status ===

def context(max_items: int = 5) -> str:
    """Generiert kompakten Kontext fuer LLM-Prompts."""
    return get_client().generate_context(max_items=max_items)


def status() -> Dict:
    """Gibt Memory-Statistiken zurueck."""
    return get_client().get_status()


def changes(since: str) -> Dict:
    """Holt alle Aenderungen seit einem Zeitstempel."""
    return get_client().get_changes_since(since)


# === Shortcuts ===

def remember(key: str, value: str, category: str = 'project') -> Dict:
    """Shortcut: Speichert einen Fakt mit hoher Konfidenz."""
    return fact(category, key, value, confidence=0.95)


def forget(key: str, category: str = 'project') -> bool:
    """Loescht einen Fakt (hard delete)."""
    client = get_client()
    conn = client._get_conn()
    try:
        cursor = conn.execute(
            "DELETE FROM usmc_facts WHERE agent_id = ? AND category = ? AND key = ?",
            (client.agent_id, category, key)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        client._close_conn(conn)
