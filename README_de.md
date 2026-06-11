<p align="center">
  <img src="assets/ellmos-logo.jpg" alt="Rinnsal Logo" width="300">
</p>

# Rinnsal

**EN [English Version](README.md)**

*Das Rinnsal: eine leichtgewichtige, local-first LLM-Agent-Infrastrukturschicht von [ellmos-ai](https://github.com/ellmos-ai).*

Rinnsal gibt kleinen autonomen Agentenprojekten die Grundschicht, die sie meist zuerst brauchen: **SQLite-Memory**, **Task-Status**, **Connector-I/O**, **Kettenautomatisierung** und optional einen **Ollama-Runner**. Es ist aus [BACH](https://github.com/ellmos-ai/bach) extrahiert, bleibt aber absichtlich kompakt: nur Python-Stdlib, keine externen Laufzeitabhängigkeiten, kein Hosted Service.

## Warum Rinnsal?

- **Agenten-Memory ohne Plattformzwang** -- Fakten, Notizen, Lessons, Sessions und promptfertiger Kontext in lokalem SQLite
- **Task-Status für länger laufende Agentenarbeit** -- Priorität, Status, Zuständigkeit und Next-Task-Auswahl
- **Connector-Gateway** -- Telegram, Discord und Home Assistant hinter einer kleinen gemeinsamen Abstraktion
- **Kettenautomatisierung** -- sequenzielle LLM-Agentenläufe mit Handoff, Loop-/Once-Modus, Logs und Stop-/Reset-Steuerung
- **Einbettbarer Kern** -- nutzbar in Python-Apps, CLI-Workflows oder lokalen Agenten-Stacks

Nutze Rinnsal, wenn BACH zu groß, USMC zu klein ist und du eine minimale lokale Python-Schicht für LLM-Agent-Infrastruktur brauchst.

## Features

- **Memory** -- Agentenübergreifender gemeinsamer Speicher mit SQLite (Fakten, Arbeitsspeicher, Lessons Learned, Sessions)
- **Tasks** -- Einfaches Aufgabenmanagement mit Prioritäten, Status-Tracking und Agent-Zuweisung
- **Connectors** -- Kanalabstraktion für Telegram, Discord, Home Assistant
- **Automation** -- LLM-Agent-Kettenorchestrierung ("Marble-Run": sequentielle Agent-Ketten mit Schleifen, Übergabe, Abbruchbedingungen)
- **Ollama** -- Lokaler LLM-Runner für die Ollama REST API (qwen3, mistral, etc.)
- **i18n** -- Internationalisierung mit JSON-Übersetzungsstrings (de, en, es, zh, ja, ru)
- **Keine Abhängigkeiten** -- reines Python stdlib, keine externen Pakete nötig
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

print(api.context())   # Kompakter Kontext für LLM-Prompts
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

tasks.activate(1)      # Auf aktiv setzen
tasks.done(1)          # Als erledigt markieren
print(tasks.next_task())  # Nächster offener Task nach Priorität
```

### Ollama (Lokales LLM)

```python
from rinnsal.auto.ollama_runner import OllamaRunner

ollama = OllamaRunner(model="qwen3:4b", base_url="http://localhost:11434")

if ollama.health():
    result = ollama.run("Explain this code")
    print(result["output"])

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
rinnsal memory facts --json              # Alle Fakten als JSON
rinnsal memory note "Meine Notiz"        # Notiz speichern
rinnsal memory context                   # LLM-Kontext generieren

# Tasks
rinnsal task add "My task" -p high       # Task erstellen (critical/high/medium/low)
rinnsal task add "Bug fix" -d "Details"  # Mit Beschreibung
rinnsal task list                        # Offene/aktive Tasks
rinnsal task list --all                  # Inklusive erledigte/abgebrochene
rinnsal task list --json                 # JSON-Ausgabe
rinnsal task show 1                      # Task-Details
rinnsal task done 1                      # Als erledigt markieren
rinnsal task activate 1                  # Auf aktiv setzen
rinnsal task cancel 1                    # Task abbrechen
rinnsal task reopen 1                    # Erledigte/abgebrochene wieder öffnen
rinnsal task delete 1                    # Dauerhaft löschen
rinnsal task count                       # Anzahl nach Status

# Chains (Automation)
rinnsal chain list                       # Ketten auflisten
rinnsal chain start mein-projekt         # Kette starten
rinnsal chain status                     # Status aller Ketten
rinnsal chain stop mein-projekt          # Kette stoppen
rinnsal chain log mein-projekt           # Log anzeigen
rinnsal chain reset mein-projekt         # Zurücksetzen
rinnsal chain create                     # Interaktiv erstellen

# Connectors
rinnsal connect list                     # Verfügbare Connectors
rinnsal connect test telegram            # Verbindungstest
rinnsal connect send telegram ID "Text"  # Nachricht senden

# Pipe (Einzelaufruf)
rinnsal pipe "Erkläre diesen Code"       # Einzelner LLM-Aufruf
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

Beispiel-Config: `config/rinnsal.example.json`.

## Architektur

```text
rinnsal/
|-- memory/        # SQLite-basierter agentenübergreifender Speicher (aus USMC)
|-- tasks/         # Aufgabenverwaltung mit SQLite (Prioritäten, Status)
|-- connectors/    # Messaging-Kanalabstraktion (aus BACH)
|-- auto/          # LLM-Agent-Kettenorchestrierung + OllamaRunner
`-- shared/        # Config-Loader, Event Bus
```

### Komponentenintegration

```text
Memory <-> Auto:       Chains lesen/schreiben Kontext aus Memory (opt-in)
Connectors <-> Auto:   Telegram-Benachrichtigungen via Connector
Event Bus:             Entkopplungsschicht zwischen Komponenten
```

## Positionierung

Rinnsal gehört zur ellmos-Infrastrukturfamilie:

| Projekt | Rolle |
|---|---|
| [USMC](https://github.com/ellmos-ai/usmc) | Gemeinsame SQLite-Memory-Primitive |
| **Rinnsal** | Memory + Tasks + Connectors + kompakte Kettenautomatisierung |
| [MarbleRun / llmauto](https://github.com/ellmos-ai/MarbleRun) | Dedizierter autonomer Chain-Runner |
| [BACH](https://github.com/ellmos-ai/bach) | Vollständiges textbasiertes Betriebssystem für LLM-Agenten |

Rinnsal ist eher eine einbettbare Infrastrukturschicht als ein vollständiges Assistenzprodukt. Zur Orientierung der Unterschied zu [OpenClaw](https://github.com/openclaw/openclaw):

| | **Rinnsal** | **OpenClaw** |
|---|---|---|
| **Fokus** | Minimale Infrastrukturschicht: Memory, Connectors, Automation | Vollständiger KI-Assistent: Messenger, native Apps, Voice, Skill-Marktplatz |
| **Philosophie** | Bausteine liefern, die Agentenlogik bleibt beim LLM | All-in-one-Ökosystem mit Community-Erweiterungen |
| **Memory** | Strukturiertes SQLite (Fakten, Lessons, Arbeitsspeicher, Sessions) | Assistant-Kontext rund um Sessions und Workspaces |
| **Connectors** | Telegram, Discord, Home Assistant (gleiches Abstraktionsmuster, wachsend) | Breite Plattformabdeckung |
| **Abhängigkeiten** | Null: reine Python-Stdlib | Node.js und npm-Ökosystem |
| **Lizenz** | MIT | MIT |

**Kurzfassung:** Rinnsal und OpenClaw teilen dasselbe Connector-Gateway-Muster, verfolgen aber entgegengesetzte Ansätze bei der Komplexität. Rinnsal bleibt minimal mit null Abhängigkeiten und strukturiertem Speicher; OpenClaw ist ein großes Assistenz-Ökosystem.

## Suchphrasen

`ellmos Rinnsal`, `Rinnsal LLM-Agent-Infrastruktur`, `local-first LLM-Agent-Memory`, `Python-Stdlib-Agent-Framework`, `SQLite-Memory für LLM-Agenten`, `leichtgewichtiges Agent-Connector-Gateway`, `BACH Rinnsal Agent Stack`

## Lizenz

MIT -- Lukas Geiger

---

## Haftung

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.
