"""
World Event Emitter

Orchestrator emits events → WebSocket → Frontend visualization
Based on FullProposal.md section 6: Event System
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import asyncio
import json
import time
from datetime import datetime


class EventType(Enum):
    """World event types from FullProposal.md section 6.2"""

    # Quest lifecycle
    QUEST_START = "quest_start"
    QUEST_COMPLETE = "quest_complete"
    QUEST_FAILED = "quest_failed"

    # Phase transitions - trigger zone movement
    PHASE_CHANGE = "phase_change"
    SPRINT_START = "sprint_start"
    SPRINT_COMPLETE = "sprint_complete"

    # Agent state - trigger sprite updates
    AGENT_ACTIVE = "agent_active"
    AGENT_IDLE = "agent_idle"
    AGENT_OUTPUT = "agent_output"
    AGENT_ERROR = "agent_error"
    AGENT_THINKING = "agent_thinking"

    # Campfire - trigger group gathering
    CAMPFIRE_START = "campfire_start"
    CAMPFIRE_MESSAGE = "campfire_message"
    CAMPFIRE_DECISION = "campfire_decision"
    CAMPFIRE_END = "campfire_end"

    # Metrics - update HUD
    BUDGET_UPDATE = "budget_update"
    TOKEN_UPDATE = "token_update"
    PROGRESS_UPDATE = "progress_update"
    CONFIDENCE_UPDATE = "confidence_update"

    # World flavor - trigger ambient effects
    AMBIENT_TRIGGER = "ambient_trigger"
    ZONE_TRANSITION = "zone_transition"
    DIALOGUE = "dialogue"


@dataclass
class WorldEvent:
    """
    Event emitted from orchestrator to world visualization.

    Schema from FullProposal.md section 6.1
    """
    type: str  # EventType value
    timestamp: float  # Unix timestamp in milliseconds
    quest_id: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "quest_id": self.quest_id,
            "data": self.data,
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class WorldEventEmitter:
    """
    Emits world events from orchestrator to connected WebSocket clients.

    Usage in orchestrator:
        emitter = WorldEventEmitter()
        await emitter.emit(EventType.AGENT_ACTIVE, {...})
        await emitter.broadcast_to_all()
    """

    def __init__(self):
        self.clients: Set[Any] = set()  # WebSocket connections
        self.event_queue: List[WorldEvent] = []
        self.current_quest_id: Optional[str] = None
        self.confidence_score: float = 0.8  # Initial confidence
        self._event_history: List[WorldEvent] = []

    async def add_client(self, websocket):
        """Add a WebSocket client"""
        self.clients.add(websocket)
        print(f"✓ World client connected. Total clients: {len(self.clients)}")

    async def remove_client(self, websocket):
        """Remove a WebSocket client"""
        self.clients.discard(websocket)
        print(f"✓ World client disconnected. Total clients: {len(self.clients)}")

    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        quest_id: Optional[str] = None,
    ) -> WorldEvent:
        """
        Emit a world event.

        Args:
            event_type: Type of event
            data: Event payload
            quest_id: Optional quest ID (uses current if not specified)

        Returns:
            The created WorldEvent
        """
        event = WorldEvent(
            type=event_type.value,
            timestamp=time.time() * 1000,  # Milliseconds
            quest_id=quest_id or self.current_quest_id or "unknown",
            data=data,
        )

        self.event_queue.append(event)
        self._event_history.append(event)

        # Broadcast immediately to all clients
        await self._broadcast_event(event)

        return event

    async def _broadcast_event(self, event: WorldEvent):
        """Broadcast event to all connected clients"""
        if not self.clients:
            return

        message = event.to_json()
        disconnected = set()

        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.add(client)

        # Remove disconnected clients
        self.clients -= disconnected

    # Convenience methods for common events

    async def quest_start(self, quest_id: str, title: str, demon_lord: str, budget: float, token_limit: int):
        """Emit quest start event"""
        self.current_quest_id = quest_id
        await self.emit(EventType.QUEST_START, {
            "title": title,
            "demon_lord": demon_lord,
            "quest_type": "unknown",  # Can be detected
            "budget": budget,
            "token_limit": token_limit,
        })

    async def quest_complete(self, success: bool, duration_min: float, cost: float, tokens_used: int):
        """Emit quest complete event"""
        await self.emit(EventType.QUEST_COMPLETE, {
            "success": success,
            "duration_min": duration_min,
            "cost": cost,
            "tokens_used": tokens_used,
            "efficiency": (tokens_used / 100000) if tokens_used > 0 else 0,
        })

    async def phase_change(self, from_phase: str, to_phase: str, sprint_number: Optional[int] = None, sprint_name: Optional[str] = None):
        """
        Emit phase change - triggers zone movement in world.

        From FullProposal.md section 6.3:
        - All active agents pathfind to new zone
        - Idle agents stay at inn
        """
        await self.emit(EventType.PHASE_CHANGE, {
            "from": from_phase,
            "to": to_phase,
            "sprint_number": sprint_number,
            "sprint_name": sprint_name,
        })

    async def agent_active(self, agent_id: str, action: str, target_file: Optional[str] = None, detail: Optional[str] = None):
        """
        Emit agent active - triggers sprite working animation.

        From FullProposal.md section 6.3:
        - Agent sprite switches to working animation
        - Functional speech bubble appears
        """
        await self.emit(EventType.AGENT_ACTIVE, {
            "agent_id": agent_id,
            "action": action,
            "target_file": target_file,
            "detail": detail,
        })

    async def agent_idle(self, agent_id: str, reason: Optional[str] = None):
        """
        Emit agent idle - agent returns to inn.

        From FullProposal.md section 6.3:
        - Agent pathfinds to inn
        - Sprite switches to idle
        - May trigger ambient dialogue line
        """
        await self.emit(EventType.AGENT_IDLE, {
            "agent_id": agent_id,
            "reason": reason,
        })

    async def agent_output(self, agent_id: str, summary: str, output_type: str = "result"):
        """
        Emit agent output - shows functional speech bubble.

        Args:
            agent_id: Agent who produced output
            summary: 1-line summary for speech bubble
            output_type: "result", "error", "thinking"
        """
        await self.emit(EventType.AGENT_OUTPUT, {
            "agent_id": agent_id,
            "summary": summary,
            "output_type": output_type,
        })

    async def agent_error(self, agent_id: str, error_summary: str):
        """
        Emit agent error - move to forge zone.

        From FullProposal.md section 6.3:
        - Affected agent pathfinds to forge
        - Anvil animation plays
        - Tense ambient line
        """
        await self.emit(EventType.AGENT_ERROR, {
            "agent_id": agent_id,
            "error_summary": error_summary,
        })

    async def campfire_start(self, reason: str, agenda: Optional[str] = None):
        """
        Emit campfire start - ALL agents gather.

        From FullProposal.md section 6.3:
        - ALL agents pathfind to campfire zone
        - Fire animation intensifies
        """
        await self.emit(EventType.CAMPFIRE_START, {
            "reason": reason,
            "agenda": agenda,
        })

    async def campfire_message(self, agent_id: str, message: str, message_type: str = "opinion"):
        """Emit campfire message - agent speaks at campfire"""
        await self.emit(EventType.CAMPFIRE_MESSAGE, {
            "agent_id": agent_id,
            "message": message,
            "message_type": message_type,
        })

    async def campfire_decision(self, decision: str, next_action: str, assigned_to: Optional[str] = None):
        """Emit campfire decision - consensus reached"""
        await self.emit(EventType.CAMPFIRE_DECISION, {
            "decision": decision,
            "next_action": next_action,
            "assigned_to": assigned_to,
        })

    async def campfire_end(self, outcome: str):
        """Emit campfire end - party disperses"""
        await self.emit(EventType.CAMPFIRE_END, {
            "outcome": outcome,
        })

    async def budget_update(self, spent: float, limit: float):
        """
        Emit budget update.

        From FullProposal.md section 6.3:
        - If >75%, dim torches in world
        """
        percentage = (spent / limit) * 100 if limit > 0 else 0
        await self.emit(EventType.BUDGET_UPDATE, {
            "spent": spent,
            "limit": limit,
            "percentage": percentage,
        })

    async def token_update(self, used: int, limit: int):
        """Emit token update"""
        percentage = (used / limit) * 100 if limit > 0 else 0
        await self.emit(EventType.TOKEN_UPDATE, {
            "used": used,
            "limit": limit,
            "percentage": percentage,
        })

    async def progress_update(self, percentage: float, completed_tasks: int, total_tasks: int):
        """Emit progress update"""
        await self.emit(EventType.PROGRESS_UPDATE, {
            "percentage": percentage,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
        })

    async def confidence_update(self, score: float, delta: float, reason: str):
        """
        Emit confidence update - shifts world palette.

        From FullProposal.md section 3.3 & 6.3:
        - Smoothly transition world palette
        - >= 0.8: Bright palette, sunny
        - 0.5-0.8: Normal palette, overcast
        - 0.3-0.5: Muted palette, fog
        - < 0.3: Dark palette, rain/storm
        """
        self.confidence_score = max(0.0, min(1.0, score))
        await self.emit(EventType.CONFIDENCE_UPDATE, {
            "score": self.confidence_score,
            "delta": delta,
            "reason": reason,
        })

    async def ambient_trigger(self, agent_id: str, context: str, mood: str):
        """
        Trigger ambient dialogue generation.

        The dialogue engine will receive this and generate an appropriate line.
        """
        await self.emit(EventType.AMBIENT_TRIGGER, {
            "agent_id": agent_id,
            "context": context,
            "mood": mood,
        })

    async def zone_transition(self, agent_id: str, from_zone: str, to_zone: str):
        """Agent moving between zones"""
        await self.emit(EventType.ZONE_TRANSITION, {
            "agent_id": agent_id,
            "from_zone": from_zone,
            "to_zone": to_zone,
        })

    async def dialogue(self, agent_id: str, text: str, dialogue_type: str = "ambient"):
        """
        Agent speaks.

        Args:
            agent_id: Agent speaking
            text: What they say
            dialogue_type: "ambient", "functional", "contextual"
        """
        await self.emit(EventType.DIALOGUE, {
            "agent_id": agent_id,
            "text": text,
            "dialogue_type": dialogue_type,
        })

    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history"""
        return [event.to_dict() for event in self._event_history[-limit:]]

    def clear_event_history(self):
        """Clear event history"""
        self._event_history.clear()


