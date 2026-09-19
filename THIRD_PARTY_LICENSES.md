# Third-Party Licenses & Dependency Audit

**Repository:** `ellmos-ai/rinnsal`  
**Package:** `rinnsal`  
**Primary License:** [MIT License](LICENSE) (Lukas Geiger)  
**Audit Date:** 2026-09-19  
**Audit Status:** PASSED (Zero External Runtime Dependencies)

---

## 1. Executive Summary

`rinnsal` is designed as Tier 2 infrastructure in the ellmos family (Extra Large Language Model Operating Systems). In accordance with the core architecture promise:
- **Direct external runtime dependencies:** **0** (Zero)
- **External package requirements:** None (`dependencies = []`)
- **Runtime environment:** Python standard library only (`>=3.10`)
- **Copyleft contagion:** None (Zero GPL/AGPL/SSPL code)
- **Execution privilege level:** `RunAsInvoker` (Unprivileged user mode, zero root/admin requirements)

---

## 2. Python Standard Library Usage (PSF-2.0)

All core modules within `rinnsal` (`rinnsal.memory`, `rinnsal.tasks`, `rinnsal.connectors`, `rinnsal.auto`, `rinnsal.i18n`) exclusively leverage components provided by the Python Standard Library licensed under the **Python Software Foundation License version 2 (PSF-2.0)**:

| Module / Component | Standard Library Submodules | License | Purpose |
|---|---|---|---|
| Memory Engine | `sqlite3`, `pathlib`, `typing`, `datetime` | PSF-2.0 / Public Domain | SQLite-backed cross-agent memory (facts, lessons, working memory, sessions) |
| Tasks Engine | `sqlite3`, `typing`, `datetime` | PSF-2.0 | Task queue management, priority states, assignment |
| Connectors Gateway | `urllib.request`, `urllib.error`, `socket`, `threading`, `json` | PSF-2.0 | Outbound HTTP/Webhook and inbound polling for Telegram, Discord, Home Assistant |
| Chain Automation | `subprocess`, `os`, `sys`, `json`, `pathlib`, `warnings` | PSF-2.0 | Local CLI runner orchestration and multi-agent pipeline handoffs |
| Internationalization | `json`, `pathlib`, `os`, `locale` | PSF-2.0 | Multi-language translation catalog (`de`, `en`, `es`, `zh`, `ja`, `ru`) |
| CLI Entrypoint | `argparse`, `sys`, `pathlib` | PSF-2.0 | Command-line interface (`rinnsal`) |

Full PSF-2.0 text: https://docs.python.org/3/license.html

---

## 3. Optional Ecosystem Seam Integration

| Extension | Canonical Repository | License | Integration Type |
|---|---|---|---|
| `taskplan` | [ellmos-ai/task-master](https://github.com/ellmos-ai/task-master) | MIT | Optional seam (`rinnsal.tasks.client`). If present in the environment, Rinnsal delegates to canonical `taskplan`; if absent, Rinnsal falls back transparently to bundled frozen primitives (`rinnsal/tasks/_bundled.py`) preserving zero-dependency behavior. |

---

## 4. Governance & Security Invariants

| ID | Invariant | Verification Method | Status |
|---|---|---|---|
| **INV-LOCAL-01** | Zero External Network Runtime Requirement | Memory and tasks operate purely against local SQLite files without outbound calls. | Verified |
| **INV-LOCAL-02** | Zero External Runtime Dependencies | `pyproject.toml` contains no runtime dependencies. | Verified |
| **INV-LOCAL-03** | Local-First Storage Isolation | All default DB states resolve to `~/.rinnsal/rinnsal.db` or explicit custom paths. | Verified |
| **INV-SEC-04** | Path Traversal Protection (CWE-22) | Chain names validated via `validate_chain_name()` preventing escape from chain/log dirs. | Verified |
| **INV-SEC-05** | Least-Privilege Execution (`RunAsInvoker`) | Zero elevated permissions needed; runs in user workspace. | Verified |
| **INV-SEC-06** | CI Token Hardening | GitHub Actions workflows declare explicit minimal `permissions` and concurrency locks. | Verified |
| **INV-SEC-07** | Non-Contagious Licensing | All code is MIT or PSF-2.0; compatible with commercial and closed applications. | Verified |
| **INV-SYNC-08** | Multi-Host Concurrency Guard | Cloud sync artifacts and internal `LOCK` system protected via `.gitignore`. | Verified |
| **INV-COMPAT-09** | Broad Python Runtime Support | Matrix-verified on Python 3.10, 3.11, 3.12, 3.13 across Linux and Windows. | Verified |
| **INV-SLA-10** | Statutory Liability Demarcation | German statutory gift note (§ 521 BGB Gefälligkeitsrecht) integrated into docs. | Verified |

---

## 5. Developer & Test Tools (Not Shipped in Wheel)

The following packages are employed strictly during testing, linting, and development. They are neither imported at runtime nor required by end-users:

| Tool | License | Use |
|---|---|---|
| `pytest` | MIT | Unit and contract test runner |
| `ruff` | MIT / Apache-2.0 | Static analysis, code formatting, and linting |
| `setuptools` | MIT | Packaging build backend (`setuptools>=77`) |
