# -*- coding: utf-8 -*-
"""
TaskClient -- Seam ueber das kanonische taskplan-Modul
========================================================

Das Task-System wurde 2026-07-11 als eigenstaendiges Modul **taskplan**
extrahiert (.AI/.MEMORY/TASKPLAN, Entscheidung [U 2026-07-11] -- .MEMORY-Saeule:
USMC + GARDENER + TASKPLAN). Kanonische Weiterentwicklung passiert DORT.

Dieses Modul ist nur noch die Weiche:
- taskplan installiert  -> kanonischer TaskClient (mit Rinnsal-Default-DB)
- taskplan fehlt        -> eingefrorener Fallback in `_bundled.py`
  (Zero-Dependency-Garantie fuer nackte rinnsal-Installs)

Beide Implementierungen nutzen dasselbe Schema (Tabelle `rinnsal_tasks`).
Der Import-Pfad `rinnsal.tasks.client.TaskClient` bleibt stabil -- er wird
vom homebase-Seam (hb_state_task_*) und vom _tasks-Scanner genutzt.

Author: Lukas Geiger
License: MIT
"""
from pathlib import Path

from ..shared.config import get_default_db_path

try:
    from taskplan.client import (
        TaskClient as _CanonicalTaskClient,
        TASK_SCHEMA_SQL,
        VALID_STATUSES,
        VALID_PRIORITIES,
    )

    TASKS_ENGINE = "taskplan"

    class TaskClient(_CanonicalTaskClient):
        """Kanonischer taskplan-TaskClient mit Rinnsal-Default-DB.

        taskplan selbst wuerde ohne db_path nach TASKPLAN_DB/RINNSAL_DB/
        ~/.taskplan/taskplan.db aufloesen; ueber Rinnsal gilt weiterhin die
        Rinnsal-Aufloesung (ENV RINNSAL_DB > config memory.db_path >
        ~/.rinnsal/rinnsal.db).
        """

        def __init__(
            self,
            db_path: str | Path | None = None,
            agent_id: str = "default"
        ):
            if db_path is None:
                db_path = get_default_db_path()
            super().__init__(db_path=db_path, agent_id=agent_id)

except ImportError:  # taskplan nicht installiert -> gebuendelter Fallback
    from ._bundled import (  # noqa: F401
        TaskClient,
        TASK_SCHEMA_SQL,
        VALID_STATUSES,
        VALID_PRIORITIES,
    )

    TASKS_ENGINE = "bundled"
