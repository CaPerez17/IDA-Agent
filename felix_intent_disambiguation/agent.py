"""
Main agent definition for the Intent Disambiguation Agent.

This module creates the root ADK Agent instance that handles intent disambiguation.
"""
from google.adk.agents import Agent

from .tools import intent_disambiguation_tool

ida_agent = Agent(
    name="felix_intent_disambiguation_agent",
    model="gemini-2.0-flash-exp",  # NOTE: placeholder, can be adjusted if needed
    description=(
        "An Intent Disambiguation Agent that detects ambiguous user messages, "
        "asks clarifying questions, and outputs a final routing decision."
    ),
    instruction=(
        "You are a lightweight intent disambiguation layer at the start of a conversation. "
        "For each user message, you may call the `intent_disambiguation_tool` to:\n"
        "- classify the user's intent using mock logic,\n"
        "- detect ambiguity,\n"
        "- ask for clarification by presenting 2-3 options when needed,\n"
        "- and finally select exactly one intent to route the conversation to.\n\n"
        "Always rely on the tool to maintain and update the internal IdaState."
    ),
    tools=[intent_disambiguation_tool],
)
