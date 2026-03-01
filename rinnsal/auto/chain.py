# -*- coding: utf-8 -*-
"""
Chain-Modus (Marble-Run) -- Sequentielle Agent-Ketten
=======================================================

Link1 -> Link2 -> ... -> LinkN -> (loop)
Based on llmauto.modes.chain. Telegram via Connector statt eigenem Code.

Author: Lukas Geiger
License: MIT
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

from .runner import ClaudeRunner
from .config import load_chain, list_chains, load_auto_config, _ACTUAL_HOME, _get_prompts_dir
from .state import ChainState
from ..shared.config import get_rinnsal_dir


def _get_log_dir() -> Path:
    """Gibt das Log-Verzeichnis zurueck."""
    log_dir = get_rinnsal_dir() / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def log(msg, chain_name="default", also_print=True):
    """Schreibt in Log-Datei und optional stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    if also_print:
        print(line)
    log_dir = _get_log_dir()
    log_file = log_dir / f"{chain_name}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def resolve_prompt(link, chain_config):
    """Liest den Prompt-Text fuer ein Kettenglied."""
    prompt_key = link.get("prompt", "")
    prompts_section = chain_config.get("prompts", {})
    prompts_dir = _get_prompts_dir()

    # 1. Prompt in der prompts-Sektion der Chain-Config nachschlagen
    if prompt_key in prompts_section:
        prompt_def = prompts_section[prompt_key]
        if isinstance(prompt_def, dict) and prompt_def.get("type") == "file":
            prompt_path = Path(prompt_def["path"])
            if not prompt_path.is_absolute():
                prompt_path = prompts_dir.parent / prompt_def["path"]
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")
            return f"Lies die Datei {prompt_path} und fuehre die darin beschriebene Aufgabe aus."
        elif isinstance(prompt_def, str):
            return prompt_def

    # 2. Direkt als Datei im prompts/ Ordner suchen
    prompt_file = prompts_dir / prompt_key
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")

    # 3. Als .txt versuchen
    prompt_file_txt = prompts_dir / f"{prompt_key}.txt"
    if prompt_file_txt.exists():
        return prompt_file_txt.read_text(encoding="utf-8")

    # 4. Fallback: Prompt-Key als Datei-Referenz verwenden
    if Path(prompt_key).exists():
        return f"Lies die Datei {prompt_key} und fuehre die darin beschriebene Aufgabe aus."

    # 5. Als inline-Prompt verwenden
    return prompt_key if prompt_key else "Fuehre die naechste Aufgabe aus."


UNTIL_FULL_SUFFIX = (
    "\n\nWICHTIG: Dein Kontext ist deine Begrenzung. Arbeite so viele Aufgaben ab "
    "wie moeglich. Erst wenn du merkst, dass dein Kontext knapp wird oder eine "
    "Komprimierung stattfindet, schliesse die aktuelle Aufgabe sauber ab, "
    "schreibe ein vollstaendiges Handoff und beende dich."
)


def _send_telegram_update(chain_name, state):
    """Sendet Telegram Status-Update via Connector (fehlertolerant)."""
    try:
        from ..shared.config import load_config
        config = load_config()
        telegram = config.get("auto", {}).get("telegram", {})
        if not telegram.get("enabled", False):
            return

        from ..connectors import load_connector
        tg = load_connector("telegram")
        if not tg.connect():
            return

        runtime = f"{state.get_runtime_hours():.1f}h"
        runde = state.get_round()
        status = state.get_status()

        text = (
            f"rinnsal [{chain_name}]\n"
            f"Runde: {runde} | Laufzeit: {runtime}\n"
            f"Status: {status}"
        )

        chat_id = telegram.get("chat_id", "")
        if chat_id:
            tg.send_message(chat_id, text)
    except Exception:
        pass  # Telegram ist optional


