"""
Package entrypoint for the Félix Intent Disambiguation Agent.

Exposes:
- ida_agent: the root ADK Agent.
- IdaState, IntentCandidate: state primitives.
"""
from .agent import ida_agent
from .state import IdaState, IntentCandidate

__all__ = ["ida_agent", "IdaState", "IntentCandidate"]

