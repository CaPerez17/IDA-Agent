"""
Simple and explainable classifier for Intent Disambiguation.

This module implements:
- TOON -> Python parser for intent definitions
- Deterministic fake embeddings (hash-based)
- Scoring logic (keyword, trigger, semantic)
- Simple classifier returning sorted candidates
"""
import re
import math
import hashlib
from typing import List, Dict, Any, Optional
from ast import literal_eval

from .config import INTENTS_TOON
from .state import IntentCandidate


def parse_toon_intents(toon_str: str) -> List[Dict[str, Any]]:
    """
    Parse TOON intent specification into a list of intent dictionaries.
    
    Expected format per line:
    id,label,keywords,description,starter_phrases,semantic_vector,triggers
    """
    lines = toon_str.strip().split('\n')
    parsed_intents = []
    
    # Skip header if it starts with 'intents'
    start_idx = 0
    if lines and lines[0].strip().startswith('intents'):
        start_idx = 1
        
    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue
            
        # Simple split by comma - assumes TOON string is well-formed as per rules
        # NOTE: For production, use a proper CSV parser or regex if values contain commas
        # But instruction says "simple, direct, not overly defensive"
        # We will use a regex split to handle quoted fields correctly
        
        # Regex to split by comma but ignore commas inside quotes or brackets
        # This is slightly more robust than split(',') but still lightweight
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)(?=(?:[^\[]*\[[^\]]*\])*[^\[]*$)', line)
        
        if len(parts) < 7:
            continue
            
        intent_id = parts[0].strip()
        label = parts[1].strip()
        
        # Keywords: remove quotes, split by comma
        keywords_raw = parts[2].strip().strip('"')
        keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
        
        description = parts[3].strip().strip('"')
        
        # Starter phrases
        starters_raw = parts[4].strip().strip('"')
        starter_phrases = [s.strip() for s in starters_raw.split(',') if s.strip()]
        
        # Semantic vector: safe eval of string list "[0.1, 0.2, ...]"
        vector_raw = parts[5].strip()
        try:
            semantic_vector = literal_eval(vector_raw)
        except (ValueError, SyntaxError):
            semantic_vector = [0.0, 0.0, 0.0]
            
        # Triggers
        triggers_raw = parts[6].strip().strip('"')
        # Handle escaped regex sequences if needed, but mostly raw string
        triggers = [t.strip() for t in triggers_raw.split(',') if t.strip()]
        # Fix escaped backslashes from TOON format (e.g. \\b -> \b)
        triggers = [t.replace('\\b', r'\b').replace('\\s', r'\s') for t in triggers]
        
        parsed_intents.append({
            "id": intent_id,
            "label": label,
            "keywords": keywords,
            "description": description,
            "starter_phrases": starter_phrases,
            "semantic_vector": semantic_vector,
            "triggers": triggers
        })
        
    return parsed_intents


def fake_embedding(text: str) -> List[float]:
    """
    Convert text into a deterministic 3D vector using SHA256.
    """
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hex_str = hash_obj.hexdigest()
    
    # Extract 3 floats from hex string
    # 8 hex chars = 4 bytes = 32 bits
    max_val = 16**8
    x = int(hex_str[0:8], 16) / max_val
    y = int(hex_str[8:16], 16) / max_val
    z = int(hex_str[16:24], 16) / max_val
    
    # Normalize to unit length
    magnitude = math.sqrt(x*x + y*y + z*z)
    if magnitude > 0:
        return [x/magnitude, y/magnitude, z/magnitude]
    return [0.0, 0.0, 1.0]


def keyword_score(message: str, keywords: List[str]) -> float:
    """
    Calculate keyword match score.
    Score = (#keywords found) / len(keywords)
    """
    if not keywords:
        return 0.0
        
    message_lower = message.lower()
    found = sum(1 for k in keywords if k.lower() in message_lower)
    return found / len(keywords)


def trigger_score(message: str, triggers: List[str]) -> float:
    """
    Calculate regex trigger match score.
    Score = (#triggers matched) / len(triggers)
    """
    if not triggers:
        return 0.0
        
    count = 0
    for pattern in triggers:
        try:
            if re.search(pattern, message, re.IGNORECASE):
                count += 1
        except re.error:
            continue
            
    return count / len(triggers)


def semantic_score(user_vec: List[float], intent_vec: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    if len(user_vec) != len(intent_vec):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(user_vec, intent_vec))
    mag_a = math.sqrt(sum(a * a for a in user_vec))
    mag_b = math.sqrt(sum(b * b for b in intent_vec))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
        
    return dot_product / (mag_a * mag_b)


def combined_score(message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute weighted combined score for an intent.
    Weights: Keyword (0.5), Trigger (0.3), Semantic (0.2)
    """
    k_score = keyword_score(message, intent["keywords"])
    t_score = trigger_score(message, intent["triggers"])
    
    user_vec = fake_embedding(message)
    s_score = semantic_score(user_vec, intent["semantic_vector"])
    # Ensure semantic score is non-negative for weighted sum
    s_score_pos = max(0.0, s_score)
    
    final = (0.5 * k_score) + (0.3 * t_score) + (0.2 * s_score_pos)
    
    return {
        "id": intent["id"],
        "label": intent["label"],
        "score": final,
        "breakdown": {
            "keyword": k_score,
            "trigger": t_score,
            "semantic": s_score
        },
        "intent_data": intent
    }


def simple_classifier(message: str, intents: List[Dict[str, Any]] = None) -> List[IntentCandidate]:
    """
    Classify a message against provided intents and return sorted candidates.
    If intents is None, defaults to parsing INTENTS_TOON.
    """
    if intents is None:
        intents = parse_toon_intents(INTENTS_TOON)
        
    candidates_data = []
    
    for intent in intents:
        result = combined_score(message, intent)
        candidates_data.append(result)
        
    # Sort by score descending
    candidates_data.sort(key=lambda x: x["score"], reverse=True)
    
    # Convert to IntentCandidate objects
    candidates = []
    for data in candidates_data:
        candidate = IntentCandidate(
            id=data["id"],
            label=data["label"],
            confidence=data["score"],
            description=data["intent_data"]["description"]
        )
        candidates.append(candidate)
        
    return candidates

