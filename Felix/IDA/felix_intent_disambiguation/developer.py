"""
Developer-only commands for debugging and experimentation.
"""
from typing import Dict, Any, List
from .state import IdaState, IntentCandidate
from .config import INTENTS_JSON, INTENTS_TOON
from .classifier import simple_classifier, parse_toon_intents, combined_score

def run_json_classifier(message: str) -> Dict[str, Any]:
    """
    Run classification using JSON intent definitions.
    """
    # simple_classifier expects intents to be passed if we want to override default TOON
    # But current simple_classifier implementation hardcodes parse_toon_intents(INTENTS_TOON)
    # We need to refactor simple_classifier to accept intents list, or replicate logic here.
    # Let's replicate for now to avoid changing classifier.py too much unless necessary.
    
    candidates_data = []
    for intent in INTENTS_JSON:
        # Ensure JSON intent has empty lists for missing fields if needed by combined_score
        # combined_score expects: keywords, triggers, semantic_vector
        # INTENTS_JSON has these.
        result = combined_score(message, intent)
        candidates_data.append(result)
    
    candidates_data.sort(key=lambda x: x["score"], reverse=True)
    
    top = candidates_data[0] if candidates_data else None
    
    return {
        "top_intent": top["id"] if top else None,
        "score": top["score"] if top else 0.0,
        "scores_raw": [
            {"id": c["id"], "score": c["score"]} for c in candidates_data
        ]
    }

def run_toon_classifier(message: str) -> Dict[str, Any]:
    """
    Run classification using TOON intent definitions.
    """
    intents = parse_toon_intents(INTENTS_TOON)
    
    candidates_data = []
    for intent in intents:
        result = combined_score(message, intent)
        candidates_data.append(result)
        
    candidates_data.sort(key=lambda x: x["score"], reverse=True)
    
    top = candidates_data[0] if candidates_data else None
    
    return {
        "top_intent": top["id"] if top else None,
        "score": top["score"] if top else 0.0,
        "scores_raw": [
            {"id": c["id"], "score": c["score"]} for c in candidates_data
        ]
    }

def handle_developer_command(command: str, state: IdaState) -> Dict[str, Any]:
    """
    Handle developer commands starting with /.
    """
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == "/switch_mode":
        if len(parts) < 2:
            return {
                "status": "ERROR",
                "message_to_user": "Usage: /switch_mode [json|toon]"
            }
        
        mode = parts[1].lower()
        if mode not in ["json", "toon"]:
             return {
                "status": "ERROR",
                "message_to_user": "Invalid mode. Use 'json' or 'toon'."
            }
            
        state.mode = mode
        return {
            "status": "ACK",
            "message_to_user": f"Developer: switched to {state.mode.upper()} mode."
        }
        
    elif cmd == "/compare_modes":
        message = state.last_user_message
        if not message:
            return {
                "status": "ERROR",
                "message_to_user": "No recent user message to compare."
            }
            
        json_res = run_json_classifier(message)
        toon_res = run_toon_classifier(message)
        
        # Analysis
        match = json_res["top_intent"] == toon_res["top_intent"]
        winner = "JSON" if json_res["score"] > toon_res["score"] else "TOON"
        if abs(json_res["score"] - toon_res["score"]) < 0.001:
            winner = "TIE"
            
        analysis = (
            f"Agreement: {'YES' if match else 'NO'}. "
            f"Higher Score: {winner}. "
            f"Diff: {abs(json_res['score'] - toon_res['score']):.4f}"
        )
        
        return {
            "status": "DEVELOPER_COMPARE",
            "json_result": json_res,
            "toon_result": toon_res,
            "analysis": analysis,
            "message_to_user": (
                f"COMPARE REPORT:\n"
                f"JSON: {json_res['top_intent']} ({json_res['score']:.3f})\n"
                f"TOON: {toon_res['top_intent']} ({toon_res['score']:.3f})\n"
                f"Analysis: {analysis}"
            )
        }
        
    else:
        return {
            "status": "ERROR",
            "message_to_user": "Unknown developer command."
        }

