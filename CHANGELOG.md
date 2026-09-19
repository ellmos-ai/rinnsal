# Changelog

## Unreleased

### CI Matrix Hardening, PEP 621 Metadata, Contract Tests & Hygiene (2026-09-19)

- **CI Matrix & Hardening (`tests.yml`, etc.)**: Hardened CI workflow matrix across Python 3.10, 3.11, 3.12, and 3.13 on both `ubuntu-latest` and `windows-latest`. Added concurrency controls (`cancel-in-progress: true`), explicit minimal token permissions (`contents: read`), and strict job timeouts (`timeout-minutes: 15`). Also hardened `stale.yml`, `welcome.yml`, `auto-assign.yml`, and `label-sync.yml` with concurrency and timeout guards.
- **PEP 621 Metadata & Tooling**: Enriched `pyproject.toml` with `license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]`, full set of `[project.urls]` (`Changelog`, `Third-Party Licenses`, `Parent Organization`, `LLM Ready`), standard `[tool.pytest.ini_options]` (`minversion = "7.0"`, `addopts = "-ra -v"`, `norecursedirs`), and `[tool.ruff]` configuration (`target-version = "py310"`, `select = ["E", "F", "W"]`).
- **Dependency Audit & SBOM (`THIRD_PARTY_LICENSES.md`)**: Created comprehensive audit confirming zero external runtime dependencies (`PSF-2.0` Python Standard Library only), `RunAsInvoker` user privilege requirement, non-viral MIT licensing, optional `taskplan` seam architecture, and 10 core governance invariants (`INV-LOCAL-01` through `INV-SLA-10`).
- **Comprehensive Contract Tests (`tests/test_metadata.py`)**: Added 9 contract tests verifying PEP 621 metadata, version parity, CI workflow security/matrix configurations, cloud-sync/LOCK system `.gitignore` rules, statutory liability notice (§ 521 BGB Gefälligkeitsrecht), SBOM audit, UTF-8 file integrity, Mermaid diagram syntax, and CLI smoke execution (`--help`, `--version`). Test suite expanded from 110 to 119 tests (100% pass rate).
- **Code Linting & Bug Fixes**: Resolved 26 static analysis linter issues across `auto/`, `cli.py`, `connectors/`, `memory/`, and `tests/` (redundant f-strings, unused imports/variables, variable shadowing `t` vs i18n translation function). Added `--version` flag to root CLI entrypoint.
- **Multi-Host & LOCK System Guardrails (`.gitignore`)**: Added explicit rules protecting against multi-host conflict files (`*conflicted copy*`, `*-ASUS*`, `*-WORKSTATION*`, `*-Mac Studio*`) and canonical lock files (`LOCK`, `LOCK.*`, `LOCK*.txt`, `LOCK.permissions.json`, `LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`).

### Discoverability, Badges & Sequence Architecture (2026-09-10)

- **Agent Interaction Sequence Diagram**: Added end-to-end Mermaid sequence diagrams illustrating the autonomous agent lifecycle (task query, context injection from SQLite memory, runner chat inference, memory lesson feedback, task completion, connector notification) across `README.md`, `README_de.md`, and `docs/architecture.md`. Validated 100% clean with `lint_mermaid.py`.
- **Badges & Discoverability**: Added `Dependencies: 0 (stdlib only)` badge and CLI quick links to both `README.md` and `README_de.md`.
- **Architecture Documentation Sync**: Synchronized module overview in `docs/architecture.md` to reflect all five core modules (`memory`, `tasks`, `connectors`, `auto`, `i18n`) and their event bus / seam integration.
- **Machine-Readable Index (`llms.txt`)**: Updated `Last-checked` verification timestamp to `2026-09-10`.

### Deep after-care round (2026-08-01)

