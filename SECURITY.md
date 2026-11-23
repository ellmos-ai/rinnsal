# Security Policy / Sicherheitsrichtlinie

> **Language:** English | [Deutsch](#deutsch)

---

## English

### Supported Versions

| Version | Supported | Notes |
|---|---|---|
| `0.1.x` (`master`) | Yes | Active security fixes |

### Trust Boundary & Security Model

Rinnsal is designed as a **local-first, zero-dependency Python stdlib** infrastructure layer:

- **Zero external runtime dependencies**: Only Python standard library modules (`sqlite3`, `urllib`, `subprocess`, `json`, `pathlib`).
- **Environment-based secrets**: Connector tokens (`RINNSAL_TELEGRAM_TOKEN`, `RINNSAL_DISCORD_TOKEN`, `RINNSAL_HA_TOKEN`) are read exclusively from environment variables — never commit `rinnsal.json` or credentials.
- **Path traversal protection (CWE-22)**: Chain names are validated via `validate_chain_name()` before constructing paths under `chains/`, `logs/`, and `state/`.
- **Unprivileged execution (`RunAsInvoker`)**: Rinnsal requires no administrator/root privileges and stores default SQLite data under `~/.rinnsal/rinnsal.db`.

### Reporting a Vulnerability (Private Disclosure)

Please **do not** report security vulnerabilities through public GitHub issues.

1. Use GitHub's **Private Vulnerability Reporting**: [Report a vulnerability](https://github.com/ellmos-ai/rinnsal/security/advisories/new).
2. There is currently no monitored security mailbox; please do not report by e-mail.

**Response SLA:**
- Initial acknowledgment: within **48 hours**
- Triage and severity assessment: within **5 business days**
- Coordinated fix and disclosure once verified

---

<a id="deutsch"></a>

## Deutsch

### Unterstützte Versionen

| Version | Unterstützt | Hinweis |
|---|---|---|
| `0.1.x` (`master`) | Ja | Aktive Sicherheitskorrekturen |

### Vertrauensgrenze & Sicherheitsmodell

Rinnsal ist als **local-first, abhängigkeitsfreie Python-Stdlib-Schicht** konzipiert:

- **Keine externen Laufzeitabhängigkeiten**: Ausschließlich Python-Standardbibliothek (`sqlite3`, `urllib`, `subprocess`, `json`, `pathlib`).
- **Secrets über Umgebungsvariablen**: Connector-Tokens (`RINNSAL_TELEGRAM_TOKEN`, `RINNSAL_DISCORD_TOKEN`, `RINNSAL_HA_TOKEN`) werden ausschließlich über Umgebungsvariablen bezogen — `rinnsal.json` und Zugangsdaten niemals committen.
- **Path-Traversal-Schutz (CWE-22)**: Chain-Namen werden vor Dateizugriffen in `chains/`, `logs/` und `state/` über `validate_chain_name()` validiert.
- **Unprivilegierte Ausführung (`RunAsInvoker`)**: Rinnsal benötigt keine Administrator-/Root-Rechte und speichert Standard-SQLite-Daten unter `~/.rinnsal/rinnsal.db`.

### Sicherheitslücken vertraulich melden

Bitte melde Sicherheitslücken **nicht** über öffentliche GitHub-Issues.

1. Nutze GitHub **Private Vulnerability Reporting**: [Schwachstelle melden](https://github.com/ellmos-ai/rinnsal/security/advisories/new).
2. Derzeit gibt es kein überwachtes Postfach für Sicherheitsmeldungen; bitte nicht per E-Mail melden.

**Reaktionszeiten (SLA):**
- Erste Rückmeldung: innerhalb von **48 Stunden**
- Triage und Bewertung: innerhalb von **5 Werktagen**
- Koordinierte Behebung und Veröffentlichung nach Verifikation
