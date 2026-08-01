# -*- coding: utf-8 -*-
"""Rinnsal Task System -- Seam ueber das kanonische taskplan-Modul.

Kanonische Implementierung: Paket `taskplan` (https://github.com/ellmos-ai/task-master).
Fallback ohne taskplan: `_bundled.py` (eingefrorene Kopie).
`TASKS_ENGINE` sagt, welche Implementierung aktiv ist ("taskplan"/"bundled").
"""
from .client import TaskClient, TASKS_ENGINE  # noqa: F401
