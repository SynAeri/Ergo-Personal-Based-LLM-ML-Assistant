"""
Persistent Identity System

Inspired by Desplega Agent Swarm's evolving identity architecture.
Each agent has identity files that evolve over time as they learn from quests.

Architecture:
- SOUL.md: Immutable core personality (never changes)
- IDENTITY.md: Learned patterns and preferences (evolves)
- TOOLS.md: Available skills and their usage patterns
- memories/: Vector store of searchable experiences
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class IdentityUpdate:
    """A learning that updates the agent's identity"""
    quest_id: str
    learning: str
    category: str  # "pattern", "preference", "skill", "relationship"
    timestamp: str
    confidence: float  # How confident are we in this learning?


class PersistentIdentity:
    """
    Evolving identity system for an agent.

    Each agent has:
    - Soul (immutable): Core personality from personalities/*.md
    - Identity (evolving): Learned patterns, preferences, expertise
    - Tools: Skill catalog with usage stats
    - Memories: Vector store of past experiences (TODO: implement with embeddings)
    """

    def __init__(self, agent_id: str, base_dir: Path):
        """
        Args:
            agent_id: Agent identifier (e.g., "rogue")
            base_dir: Base directory for identity files (e.g., Project_Epic/identities/)
        """
        self.agent_id = agent_id
        self.base_dir = Path(base_dir)
        self.agent_dir = self.base_dir / agent_id

        # File paths
        self.soul_file = self.agent_dir / "SOUL.md"
        self.identity_file = self.agent_dir / "IDENTITY.md"
        self.tools_file = self.agent_dir / "TOOLS.md"
        self.learnings_file = self.agent_dir / "learnings.json"

        # Ensure directory exists
        self.agent_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize
        self.soul = self._load_soul()
        self.identity = self._load_identity()
        self.tools = self._load_tools()
        self.learnings: List[IdentityUpdate] = self._load_learnings()

    def _load_soul(self) -> str:
        """
        Load immutable soul from personalities/ dir.

        The soul is the base personality file that never changes.
        This is our source of truth for who the agent is at core.
        """
        # Load from personalities directory
        personality_file = self.base_dir.parent / "personalities" / f"{self.agent_id}.md"
        if personality_file.exists():
            return personality_file.read_text()

        # If not found, create minimal soul
        return f"""# {self.agent_id.title()} - Base Personality

This agent's core personality. Define their role, goal, and backstory.
"""

    def _load_identity(self) -> str:
        """
        Load evolving identity file.

        If doesn't exist, create from template.
        """
        if not self.identity_file.exists():
            self._create_initial_identity()

        return self.identity_file.read_text()

    def _create_initial_identity(self):
        """Create initial identity file"""
        template = f"""# {self.agent_id.title()} - Evolving Identity

*Last updated: Never*
*Quests completed: 0*

---

## Learned Patterns

_This section evolves as the agent completes quests._

No patterns learned yet.

---

## Preferences

_How this agent prefers to work._

No preferences learned yet.

---

## Expertise Areas

_Domains where this agent has demonstrated skill._

No expertise areas identified yet.

---

## Relationships

_How this agent works with other party members._

No relationship patterns learned yet.

---

## Notable Achievements

_Memorable moments from past quests._

No achievements yet.

---

*This identity file evolves automatically as the agent learns from experience.*
"""
        self.identity_file.write_text(template)

    def _load_tools(self) -> Dict[str, Any]:
        """Load tools catalog"""
        if not self.tools_file.exists():
            return {}

        # Parse markdown tools file (simplified)
        return {}

    def _load_learnings(self) -> List[IdentityUpdate]:
        """Load accumulated learnings"""
        if not self.learnings_file.exists():
            return []

        with open(self.learnings_file) as f:
            data = json.load(f)
            return [
                IdentityUpdate(
                    quest_id=item["quest_id"],
                    learning=item["learning"],
                    category=item["category"],
                    timestamp=item["timestamp"],
                    confidence=item["confidence"],
                )
                for item in data
            ]

    def add_learning(self, update: IdentityUpdate):
        """
        Add a new learning to the agent's identity.

        This would eventually:
        1. Add to learnings list
        2. Update IDENTITY.md with the learning
        3. If confidence > threshold, embed into soul prompt
        """
        self.learnings.append(update)
        self._save_learnings()

        # Update IDENTITY.md
        self._update_identity_file(update)

    def _save_learnings(self):
        """Save learnings to JSON"""
        data = [
            {
                "quest_id": l.quest_id,
                "learning": l.learning,
                "category": l.category,
                "timestamp": l.timestamp,
                "confidence": l.confidence,
            }
            for l in self.learnings
        ]
        with open(self.learnings_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _update_identity_file(self, update: IdentityUpdate):
        """
        Update IDENTITY.md with new learning.

        This is simplified—in production, use proper markdown parsing.
        """
        current = self.identity

        # Map category to section
        section_map = {
            "pattern": "## Learned Patterns",
            "preference": "## Preferences",
            "skill": "## Expertise Areas",
            "relationship": "## Relationships",
        }

        section = section_map.get(update.category, "## Learned Patterns")

        # Find section and append (simplified)
        if section in current:
            # TODO: Proper markdown manipulation
            # For now, just append to file
            with open(self.identity_file, 'a') as f:
                f.write(f"\n### From Quest {update.quest_id}\n")
                f.write(f"{update.learning}\n")

    def get_identity_context(self) -> str:
        """
        Get identity context to include in agent prompt.

        Combines soul + learned identity for full context.
        """
        context = f"""# Agent Identity: {self.agent_id.title()}

## Core Personality (Soul)
{self.soul[:1000]}  # Truncate if too long

## Learned Identity
{self.identity[:500]}  # Recent learnings

## Total Quests Completed: {len(set(l.quest_id for l in self.learnings))}
"""
        return context

    def search_experiences(self, query: str, k: int = 5) -> List[str]:
        """
        Search past experiences using semantic search.

        TODO: Implement with embeddings and vector DB.
        For now, returns empty list.
        """
        # In production:
        # 1. Embed query
        # 2. Search vector store of memories
        # 3. Return top k relevant experiences
        return []

    def record_quest_completion(self, quest_id: str, learnings: List[str]):
        """
        Record learnings from a completed quest.

        Args:
            quest_id: The quest that was completed
            learnings: List of insights extracted
        """
        from datetime import datetime

        for learning in learnings:
            update = IdentityUpdate(
                quest_id=quest_id,
                learning=learning,
                category="pattern",  # Could be auto-classified
                timestamp=datetime.now().isoformat(),
                confidence=0.8,  # Could be computed
            )
            self.add_learning(update)

        print(f"✓ Recorded {len(learnings)} learnings for {self.agent_id} from quest {quest_id}")


# Example usage:
"""
# Initialize identity system for an agent
identity = PersistentIdentity(
    agent_id="rogue",
    base_dir=Path("Project_Epic/identities")
)

# During quest execution, record experiences as memories (via AgentMemory class)
# ...

# At quest completion, extract and record learnings
identity.record_quest_completion(
    quest_id="quest_123",
    learnings=[
        "Learned: JWT token generation requires jsonwebtoken crate version 8.3+",
        "Learned: CORS middleware must be configured before auth middleware",
        "Preference: Prefer match expressions over if-let for Result handling",
    ]
)

# When building agent prompt, include evolved identity
context = identity.get_identity_context()
# Pass this context to agent's system prompt

# Identity file now contains:
# - Core soul (unchanged)
# - Learned patterns from quest
# - Accumulated wisdom from all quests
"""
