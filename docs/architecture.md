# Architektur

## Ueberblick

Rinnsal besteht aus drei unabhaengigen Modulen plus einer gemeinsamen Infrastrukturschicht:

```
rinnsal/
├── memory/        ← USMC (United Shared Memory Client)
├── connectors/    ← BACH Connector Framework
├── auto/          ← llmauto (Marble-Run Engine)
└── shared/        ← Config + Event-Bus (NEU)
```

## Design-Prinzipien

1. **Zero Dependencies** -- Nur Python stdlib. Kein `requests`, `aiohttp`, etc.
2. **Modular** -- Jede Komponente ist einzeln nutzbar.
3. **ENV-basierte Secrets** -- Keine Secrets in Dateien oder Datenbanken.
4. **Konfigurierbar** -- Zentrales `rinnsal.json`, Suchpfade: `./` und `~/.rinnsal/`.

## Komponenten-Integration

```
┌─────────┐      ┌──────────────┐      ┌──────────┐
│ Memory  │◄────►│  Auto/Chain  │◄────►│Connectors│
│ (SQLite)│      │  (Marble-Run)│      │(Telegram,│
└────┬────┘      └──────┬───────┘      │ Discord) │
     │                  │              └────┬─────┘
     └──────────┬───────┘                   │
                ▼                           │
          ┌──────────┐                      │
          │ Event-Bus│◄─────────────────────┘
          └──────────┘
```

- **Memory ↔ Auto**: Chain-Engine liest optional Kontext aus Memory, schreibt Ergebnisse zurueck.
- **Connectors ↔ Auto**: Telegram-Notifications nach Chain-Links via Connector-Factory.
- **Event-Bus**: Entkopplungsschicht fuer komponentenuebergreifende Events.

## State-Management

Chain-State wird im Dateisystem gespeichert (`~/.rinnsal/state/<chain>/`):

| Datei | Inhalt |
|---|---|
| `status.txt` | RUNNING, STOPPED, COMPLETED, ALL_DONE, READY |
| `round_counter.txt` | Aktuelle Rundennummer |
| `start_time.txt` | ISO-Startzeit |
| `handoff.md` | Agent-zu-Agent Uebergabe-Dokument |
| `STOP` | Stop-Marker (Existenz = Stop angefordert) |
