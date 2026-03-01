# -*- coding: utf-8 -*-
"""
Rinnsal Memory Database Schema + Migration
============================================

SQLite-Schema fuer Facts, Working Memory, Lessons, Sessions.
Based on USMC schema.

Author: Lukas Geiger
License: MIT
"""
import sqlite3
from typing import Optional

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Facts: Persistente Fakten mit Konfidenz und Agent-Tracking
CREATE TABLE IF NOT EXISTS usmc_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    source TEXT,
    agent_id TEXT NOT NULL DEFAULT 'default',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(agent_id, category, key)
);

-- Working Memory: Temporaere Notizen, Kontext, Scratchpad
CREATE TABLE IF NOT EXISTS usmc_working (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL DEFAULT 'note',
    content TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    tags TEXT,
    agent_id TEXT NOT NULL DEFAULT 'default',
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Lessons Learned: Erfahrungen und Problemloesungen
CREATE TABLE IF NOT EXISTS usmc_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL DEFAULT 'general',
    severity TEXT NOT NULL DEFAULT 'medium',
    title TEXT NOT NULL,
    problem TEXT NOT NULL,
    solution TEXT NOT NULL,
    agent_id TEXT NOT NULL DEFAULT 'default',
    is_active INTEGER DEFAULT 1,
    confidence REAL DEFAULT 1.0,
    times_shown INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Sessions: Agent-Session-Tracking fuer Kontinuitaet
CREATE TABLE IF NOT EXISTS usmc_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    current_task TEXT,
    handoff_notes TEXT
);

-- Schema-Version tracking
CREATE TABLE IF NOT EXISTS usmc_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Indizes fuer Performance
CREATE INDEX IF NOT EXISTS idx_facts_category ON usmc_facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_agent ON usmc_facts(agent_id);
CREATE INDEX IF NOT EXISTS idx_facts_updated ON usmc_facts(updated_at);
CREATE INDEX IF NOT EXISTS idx_working_active ON usmc_working(is_active);
CREATE INDEX IF NOT EXISTS idx_working_agent ON usmc_working(agent_id);
CREATE INDEX IF NOT EXISTS idx_lessons_active ON usmc_lessons(is_active);
CREATE INDEX IF NOT EXISTS idx_lessons_severity ON usmc_lessons(severity);
CREATE INDEX IF NOT EXISTS idx_sessions_agent ON usmc_sessions(agent_id);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Erstellt alle Tabellen und setzt Schema-Version."""
    conn.executescript(SCHEMA_SQL)
    conn.execute(
        "INSERT OR REPLACE INTO usmc_meta (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),)
    )
    conn.commit()


def get_schema_version(conn: sqlite3.Connection) -> Optional[int]:
    """Liest aktuelle Schema-Version aus der DB."""
    try:
        row = conn.execute(
            "SELECT value FROM usmc_meta WHERE key = 'schema_version'"
        ).fetchone()
        return int(row[0]) if row else None
    except sqlite3.OperationalError:
        return None


def migrate(conn: sqlite3.Connection) -> None:
    """Fuehrt ggf. Schema-Migration durch."""
    version = get_schema_version(conn)
    if version is None:
        init_db(conn)
        return
    # Zukuenftige Migrationen hier:
    # if version < 2:
    #     _migrate_v1_to_v2(conn)
