"""
Interactive CLI demo for the Félix Intent Disambiguation Agent.

This script simulates a live conversation loop, allowing you to:
- Interact with the agent in real-time.
- See the internal state transitions (initial -> awaiting_clarification -> resolved).
- Visualize tool calls and classification scores.
- Use developer commands (/switch_mode, /compare_modes).
- Run experiments comparing JSON vs TOON efficiency.

Usage:
    python interactive_demo.py
"""
import sys
import json
import pprint
import time
from typing import Any, Dict, List

# Import agent and state components
from felix_intent_disambiguation import ida_agent, IdaState
from felix_intent_disambiguation.tools import intent_disambiguation_tool
from felix_intent_disambiguation.developer import handle_developer_command

# Import analysis tools for experiment mode
try:
    from analysis.classifier_compare import compare_json_vs_toon
except ImportError:
    # Fallback if running from wrong directory
    sys.path.append('.')
    from analysis.classifier_compare import compare_json_vs_toon

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def print_section(title: str, content: Any):
    print(f"\n--- {title} ---")
    if isinstance(content, (dict, list)):
        pprint.pprint(content, indent=2, width=80)
    else:
        print(content)

def format_state(state: IdaState) -> Dict[str, Any]:
    """Helper to pretty-print state without clutter."""
    return {
        "phase": state.phase,
        "mode": state.mode,
        "last_user_message": state.last_user_message,
        "selected_intent_id": state.selected_intent_id,
        "ambiguity_reason": state.ambiguity_reason,
        "candidate_count": len(state.candidate_intents) if state.candidate_intents else 0,
        "top_candidate": (
            f"{state.candidate_intents[0].id} ({state.candidate_intents[0].confidence:.2f})"
            if state.candidate_intents else None
        )
    }

def show_experiment_report(original_message: str):
    """Shows efficiency and scoring comparison for the resolved interaction."""
    print_header("EXPERIMENT ANALYSIS REPORT")
    print(f"Analyzing message: \"{original_message}\"")
    
    try:
        result = compare_json_vs_toon(original_message)
        
        print("\n1. EFFICIENCY METRICS:")
        print(f"   JSON Spec Size: {result['json_length']} chars (~{result['json_tokens']:.1f} tokens)")
        print(f"   TOON Spec Size: {result['toon_length']} chars (~{result['toon_tokens']:.1f} tokens)")
        print(f"   -> Compression: TOON is {result['toon_length']/result['json_length']:.2f}x the size of JSON")
        
        print("\n2. CLASSIFICATION COMPARISON:")
        
        # JSON Stats
        json_top = result['top_json']
        if json_top:
            print(f"   JSON Mode: Selected '{json_top['id']}' (Score: {json_top['score']:.3f})")
        else:
            print("   JSON Mode: No result")
            
        # TOON Stats
        toon_top = result['top_toon']
        if toon_top:
            print(f"   TOON Mode: Selected '{toon_top['id']}' (Score: {toon_top['score']:.3f})")
        else:
            print("   TOON Mode: No result")
            
        # Winner
        if json_top and toon_top:
            diff = toon_top['score'] - json_top['score']
            if diff > 0:
                print(f"   -> TOON had higher confidence (+{diff:.3f})")
            elif diff < 0:
                print(f"   -> JSON had higher confidence (+{abs(diff):.3f})")
            else:
                print(f"   -> Both modes had identical confidence")
                
    except Exception as e:
        print(f"Error generating report: {e}")
    
    print("\n" + "="*60)

def show_session_comparison(history: List[Dict[str, Any]]):
    """Compares full flows stored in session history."""
    print_header("SESSION FLOW COMPARISON REPORT")
    
    if not history:
        print("No completed flows in history yet.")
        return

    # Group by original message
    grouped = {}
    for entry in history:
        msg = entry['message']
        if msg not in grouped:
            grouped[msg] = {'json': None, 'toon': None}
        grouped[msg][entry['mode']] = entry

    # Display comparison
    found_comparison = False
    for msg, modes in grouped.items():
        json_run = modes['json']
        toon_run = modes['toon']
        
        if json_run or toon_run:
            print(f"\nMessage: \"{msg}\"")
            print("-" * 40)
            
            # JSON Row
            if json_run:
                print(f"  JSON Mode: Resolved to '{json_run['resolved_intent']}' "
                      f"(Score: {json_run['top_score']:.3f}, Steps: {json_run['steps']})")
            else:
                print("  JSON Mode: [Not run]")
                
            # TOON Row
            if toon_run:
                print(f"  TOON Mode: Resolved to '{toon_run['resolved_intent']}' "
                      f"(Score: {toon_run['top_score']:.3f}, Steps: {toon_run['steps']})")
            else:
                print("  TOON Mode: [Not run]")
            
            # Delta
            if json_run and toon_run:
                found_comparison = True
                score_diff = toon_run['top_score'] - json_run['top_score']
                steps_diff = toon_run['steps'] - json_run['steps']
                print(f"  -> Delta: Score {score_diff:+.3f}, Steps {steps_diff:+d}")
                if json_run['resolved_intent'] != toon_run['resolved_intent']:
                    print("  -> ⚠️ DIFFERENT INTENTS RESOLVED!")
            
    if not found_comparison:
        print("\nTip: Run the same message in both modes to see a direct comparison.")

