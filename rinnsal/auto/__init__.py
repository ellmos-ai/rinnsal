# -*- coding: utf-8 -*-
"""
Rinnsal Auto -- LLM Agent Chain Orchestration
================================================

Based on llmauto. Sequential agent chains (Marble-Run).

Usage:
    from rinnsal.auto import runner, chain

    # Single call:
    r = runner.ClaudeRunner()
    result = r.run("Analysiere den Code.")

    # Chain:
    chain.run_chain("mein-projekt")
"""
