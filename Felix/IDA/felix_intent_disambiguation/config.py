"""
Configuration constants for the Intent Disambiguation Agent.

This module defines:
- Supported intent definitions (placeholders for now)
- Thresholds for ambiguity detection
- Other configuration constants

DO NOT implement classification logic here - just define constants.
"""
from typing import Dict, List, Any

# Supported intents - simple dict structure for now
# Format: { "id": "intent_id", "label": "Human Readable Label", "keywords": [...] }
INTENTS_JSON: List[Dict[str, Any]] = [
    {
        "id": "send_money",
        "label": "Send Money",
        "keywords": ["send", "transfer", "money", "cash", "wire", "enviar", "mandar", "dinero", "transferir"],
        "description": "User wants to send or transfer money to someone",
        "starter_phrases": [
            "I need to send money",
            "I want to transfer cash",
            "Can I send funds",
            "Transfer money please"
        ],
        "semantic_vector": [0.82, 0.10, 0.08],
        "triggers": [r"\btransfer\b", r"\bsend money\b", r"\bsend\b", r"\bwire\b", r"\benviar\b", r"\bmandar\b"]
    },
    {
        "id": "check_balance",
        "label": "Check Balance",
        "keywords": ["balance", "check", "available", "account", "funds", "saldo", "balance", "cuanto", "tengo"],
        "description": "User wants to check their account balance",
        "starter_phrases": [
            "What's my balance",
            "Check my available funds",
            "Show me my balance",
            "How much do I have"
        ],
        "semantic_vector": [0.05, 0.10, 0.85],
        "triggers": [r"\bbalance\b", r"\bcheck\b", r"\bavailable\b", r"\bsaldo\b"]
    },
    {
        "id": "pay_bill",
        "label": "Pay Bill",
        "keywords": ["bill", "pay", "payment", "due", "invoice", "pagar", "factura", "recibo", "servicio"],
        "description": "User wants to pay a bill or invoice",
        "starter_phrases": [
            "I need to pay my bill",
            "Can I pay services",
            "Pay invoice please",
            "I want to pay bills"
        ],
        "semantic_vector": [0.12, 0.80, 0.08],
        "triggers": [r"\bpay\b", r"\bbill\b", r"\binvoice\b", r"\bpagar\b", r"\bfactura\b"]
    },
    {
        "id": "transaction_history",
        "label": "Transaction History",
        "keywords": ["history", "transactions", "statement", "past", "recent", "historia", "movimientos", "transacciones"],
        "description": "User wants to view their transaction history",
        "starter_phrases": ["Show my history", "Recent transactions"],
        "semantic_vector": [0.2, 0.2, 0.2],
        "triggers": [r"\bhistory\b", r"\btransactions\b", r"\bmovimientos\b"]
    },
    {
        "id": "card_management",
        "label": "Card Management",
        "keywords": ["card", "debit", "credit", "block", "unblock", "replace", "tarjeta", "bloquear", "desbloquear"],
        "description": "User wants to manage their card (block, unblock, replace, etc.)",
        "starter_phrases": ["Block my card", "I lost my card"],
        "semantic_vector": [0.3, 0.3, 0.3],
        "triggers": [r"\bcard\b", r"\bblock\b", r"\btarjeta\b"]
    },
]

# For backward compatibility if code uses SUPPORTED_INTENTS
SUPPORTED_INTENTS = INTENTS_JSON

INTENTS_TOON: str = """
intents[5]{id,label,keywords,description,starter_phrases,semantic_vector,triggers}:
  send_money,Send Money,"send,transfer,money,cash,enviar,mandar,dinero","User wants to transfer funds.","I need to send money,I want to transfer cash",[0.82,0.10,0.08],"\\btransfer\\b,\\bsend money\\b,\\bsend\\b,\\benviar\\b,\\bmandar\\b"
  pay_bill,Pay Bill,"pay,bill,payment,pagar,factura,recibo","User wants to pay a service.","I need to pay my bill,Can I pay services",[0.12,0.80,0.08],"\\bpay\\b,\\bbill\\b,\\bpagar\\b"
  check_balance,Check Balance,"balance,check,available,saldo,cuanto,tengo","User wants to check balance.","What's my balance,Check my available funds",[0.05,0.10,0.85],"\\bbalance\\b,\\bcheck\\b,\\bsaldo\\b"
  transaction_history,Transaction History,"history,transactions,statement,movimientos,historial","View past transactions.","Show my history",[0.2,0.2,0.2],"\\bhistory\\b,\\bmovimientos\\b"
  card_management,Card Management,"card,block,replace,tarjeta,bloquear","Manage cards.","Block my card",[0.3,0.3,0.3],"\\bcard\\b,\\btarjeta\\b"
"""

# Ambiguity detection thresholds
CONFIDENCE_MIN: float = 0.3
"""
Minimum confidence score required for an intent to be considered a valid candidate.
Intents below this threshold are filtered out.
"""

CONFIDENCE_MARGIN: float = 0.15
"""
Maximum difference between top candidates for the result to be considered unambiguous.
If the difference between the top two candidates is less than this margin, 
the message is considered ambiguous.
"""

MAX_CANDIDATES_TO_SHOW: int = 3
"""
Maximum number of candidate intents to present to the user during clarification.
"""
