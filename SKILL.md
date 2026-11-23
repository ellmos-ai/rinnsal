---
name: rinnsal
version: 0.1.0
description: "Use Rinnsal CLI and Python APIs for local-first SQLite agent memory, task management, messaging connectors (Telegram, Discord, Home Assistant), and sequential LLM agent chains. Pure Python 3.10+ stdlib with zero external runtime dependencies."
---

# Rinnsal — Product Skill for Agents & Users

**Supported version:** `rinnsal 0.1.0` (Python `>=3.10`, zero external runtime dependencies).
**Entrypoints:** CLI (`rinnsal ...`, `python -m rinnsal ...`, `launcher.py ...`) and Python package (`rinnsal.memory`, `rinnsal.tasks`, `rinnsal.connectors`, `rinnsal.auto`, `rinnsal.i18n`).

> [!NOTE]
> This file documents **how to use Rinnsal** as a product (human + LLM dual use). For repository contribution rules, see [CONTRIBUTING.md](CONTRIBUTING.md). For machine-readable overview and search terms, see [llms.txt](llms.txt) (compatibility pointer: [llm.txt](llm.txt)).

---

## 1. Capabilities & Boundaries

**Use Rinnsal when:**
- You need persistent cross-agent **SQLite memory** (facts, working notes, lessons learned, sessions) without external databases.
- You need lightweight **task tracking** (`open`, `active`, `done`, `cancelled`; priorities `critical`, `high`, `medium`, `low`) sharing the same SQLite database (optionally delegating to `taskplan` if installed).
- You want to send/poll messages via **connectors** (`telegram`, `discord`, `homeassistant`) using environment-based secrets.
- You want sequential **agent chains** (`rinnsal chain ...`) or single calls (`rinnsal pipe ...`) backed by local Ollama or Claude CLI.

**Rinnsal does NOT:**
- Require or ship external PyPI runtime dependencies.
- Store secrets in git-tracked files or SQLite (tokens come from environment variables).
- Run a web GUI or full OS handler catalog (see [BACH](https://github.com/ellmos-ai/bach) for the full OS).

---

## 2. Installation & Configuration

```bash
pip install -e .
rinnsal --version   # rinnsal 0.1.0
```

**Environment variables (no secrets in files):**
- `RINNSAL_DB` — Override default SQLite DB path (`~/.rinnsal/rinnsal.db`)
- `RINNSAL_LANG` — Output language (`de`, `en`, `es`, `zh`, `ja`, `ru`)
- `RINNSAL_TELEGRAM_TOKEN` — Telegram Bot API token
- `RINNSAL_DISCORD_TOKEN` — Discord Bot token
- `RINNSAL_HA_TOKEN` — Home Assistant REST API token

Config lookup order: `./rinnsal.json` → `~/.rinnsal/config.json` (template: `config/rinnsal.example.json`).

---

## 3. CLI Reference & Structured Output

Global flags (must precede subcommand): `--db <path>`, `--agent <id>`, `--lang {de,en,es,zh,ja,ru}`, `--version` / `-V`.

```bash
# Status & version
rinnsal --lang en status
rinnsal version

# Memory (SQLite)
rinnsal --db ./agent.db --agent worker-1 memory status
rinnsal --db ./agent.db --agent worker-1 memory fact project stack "Python stdlib" --confidence 1.0
rinnsal --db ./agent.db memory facts --category project --json
rinnsal --db ./agent.db memory note "Verified metadata contract"
rinnsal --db ./agent.db memory context

# Tasks (SQLite / optional taskplan seam)
rinnsal --db ./agent.db task add "Run contract checks" -p high -d "Before PR" --tags ci
rinnsal --db ./agent.db task list --json
rinnsal --db ./agent.db task show 1
rinnsal --db ./agent.db task activate 1
rinnsal --db ./agent.db task done 1
rinnsal --db ./agent.db task cancel 1
rinnsal --db ./agent.db task reopen 1
rinnsal --db ./agent.db task count
rinnsal --db ./agent.db task delete 1

# Connectors (Telegram / Discord / Home Assistant)
rinnsal connect list
rinnsal connect test telegram
rinnsal connect send telegram "<recipient>" "<message>"

# Chains & single LLM call
rinnsal chain list
rinnsal chain status
rinnsal chain start <chain_name>
rinnsal chain stop <chain_name> --reason "manual stop"
rinnsal chain log <chain_name> -n 20
rinnsal chain reset <chain_name>
rinnsal pipe "Summarize module structure"
```

**Exit codes & verification:**
- Exit `0`: command succeeded (use `--json` on `memory facts` and `task list` for deterministic machine readback).
- Exit `1`: invalid arguments, unknown subcommand, traversal-rejected chain name (`validate_chain_name()`), or runtime error (`[ERROR] ...` on stderr).

---

## 4. Python API Quick Reference

```python
from rinnsal.memory import api as mem
from rinnsal.tasks import api as tasks
from rinnsal.connectors import load_connector

# Memory
mem.init(db_path="./agent.db", agent_id="worker-1")
mem.fact("project", "runtime", "python-stdlib", confidence=1.0)
mem.note("Step 1 completed")
context_prompt = mem.context()
stats = mem.status()

# Tasks
tasks.init(db_path="./agent.db", agent_id="worker-1")
created = tasks.add("Verify tests", priority="high")
open_tasks = tasks.list()
tasks.activate(created["id"])
tasks.done(created["id"])

# Connectors (reads ENV token automatically if configured)
tg = load_connector("telegram")
```

---

## 5. Deep Documentation

- [README.md](README.md) / [README_de.md](README_de.md) — Overview, positioning, and quickstart
- [docs/memory.md](docs/memory.md) — Memory schema and confidence merge rules
- [docs/connectors.md](docs/connectors.md) — Connector configuration and polling
- [docs/automation.md](docs/automation.md) — Chain orchestration and handoff protocol
- [docs/architecture.md](docs/architecture.md) — Module layout and event bus
