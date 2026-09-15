"""
State management for the Intent Disambiguation Agent.

This module defines pure dataclasses for representing agent state and intent candidates.
No ADK imports or side effects here - keep it clean and testable.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Literal


@dataclass
class IntentCandidate:
    """
    Represents a single possible intent classification result.
    
    Attributes:
        id: Machine-friendly identifier, e.g. "send_money"
        label: Human-readable label, e.g. "Send money"
        confidence: Confidence score between 0.0 and 1.0
        description: Brief description of what this intent represents
    """
    id: str
    label: str
    confidence: float
    description: str


@dataclass
class IdaState:
    """
    State for the Intent Disambiguation Agent across conversation turns.
    
    This state is maintained throughout the disambiguation process and tracks:
    - Current phase of the conversation
    - User messages
    - Candidate intents with confidence scores
    - Final selected intent (once resolved)
    - Reason for ambiguity (if detected)
    
    Attributes:
        phase: Current phase of the disambiguation process
        last_user_message: The most recent message from the user
        candidate_intents: List of possible intents with confidence scores
        selected_intent_id: The final selected intent ID (None until resolved)
        ambiguity_reason: Explanation of why ambiguity was detected (if applicable)
    """
    phase: Literal["initial", "awaiting_clarification", "resolved"] = "initial"
    last_user_message: Optional[str] = None
    candidate_intents: List[IntentCandidate] = field(default_factory=list)
    selected_intent_id: Optional[str] = None
    ambiguity_reason: Optional[str] = None
    mode: Literal["json", "toon"] = "json"


