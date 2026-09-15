"""
Tools for the Intent Disambiguation Agent.

This module defines the primary FunctionTool that contains the core business logic
for intent disambiguation.
"""
from typing import Any, Dict, List, Optional

from google.adk.tools import FunctionTool

from .state import IdaState, IntentCandidate
from .classifier import simple_classifier, parse_toon_intents
from .config import INTENTS_TOON, INTENTS_JSON
from .developer import handle_developer_command


def resolve_clarification(
    clarification: str,
    candidates: List[IntentCandidate],
    intents_data: List[Dict[str, Any]]
) -> str:
    """
    Resolves the user's clarification message to a specific intent ID.
    
    Logic:
    1. Exact ID match (case-insensitive)
    2. Label match
    3. Keyword match against candidate intent definitions
    4. Fallback to top candidate
    """
    clarification_lower = clarification.lower().strip()
    
    # 1. Exact ID match
    for cand in candidates:
        if cand.id.lower() in clarification_lower:
            return cand.id
            
    # 2. Label match
    for cand in candidates:
        if cand.label.lower() in clarification_lower:
            return cand.id
            
    # 3. Keyword match (using full intent definition for keywords)
    # Map candidate IDs to their full definition to access keywords
    intent_map = {i["id"]: i for i in intents_data}
    
    for cand in candidates:
        intent_def = intent_map.get(cand.id)
        if not intent_def:
            continue
            
        for keyword in intent_def.get("keywords", []):
            if keyword.lower() in clarification_lower:
                return cand.id
                
    # 4. Fallback: return top candidate
    if candidates:
        return candidates[0].id
        
    # Should not happen if candidates list is populated, but safe fallback
    return "unknown"


def intent_disambiguation_function(
    user_message: str,
    state: IdaState,
) -> Dict[str, Any]:
    """
    Detects ambiguous user intents, asks for clarification, 
    and returns a final routing decision once resolved.
    
    Core business logic for intent disambiguation.
    This function will:
    - Run a mock intent classifier over `user_message`.
    - Decide if the result is ambiguous based on mock scores and thresholds.
    - Update and return an updated IdaState.
    - Return a structured result that the ADK agent can send back.
    
    Args:
        user_message: The text input from the user.
        state: The current IdaState instance to update.
        
    Returns:
        A dictionary containing:
        - "state": Updated IdaState (as dict or serialized)
        - "response": The agent's response message to the user
        - "is_resolved": Boolean indicating if intent has been resolved
        - "selected_intent_id": The final intent ID (if resolved)
    """
    # Developer-only commands
    if user_message.startswith("/"):
        # handle commands WITHOUT modifying phase logic
        return handle_developer_command(user_message, state)

    # Determine intents based on mode (needed for both phases)
    if state.mode == "json":
        intents = INTENTS_JSON
    else:
        intents = parse_toon_intents(INTENTS_TOON)

    # 1. Save user_message into state
    # NOTE: In "awaiting_clarification", user_message is the clarification.
    # state.last_user_message preserves the ORIGINAL message if needed,
    # but here we update it to reflect the latest interaction.
    # Alternatively, we could store original message separately if required.
    # For this simple flow, updating it is fine as we use candidates list for context.
    state.last_user_message = user_message
    
    # --- PHASE: INITIAL ---
    if state.phase == "initial":
        # 2. Call simple_classifier to obtain sorted candidates
        candidates = simple_classifier(user_message, intents)
        
        # 3. Extract top 3 candidates and store them
        top_candidates = candidates[:3]
        state.candidate_intents = top_candidates
        
        if not top_candidates:
            state.phase = "awaiting_clarification"
            state.ambiguity_reason = "no_candidates"
            return {
                "status": "NEED_CLARIFICATION",
                "message_to_user": "I didn't understand that. Could you please rephrase?",
                "options": []
            }
            
        top = top_candidates[0]
        second = top_candidates[1] if len(top_candidates) > 1 else None
        
        # 4. Ambiguity detection
        is_ambiguous = False
        reason = None
        
        if top.confidence < 0.30:
            is_ambiguous = True
            reason = "low_confidence"
        elif second and abs(top.confidence - second.confidence) < 0.15:
            is_ambiguous = True
            reason = "close_scores"
            
        # 5. If RESOLVED
        if not is_ambiguous:
            state.phase = "resolved"
            state.selected_intent_id = top.id
            state.ambiguity_reason = None
            
            return {
                "status": "RESOLVED",
                "route_to": top.id,
                "message_to_user": f"Great, I will help you with {top.label.lower()}."
            }
            
        # 6. If AMBIGUOUS
        else:
            state.phase = "awaiting_clarification"
            state.ambiguity_reason = reason
            
            return {
                "status": "NEED_CLARIFICATION",
                "message_to_user": "I’m not sure what you meant. Can you clarify your intent?",
                "options": [
                    {"id": cand.id, "label": cand.label}
                    for cand in top_candidates
                ]
            }
            
    # --- PHASE: AWAITING CLARIFICATION ---
    elif state.phase == "awaiting_clarification":
        # Validate we have candidates to choose from
        if not state.candidate_intents:
            # Edge case: lost state or empty candidates. Fallback to re-classify as initial.
            state.phase = "initial"
            return intent_disambiguation_function(user_message, state)

        # Resolve using helper logic
        selected_id = resolve_clarification(
            clarification=user_message,
            candidates=state.candidate_intents,
            intents_data=intents
        )
        
        # Update state to RESOLVED
        state.phase = "resolved"
        state.selected_intent_id = selected_id
        state.ambiguity_reason = None  # Clear ambiguity as it is now resolved
        
        return {
            "status": "RESOLVED",
            "route_to": selected_id,
            "message_to_user": f"Thanks! I will route you to {selected_id}."
        }
        
    return {
        "status": "ERROR",
        "message_to_user": "Unknown state phase."
    }


intent_disambiguation_tool = FunctionTool(
    func=intent_disambiguation_function,
)
