"""
Ambient Dialogue Engine

Generates contextual, in-character dialogue for agents using LLMs.
Based on FullProposal.md section 7: Ambient Dialogue Engine

Pattern: Technical events → Fantasy narrative
Example: "Tests failing" → Tank says "These weapons aren't holding up. To the forge!"
"""
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
import time
import random


class DialogueTrigger(Enum):
    """When dialogue should be generated (FullProposal section 7.1)"""

    # Event-driven (always fire)
    PHASE_CHANGE = "phase_change"
    CAMPFIRE_START = "campfire_start"
    QUEST_COMPLETE = "quest_complete"
    AGENT_ERROR = "agent_error"

    # Probabilistic (fire randomly)
    AGENT_IDLE = "agent_idle"  # 30% chance
    IDLE_TICK_60S = "idle_tick_60s"  # 20% chance after 60s idle
    SPRINT_MIDPOINT = "sprint_midpoint"  # 40% chance

    # Contextual (the "blacksmith" pattern)
    TESTS_FAIL = "tests_fail"
    DEPENDENCY_NEEDED = "dependency_needed"
    ARCHITECTURE_REVIEW = "architecture_review"
    BUDGET_WARNING = "budget_warning"
    REPEATED_FAILURE = "repeated_failure"


class DialogueType(Enum):
    """Type of dialogue"""
    FUNCTIONAL = "functional"  # Actual agent output summary
    AMBIENT = "ambient"  # Idle flavor text
    CONTEXTUAL = "contextual"  # Event-driven narrative
    VICTORY = "victory"  # Quest success
    FRUSTRATED = "frustrated"  # Errors/problems


@dataclass
class DialoguePrompt:
    """Template for generating dialogue"""
    agent_id: str
    personality: str  # Agent's personality traits
    speech_pattern: str  # How they talk
    current_location: str  # Zone name
    quest_title: str
    current_phase: str
    agent_current_task: Optional[str]
    confidence_level: str  # "high", "normal", "low", "critical"
    triggering_event: str  # What caused this dialogue
    dialogue_type: DialogueType

    def build_prompt(self) -> str:
        """Build the LLM prompt for dialogue generation"""
        return f"""You are {self.agent_id.title()}, a {self.personality} in an adventuring party.

Your personality: {self.personality}
Your speech style: {self.speech_pattern}

Context:
- Current location: {self.current_location}
- Quest: {self.quest_title} (Phase: {self.current_phase})
- Your current task: {self.agent_current_task or "resting"}
- Party mood: {self.confidence_level}
- Recent event: {self.triggering_event}

Generate ONE ambient line (under 12 words) that:
- Stays in character
- References the current situation naturally
- {self._get_type_specific_instruction()}
- Just the line. No quotes. No attribution.
"""

    def _get_type_specific_instruction(self) -> str:
        """Get instruction based on dialogue type"""
        if self.dialogue_type == DialogueType.CONTEXTUAL:
            return "Hints at the technical event using fantasy metaphor"
        elif self.dialogue_type == DialogueType.AMBIENT:
            return "Is casual flavor dialogue—hobbies, memories, observations"
        elif self.dialogue_type == DialogueType.FRUSTRATED:
            return "Expresses concern without breaking character"
        elif self.dialogue_type == DialogueType.VICTORY:
            return "Celebrates the victory in character"
        else:
            return "Reflects your current state"


