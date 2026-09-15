"""
Compare JSON-based vs TOON-based intent classification for fintech intents.

This module provides standalone experimentation tools to compare:
- JSON intent definitions (Python dicts)
- TOON intent definitions (structured text format)

Both approaches use the same scoring mechanisms:
- Pattern matching (regex triggers)
- Keyword matching
- Semantic similarity (cosine similarity)
- Starter phrase similarity (SequenceMatcher)
"""
import re
import json
import math
import hashlib
from difflib import SequenceMatcher
from typing import List, Dict, Any


# --------------------------------------------------------------
# 2. JSON INTENT DEFINITIONS
# --------------------------------------------------------------

INTENTS_JSON: List[Dict[str, Any]] = [
    {
        "id": "send_money",
        "label": "Send Money",
        "keywords": ["send", "transfer", "money", "cash", "wire"],
        "description": "User wants to transfer funds to another person or account.",
        "starter_phrases": [
            "I need to send money",
            "I want to transfer cash",
            "Can I send funds",
            "Transfer money please"
        ],
        "semantic_vector": [0.82, 0.10, 0.08],
        "triggers": [r"\btransfer\b", r"\bsend money\b", r"\bsend\b", r"\bwire\b"]
    },
    {
        "id": "pay_bill",
        "label": "Pay Bill",
        "keywords": ["pay", "bill", "payment", "due", "invoice"],
        "description": "User wants to pay a service bill or invoice.",
        "starter_phrases": [
            "I need to pay my bill",
            "Can I pay services",
            "Pay invoice please",
            "I want to pay bills"
        ],
        "semantic_vector": [0.12, 0.80, 0.08],
        "triggers": [r"\bpay\b", r"\bbill\b", r"\binvoice\b"]
    },
    {
        "id": "check_balance",
        "label": "Check Balance",
        "keywords": ["balance", "check", "available", "account", "funds"],
        "description": "User wants to check their account balance.",
        "starter_phrases": [
            "What's my balance",
            "Check my available funds",
            "Show me my balance",
            "How much do I have"
        ],
        "semantic_vector": [0.05, 0.10, 0.85],
        "triggers": [r"\bbalance\b", r"\bcheck\b", r"\bavailable\b"]
    }
]


# --------------------------------------------------------------
# 3. TOON INTENT DEFINITIONS
# --------------------------------------------------------------

INTENTS_TOON: str = """
intents[3]{id,label,keywords,description,starter_phrases,semantic_vector,triggers}:
  send_money,Send Money,"send,transfer,money,cash","User wants to transfer funds.","I need to send money,I want to transfer cash",[0.82,0.10,0.08],"\\btransfer\\b,\\bsend money\\b,\\bsend\\b"
  pay_bill,Pay Bill,"pay,bill,payment","User wants to pay a service.","I need to pay my bill,Can I pay services",[0.12,0.80,0.08],"\\bpay\\b,\\bbill\\b"
  check_balance,Check Balance,"balance,check,available","User wants to check balance.","What's my balance,Check my available funds",[0.05,0.10,0.85],"\\bbalance\\b,\\bcheck\\b"
"""


# --------------------------------------------------------------
# 4. PARSE TOON → PYTHON
# --------------------------------------------------------------

