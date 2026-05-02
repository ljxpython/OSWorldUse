"""Deprecated historical adapter route for CUA integration.

This package is kept only as reference code for the original mm_agents-based
adapter design. It is no longer maintained, is not used by the current
evaluation path, and must not be treated as a fallback.

Current supported integration path:
- osworld_cua_bridge/
- scripts/python/run_multienv_cua_blackbox.py
- lib_run_single.run_single_example_cua_blackbox()
"""

from mm_agents.cua.agent import CUAAdapterAgent
from mm_agents.cua.translator import CUAActionTranslator
from mm_agents.cua.types import (
    BRIDGE_PROTOCOL_VERSION,
    DEFAULT_ADAPTER_VERSION,
    DEFAULT_EVAL_PROFILE,
    CUAAction,
    CUAPrediction,
    CUARuntimeMetadata,
)

__all__ = [
    "BRIDGE_PROTOCOL_VERSION",
    "DEFAULT_ADAPTER_VERSION",
    "DEFAULT_EVAL_PROFILE",
    "CUAAction",
    "CUAActionTranslator",
    "CUAAdapterAgent",
    "CUAPrediction",
    "CUARuntimeMetadata",
]
