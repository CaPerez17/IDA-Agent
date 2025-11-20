# Félix Intent Disambiguation Agent (IDA)

A lightweight Intent Disambiguation Agent built with Google ADK (Agent Development Kit) that detects ambiguous user messages, asks for clarification, and routes conversations to the appropriate intent handlers.

## 📋 Overview

This project implements a conversational agent that acts as an **intent disambiguation layer** at the start of user interactions. When a user's initial message is vague or maps to multiple possible intents, the IDA:

1. **Detects ambiguity** using lightweight mock classification logic
2. **Pauses normal processing** to ask for clarification
3. **Presents top 3 candidate intents** to the user
4. **Resolves the intent** based on user confirmation
5. **Returns structured routing decisions** for downstream agents

Built as part of the **Félix AI Engineer Technical Assessment**.

## 🏗️ Architecture

The agent follows a clean, modular architecture:

```
felix_intent_disambiguation/
├── agent.py          # Main ADK Agent definition
├── tools.py          # Core disambiguation logic (FunctionTool)
├── classifier.py     # Lightweight mock classifier
├── state.py          # State management (IdaState, IntentCandidate)
├── config.py         # Intent definitions (JSON & TOON formats)
├── developer.py      # Developer debugging commands
└── __init__.py       # Package exports
```

### Key Components

- **Single ADK Agent**: `ida_agent` - The root conversational agent
- **State Machine**: `initial` → `awaiting_clarification` → `resolved`
- **Mock Classifier**: Deterministic scoring using keywords, regex triggers, and hash-based embeddings
- **Dual Format Support**: JSON (default) and TOON (experimental) intent definitions

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd IDA
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Interactive Demo

```bash
python interactive_demo.py
```

The demo will prompt you to choose:
- **Normal Mode**: Standard user interaction flow
- **Experiment Mode**: Compare JSON vs TOON classification efficiency

### Running Tests

```bash
pytest tests/
```

## 💡 Usage Examples

### Basic Interaction Flow

```python
from felix_intent_disambiguation import ida_agent, IdaState
from felix_intent_disambiguation.tools import intent_disambiguation_tool

# Initialize state
state = IdaState()

# First message (ambiguous)
result = intent_disambiguation_tool.func("I want to handle my money", state)
# Returns: {"status": "NEED_CLARIFICATION", "options": [...]}

# User clarifies
result = intent_disambiguation_tool.func("send money to mom", state)
# Returns: {"status": "RESOLVED", "route_to": "send_money"}
```

### Developer Commands

The agent supports hidden developer commands for experimentation:

- **`/switch_mode json`** - Switch to JSON classification mode (default)
- **`/switch_mode toon`** - Switch to experimental TOON mode
- **`/compare_modes`** - Compare JSON vs TOON results for completed flows

## 🔧 Features

### Intent Classification

The classifier uses a **weighted scoring system**:

- **Keywords** (50%): Exact keyword matches in user message
- **Regex Triggers** (30%): Pattern matching with predefined triggers
- **Semantic Similarity** (20%): Hash-based deterministic embeddings

### Ambiguity Detection

An intent is considered ambiguous if:
- Top candidate score < `CONFIDENCE_MIN` (0.30), OR
- Score difference between top 2 candidates < `CONFIDENCE_MARGIN` (0.15)

### Supported Intents

- **Send Money**: Transfer funds to another person or account
- **Check Balance**: View account balance
- **Pay Bill**: Pay service bills or invoices
- **Transaction History**: View past transactions
- **Card Management**: Block, unblock, or replace cards

*Note: Keywords support both English and Spanish.*

## 📊 Experiment Mode

When running in **Experiment Mode**, the demo automatically:

1. Tracks completed conversation flows
2. Compares JSON vs TOON classification efficiency
3. Shows compression ratios (TOON is ~0.36x the size of JSON)
4. Displays score differences and routing decisions

### Running Comparison Analysis

```bash
python analysis/classifier_compare.py
```

This standalone script runs predefined test cases and shows detailed comparison metrics.

## 🧪 Testing

The project includes basic tests for state management:

```bash
pytest tests/test_disambiguation_logic.py
```

## 📁 Project Structure

```
IDA/
├── felix_intent_disambiguation/    # Main package
│   ├── agent.py                     # ADK Agent definition
│   ├── tools.py                     # Core disambiguation logic
│   ├── classifier.py                # Mock classifier implementation
│   ├── state.py                     # State dataclasses
│   ├── config.py                    # Intent definitions
│   ├── developer.py                 # Developer commands
│   └── __init__.py                  # Package exports
├── analysis/                        # Experimental analysis tools
│   └── classifier_compare.py       # JSON vs TOON comparison
├── tests/                           # Test suite
│   └── test_disambiguation_logic.py
├── interactive_demo.py              # Interactive CLI demo
├── demo.py                          # Automated demo scenarios
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🎯 Design Decisions

### Why Mock Logic?

As per the assessment requirements: *"lightweight mock logic is perfectly fine"*. The classifier uses:
- Simple keyword matching (no ML models)
- Deterministic hash-based embeddings (no external APIs)
- Explainable scoring (transparent weights)

### Why Two Formats?

- **JSON**: Default, human-readable, easy to maintain
- **TOON**: Experimental compact format (~64% smaller), demonstrates efficiency gains

### State Management

The agent maintains conversation state across turns using the `IdaState` dataclass, allowing multi-turn clarification flows without external storage.

## 📝 License

This project was created as part of a technical assessment for Félix.

## 👤 Author

Camilo Pérez Martínez

## 🙏 Acknowledgments

- Google ADK framework for agent infrastructure
- Félix team for the technical assessment opportunity

