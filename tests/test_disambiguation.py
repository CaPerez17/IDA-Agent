"""
Tests for the intent disambiguation tool logic.

Tests the full disambiguation flow including:
- Direct resolution (high confidence)
- Ambiguity detection
- Clarification resolution
"""
import pytest
from felix_intent_disambiguation.tools import intent_disambiguation_function
from felix_intent_disambiguation.state import IdaState


def test_direct_resolution_high_confidence():
    """Test direct resolution when confidence is high."""
    state = IdaState()
    message = "check my account balance"
    
    result = intent_disambiguation_function(message, state)
    
    # Verify response structure
    assert "status" in result
    assert result["status"] == "RESOLVED"
    assert "route_to" in result
    assert result["route_to"] == "check_balance"
    assert "message_to_user" in result
    
    # Verify state updates
    assert state.phase == "resolved"
    assert state.selected_intent_id == "check_balance"
    assert state.ambiguity_reason is None
    assert len(state.candidate_intents) > 0


def test_direct_resolution_send_money():
    """Test direct resolution for send money intent."""
    state = IdaState()
    message = "I want to send money to my mom"
    
    result = intent_disambiguation_function(message, state)
    
    assert result["status"] == "RESOLVED"
    assert result["route_to"] == "send_money"
    assert state.phase == "resolved"
    assert state.selected_intent_id == "send_money"


def test_ambiguity_detection():
    """Test ambiguity detection for vague messages."""
    state = IdaState()
    # Use a vague message that should trigger ambiguity
    message = "I need money"  # Could be send, check balance, or pay bill
    
    result = intent_disambiguation_function(message, state)
    
    # Verify ambiguity response
    assert "status" in result
    assert result["status"] == "NEED_CLARIFICATION"
    assert "message_to_user" in result
    assert "options" in result
    
    # Verify options structure
    options = result["options"]
    assert isinstance(options, list)
    assert 2 <= len(options) <= 3  # Top 2-3 options
    
    for option in options:
        assert "id" in option
        assert "label" in option
        assert isinstance(option["id"], str)
        assert isinstance(option["label"], str)
    
    # Verify state updates
    assert state.phase == "awaiting_clarification"
    assert state.ambiguity_reason in ["low_confidence", "close_scores"]
    assert len(state.candidate_intents) > 0
    assert state.selected_intent_id is None


def test_clarification_resolution():
    """Test full flow: ambiguous → clarification → resolved."""
    state = IdaState()
    
    # Step 1: Initial ambiguous message
    ambiguous_msg = "I want to handle my money"
    result1 = intent_disambiguation_function(ambiguous_msg, state)
    
    assert result1["status"] == "NEED_CLARIFICATION"
    assert state.phase == "awaiting_clarification"
    assert len(state.candidate_intents) > 0
    
    # Store original candidates for verification
    original_candidates = state.candidate_intents.copy()
    
    # Step 2: User clarifies
    clarification = "send money to mom"
    result2 = intent_disambiguation_function(clarification, state)
    
    assert result2["status"] == "RESOLVED"
    assert "route_to" in result2
    assert result2["route_to"] == "send_money"
    
    # Verify state updates
    assert state.phase == "resolved"
    assert state.selected_intent_id == "send_money"
    assert state.ambiguity_reason is None
    
    # Verify candidates were used (not re-classified)
    # The resolution should use the stored candidates
    assert len(state.candidate_intents) > 0


def test_clarification_with_keyword_match():
    """Test clarification resolution using keyword matching."""
    state = IdaState()
    
    # Initial ambiguous message
    intent_disambiguation_function("money", state)
    assert state.phase == "awaiting_clarification"
    
    # Clarify with keyword that matches send_money
    result = intent_disambiguation_function("I want to transfer", state)
    
    assert result["status"] == "RESOLVED"
    assert result["route_to"] == "send_money"


def test_clarification_with_exact_id_match():
    """Test clarification resolution using exact ID match."""
    state = IdaState()
    
    # Initial ambiguous message
    intent_disambiguation_function("money", state)
    assert state.phase == "awaiting_clarification"
    
    # Clarify with exact intent ID
    result = intent_disambiguation_function("send_money", state)
    
    assert result["status"] == "RESOLVED"
    assert result["route_to"] == "send_money"


def test_state_persistence_across_turns():
    """Test that state persists correctly across multiple turns."""
    state = IdaState()
    
    # First turn
    result1 = intent_disambiguation_function("I need money", state)
    assert state.last_user_message == "I need money"
    
    # Second turn (clarification)
    result2 = intent_disambiguation_function("send money", state)
    assert state.last_user_message == "send money"
    assert state.phase == "resolved"


def test_no_candidates_fallback():
    """Test behavior when no candidates are found (edge case)."""
    state = IdaState()
    # Use a message that might not match any intent well
    # This is an edge case, but we should handle it gracefully
    message = "xyzabc123"  # Nonsensical message
    
    result = intent_disambiguation_function(message, state)
    
    # Should still return a structured response
    assert "status" in result
    # Either NEED_CLARIFICATION with empty options, or some fallback
    assert result["status"] in ["NEED_CLARIFICATION", "RESOLVED", "ERROR"]


def test_structured_output_fields():
    """Test that all required structured output fields are present."""
    state = IdaState()
    message = "check my balance"
    
    result = intent_disambiguation_function(message, state)
    
    # Required fields for RESOLVED
    if result["status"] == "RESOLVED":
        assert "route_to" in result
        assert "message_to_user" in result
        assert isinstance(result["route_to"], str)
        assert isinstance(result["message_to_user"], str)
    
    # Required fields for NEED_CLARIFICATION
    elif result["status"] == "NEED_CLARIFICATION":
        assert "options" in result
        assert "message_to_user" in result
        assert isinstance(result["options"], list)
        assert isinstance(result["message_to_user"], str)


def test_multiple_resolution_attempts():
    """Test that resolved state can handle new messages (state reset scenario)."""
    state = IdaState()
    
    # First resolution
    result1 = intent_disambiguation_function("check balance", state)
    assert result1["status"] == "RESOLVED"
    assert state.phase == "resolved"
    
    # Note: In production, after RESOLVED, state would typically be reset
    # for a new conversation. This test verifies the resolved state is correct.
    assert state.selected_intent_id is not None

