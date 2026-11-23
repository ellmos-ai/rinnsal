# Contributing to Rinnsal / Mitwirken an Rinnsal

> **Language:** English | [Deutsch](#deutsch)

---

## English

Thanks for your interest in contributing to **Rinnsal**!

### Getting Started

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/ellmos-ai/rinnsal.git
   cd rinnsal
   ```
2. Install in editable mode with dev tools:
   ```bash
   pip install -e ".[dev]"
   ```
   (Rinnsal itself has zero runtime dependencies — only Python 3.10+ stdlib.)

### Quality Gates

Before opening a pull request, verify all checks pass locally:

```bash
ruff check --no-cache rinnsal tests launcher.py
pytest -ra -v
python -m unittest discover -s tests -v
python -m compileall -q rinnsal tests
python -m pip check
```

### How to Contribute

- **Bug fixes**: Open an issue or submit a focused PR on a feature/fix branch
- **New connectors**: Welcome (follow the `BaseConnector` contract in `rinnsal/connectors/base.py`)
- **Chain patterns**: New automation templates under `chains/`
- **Documentation**: Always appreciated (keep `README.md`, `README_de.md`, `llms.txt`, and `SKILL.md` aligned)

### Guidelines

- Keep the zero-dependency philosophy (Python standard library only at runtime)
- Target Python 3.10+ with clear type hints where practical
- One focused change per PR; never bump package versions in hygiene/docs PRs (version bumps happen in dedicated releases)
- Never commit secrets, local `.db`/`.sqlite` runtime databases, or host-specific config files (`rinnsal.json`)
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md)

### License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

<a id="deutsch"></a>

## Deutsch

Vielen Dank für dein Interesse an der Mitarbeit bei **Rinnsal**!

### Einstieg

1. Repository forken und klonen:
   ```bash
   git clone https://github.com/ellmos-ai/rinnsal.git
   cd rinnsal
   ```
2. Editierbar inklusive Entwickler-Werkzeugen installieren:
   ```bash
   pip install -e ".[dev]"
   ```
   (Rinnsal selbst hat null Laufzeitabhängigkeiten — ausschließlich Python 3.10+ Standardbibliothek.)

### Qualitäts-Gates

Vor einem Pull Request bitte alle Prüfungen lokal ausführen:

```bash
ruff check --no-cache rinnsal tests launcher.py
pytest -ra -v
python -m unittest discover -s tests -v
python -m compileall -q rinnsal tests
python -m pip check
```

### Möglichkeiten zur Mitarbeit

- **Fehlerbehebungen**: Issue eröffnen oder fokussierten PR auf eigenem Branch einreichen
- **Neue Connectors**: Willkommen (Schnittstelle `BaseConnector` in `rinnsal/connectors/base.py` einhalten)
- **Ketten-Vorlagen**: Neue Automations-Templates unter `chains/`
- **Dokumentation**: Sehr willkommen (`README.md`, `README_de.md`, `llms.txt` und `SKILL.md` synchron halten)

### Richtlinien

- Null-Abhängigkeits-Prinzip wahren (zur Laufzeit nur Python-Standardbibliothek)
- Python 3.10+ unterstützen und klare Type-Hints verwenden
- Eine klar abgegrenzte Änderung je PR; Versionsnummern nur in expliziten Release-PRs ändern
- Niemals Secrets, lokale `.db`/`.sqlite`-Laufzeitdatenbanken oder lokale Konfigurationsdateien (`rinnsal.json`) committen
- [Verhaltenskodex](CODE_OF_CONDUCT.md) und [Sicherheitsrichtlinie](SECURITY.md) beachten

### Lizenz

Mit deinem Beitrag erklärst du dich einverstanden, dass deine Änderungen unter der [MIT-Lizenz](LICENSE) veröffentlicht werden.
