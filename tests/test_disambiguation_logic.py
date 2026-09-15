"""
Tests for the Intent Disambiguation Agent logic.

This module contains tests for state management and disambiguation logic.
"""
from felix_intent_disambiguation.state import IdaState, IntentCandidate


def test_ida_state_default_phase_is_initial():
    """Test that IdaState initializes with phase='initial'."""
    state = IdaState()
    assert state.phase == "initial"