- **i18n is now reachable, not just present.** `set_language()` existed but was never called: there was no switch, no environment variable, and no locale detection, so the six declared languages could not be selected at all. Added `resolve_language()` / `apply_language()` (precedence: `--lang` > `RINNSAL_LANG` > system locale > default) and a global `--lang` flag.
- **Translation catalog filled.** It previously held a single key (`status.title`) with `es`/`zh`/`ja`/`ru` empty. The complete `status` command is now translated into all six languages and was verified in real terminal output (glyphs and column alignment). A regression test fails if any key is left untranslated in any language -- otherwise `t()` silently falls back to the lead language and the gap never surfaces.
- **`taskplan` references point to the public repository** ([ellmos-ai/task-master](https://github.com/ellmos-ai/task-master)) instead of an internal, unresolvable module path. The relationship is now also documented in the README positioning table and in `llms.txt`.
- **`.gitattributes` added.** Without it, a checkout on Linux/macOS reports the whole tree as modified after a Windows commit.

### Technical Hygiene & Maintenance (2026-07-30)

- **Verification & Status Update**: Verified pytest test suite (102/102 passed in 0.55s, 100% green). Updated `llms.txt` verification timestamp to `2026-07-30`. Verified PEP 621 metadata, file integrity, and repository hygiene.

### Documentation & Maintenance (2026-07-27)

- **Verification & Status Update**: Verified test suite contract (102/102 passed in 1.06s). Updated `llms.txt` verification timestamp to `2026-07-27`.

- **Discoverability & Visual Presentation**: Added Shields.io badges (Pytest 102 passed, Python 3.10+, Local-First Privacy, LLM-Ready) and machine-readable AI agent callouts (`> [!NOTE]`) referencing `llms.txt` in both English (`README.md`) and German (`README_de.md`).
- **System Architecture Diagram**: Integrated a Mermaid flowchart visualizing Rinnsal's tier positioning between USMC (Tier 1 primitive) and BACH (Tier 3 OS) across its five core modules.
- **Project Configuration**: Added `[tool.pytest.ini_options]` to `pyproject.toml` for standard pytest execution (`pythonpath = ["."]`, `testpaths = ["tests"]`).
- **Machine-Readable Index (`llms.txt`)**: Updated header `Last-checked` timestamp to `2026-07-25`.

### Added


- **Tasks module** (`rinnsal/tasks`): SQLite-based task management (statuses open/active/done/cancelled, priorities, tags) sharing the database with the memory system. `TaskClient`, high-level singleton API, and CLI commands `rinnsal task add|list|show|done|activate|cancel|reopen|delete|count`. Tasks are also shown in `rinnsal status`.
- **OllamaRunner** (`rinnsal/auto/ollama_runner.py`): runner for local Ollama models alongside `ClaudeRunner`.
- GitHub Actions smoke workflow for Python 3.10, 3.11, 3.12, and 3.13 with unittest discovery and compileall.
- Smoke tests for the tasks module (`tests/test_tasks.py`): TaskClient CRUD, status transitions, semantic priority ordering, and the high-level singleton API.
- **i18n module** (`rinnsal/i18n`): Internationalization infrastructure with JSON-based translation strings. Supports de, en, es, zh, ja, ru with fallback chain (en → de → key). CLI output starts using `t()` for translatable strings.

### Changed

- **Tasks module extracted to `taskplan`** (2026-07-11): the canonical task implementation now lives in the standalone [`taskplan` package](https://github.com/ellmos-ai/task-master). `rinnsal.tasks.client` became a seam that prefers an installed `taskplan` (subclass injecting rinnsal's default DB resolution) and falls back to the frozen bundled copy (`rinnsal/tasks/_bundled.py`) when `taskplan` is not installed — zero-dependency installs keep working. Import path `rinnsal.tasks.client.TaskClient`, schema (table `rinnsal_tasks`), and behavior are unchanged; `rinnsal.tasks.TASKS_ENGINE` reports the active implementation.
- Default database path is now `~/.rinnsal/rinnsal.db` instead of `rinnsal.db` in the current working directory. Override via the `RINNSAL_DB` environment variable or the `memory.db_path` config key; explicit `--db`/`db_path` arguments keep precedence.
- Known user home paths for chain config normalization are no longer hardcoded; they are read from the config key `auto.known_user_homes` or the `RINNSAL_KNOWN_HOMES` environment variable.
- The default LLM model name is now a single constant `rinnsal.shared.config.DEFAULT_MODEL` (was duplicated as a string literal in four modules).
- Package version is now sourced dynamically from `rinnsal.__version__` (`dynamic = ["version"]` in `pyproject.toml`); the version is no longer maintained in two places.
- Build requirement raised to `setuptools>=77`, matching the PEP-639 `license = "MIT"` string in `pyproject.toml` (older setuptools failed the build).

### Security

- Chain names are now validated (`validate_chain_name()`) before being used in `chains/`, `logs/`, and `state/` file paths. Previously, names containing path separators or `..` could read or write files outside those directories (path traversal, CWE-22), e.g. via `rinnsal chain start "../../other_file"`.

### Fixed

- `load_config()` now returns a copy: mutating the returned dict no longer poisoned the process-wide config cache for later callers.
- In-memory databases (`db_path=":memory:"`) are now usable from background threads: the shared connection is created with `check_same_thread=False`. This matters for connector poll threads (Telegram/Discord `on_message`) writing to memory/tasks.
- Removed the dead config key `auto.telegram.bot_token_env` from defaults and the example config: it was never read — chain status updates always use the token of the `connectors.telegram` entry.
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
