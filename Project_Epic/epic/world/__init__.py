"""
World Visualization System

Emits events from orchestrator → frontend visualization.
Based on FullProposal.md sections 6-7.
"""
from .event_emitter import WorldEventEmitter, WorldEvent, EventType
from .dialogue_engine import DialogueEngine, DialogueTrigger

__all__ = ["WorldEventEmitter", "WorldEvent", "EventType", "DialogueEngine", "DialogueTrigger"]
