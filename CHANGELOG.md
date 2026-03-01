# Changelog

## 0.1.0 (2026-03-01)

Initial release. Extracted from [BACH](https://github.com/lukisch) agent system.

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
