# -*- coding: utf-8 -*-
"""
Rinnsal Memory -- Cross-Agent Shared Memory
=============================================

Based on USMC (United Shared Memory Client).

Usage (Client):
    from rinnsal.memory import MemoryClient
    client = MemoryClient(db_path="rinnsal.db", agent_id="opus")
    client.add_fact("system", "os", "Windows 11")

Usage (High-Level API):
    from rinnsal.memory import api
    api.init(agent_id="opus")
    api.fact("system", "os", "Windows 11")
    print(api.context())
"""
from .client import MemoryClient
from . import api

__all__ = ["MemoryClient", "api"]
