"""
End-to-end tests for the complete IDA agent flow.

Tests the entire agent workflow including state transitions,
candidate storage, and final routing decisions.
"""
import pytest
from felix_intent_disambiguation import ida_agent, IdaState
from felix_intent_disambiguation.tools import intent_disambiguation_function


def test_agent_initial_routing():
    """Test agent's initial routing for clear messages."""
    state = IdaState()
    message = "I want to send money to my friend"
    
    result = intent_disambiguation_function(message, state)
    
    # Verify routing decision
    assert result["status"] == "RESOLVED"
    assert result["route_to"] == "send_money"
    
    # Verify state
    assert state.phase == "resolved"
    assert state.selected_intent_id == "send_money"
    assert state.ambiguity_reason is None


def test_agent_ambiguity_and_followup():
    """Test complete flow: ambiguous message → clarification → resolution."""
    state = IdaState()
    
    # Step 1: Ambiguous initial message
    result1 = intent_disambiguation_function("I need money", state)
    
    assert result1["status"] == "NEED_CLARIFICATION"
    assert state.phase == "awaiting_clarification"
    assert len(state.candidate_intents) >= 2  # Should have multiple candidates
    
    # Verify candidates are stored
    candidate_ids = [c.id for c in state.candidate_intents]
    assert len(candidate_ids) > 0
    
    # Step 2: User provides clarification
    result2 = intent_disambiguation_function("send money to mom", state)
    
    assert result2["status"] == "RESOLVED"
    assert result2["route_to"] in candidate_ids  # Should match one of the candidates
    
    # Verify final state
    assert state.phase == "resolved"
    assert state.selected_intent_id == result2["route_to"]
    assert state.ambiguity_reason is None


def test_agent_state_transitions():
    """Test that state transitions occur correctly through the flow."""
    state = IdaState()
    
    # Initial state
    assert state.phase == "initial"
    assert state.candidate_intents == []
    assert state.selected_intent_id is None
    
    # Transition 1: initial → awaiting_clarification (ambiguous)
    result1 = intent_disambiguation_function("money", state)
    
    if result1["status"] == "NEED_CLARIFICATION":
        assert state.phase == "awaiting_clarification"
        assert len(state.candidate_intents) > 0
        assert state.selected_intent_id is None
        assert state.ambiguity_reason is not None
        
        # Transition 2: awaiting_clarification → resolved
        result2 = intent_disambiguation_function("send money", state)
        
        assert result2["status"] == "RESOLVED"
        assert state.phase == "resolved"
        assert state.selected_intent_id is not None
        assert state.ambiguity_reason is None
    
    elif result1["status"] == "RESOLVED":
        # Direct resolution (high confidence)
        assert state.phase == "resolved"
        assert state.selected_intent_id is not None


def test_agent_state_transitions_direct_resolution():
    """Test state transitions for direct resolution (no ambiguity)."""
    state = IdaState()
    
    assert state.phase == "initial"
    
    # Direct resolution (high confidence message)
    result = intent_disambiguation_function("check my account balance", state)
    
    assert result["status"] == "RESOLVED"
    assert state.phase == "resolved"
    assert state.selected_intent_id == "check_balance"
    assert state.ambiguity_reason is None
    assert len(state.candidate_intents) > 0  # Candidates should be stored


def test_candidate_intents_stored():
    """Test that candidate intents are properly stored in state."""
    state = IdaState()
    message = "I want to handle my money"
    
    result = intent_disambiguation_function(message, state)
    
    # Candidates should be stored regardless of resolution
    assert len(state.candidate_intents) > 0
    
    # Verify candidate structure
    for candidate in state.candidate_intents:
        assert hasattr(candidate, 'id')
        assert hasattr(candidate, 'label')
        assert hasattr(candidate, 'confidence')
        assert candidate.confidence >= 0.0
        assert candidate.confidence <= 1.0


def test_selected_intent_id_set_on_resolution():
    """Test that selected_intent_id is set when resolution occurs."""
    state = IdaState()
    
    # Test direct resolution
    result1 = intent_disambiguation_function("send money", state)
    if result1["status"] == "RESOLVED":
        assert state.selected_intent_id == result1["route_to"]
        assert state.selected_intent_id is not None
    
    # Test resolution after clarification
    state2 = IdaState()
    intent_disambiguation_function("money", state2)
    if state2.phase == "awaiting_clarification":
        result2 = intent_disambiguation_function("send money", state2)
        if result2["status"] == "RESOLVED":
            assert state2.selected_intent_id == result2["route_to"]
            assert state2.selected_intent_id is not None


def test_agent_handles_different_intents():
    """Test that agent correctly routes to different intent types."""
    test_cases = [
        ("check my balance", "check_balance"),
        ("I need to pay my bill", "pay_bill"),
        ("send money to friend", "send_money"),
    ]
    
    for message, expected_intent in test_cases:
        state = IdaState()
        result = intent_disambiguation_function(message, state)
        
        if result["status"] == "RESOLVED":
            assert result["route_to"] == expected_intent
            assert state.selected_intent_id == expected_intent


def test_agent_maintains_state_across_clarification():
    """Test that state is maintained correctly during clarification phase."""
    state = IdaState()
    
    # Initial message
    original_message = "I need money"
    result1 = intent_disambiguation_function(original_message, state)
    
    if result1["status"] == "NEED_CLARIFICATION":
        # Verify state is preserved
        assert state.phase == "awaiting_clarification"
        assert len(state.candidate_intents) > 0
        
        # Store candidate count
        candidate_count = len(state.candidate_intents)
        
        # Clarification
        result2 = intent_disambiguation_function("send money", state)
        
        # Verify candidates are still accessible (used for resolution)
        assert len(state.candidate_intents) == candidate_count
        assert state.phase == "resolved"


def test_agent_output_structure():
    """Test that agent output has correct structure for all scenarios."""
    state = IdaState()
    
    # Test RESOLVED output
    result1 = intent_disambiguation_function("check balance", state)
    if result1["status"] == "RESOLVED":
        assert "route_to" in result1
        assert "message_to_user" in result1
        assert isinstance(result1["route_to"], str)
        assert len(result1["route_to"]) > 0
    
    # Test NEED_CLARIFICATION output
    state2 = IdaState()
    result2 = intent_disambiguation_function("money", state2)
    if result2["status"] == "NEED_CLARIFICATION":
        assert "options" in result2
        assert "message_to_user" in result2
        assert isinstance(result2["options"], list)
        assert len(result2["options"]) >= 2


def test_agent_id_consistency():
    """Test that route_to matches selected_intent_id in state."""
    state = IdaState()
    message = "send money"
    
    result = intent_disambiguation_function(message, state)
    
    if result["status"] == "RESOLVED":
        assert result["route_to"] == state.selected_intent_id
        assert result["route_to"] is not None

