import time
from felix_intent_disambiguation.state import IdaState
from felix_intent_disambiguation.tools import intent_disambiguation_function

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def run_interaction(scenario_name, messages, initial_mode="json"):
    print_separator(f"SCENARIO: {scenario_name}")
    
    # Initialize State
    state = IdaState()
    
    # Switch mode if needed (simulating developer command first if not default)
    if initial_mode == "toon":
        print("🔹 [Developer] Switching to TOON mode...")
        res = intent_disambiguation_function("/switch_mode toon", state)
        print(f"   System: {res['message_to_user']}\n")

    for i, user_msg in enumerate(messages):
        print(f"👤 User: \"{user_msg}\"")
        
        # Add a small delay for realism
        time.sleep(0.5)
        
        # Call the tool
        result = intent_disambiguation_function(user_msg, state)
        
        # Print Agent Response
        print(f"🤖 Agent: \"{result.get('message_to_user', '')}\"")
        
        # Print Status & Routing info
        status = result.get('status')
        if status == "NEED_CLARIFICATION":
            options = [opt['label'] for opt in result.get('options', [])]
            print(f"   [Status: {status}]")
            print(f"   [Options Presented: {', '.join(options)}]")
            print(f"   [Internal Phase: {state.phase}]")
        elif status == "RESOLVED":
            route = result.get('route_to')
            print(f"   [Status: {status}]")
            print(f"   [Routed To: {route}]")
            print(f"   [Internal Phase: {state.phase}]")
        
        print("-" * 40)

if __name__ == "__main__":
    # --- SCENARIO 1: Ambiguity & Resolution (Standard Flow) ---
    run_interaction(
        "Handling Ambiguity (JSON Mode)",
        [
            "I want to handle my money",  # Vague -> triggers clarification
            "send money to mom"           # Clarification -> resolves to send_money
        ]
    )

    # --- SCENARIO 2: Direct Resolution (Standard Flow) ---
    run_interaction(
        "Direct Resolution (JSON Mode)",
        [
            "check my account balance"    # Clear -> resolves immediately
        ]
    )

    # --- SCENARIO 3: Developer Mode (TOON) ---
    run_interaction(
        "Developer Experiment (TOON Mode)",
        [
            "I need to pay services",     # Ambiguous in TOON logic
            "pay_bill"                    # Direct ID match clarification
        ],
        initial_mode="toon"
    )

