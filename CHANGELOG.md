# Changelog

## Unreleased

### Added

- **Tasks module** (`rinnsal/tasks`): SQLite-based task management (statuses open/active/done/cancelled, priorities, tags) sharing the database with the memory system. `TaskClient`, high-level singleton API, and CLI commands `rinnsal task add|list|show|done|activate|cancel|reopen|delete|count`. Tasks are also shown in `rinnsal status`.
- **OllamaRunner** (`rinnsal/auto/ollama_runner.py`): runner for local Ollama models alongside `ClaudeRunner`.
- GitHub Actions smoke workflow for Python 3.10, 3.11, 3.12, and 3.13 with unittest discovery and compileall.
- Smoke tests for the tasks module (`tests/test_tasks.py`): TaskClient CRUD, status transitions, semantic priority ordering, and the high-level singleton API.
- **i18n module** (`rinnsal/i18n`): Internationalization infrastructure with JSON-based translation strings. Supports de, en, es, zh, ja, ru with fallback chain (en → de → key). CLI output starts using `t()` for translatable strings.

### Changed

- Default database path is now `~/.rinnsal/rinnsal.db` instead of `rinnsal.db` in the current working directory. Override via the `RINNSAL_DB` environment variable or the `memory.db_path` config key; explicit `--db`/`db_path` arguments keep precedence.
- Known user home paths for chain config normalization are no longer hardcoded; they are read from the config key `auto.known_user_homes` or the `RINNSAL_KNOWN_HOMES` environment variable.
- The default LLM model name is now a single constant `rinnsal.shared.config.DEFAULT_MODEL` (was duplicated as a string literal in four modules).
- Package version is now sourced dynamically from `rinnsal.__version__` (`dynamic = ["version"]` in `pyproject.toml`); the version is no longer maintained in two places.
- Build requirement raised to `setuptools>=77`, matching the PEP-639 `license = "MIT"` string in `pyproject.toml` (older setuptools failed the build).

### Fixed

- `rinnsal chain start` no longer crashes on Linux/macOS: the `{HOME}`/`{BASH_HOME}` placeholder substitution assumed a Windows drive letter and raised `ValueError` on POSIX home paths.
- Invalid chain `deadline` values no longer crash shutdown checks; they now emit a `RuntimeWarning` and the chain keeps evaluating the remaining stop conditions.
- `translations.json` is now packaged inside `rinnsal.i18n` (moved from the repo-root `locales/` directory) and loaded via `importlib.resources`, so translations work for pip installs and the PyInstaller build. A legacy repo-root fallback remains for old checkouts.
- `rinnsal/connectors/telegram.py`: Corrected type hint `any` → `Any` (import from `typing`); lowercase `any` resolves to the builtin, not the type hint.
- `rinnsal/i18n`: `get_missing()` signature corrected to `Optional[str]`; ambiguous loop variable `l` renamed; docstring no longer references an internal pipeline path.
- `rinnsal/auto/chain.py`: removed an unused `rinnsal_dir` assignment in `run_chain()`.

## 0.1.0 (2026-03-01)

Initial release. Extracted from the [BACH](https://github.com/ellmos-ai/bach) agent system.

### Features

- **Memory** (from USMC): Cross-agent shared memory with SQLite backend
  - Facts, Working Memory, Lessons Learned, Sessions
  - Confidence-based merge, multi-agent support
  - High-level singleton API + direct client

- **Connectors** (from BACH): Channel abstraction for messaging platforms
  - Telegram Bot API (polling, send, voice, file upload)
  - Discord (Bot + Webhook dual mode)
  - Home Assistant REST API
  - Registry + factory pattern, ENV-based secrets

- **Automation** (from llmauto): LLM agent chain orchestration
  - ClaudeRunner: subprocess wrapper for Claude CLI
  - Chain engine: sequential agent chains with loop/once modes
  - State management: rounds, handoff, shutdown conditions
  - Skip-pattern protection, status manipulation guard

- **CLI**: Unified entry point (`rinnsal`)
  - `rinnsal status` / `rinnsal memory` / `rinnsal chain` / `rinnsal connect`

- **Shared infrastructure**
  - Central config loader (JSON + ENV)
  - Minimal event bus for component decoupling
