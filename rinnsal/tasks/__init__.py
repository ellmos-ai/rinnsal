# -*- coding: utf-8 -*-
"""Rinnsal Task System -- Seam ueber das kanonische taskplan-Modul.

Kanonische Implementierung: .AI/.MODULES/.MEMORY/TASKPLAN (Paket `taskplan`).
Fallback ohne taskplan: `_bundled.py` (eingefrorene Kopie).
`TASKS_ENGINE` sagt, welche Implementierung aktiv ist ("taskplan"/"bundled").
"""
from .client import TaskClient, TASKS_ENGINE  # noqa: F401
