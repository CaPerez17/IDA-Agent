"""
Tests for the classifier module.

Tests keyword scoring, trigger scoring, semantic scoring,
and the simple_classifier function.
"""
import pytest
from felix_intent_disambiguation.classifier import (
    keyword_score,
    trigger_score,
    semantic_score,
    fake_embedding,
    simple_classifier
)
from felix_intent_disambiguation.config import INTENTS_JSON


def test_keyword_score_basic():
    """Test basic keyword scoring functionality."""
    keywords = ["send", "transfer", "money"]
    
    # Perfect match (all keywords present)
    score = keyword_score("I want to send transfer money", keywords)
    assert score == 1.0  # 3/3 keywords found
    
    # Partial match
    score = keyword_score("I want to send money", keywords)
    assert score == pytest.approx(0.666, abs=0.001)  # 2/3 keywords found
    
    # Partial match
    score = keyword_score("send cash", keywords)
    assert score == pytest.approx(0.333, abs=0.001)  # 1/3 keywords found
    
    # No match
    score = keyword_score("hello world", keywords)
    assert score == 0.0
    
    # Empty keywords
    score = keyword_score("any message", [])
    assert score == 0.0


def test_keyword_score_case_insensitive():
    """Test that keyword matching is case-insensitive."""
    keywords = ["send", "MONEY", "Transfer"]
    
    score = keyword_score("SEND MONEY TRANSFER", keywords)
    assert score == 1.0


def test_trigger_score_regex():
    """Test regex trigger scoring."""
    triggers = [r"\btransfer\b", r"\bsend\b", r"\bmoney\b"]
    
    # All triggers match
    score = trigger_score("I want to transfer and send money", triggers)
    assert score == 1.0  # 3/3 triggers matched
    
    # Partial match
    score = trigger_score("transfer funds", triggers)
    assert score == pytest.approx(0.333, abs=0.001)  # 1/3 triggers matched
    
    # No match
    score = trigger_score("hello world", triggers)
    assert score == 0.0
    
    # Empty triggers
    score = trigger_score("any message", [])
    assert score == 0.0


def test_trigger_score_case_insensitive():
    """Test that trigger matching is case-insensitive."""
    triggers = [r"\btransfer\b"]
    
    score = trigger_score("TRANSFER money", triggers)
    assert score == 1.0


def test_semantic_score_determinism():
    """Test that semantic scoring is deterministic."""
    user_vec = [0.5, 0.5, 0.707]
    intent_vec = [0.707, 0.0, 0.707]
    
    score1 = semantic_score(user_vec, intent_vec)
    score2 = semantic_score(user_vec, intent_vec)
    
    assert score1 == score2  # Deterministic
    
    # Test cosine similarity calculation
    assert 0.0 <= score1 <= 1.0  # Cosine similarity range


def test_semantic_score_orthogonal_vectors():
    """Test semantic score with orthogonal vectors."""
    user_vec = [1.0, 0.0, 0.0]
    intent_vec = [0.0, 1.0, 0.0]
    
    score = semantic_score(user_vec, intent_vec)
    assert score == pytest.approx(0.0, abs=0.001)  # Orthogonal = 0 similarity


def test_fake_embedding_determinism():
    """Test that fake_embedding produces deterministic results."""
    text = "test message"
    
    vec1 = fake_embedding(text)
    vec2 = fake_embedding(text)
    
    assert vec1 == vec2  # Deterministic
    
    # Check vector properties
    assert len(vec1) == 3
    assert all(isinstance(x, float) for x in vec1)
    
    # Check normalization (unit vector)
    magnitude = sum(x*x for x in vec1) ** 0.5
    assert pytest.approx(magnitude, abs=0.001) == 1.0


def test_simple_classifier_top_intent_json():
    """Test that simple_classifier returns correct top intent for JSON intents."""
    message = "I want to send money"
    
    candidates = simple_classifier(message, INTENTS_JSON)
    
    assert len(candidates) > 0
    assert candidates[0].id == "send_money"
    assert candidates[0].confidence > 0
    assert candidates[0].label == "Send Money"


def test_simple_classifier_multiple_candidates():
    """Test that simple_classifier returns multiple candidates sorted by score."""
    message = "I want to handle my money"  # Ambiguous message
    
    candidates = simple_classifier(message, INTENTS_JSON)
    
    assert len(candidates) >= 2
    
    # Verify sorting (descending by confidence)
    for i in range(len(candidates) - 1):
        assert candidates[i].confidence >= candidates[i + 1].confidence
    
    # Verify all scores are positive
    for candidate in candidates:
        assert candidate.confidence >= 0.0
        assert candidate.confidence <= 1.0


def test_simple_classifier_all_intents_present():
    """Test that simple_classifier returns candidates for all intents."""
    message = "test"
    
    candidates = simple_classifier(message, INTENTS_JSON)
    
    # Should have at least as many candidates as intents
    assert len(candidates) >= len(INTENTS_JSON)
    
    # Verify all candidates have required fields
    for candidate in candidates:
        assert hasattr(candidate, 'id')
        assert hasattr(candidate, 'label')
        assert hasattr(candidate, 'confidence')
        assert hasattr(candidate, 'description')
        assert isinstance(candidate.confidence, float)


def test_simple_classifier_check_balance():
    """Test classifier with check balance message."""
    message = "check my account balance"
    
    candidates = simple_classifier(message, INTENTS_JSON)
    
    assert len(candidates) > 0
    # Should rank check_balance highly
    top_ids = [c.id for c in candidates[:3]]
    assert "check_balance" in top_ids


def test_simple_classifier_pay_bill():
    """Test classifier with pay bill message."""
    message = "I need to pay my bill"
    
    candidates = simple_classifier(message, INTENTS_JSON)
    
    assert len(candidates) > 0
    # Should rank pay_bill highly
    top_ids = [c.id for c in candidates[:3]]
    assert "pay_bill" in top_ids

