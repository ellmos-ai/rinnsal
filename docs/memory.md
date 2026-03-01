# Memory

Cross-Agent Shared Memory basierend auf SQLite. Urspruenglich entwickelt als USMC (United Shared Memory Client).

## Schema

| Tabelle | Zweck |
|---|---|
| `usmc_facts` | Persistente Fakten mit Confidence-Score |
| `usmc_working` | Temporaere Notizen (Soft-Delete via `is_active`) |
| `usmc_lessons` | Lessons Learned mit Severity |
| `usmc_sessions` | Session-Tracking mit Handoff-Notes |

## Verwendung

### Client (direkt)

```python
from rinnsal.memory import MemoryClient

client = MemoryClient(db_path="rinnsal.db", agent_id="opus")
client.add_fact("system", "os", "Windows 11", confidence=0.95)
client.add_working("Aktueller Task")
client.add_lesson("Bug", "Problem", "Loesung", severity="high")
```

### API (Singleton)

```python
from rinnsal.memory import api

api.init(agent_id="opus")
api.fact("system", "os", "Windows 11")
api.note("Meine Notiz")
api.remember("key", "value")  # Shortcut: fact mit confidence=0.95
api.forget("key")             # Hard delete
```

## Confidence-Merge

Beim Speichern eines Facts wird die bestehende Confidence geprueft:
- Neue Confidence >= bestehende → Ueberschreiben
- Neue Confidence < bestehende → Nicht ueberschreiben

## Multi-Agent

Jeder Eintrag ist einem `agent_id` zugeordnet. Verschiedene Agents koennen parallel auf dieselbe DB zugreifen (WAL-Mode).
