# Automation

LLM Agent Chain Orchestration ("Marble-Run"). Sequentielle Agent-Ketten mit Loops, Handoff und Shutdown-Bedingungen.

## Konzept

Eine **Chain** (Kette) besteht aus **Links** (Gliedern). Jedes Glied ruft einen LLM-Agent (Claude CLI) auf. Nach einem vollen Durchlauf beginnt der Loop von vorne.

```
Link1 (Worker) → Link2 (Reviewer) → Link3 (Controller) → [Loop]
```

## Quick Start

```bash
# Kette erstellen (interaktiv)
rinnsal chain create

# Kette starten
rinnsal chain start mein-projekt

# Status pruefen
rinnsal chain status mein-projekt

# Stoppen
rinnsal chain stop mein-projekt
```

## Chain-Config (JSON)

```json
{
    "chain_name": "mein-projekt",
    "mode": "loop",
    "max_rounds": 20,
    "runtime_hours": 4,
    "max_consecutive_blocks": 3,
    "links": [
        {
            "name": "worker",
            "role": "worker",
            "model": "claude-sonnet-4-6",
            "prompt": "worker_prompt",
            "until_full": true
        },
        {
            "name": "reviewer",
            "role": "reviewer",
            "model": "claude-opus-4-6",
            "prompt": "reviewer_prompt",
            "telegram_update": true
        }
    ],
    "prompts": {
        "worker_prompt": {"type": "file", "path": "prompts/worker.txt"},
        "reviewer_prompt": "Pruefe die Arbeit und schreibe ein Handoff."
    }
}
```

## Shutdown-Bedingungen

Die Chain stoppt automatisch bei:
- **STOP-Datei**: Manuell via `rinnsal chain stop`
- **ALL_DONE**: Status in `status.txt`
- **Deadline**: Konfiguriertes ISO-Datum
- **Runtime**: Maximale Laufzeit in Stunden
- **Max Rounds**: Maximale Rundenanzahl
- **Max Blocks**: Zu viele aufeinanderfolgende BLOCKED-Eintraege im Handoff

## Schutz-Mechanismen

- **Skip-Pattern-Schutz**: Wenn ein Worker den Handoff mit nur "SKIPPED" ueberschreibt, wird der vorherige Handoff wiederhergestellt.
- **Status-Manipulation-Guard**: Worker duerfen `status.txt` nicht auf COMPLETED setzen.
- **Continue-Modus**: Jedes Glied kann seine eigene Konversation fortsetzen (`"continue": true`).

## Prompts

Platzhalter in Prompts:
- `{HOME}` → Windows-Home-Pfad (z.B. `C:\Users\Name`)
- `{BASH_HOME}` → Bash-Home-Pfad (z.B. `/c/Users/Name`)