def run_chain(chain_name, background=False):
    """Startet eine Kette (Hauptfunktion)."""
    rinnsal_dir = get_rinnsal_dir()

    config = load_chain(chain_name)
    links = config.get("links", [])
    if not links:
        print(f"Fehler: Kette '{chain_name}' hat keine Glieder (links).")
        return 1

    mode = config.get("mode", "loop")
    state = ChainState(chain_name)

    # Hintergrund-Start
    if background:
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)
        env["PYTHONIOENCODING"] = "utf-8"
        subprocess.Popen(
            [sys.executable, "-m", "rinnsal", "chain", "start", chain_name],
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
        )
        print(f"Kette '{chain_name}' im Hintergrund gestartet (neues Fenster).")
        print(f"Status:  rinnsal chain status {chain_name}")
        print(f"Stoppen: rinnsal chain stop {chain_name}")
        return 0

    # Startzeit + Status setzen
    state.record_start()
    state.set_status("RUNNING")

    log("=" * 60, chain_name)
    log(f"CHAIN GESTARTET: {chain_name}", chain_name)
    log(f"Modus: {mode} | Glieder: {len(links)} | Max-Runden: {config.get('max_rounds', '-')}", chain_name)
    log(f"Runtime-Limit: {config.get('runtime_hours', 0)}h | Deadline: {config.get('deadline', '-')}", chain_name)
    log("=" * 60, chain_name)

    global_config = load_auto_config()

    try:
        while True:
            for i, link in enumerate(links):
                should_stop, reason = state.check_shutdown(config)
                if should_stop:
                    log(f"SHUTDOWN: {reason}", chain_name)
                    state.set_status("STOPPED")
                    _send_telegram_update(chain_name, state)
                    return 0

                link_name = link.get("name", f"link-{i+1}")
                role = link.get("role", "worker")
                model = link.get("model") or global_config.get("default_model", "claude-sonnet-4-6")
                fallback = link.get("fallback_model")

                # Continue-Modus
                use_continue = link.get("continue", False)
                if use_continue:
                    link_cwd = state.state_dir / f"{link_name}-workspace"
                    link_cwd.mkdir(parents=True, exist_ok=True)
                    marker = link_cwd / ".session_marker"
                    is_continuation = marker.exists()
                    runner_cwd = str(link_cwd)
                else:
                    is_continuation = False
                    runner_cwd = None

                runner = ClaudeRunner(
                    model=model,
                    fallback_model=fallback,
                    permission_mode=global_config.get("default_permission_mode", "dontAsk"),
                    allowed_tools=global_config.get("default_allowed_tools"),
                    timeout=global_config.get("default_timeout_seconds", 1800),
                    cwd=runner_cwd,
                )

                # Prompt aufloesen + {HOME}/{BASH_HOME} ersetzen
                prompt_text = resolve_prompt(link, config)
                home_win = _ACTUAL_HOME.rstrip(os.sep)
                drive, rest = home_win.split(":", 1)
                home_bash = "/" + drive.lower() + rest.replace("\\", "/")
                prompt_text = prompt_text.replace("{HOME}", home_win)
                prompt_text = prompt_text.replace("{BASH_HOME}", home_bash)

                if link.get("until_full", False):
                    prompt_text += UNTIL_FULL_SUFFIX

                handoff_before = state.get_handoff()

                if is_continuation:
                    log(f"{link_name} ({role}): CONTINUE {model}...", chain_name)
                else:
                    log(f"{link_name} ({role}): Starte {model}...", chain_name)
                result = runner.run(prompt_text, continue_conversation=is_continuation)

                was_skip = state.protect_handoff_from_skip(link_name, handoff_before)
                if was_skip:
                    log(f"  SKIP-SCHUTZ: {link_name} hat Handoff mit SKIP ueberschrieben -> wiederhergestellt", chain_name)

                # Output-Log
                log_dir = _get_log_dir()
                output_log = log_dir / f"{chain_name}_{link_name}.log"
                try:
                    with open(output_log, "a", encoding="utf-8") as f:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"\n{'='*60}\n")
                        f.write(f"[{ts}] Runde {state.get_round()+1} | {link_name} | {model}\n")
                        f.write(f"{'='*60}\n")
                        if result["output"]:
                            f.write(result["output"])
                            f.write("\n")
                        if result["stderr"]:
                            f.write(f"\n--- STDERR ---\n{result['stderr']}\n")
                except Exception as e:
                    log(f"  WARNUNG: Output-Log fehlgeschlagen: {e}", chain_name)

                if use_continue and result["success"] and not is_continuation:
                    marker.touch()

                if result["success"]:
                    log(f"{link_name}: OK ({result['duration_s']:.0f}s)", chain_name)
                else:
                    log(f"{link_name}: FEHLER (rc={result['returncode']}, {result['duration_s']:.0f}s)", chain_name)
                    stderr_short = result["stderr"][:200] if result["stderr"] else ""
                    if stderr_short:
                        log(f"  stderr: {stderr_short}", chain_name)
                    time.sleep(30)

                # Status-Schutz
                current_status = state.get_status()
                if current_status not in ("RUNNING", "ALL_DONE"):
                    log(f"  STATUS-KORREKTUR: '{current_status}' -> 'RUNNING'", chain_name)
                    state.set_status("RUNNING")

                if link.get("telegram_update", False):
                    _send_telegram_update(chain_name, state)

                time.sleep(5)

            # Nach vollem Zyklus
            current_round = state.increment_round()
            log(f"RUNDE {current_round} ABGESCHLOSSEN", chain_name)

            if mode in ("once", "deadend"):
                log(f"Modus '{mode}': Kette beendet nach einem Durchlauf.", chain_name)
                state.set_status("COMPLETED")
                _send_telegram_update(chain_name, state)
                return 0

    except KeyboardInterrupt:
        log("MANUELL GESTOPPT (Ctrl+C)", chain_name)
        state.set_status("STOPPED")
        return 0