def run_interactive_loop():
    print_header("Félix IDA - Interactive Developer Console")
    
    # --- Initial Configuration ---
    experiment_mode = False
    while True:
        mode_input = input("Do you want to run in EXPERIMENT mode? (y/n): ").strip().lower()
        if mode_input in ['y', 'yes']:
            experiment_mode = True
            break
        elif mode_input in ['n', 'no']:
            experiment_mode = False
            break
    
    initial_mode = "json"
    if experiment_mode:
        while True:
            m_input = input("Select initial classifier mode (json/toon): ").strip().lower()
            if m_input in ['json', 'toon']:
                initial_mode = m_input
                break
    
    print("\nCommands:")
    print("  /exit              - Quit the demo")
    print("  /switch_mode toon  - Switch to experimental TOON mode")
    print("  /compare_modes     - Compare completed flows in session history")
    print(f"\nStarting in [{initial_mode.upper()}] mode...")
    print("Type a message to start...\n")

    # Initialize state once for the session
    state = IdaState()
    state.mode = initial_mode
    
    # Track the original message that started a flow to analyze it later
    current_flow_message = None
    current_flow_steps = 0
    current_top_score = 0.0
    
    # Session History: List of {message, mode, resolved_intent, top_score, steps}
    session_history = []
    
    while True:
        try:
            user_input = input("\n👤 USER > ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["/exit", "/quit"]:
                print("\nExiting demo. Goodbye!")
                sys.exit(0)

            # Handle /compare_modes locally in the demo wrapper
            if user_input.lower() == "/compare_modes":
                show_session_comparison(session_history)
                continue

            # Track original message for experiment analysis
            if state.phase == "initial" and not user_input.startswith("/"):
                current_flow_message = user_input
                current_flow_steps = 0
                current_top_score = 0.0

            current_flow_steps += 1

            # --- Step 1: Agent Processing (Simulated) ---
            print_section("AGENT ACTION", "Analyzing input...")

            # --- Step 2: Tool Execution ---
            print(f"🛠  TOOL CALL: intent_disambiguation_tool(message='{user_input}')")
            
            # Execute the tool function directly to show internal logic
            tool_result = intent_disambiguation_tool.func(user_input, state)
            
            print_section("TOOL RESULT", tool_result)
            
            # Capture score from first turn for history
            if state.phase in ["awaiting_clarification", "resolved"] and current_flow_steps == 1:
                 if state.candidate_intents:
                     current_top_score = state.candidate_intents[0].confidence
            
            # --- Step 3: Ambiguity & Logic Explanation ---
            status = tool_result.get("status")
            
            if status == "NEED_CLARIFICATION":
                reason = state.ambiguity_reason
                print(f"\n⚠️  AMBIGUITY DETECTED: {reason}")
                if reason == "low_confidence":
                    print("   -> Top candidate score was below threshold (< 0.30).")
                elif reason == "close_scores":
                    print("   -> Top candidates had very similar scores (diff < 0.15).")
                elif reason == "no_candidates":
                    print("   -> No valid intents found.")
                
                print("   Top Candidates:")
                for c in state.candidate_intents[:3]:
                    print(f"   - {c.id}: {c.confidence:.3f}")

            elif status == "RESOLVED":
                print(f"\n✅  RESOLVED")
                print(f"   -> Final Intent: {state.selected_intent_id}")
                if state.phase == "resolved" and not state.ambiguity_reason:
                     print("   -> High confidence. No clarification needed.")
                else:
                     print("   -> Resolved after clarification.")

            elif status == "ACK":
                print(f"\nℹ️  SYSTEM COMMAND ACKNOWLEDGED")

            elif status == "DEVELOPER_COMPARE":
                print(f"\n🔍  DEVELOPER COMPARISON RUN")
                # Fallback if user types /compare_modes inside agent logic (though we trap it above now)
                pass

            # --- Step 4: Updated State ---
            print_section("UPDATED STATE", format_state(state))
            
            # --- Step 5: Final Agent Response ---
            agent_response = tool_result.get("message_to_user", "No response text.")
            print(f"\n🤖 AGENT RESPONSE: \"{agent_response}\"")
            
            # --- Step 6: Experiment Report (if enabled and resolved) ---
            if experiment_mode and status == "RESOLVED" and current_flow_message:
                # Save to history
                session_history.append({
                    "message": current_flow_message,
                    "mode": state.mode,
                    "resolved_intent": state.selected_intent_id,
                    "top_score": current_top_score,
                    "steps": current_flow_steps
                })
                
                time.sleep(0.5)
                show_experiment_report(current_flow_message)
                current_flow_message = None # Reset for next flow

            # Reset state if resolved (to allow new interactions in same loop)
            if state.phase == "resolved":
                print("\n[ℹ️  Conversation flow complete. State reset for next turn.]")
                # Preserve mode, reset flow
                current_mode = state.mode
                state = IdaState() 
                state.mode = current_mode

        except KeyboardInterrupt:
            print("\n\nExiting demo. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_interactive_loop()