class DialogueEngine:
    """
    Generates contextual ambient dialogue for agents.

    Uses cheap LLM (Gemini Flash) for ~$0.0001 per line.
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Optional LLM client (Gemini Flash recommended)
        """
        self.llm_client = llm_client
        self.cooldowns: Dict[str, float] = {}  # agent_id → last_dialogue_time
        self.min_cooldown = 30  # seconds between dialogue for same agent

        # Load personality data (from personalities/*.md files)
        self.agent_personalities = self._load_personalities()

        # Contextual dialogue templates
        self.contextual_templates = self._build_contextual_templates()

    def _load_personalities(self) -> Dict[str, Dict[str, str]]:
        """
        Load agent personalities from personalities/*.md files.

        In production, parse the markdown files.
        For now, hardcoded summaries.
        """
        return {
            "planner": {
                "personality": "cautious, thorough, detail-oriented scout",
                "speech_pattern": "measured sentences, references paths and maps"
            },
            "mage": {
                "personality": "thoughtful, principled, long-term thinker",
                "speech_pattern": "speaks in patterns and principles"
            },
            "rogue": {
                "personality": "bold, pragmatic, action-oriented",
                "speech_pattern": "short, combat metaphors, confident"
            },
            "tank": {
                "personality": "rigorous, uncompromising, protective",
                "speech_pattern": "direct, quality-focused, defensive metaphors"
            },
            "support": {
                "personality": "helpful, organized, encyclopedic",
                "speech_pattern": "references archives and memory"
            },
            "healer": {
                "personality": "reflective, learning-focused chronicler",
                "speech_pattern": "thoughtful, references lessons and wisdom"
            }
        }

    def _build_contextual_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Build contextual dialogue templates.

        The "blacksmith" pattern from FullProposal section 7.2.
        Maps technical events → fantasy narrative.
        """
        return {
            "tests_fail": {
                "tank": "These weapons aren't holding up. We should visit the forge.",
                "rogue": "Something's off. I can feel it.",
                "planner": "We need to regroup. Back to the campfire.",
            },
            "dependency_needed": {
                "support": "I think the merchant at the bazaar has what we need.",
                "planner": "We're missing supplies. Let's visit the market.",
            },
            "architecture_review": {
                "mage": "Something doesn't feel right. Let me consult the archives.",
                "tank": "I don't trust this structure. Mage should review it.",
            },
            "sprint_complete": {
                "rogue": "Another one down. Who's buying ale?",
                "healer": "Let me record our progress before we celebrate.",
                "planner": "Good work. Let's regroup at the campfire.",
            },
            "budget_warning": {
                "support": "Our supplies are running low...",
                "planner": "We need to be more careful with resources.",
            },
            "high_confidence": {
                "mage": "The patterns are aligning. This will work.",
                "tank": "All checks passing. We're in good shape.",
            },
            "low_confidence": {
                "mage": "I sense a disturbance in the architecture.",
                "planner": "Maybe we should visit the forge to regroup.",
            },
            "repeated_failure": {
                "rogue": "We keep hitting the same trap. There's something we're missing.",
                "tank": "I agree. The problem is upstream.",
                "planner": "Let's gather at the campfire. We need a new approach.",
            }
        }

    def should_trigger(self, agent_id: str, trigger: DialogueTrigger) -> bool:
        """
        Check if dialogue should be generated.

        Applies cooldowns and probabilities from FullProposal section 7.1.
        """
        # Check cooldown
        if agent_id in self.cooldowns:
            time_since_last = time.time() - self.cooldowns[agent_id]
            if time_since_last < self.min_cooldown:
                return False

        # Check probability
        probabilities = {
            DialogueTrigger.AGENT_IDLE: 0.3,
            DialogueTrigger.IDLE_TICK_60S: 0.2,
            DialogueTrigger.SPRINT_MIDPOINT: 0.4,
        }

        if trigger in probabilities:
            return random.random() < probabilities[trigger]

        # Event-driven triggers always fire
        return True

    def generate_dialogue(
        self,
        agent_id: str,
        trigger: DialogueTrigger,
        context: Dict[str, any],
    ) -> Optional[str]:
        """
        Generate dialogue for an agent.

        Args:
            agent_id: Agent speaking
            trigger: What triggered this dialogue
            context: Current quest context

        Returns:
            Generated dialogue line, or None if shouldn't trigger
        """
        # Check if should trigger
        if not self.should_trigger(agent_id, trigger):
            return None

        # Get contextual template if available
        event_key = trigger.value
        if event_key in self.contextual_templates:
            templates = self.contextual_templates[event_key]
            if agent_id in templates:
                # Use pre-written contextual line
                line = templates[agent_id]
                self.cooldowns[agent_id] = time.time()
                return line

        # Generate with LLM if available
        if self.llm_client:
            line = self._generate_with_llm(agent_id, trigger, context)
            if line:
                self.cooldowns[agent_id] = time.time()
                return line

        # Fallback: generic line
        fallback_lines = self._get_fallback_lines(agent_id)
        if fallback_lines:
            line = random.choice(fallback_lines)
            self.cooldowns[agent_id] = time.time()
            return line

        return None

    def _generate_with_llm(
        self,
        agent_id: str,
        trigger: DialogueTrigger,
        context: Dict[str, any]
    ) -> Optional[str]:
        """
        Generate dialogue using LLM (Gemini Flash).

        Cost: ~$0.0001 per call
        """
        if not self.llm_client:
            return None

        # Get agent personality
        personality_data = self.agent_personalities.get(agent_id, {})

        # Determine dialogue type
        dialogue_type = self._determine_dialogue_type(trigger)

        # Build prompt
        prompt_data = DialoguePrompt(
            agent_id=agent_id,
            personality=personality_data.get("personality", "experienced adventurer"),
            speech_pattern=personality_data.get("speech_pattern", "speaks clearly"),
            current_location=context.get("zone", "unknown"),
            quest_title=context.get("quest_title", "current quest"),
            current_phase=context.get("phase", "working"),
            agent_current_task=context.get("task", None),
            confidence_level=context.get("confidence_level", "normal"),
            triggering_event=context.get("event_description", trigger.value),
            dialogue_type=dialogue_type,
        )

        prompt = prompt_data.build_prompt()

        try:
            # Call LLM (implementation depends on client)
            # response = self.llm_client.generate(prompt, max_tokens=50)
            # return response.strip()

            # Placeholder for now
            return None
        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return None

    def _determine_dialogue_type(self, trigger: DialogueTrigger) -> DialogueType:
        """Determine dialogue type from trigger"""
        if trigger == DialogueTrigger.QUEST_COMPLETE:
            return DialogueType.VICTORY
        elif trigger in [DialogueTrigger.AGENT_ERROR, DialogueTrigger.TESTS_FAIL]:
            return DialogueType.FRUSTRATED
        elif trigger in [DialogueTrigger.PHASE_CHANGE, DialogueTrigger.TESTS_FAIL]:
            return DialogueType.CONTEXTUAL
        else:
            return DialogueType.AMBIENT

    def _get_fallback_lines(self, agent_id: str) -> List[str]:
        """Get fallback lines when LLM unavailable"""
        fallbacks = {
            "planner": [
                "Let me check the map...",
                "I see a pattern here.",
                "We should consider our options carefully.",
            ],
            "mage": [
                "The architecture reveals itself.",
                "There's wisdom in patience.",
                "I've seen this pattern before.",
            ],
            "rogue": [
                "Give me five minutes.",
                "I work better in the shadows.",
                "Target acquired.",
            ],
            "tank": [
                "These defenses need checking.",
                "Quality over speed.",
                "I'll verify this thoroughly.",
            ],
            "support": [
                "I found something in the archives.",
                "Let me consult my notes.",
                "I remember a similar case.",
            ],
            "healer": [
                "We should document this.",
                "What can we learn from this?",
                "Let me record our progress.",
            ]
        }
        return fallbacks.get(agent_id, [])

    def get_contextual_dialogue(
        self,
        event_type: str,
        agent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get pre-written contextual dialogue for an event.

        This is the "blacksmith pattern" - technical events → fantasy narrative.

        Args:
            event_type: The technical event (e.g., "tests_fail")
            agent_id: Specific agent, or None for any available

        Returns:
            Dialogue line, or None
        """
        if event_type not in self.contextual_templates:
            return None

        templates = self.contextual_templates[event_type]

        if agent_id and agent_id in templates:
            return templates[agent_id]

        # Return any agent's line for this event
        if templates:
            return random.choice(list(templates.values()))

        return None


# Example usage:
"""
from epic.world import DialogueEngine, DialogueTrigger

dialogue_engine = DialogueEngine()

# When tests fail
line = dialogue_engine.generate_dialogue(
    agent_id="tank",
    trigger=DialogueTrigger.TESTS_FAIL,
    context={
        "zone": "arena",
        "quest_title": "Implement JWT Auth",
        "phase": "testing",
        "confidence_level": "low",
        "event_description": "3 tests failing in auth module"
    }
)
# Returns: "These weapons aren't holding up. We should visit the forge."

# When agent is idle
line = dialogue_engine.generate_dialogue(
    agent_id="mage",
    trigger=DialogueTrigger.AGENT_IDLE,
    context={
        "zone": "tavern",
        "quest_title": "Implement JWT Auth",
        "phase": "idle",
        "task": None
    }
)
# Returns: "There's wisdom in patience." (or LLM-generated line if client available)

# Get contextual line directly
line = dialogue_engine.get_contextual_dialogue("tests_fail", "rogue")
# Returns: "Something's off. I can feel it."
"""