# Global emitter instance (singleton pattern)
_global_emitter: Optional[WorldEventEmitter] = None


def get_world_emitter() -> WorldEventEmitter:
    """Get or create global world event emitter"""
    global _global_emitter
    if _global_emitter is None:
        _global_emitter = WorldEventEmitter()
    return _global_emitter


# Example usage in orchestrator:
"""
from epic.world import get_world_emitter, EventType

# Get emitter instance
emitter = get_world_emitter()

# Quest starts
await emitter.quest_start(
    quest_id="quest_123",
    title="Implement JWT Authentication",
    demon_lord="Shadow Thief JWT",
    budget=10.0,
    token_limit=100000
)

# Phase changes
await emitter.phase_change(
    from_phase="planning",
    to_phase="sprint_1",
    sprint_number=1,
    sprint_name="Protect the Royal Seal"
)

# Agent becomes active
await emitter.agent_active(
    agent_id="rogue",
    action="Implementing token generation",
    target_file="src/auth/jwt.rs"
)

# Agent produces output
await emitter.agent_output(
    agent_id="rogue",
    summary="Token generation implemented",
    output_type="result"
)

# Campfire gathering
await emitter.campfire_start(
    reason="Sprint review",
    agenda="Discuss progress and next steps"
)

await emitter.campfire_message(
    agent_id="planner",
    message="We've completed 3 out of 5 planned tasks"
)

await emitter.campfire_decision(
    decision="Continue with current approach",
    next_action="Implement token validation",
    assigned_to="rogue"
)

await emitter.campfire_end(outcome="Consensus reached, moving forward")

# Confidence changes (affects world visuals)
await emitter.confidence_update(
    score=0.75,
    delta=-0.05,
    reason="test failures detected"
)

# Ambient dialogue trigger
await emitter.ambient_trigger(
    agent_id="rogue",
    context="waiting for tests to complete",
    mood="focused"
)
"""