def parse_toon_intents(toon_str: str) -> List[Dict[str, Any]]:
    """
    Parse the TOON intent specification into a list of intent dicts.
    
    Steps:
      - Skip header line
      - Process each row
      - Split by comma respecting the structure
      - Convert:
          keywords → List[str]
          starter_phrases → List[str]
          semantic_vector → List[float]
          triggers → List[str]
    
    Args:
        toon_str: The TOON format string containing intent definitions.
        
    Returns:
        A list of intent dictionaries with the same structure as INTENTS_JSON.
    """
    lines = toon_str.strip().split('\n')
    parsed_intents = []
    
    # Skip header line (starts with "intents")
    data_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('intents')]
    
    for line in data_lines:
        if not line:
            continue
        
        # More robust parsing: handle quoted strings and brackets
        parts = []
        current = ""
        in_quotes = False
        in_brackets = False
        
        i = 0
        while i < len(line):
            char = line[i]
            
            if char == '"' and (i == 0 or line[i-1] != '\\'):
                in_quotes = not in_quotes
                current += char
            elif char == '[' and not in_quotes:
                in_brackets = True
                current += char
            elif char == ']' and not in_quotes:
                in_brackets = False
                current += char
            elif char == ',' and not in_quotes and not in_brackets:
                parts.append(current.strip())
                current = ""
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current.strip())
        
        if len(parts) < 7:
            continue
        
        # Extract fields
        intent_id = parts[0].strip()
        label = parts[1].strip()
        
        # Parse keywords (remove quotes, split by comma)
        keywords_str = parts[2].strip().strip('"')
        keywords = [k.strip() for k in keywords_str.split(',')]
        
        # Description (remove quotes)
        description = parts[3].strip().strip('"')
        
        # Parse starter_phrases (remove quotes, split by comma)
        starters_str = parts[4].strip().strip('"')
        starter_phrases = [s.strip() for s in starters_str.split(',')]
        
        # Parse semantic_vector (remove brackets, split by comma)
        vector_str = parts[5].strip().strip('[]')
        semantic_vector = [float(x.strip()) for x in vector_str.split(',')]
        
        # Parse triggers (remove quotes, split by comma, preserve escaped sequences)
        triggers_str = parts[6].strip().strip('"')
        # Split by comma but preserve escaped sequences
        triggers = []
        current_trigger = ""
        i = 0
        while i < len(triggers_str):
            char = triggers_str[i]
            if char == ',' and (i == 0 or triggers_str[i-1] != '\\'):
                triggers.append(current_trigger.strip())
                current_trigger = ""
            else:
                current_trigger += char
            i += 1
        if current_trigger:
            triggers.append(current_trigger.strip())
        
        # Convert escaped sequences to raw strings for regex
        # In TOON, \\b becomes \b in Python string, which is correct for regex
        # But we need to ensure they're treated as raw strings
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


# --------------------------------------------------------------
# 5. FAKE EMBEDDING FOR USER MESSAGE
# --------------------------------------------------------------

def fake_embedding(text: str) -> List[float]:
    """
    Convert text into a deterministic 3D vector.
    
    Uses hashlib.sha256(text.encode()).hexdigest() to generate 3 small floats.
    Normalizes the vector to unit length.
    
    Args:
        text: Input text to embed.
        
    Returns:
        A normalized 3D vector [x, y, z] with unit length.
    """
    hash_obj = hashlib.sha256(text.encode())
    hex_str = hash_obj.hexdigest()
    
    # Extract 3 floats from hex string (each 8 hex chars = 4 bytes)
    x = int(hex_str[0:8], 16) / (16**8)
    y = int(hex_str[8:16], 16) / (16**8)
    z = int(hex_str[16:24], 16) / (16**8)
    
    # Normalize to unit length
    magnitude = math.sqrt(x*x + y*y + z*z)
    if magnitude > 0:
        return [x/magnitude, y/magnitude, z/magnitude]
    return [0.0, 0.0, 1.0]


# --------------------------------------------------------------
# 6. SCORING FUNCTIONS
# --------------------------------------------------------------

def pattern_score(message: str, triggers: List[str]) -> float:
    """
    Count how many regex triggers match the message.
    
    score = matches / len(triggers)
    
    Args:
        message: User message to score.
        triggers: List of regex pattern strings.
        
    Returns:
        Score between 0.0 and 1.0.
    """
    if not triggers:
        return 0.0
    
    matches = 0
    for pattern in triggers:
        try:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1
        except re.error:
            # Invalid regex, skip
            continue
    
    return matches / len(triggers)


def keyword_score(message: str, keywords: List[str]) -> float:
    """
    Count keywords found in message.
    
    score = found / len(keywords)
    
    Args:
        message: User message to score.
        keywords: List of keyword strings to search for.
        
    Returns:
        Score between 0.0 and 1.0.
    """
    if not keywords:
        return 0.0
    
    message_lower = message.lower()
    found = sum(1 for keyword in keywords if keyword.lower() in message_lower)
    
    return found / len(keywords)


