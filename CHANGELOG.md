# Changelog

## Unreleased

### Added

- **i18n module** (`rinnsal/i18n`): Internationalization infrastructure with JSON-based translation strings (`locales/translations.json`). Supports de, en, es, zh, ja, ru with fallback chain (en → de → key). CLI output starts using `t()` for translatable strings.

### Fixed

- `rinnsal/connectors/telegram.py`: Corrected type hint `any` → `Any` (import from `typing`); lowercase `any` resolves to the builtin, not the type hint.

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
