<p align="center">
  <img src="assets/ellmos-logo.jpg" alt="Rinnsal logo" width="300">
</p>

# Rinnsal

**DE [Deutsche Version](README_de.md)**

[![Rinnsal smoke tests](https://github.com/ellmos-ai/rinnsal/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/ellmos-ai/rinnsal/actions/workflows/tests.yml)

*The trickle: a lightweight, local-first LLM agent infrastructure layer by [ellmos-ai](https://github.com/ellmos-ai).*

Rinnsal gives small autonomous-agent projects the boring infrastructure they usually need first: **SQLite memory**, **task state**, **connector I/O**, **chain automation**, and an optional **Ollama runner**. It is extracted from [BACH](https://github.com/ellmos-ai/bach), but intentionally stays compact: Python stdlib only, no external runtime dependencies, no hosted service.

## Why Rinnsal?

- **Agent memory without a platform** -- facts, notes, lessons, sessions, and prompt-ready context in local SQLite
- **Task state for long-running agent work** -- priority, status, ownership, and next-task selection
- **Connector gateway** -- Telegram, Discord, and Home Assistant behind one small abstraction
- **Chain automation** -- sequential LLM-agent runs with handoff, loop/once modes, logs, and stop/reset controls
- **Embeddable core** -- use Rinnsal inside another Python app, CLI workflow, or local agent stack

Use it when BACH is too large, USMC is too small, and you want a minimal local Python layer for LLM agent infrastructure.

## Features

- **Memory** -- Cross-agent shared memory with SQLite (facts, working memory, lessons learned, sessions)
- **Tasks** -- Simple task management with priorities, status tracking, and agent assignment
- **Connectors** -- Channel abstraction for Telegram, Discord, Home Assistant
- **Automation** -- LLM agent chain orchestration ("Marble-Run": sequential agent chains with loops, handoff, shutdown conditions)
- **Ollama** -- Local LLM runner for Ollama REST API (qwen3, mistral, etc.)
- **i18n** -- Internationalization with JSON translation strings (de, en, es, zh, ja, ru)
- **Zero dependencies** -- Pure Python stdlib, no external packages required
- **Python 3.10+**

CI runs the package smoke suite on Python 3.10, 3.11, 3.12, and 3.13.

## Install

```bash
pip install -e .
```

## Quick Start

### Memory

```python
from rinnsal.memory import api

api.init(agent_id="my-agent")
api.fact("system", "os", "Windows 11")
api.note("Current task: implement feature")
api.lesson("UTF-8 bug", "cp1252 encoding", "PYTHONIOENCODING=utf-8", severity="high")

print(api.context())   # Compact context for LLM prompts
print(api.status())    # Statistics
```

### Tasks

```python
from rinnsal.tasks import api as tasks

tasks.init(agent_id="my-agent")
tasks.add("Implement feature X", priority="high", description="Details here")
tasks.add("Fix encoding bug", priority="critical")

for t in tasks.list():
    print(f"[{t['id']}] {t['title']} ({t['status']})")

tasks.activate(1)      # Set to active
tasks.done(1)          # Mark as done
print(tasks.next_task())  # Next open task by priority
```

### Ollama (Local LLM)

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

print(ollama.available_models())  # List installed models
```

### Connectors

```python
from rinnsal.connectors import load_connector

# Token via ENV: export RINNSAL_TELEGRAM_TOKEN=123:ABC...
tg = load_connector("telegram")
tg.connect()
tg.send_message("chat_id", "Hello from Rinnsal!")
```

### Automation

```python
from rinnsal.auto.runner import ClaudeRunner

runner = ClaudeRunner(model="claude-sonnet-4-6")
result = runner.run("Analyze the code in src/")
print(result["output"])
```

## CLI

```bash
rinnsal status                           # Overall status
rinnsal version                          # Version

# Memory
rinnsal memory status                    # Memory statistics
rinnsal memory fact system os "Win 11"   # Store fact
rinnsal memory facts --json              # All facts as JSON
rinnsal memory note "My note"            # Store note
rinnsal memory context                   # Generate LLM context

# Tasks
rinnsal task add "My task" -p high       # Create task (critical/high/medium/low)
rinnsal task add "Bug fix" -d "Details"  # With description
rinnsal task list                        # Open/active tasks
rinnsal task list --all                  # Including done/cancelled
rinnsal task list --json                 # JSON output
rinnsal task show 1                      # Task details
rinnsal task done 1                      # Mark as done
rinnsal task activate 1                  # Set to active
rinnsal task cancel 1                    # Cancel task
rinnsal task reopen 1                    # Reopen done/cancelled
rinnsal task delete 1                    # Delete permanently
rinnsal task count                       # Count by status

# Chains (Automation)
rinnsal chain list                       # List chains
rinnsal chain start my-project           # Start chain
rinnsal chain status                     # Status of all chains
rinnsal chain stop my-project            # Stop chain
rinnsal chain log my-project             # Show log
rinnsal chain reset my-project           # Reset chain
rinnsal chain create                     # Create interactively

# Connectors
rinnsal connect list                     # Available connectors
rinnsal connect test telegram            # Connection test
rinnsal connect send telegram ID "Text"  # Send message

# Pipe (single call)
rinnsal pipe "Explain this code"         # Single LLM call
```

## Configuration

Rinnsal looks for configuration in this order:

1. `./rinnsal.json` (current directory)
2. `~/.rinnsal/config.json` (user home)

Secrets are set only via environment variables:

```bash
export RINNSAL_TELEGRAM_TOKEN="123456:ABC-DEF..."
export RINNSAL_DISCORD_TOKEN="..."
export RINNSAL_HA_TOKEN="..."
```

Example config: `config/rinnsal.example.json`.

### Database location

By default, Rinnsal stores its SQLite database at `~/.rinnsal/rinnsal.db`
(the directory is created on demand). Override the default with the
`RINNSAL_DB` environment variable or the `memory.db_path` config key.
An explicit `--db` CLI option or `db_path` parameter always takes precedence.

## Architecture

```text
rinnsal/
|-- memory/        # SQLite-based cross-agent memory (from USMC)
|-- tasks/         # Task management with SQLite (priorities, status)
|-- connectors/    # Messaging channel abstraction (from BACH)
|-- auto/          # LLM agent chain orchestration + OllamaRunner
`-- shared/        # Config loader, event bus
```

### Component Integration

```text
Memory <-> Auto:       Chains read/write context from Memory (opt-in)
Connectors <-> Auto:   Telegram notifications via Connector
Event Bus:             Decoupling layer between components
```

## Positioning

Rinnsal belongs to the ellmos infrastructure family:

| Project | Role |
|---|---|
| [USMC](https://github.com/ellmos-ai/usmc) | Shared SQLite memory primitive |
| **Rinnsal** | Memory + tasks + connectors + compact chain automation |
| [MarbleRun / llmauto](https://github.com/ellmos-ai/MarbleRun) | Dedicated autonomous chain runner |
| [BACH](https://github.com/ellmos-ai/bach) | Full text-based operating system for LLM agents |

Rinnsal is closer to an embeddable infrastructure layer than a full assistant product. For orientation, here is the difference to [OpenClaw](https://github.com/openclaw/openclaw):

| | **Rinnsal** | **OpenClaw** |
|---|---|---|
| **Focus** | Minimal infrastructure layer: memory, connectors, automation | Full AI assistant: messengers, native apps, voice, skill marketplace |
| **Philosophy** | Provide building blocks, let the LLM handle the rest | All-in-one ecosystem with community-driven extensions |
| **Memory** | Structured SQLite (facts, lessons, working memory, sessions) | Session/workspace-oriented assistant context |
| **Connectors** | Telegram, Discord, Home Assistant (same abstraction pattern, growing) | Broad platform coverage |
| **Dependencies** | Zero: pure Python stdlib | Node.js and npm ecosystem |
| **License** | MIT | MIT |

**In short:** Rinnsal and OpenClaw share the connector gateway pattern, but take opposite approaches to complexity. Rinnsal stays minimal with zero dependencies and structured memory; OpenClaw is a large assistant ecosystem.

## Search Phrases

`ellmos Rinnsal`, `Rinnsal LLM agent infrastructure`, `local-first LLM agent memory`, `Python stdlib agent framework`, `SQLite memory for LLM agents`, `lightweight agent connector gateway`, `BACH Rinnsal agent stack`

## License

MIT -- Lukas Geiger

---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.