def semantic_score(user_vec: List[float], intent_vec: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        user_vec: User message embedding vector.
        intent_vec: Intent semantic vector.
        
    Returns:
        Cosine similarity score between -1.0 and 1.0 (typically 0.0 to 1.0).
    """
    if len(user_vec) != len(intent_vec):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(user_vec, intent_vec))
    
    magnitude_user = math.sqrt(sum(x*x for x in user_vec))
    magnitude_intent = math.sqrt(sum(x*x for x in intent_vec))
    
    if magnitude_user == 0 or magnitude_intent == 0:
        return 0.0
    
    return dot_product / (magnitude_user * magnitude_intent)


def starter_phrase_score(message: str, starters: List[str]) -> float:
    """
    Use difflib.SequenceMatcher to compute similarity.
    
    Return the maximum similarity among all starters.
    Range 0-1.
    
    Args:
        message: User message to score.
        starters: List of starter phrase strings.
        
    Returns:
        Maximum similarity score between 0.0 and 1.0.
    """
    if not starters:
        return 0.0
    
    message_lower = message.lower()
    max_similarity = 0.0
    
    for starter in starters:
        similarity = SequenceMatcher(None, message_lower, starter.lower()).ratio()
        max_similarity = max(max_similarity, similarity)
    
    return max_similarity


# --------------------------------------------------------------
# 7. COMBINED SCORE
# --------------------------------------------------------------

def combined_score(message: str, intent: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute pattern, keyword, semantic, and starter phrase scores.
    
    Weighting:
      0.40 pattern
      0.30 keyword
      0.20 semantic
      0.10 starter
    
    Args:
        message: User message to classify.
        intent: Intent dictionary with all required fields.
        
    Returns:
        Dictionary with all score components plus final weighted score:
        {
            "pattern": float,
            "keyword": float,
            "semantic": float,
            "starter": float,
            "final": float
        }
    """
    user_vec = fake_embedding(message)
    
    pattern = pattern_score(message, intent.get("triggers", []))
    keyword = keyword_score(message, intent.get("keywords", []))
    semantic = semantic_score(user_vec, intent.get("semantic_vector", []))
    starter = starter_phrase_score(message, intent.get("starter_phrases", []))
    
    # Ensure semantic score is non-negative for weighted average
    semantic_positive = max(0.0, semantic)
    
    final = (
        0.40 * pattern +
        0.30 * keyword +
        0.20 * semantic_positive +
        0.10 * starter
    )
    
    return {
        "pattern": pattern,
        "keyword": keyword,
        "semantic": semantic,
        "starter": starter,
        "final": final
    }


# --------------------------------------------------------------
# 8. CLASSIFIERS
# --------------------------------------------------------------

def classify_json(message: str) -> List[Dict[str, Any]]:
    """
    Classify message using JSON intent definitions.
    
    Returns a list of candidates:
    [
      {"id": ..., "score": final, "pattern":..., "keywords":..., ...},
      ...
    ]
    Sorted descending by score.
    
    Args:
        message: User message to classify.
        
    Returns:
        List of candidate dictionaries with scores, sorted by final score descending.
    """
    candidates = []
    
    for intent in INTENTS_JSON:
        scores = combined_score(message, intent)
        candidate = {
            "id": intent["id"],
            "label": intent["label"],
            "score": scores["final"],
            "pattern": scores["pattern"],
            "keyword": scores["keyword"],
            "semantic": scores["semantic"],
            "starter": scores["starter"]
        }
        candidates.append(candidate)
    
    # Sort by final score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    return candidates


def classify_toon(message: str, toon_intents: List[Dict[str, Any]]) -> tuple[str, List[float]]:
    """
    Classify message using TOON intent definitions.
    
    Returns a TOON table string with ranking and sorted scores list.
    
    Args:
        message: User message to classify.
        toon_intents: List of parsed TOON intent dictionaries.
        
    Returns:
        Tuple of (TOON report string, sorted scores list).
    """
    candidates = []
    
    for intent in toon_intents:
        scores = combined_score(message, intent)
        candidates.append({
            "id": intent["id"],
            "score": scores["final"],
            "pattern": scores["pattern"],
            "keyword": scores["keyword"],
            "semantic": scores["semantic"],
            "starter": scores["starter"]
        })
    
    # Sort by final score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Build TOON report
    report_lines = [
        "classifier_report:",
        f"  candidates[{len(candidates)}]{{id,score,pattern,keywords,semantic,starter}}:"
    ]
    
    for cand in candidates:
        report_lines.append(
            f"    {cand['id']},{cand['score']:.3f},{cand['pattern']:.3f},"
            f"{cand['keyword']:.3f},{cand['semantic']:.3f},{cand['starter']:.3f}"
        )
    
    report_str = "\n".join(report_lines)
    scores_list = [c["score"] for c in candidates]
    
    return report_str, scores_list


# --------------------------------------------------------------
# 9. COMPARATOR
# --------------------------------------------------------------

def compare_json_vs_toon(message: str) -> Dict[str, Any]:
    """
    Compare JSON vs TOON classification approaches.
    
    Performs:
      - JSON classification
      - TOON classification
      - Length of JSON spec
      - Length of TOON spec
      - Estimated token count (len(text)/4.0 approximate)
    
    Args:
        message: User message to classify.
        
    Returns:
        Dictionary summarizing:
        - top_json: Top JSON candidate
        - top_toon: Top TOON candidate
        - json_length: Length of JSON spec in characters
        - toon_length: Length of TOON spec in characters
        - json_tokens: Estimated token count for JSON
        - toon_tokens: Estimated token count for TOON
    """
    # JSON classification
    json_candidates = classify_json(message)
    top_json = json_candidates[0] if json_candidates else None
    
    # TOON classification
    toon_intents = parse_toon_intents(INTENTS_TOON)
    toon_report, toon_scores = classify_toon(message, toon_intents)
    
    # Get top TOON candidate (scores are already sorted descending)
    top_toon = None
    if toon_scores and toon_scores[0] > 0:
        # Re-classify to get full details for top candidate
        candidates = []
        for intent in toon_intents:
            scores = combined_score(message, intent)
            candidates.append({
                "id": intent["id"],
                "label": intent["label"],
                "score": scores["final"]
            })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_toon = candidates[0] if candidates else None
    
    # Calculate lengths
    json_str = json.dumps(INTENTS_JSON, indent=2)
    json_length = len(json_str)
    toon_length = len(INTENTS_TOON)
    
    # Estimate tokens (rough approximation: 4 chars per token)
    json_tokens = json_length / 4.0
    toon_tokens = toon_length / 4.0
    
    return {
        "top_json": top_json,
        "top_toon": top_toon,
        "json_length": json_length,
        "toon_length": toon_length,
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "toon_report": toon_report
    }


# --------------------------------------------------------------
# 10. MAIN EXECUTION BLOCK
# --------------------------------------------------------------

if __name__ == "__main__":
    # Parse TOON intents
    toon_intents = parse_toon_intents(INTENTS_TOON)
    print(f"Parsed {len(toon_intents)} TOON intents\n")
    
    # Test messages
    test_messages = [
        "I want to send money",
        "I need to pay services",
        "What's my balance?",
        "Transfer or pay something"
    ]
    
    # Process each message
    for i, message in enumerate(test_messages, 1):
        print(f"{'='*60}")
        print(f"Test Message {i}: {message}")
        print(f"{'='*60}\n")
        
        result = compare_json_vs_toon(message)
        
        print("JSON Classification:")
        if result["top_json"]:
            print(f"  Top Intent: {result['top_json']['id']} ({result['top_json']['label']})")
            print(f"  Score: {result['top_json']['score']:.3f}")
            print(f"  Components: pattern={result['top_json']['pattern']:.3f}, "
                  f"keyword={result['top_json']['keyword']:.3f}, "
                  f"semantic={result['top_json']['semantic']:.3f}, "
                  f"starter={result['top_json']['starter']:.3f}")
        
        print("\nTOON Classification:")
        if result["top_toon"]:
            print(f"  Top Intent: {result['top_toon']['id']} ({result['top_toon']['label']})")
            print(f"  Score: {result['top_toon']['score']:.3f}")
        
        print("\nSpecification Comparison:")
        print(f"  JSON length: {result['json_length']} chars ({result['json_tokens']:.1f} tokens)")
        print(f"  TOON length: {result['toon_length']} chars ({result['toon_tokens']:.1f} tokens)")
        print(f"  Compression ratio: {result['toon_length']/result['json_length']:.2f}x")
        
        print("\nTOON Classifier Report:")
        print(result["toon_report"])
        print("\n")