def show_status(chain_name=None):
    """Zeigt Status einer oder aller Ketten."""
    rinnsal_dir = get_rinnsal_dir()
    state_dir = rinnsal_dir / "state"

    if chain_name:
        names = [chain_name]
    else:
        if state_dir.exists():
            names = [d.name for d in state_dir.iterdir() if d.is_dir()]
        else:
            names = []

    if not names:
        print("Keine laufenden oder beendeten Ketten gefunden.")
        return 0

    for name in names:
        state = ChainState(name)
        status = state.get_status()
        runde = state.get_round()
        runtime = f"{state.get_runtime_hours():.1f}h" if state.start_time_file.exists() else "-"

        handoff = state.get_handoff()
        last_task, last_status, last_role = "-", "-", "-"
        for line in handoff.split("\n"):
            if line.startswith("## Task:"):
                last_task = line.split(":", 1)[1].strip()
            elif line.startswith("## Status:") or line.startswith("## Urteil:"):
                last_status = line.split(":", 1)[1].strip()
            elif line.startswith("## Rolle:"):
                last_role = line.split(":", 1)[1].strip()

        try:
            config = load_chain(name)
            max_rounds = config.get("max_rounds", "?")
            max_runtime = f"{config.get('runtime_hours', '?')}h"
        except FileNotFoundError:
            max_rounds = "?"
            max_runtime = "?"

        print("=" * 50)
        print(f"  KETTE: {name}")
        print("=" * 50)
        print(f"  Status:       {status}")
        print(f"  Runde:        {runde} / {max_rounds}")
        print(f"  Laufzeit:     {runtime} / {max_runtime} max")
        print(f"  Letztes Glied: {last_role}")
        print(f"  Letzter Task: {last_task}")
        print(f"  Task-Status:  {last_status}")

        if state.is_stop_requested():
            print(f"  !!! STOP: {state.get_stop_reason()}")

        print("=" * 50)
        print()

    return 0


def stop_chain(chain_name, reason=None):
    """Erstellt STOP-Datei fuer eine Kette."""
    state = ChainState(chain_name)
    reason = reason or "Manuell gestoppt via rinnsal"
    state.request_stop(reason)
    print(f"STOP-Datei erstellt fuer '{chain_name}'.")
    print(f"Pipeline stoppt nach aktuellem Glied.")
    print(f"Grund: {reason}")
    return 0


def show_log(chain_name, lines=20):
    """Zeigt Log-Eintraege einer Kette."""
    log_dir = _get_log_dir()
    log_file = log_dir / f"{chain_name}.log"
    if not log_file.exists():
        print(f"Kein Log fuer '{chain_name}' vorhanden.")
        return 0
    content = log_file.read_text(encoding="utf-8").strip().split("\n")
    for line in content[-lines:]:
        print(line)
    return 0


def reset_chain(chain_name):
    """Setzt State einer Kette zurueck."""
    state = ChainState(chain_name)
    state.reset()
    print(f"Kette '{chain_name}' zurueckgesetzt auf Runde 0.")
    print(f"Starten mit: rinnsal chain start {chain_name}")
    return 0
