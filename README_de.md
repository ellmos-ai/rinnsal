<p align="center">
  <img src="assets/ellmos-logo.jpg" alt="Rinnsal Logo" width="300">
</p>

# Rinnsal

**🇬🇧 [English Version](README.md)**

*Das Rinnsal -- leichtgewichtige LLM-Agent-Infrastruktur von [ellmos-ai](https://github.com/ellmos-ai).*

Leichtgewichtige LLM-Agent-Infrastruktur: **Memory**, **Connectors**, **Automation**.

Extrahiert aus [BACH](https://github.com/lukisch) -- einem umfassenden Agent-System mit 73 Handlern, 322 Tools und 24 Protokollen. Rinnsal übernimmt nur die Infrastrukturschicht und überlässt Agent-/Skill-/Tool-Logik den LLM-Anbietern.

## Features

- **Memory** -- Agentenübergreifender gemeinsamer Speicher mit SQLite (Fakten, Arbeitsspeicher, Lessons Learned, Sessions)
- **Tasks** -- Einfaches Aufgabenmanagement mit Prioritäten, Status-Tracking und Agent-Zuweisung
- **Connectors** -- Kanalabstraktion für Telegram, Discord, Home Assistant
- **Automation** -- LLM-Agent-Kettenorchestrierung ("Marble-Run": sequentielle Agent-Ketten mit Schleifen, Übergabe, Abbruchbedingungen)
- **Ollama** -- Lokaler LLM-Runner für die Ollama REST API (qwen3, mistral, etc.)
- **Keine Abhängigkeiten** -- Reines Python stdlib, keine externen Pakete nötig
- **Python 3.10+**

## Installation

```bash
pip install -e .
```

## Schnellstart

### Memory

```python
from rinnsal.memory import api

api.init(agent_id="my-agent")
api.fact("system", "os", "Windows 11")
api.note("Aktueller Task: Feature implementieren")
api.lesson("UTF-8 Bug", "cp1252 Encoding", "PYTHONIOENCODING=utf-8", severity="high")

print(api.context())   # Kompakter Kontext fuer LLM-Prompts
print(api.status())    # Statistiken
```

### Tasks

```python
from rinnsal.tasks import api as tasks

tasks.init(agent_id="my-agent")
tasks.add("Implement feature X", priority="high", description="Details here")
tasks.add("Fix encoding bug", priority="critical")

for t in tasks.list():
    print(f"[{t['id']}] {t['title']} ({t['status']})")

tasks.activate(1)      # Set to 'active'
tasks.done(1)          # Mark as done
print(tasks.next_task())  # Next open task by priority
```

### Ollama (Lokales LLM)

```python
from rinnsal.auto.ollama_runner import OllamaRunner

ollama = OllamaRunner(model="qwen3:4b", base_url="http://localhost:11434")

if ollama.health():
    result = ollama.run("Explain this code")
    print(result["output"])

    # Chat mit Nachrichtenverlauf
    result = ollama.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ])
    print(result["output"])

print(ollama.available_models())  # Installierte Modelle auflisten
```

### Connectors

```python
from rinnsal.connectors import load_connector

# Token via ENV: export RINNSAL_TELEGRAM_TOKEN=123:ABC...
tg = load_connector("telegram")
tg.connect()
tg.send_message("chat_id", "Hallo von Rinnsal!")
```

### Automation

```python
from rinnsal.auto.runner import ClaudeRunner

runner = ClaudeRunner(model="claude-sonnet-4-6")
result = runner.run("Analysiere den Code in src/")
print(result["output"])
```

## CLI

```bash
rinnsal status                           # Gesamtstatus
rinnsal version                          # Version

# Memory
rinnsal memory status                    # Memory-Statistiken
rinnsal memory fact system os "Win 11"   # Fakt speichern
rinnsal memory facts --json              # Alle Fakten (JSON)
rinnsal memory note "Meine Notiz"        # Notiz speichern
rinnsal memory context                   # LLM-Kontext generieren

# Tasks
rinnsal task add "My task" -p high          # Task erstellen (critical/high/medium/low)
rinnsal task add "Bug fix" -d "Details"     # Mit Beschreibung
rinnsal task list                           # Offene/aktive Tasks
rinnsal task list --all                     # Inklusive erledigte/abgebrochene
rinnsal task list --json                    # JSON-Ausgabe
rinnsal task show 1                         # Task-Details
rinnsal task done 1                         # Als erledigt markieren
rinnsal task activate 1                     # Auf aktiv setzen
rinnsal task cancel 1                       # Task abbrechen
rinnsal task reopen 1                       # Erledigte/abgebrochene wieder öffnen
rinnsal task delete 1                       # Dauerhaft löschen
rinnsal task count                          # Anzahl nach Status

# Chains (Automation)
rinnsal chain list                       # Ketten auflisten
rinnsal chain start mein-projekt         # Kette starten
rinnsal chain status                     # Status aller Ketten
rinnsal chain stop mein-projekt          # Kette stoppen
rinnsal chain log mein-projekt           # Log anzeigen
rinnsal chain reset mein-projekt         # Zuruecksetzen
rinnsal chain create                     # Interaktiv erstellen

# Connectors
rinnsal connect list                     # Verfuegbare Connectors
rinnsal connect test telegram            # Verbindungstest
rinnsal connect send telegram ID "Text"  # Nachricht senden

# Pipe (Einzelaufruf)
rinnsal pipe "Erklaere diesen Code"      # Einzelner LLM-Aufruf
```

## Konfiguration

Rinnsal sucht die Config in folgender Reihenfolge:

1. `./rinnsal.json` (aktuelles Verzeichnis)
2. `~/.rinnsal/config.json` (User-Home)

Secrets werden ausschließlich via Umgebungsvariablen gesetzt:

```bash
export RINNSAL_TELEGRAM_TOKEN="123456:ABC-DEF..."
export RINNSAL_DISCORD_TOKEN="..."
export RINNSAL_HA_TOKEN="..."
```

Beispiel-Config: siehe `config/rinnsal.example.json`

## Architektur

```
rinnsal/
├── memory/        # SQLite-basierter agentenübergreifender Speicher (aus USMC)
├── tasks/         # Aufgabenverwaltung mit SQLite (Prioritäten, Status)
├── connectors/    # Messaging-Kanalabstraktion (aus BACH)
├── auto/          # LLM-Agent-Kettenorchestrierung + OllamaRunner
└── shared/        # Config-Loader, Event Bus
```

### Komponentenintegration

```
Memory <-> Auto:       Chains lesen/schreiben Kontext aus Memory (opt-in)
Connectors <-> Auto:   Telegram-Benachrichtigungen via Connector
Event Bus:             Entkopplungsschicht zwischen Komponenten
```

## Siehe auch: OpenClaw

Wie schneidet Rinnsal im Vergleich zu [OpenClaw](https://github.com/openclaw/openclaw) ab, dem populären Open-Source-KI-Assistenten (274K+ Stars)?

| | **Rinnsal** | **OpenClaw** |
|---|---|---|
| **Focus** | Minimal infrastructure layer -- Memory, Connectors, Automation | Full AI assistant -- 20+ messengers, native apps, voice, skill marketplace |
| **Philosophy** | Provide building blocks, let the LLM handle the rest | All-in-one ecosystem with community-driven extensions |
| **Memory** | Structured SQLite (facts, lessons, working memory, sessions) | Session-based with `/compact`, workspace files |
| **Connectors** | Telegram, Discord, Home Assistant (same abstraction pattern, growing) | 20+ platforms (WhatsApp, Slack, Signal, Teams, Matrix...) |
| **Dependencies** | Zero -- pure Python stdlib | Node.js 22+, numerous npm packages |
| **License** | MIT | MIT |

**Kurzfassung:** Rinnsal und OpenClaw teilen dasselbe Connector-Gateway-Muster, verfolgen aber entgegengesetzte Ansätze bei der Komplexität. Rinnsal bleibt minimal mit null Abhängigkeiten und strukturiertem Speicher. OpenClaw setzt auf native Apps, Sprachsteuerung und eine große Community. Unterschiedliche Ausgangspunkte, die bei den Connectors potenziell konvergieren.

## Lizenz

MIT -- Lukas Geiger
