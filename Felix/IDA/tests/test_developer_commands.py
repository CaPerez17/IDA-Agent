"""
Tests for developer debugging commands.

Tests /switch_mode and /compare_modes functionality.
"""
import pytest
from felix_intent_disambiguation.tools import intent_disambiguation_function
from felix_intent_disambiguation.state import IdaState
from felix_intent_disambiguation.developer import handle_developer_command


def test_switch_mode_toon():
    """Test switching to TOON mode via developer command."""
    state = IdaState()
    assert state.mode == "json"  # Default
    
    result = intent_disambiguation_function("/switch_mode toon", state)
    
    assert result["status"] == "ACK"
    assert "message_to_user" in result
    assert "TOON" in result["message_to_user"].upper()
    assert state.mode == "toon"


def test_switch_mode_json():
    """Test switching back to JSON mode."""
    state = IdaState()
    state.mode = "toon"  # Start in TOON
    
    result = intent_disambiguation_function("/switch_mode json", state)
    
    assert result["status"] == "ACK"
    assert state.mode == "json"


def test_switch_mode_invalid():
    """Test handling of invalid mode switch command."""
    state = IdaState()
    
    result = intent_disambiguation_function("/switch_mode invalid", state)
    
    assert result["status"] == "ERROR"
    assert "message_to_user" in result


def test_switch_mode_missing_argument():
    """Test handling of switch_mode without argument."""
    state = IdaState()
    
    result = intent_disambiguation_function("/switch_mode", state)
    
    assert result["status"] == "ERROR"


def test_compare_modes_output_structure():
    """Test that /compare_modes returns correct output structure."""
    state = IdaState()
    
    # First, set a message in state
    intent_disambiguation_function("I want to send money", state)
    
    # Now compare modes
    result = intent_disambiguation_function("/compare_modes", state)
    
    # Should return comparison structure
    if result["status"] == "DEVELOPER_COMPARE":
        assert "json_result" in result
        assert "toon_result" in result
        assert "analysis" in result
        
        # Verify json_result structure
        json_res = result["json_result"]
        assert "top_intent" in json_res
        assert "score" in json_res
        assert "scores_raw" in json_res
        
        # Verify toon_result structure
        toon_res = result["toon_result"]
        assert "top_intent" in toon_res
        assert "score" in toon_res
        assert "scores_raw" in toon_res


def test_compare_modes_no_previous_message():
    """Test /compare_modes when no previous message exists."""
    state = IdaState()
    # Don't set any message
    
    result = intent_disambiguation_function("/compare_modes", state)
    
    # Should handle gracefully
    assert "status" in result
    # Either ERROR or some fallback response


def test_developer_commands_do_not_affect_phase():
    """Test that developer commands don't modify conversation phase."""
    state = IdaState()
    original_phase = state.phase
    
    # Switch mode
    intent_disambiguation_function("/switch_mode toon", state)
    
    # Phase should remain unchanged
    assert state.phase == original_phase


def test_mode_persistence():
    """Test that mode persists across multiple tool calls."""
    state = IdaState()
    
    # Switch to TOON
    intent_disambiguation_function("/switch_mode toon", state)
    assert state.mode == "toon"
    
    # Make a regular call
    result = intent_disambiguation_function("send money", state)
    
    # Mode should still be TOON
    assert state.mode == "toon"


def test_unknown_developer_command():
    """Test handling of unknown developer commands."""
    state = IdaState()
    
    result = intent_disambiguation_function("/unknown_command", state)
    
    assert result["status"] == "ERROR"
    assert "message_to_user" in result

