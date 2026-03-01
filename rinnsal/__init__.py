# -*- coding: utf-8 -*-
"""
Rinnsal -- Lightweight LLM Agent Infrastructure
=================================================

Extracted from BACH: Memory, Connectors, Automation.
Zero external dependencies, pure Python stdlib.

Components:
    rinnsal.memory      -- Cross-agent shared memory (SQLite)
    rinnsal.connectors  -- Messaging channel abstraction
    rinnsal.auto        -- LLM agent chain orchestration

Quick start:
    from rinnsal.memory import api
    api.init()
    api.fact("system", "os", "Windows 11")
    print(api.status())

Author: Lukas Geiger
License: MIT
"""

__version__ = "0.1.0"
