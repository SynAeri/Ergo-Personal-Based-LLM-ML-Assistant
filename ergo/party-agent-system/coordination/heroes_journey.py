"""
Heroes Journey - Quest phase management with thematic sprint naming
Each quest type has unique aesthetic for sprints
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio


class QuestType(Enum):
    """Different types of quests with unique aesthetics"""
    WEB_APP = "web_app"           # "Save the Holy City"
    API_SERVICE = "api_service"   # "Forge the Sacred Weapon"
    DATABASE = "database"         # "Delve into the Ancient Catacombs"
    AUTHENTICATION = "auth"       # "Protect the Royal Seal"
    REFACTOR = "refactor"         # "Purify the Corrupted Temple"
    BUG_FIX = "bug_fix"          # "Slay the Shadow Beast"
    FEATURE = "feature"           # "Claim the Lost Artifact"
    TESTING = "testing"           # "Fortify the Castle Walls"


@dataclass
class QuestPhase:
    """A single phase in the hero's journey"""
    phase_name: str
    phase_type: str  # "campfire" or "sprint"
    theme: str       # Thematic description
    objective: str   # What needs to be accomplished
    success_criteria: List[str]
    max_duration_minutes: Optional[int] = None


class HeroesJourney:
    """
    Manages the hero's journey through a quest

    Each quest type has thematically appropriate sprint names:
    - Web App: "Save the Holy City from an Elder Vampire"
    - API: "Forge the Sacred Weapon in Dragon Fire"
    - Database: "Delve into the Ancient Catacombs"
    """

    # Thematic sprint templates per quest type
    QUEST_THEMES = {
        QuestType.WEB_APP: {
            "demon_lord": "Elder Vampire Lord {feature_name}",
            "sprints": [
                {
                    "name": "🏰 Save the Holy City",
                    "description": "Establish the foundation - routing, components, state",
                    "aesthetic": "The city walls must be rebuilt before the vampire arrives"
                },
                {
                    "name": "⚔️ Vanquish the Vampire Horde",
                    "description": "Implement core functionality and business logic",
                    "aesthetic": "The vampire's minions swarm the streets"
                },
                {
                    "name": "🌅 Restore the Light",
                    "description": "Polish, styling, and final touches",
                    "aesthetic": "Dawn breaks over the liberated city"
                }
            ]
        },
        QuestType.API_SERVICE: {
            "demon_lord": "Chaos Dragon {feature_name}",
            "sprints": [
                {
                    "name": "⚒️ Forge the Sacred Weapon",
                    "description": "Create API structure, endpoints, and schemas",
                    "aesthetic": "The legendary smith fires up the forge"
                },
                {
                    "name": "🔥 Temper in Dragon Fire",
                    "description": "Implement business logic and validation",
                    "aesthetic": "The blade must be tested in the flames"
                },
                {
                    "name": "✨ Imbue with Ancient Magic",
                    "description": "Add middleware, auth, error handling",
                    "aesthetic": "The mage enchants the weapon with protective runes"
                }
            ]
        },
        QuestType.DATABASE: {
            "demon_lord": "Lich King {feature_name}",
            "sprints": [
                {
                    "name": "🕯️ Delve into the Catacombs",
                    "description": "Design schema, migrations, and models",
                    "aesthetic": "The party descends into ancient depths"
                },
                {
                    "name": "💀 Face the Undead Guardians",
                    "description": "Implement queries, transactions, and indexing",
                    "aesthetic": "Skeletal warriors rise to defend the crypt"
                },
                {
                    "name": "📜 Claim the Forbidden Knowledge",
                    "description": "Optimize queries, add caching, finalize",
                    "aesthetic": "The ancient grimoire's secrets are revealed"
                }
            ]
        },
        QuestType.AUTHENTICATION: {
            "demon_lord": "Shadow Thief {feature_name}",
            "sprints": [
                {
                    "name": "🔐 Protect the Royal Seal",
                    "description": "Implement authentication flow and token generation",
                    "aesthetic": "The royal seal must not fall into enemy hands"
                },
                {
                    "name": "🛡️ Fortify the Gate",
                    "description": "Add authorization, permissions, and middleware",
                    "aesthetic": "Every entrance must be guarded"
                },
                {
                    "name": "👁️ Set the Watchers",
                    "description": "Logging, monitoring, and security audits",
                    "aesthetic": "The night watch begins their eternal vigil"
                }
            ]
        },
        QuestType.REFACTOR: {
            "demon_lord": "Corruption Demon {feature_name}",
            "sprints": [
                {
                    "name": "🧹 Purify the Corrupted Temple",
                    "description": "Clean up code structure and remove duplication",
                    "aesthetic": "The temple has been defiled by dark magic"
                },
                {
                    "name": "⚡ Exorcise the Evil Spirits",
                    "description": "Refactor complex logic and improve patterns",
                    "aesthetic": "Banish the demons that haunt this place"
                },
                {
                    "name": "🕊️ Consecrate the Sacred Ground",
                    "description": "Add tests, documentation, and final polish",
                    "aesthetic": "The temple stands pure once more"
                }
            ]
        },
        QuestType.BUG_FIX: {
            "demon_lord": "Shadow Beast {bug_name}",
            "sprints": [
                {
                    "name": "🔍 Track the Beast",
                    "description": "Investigate, reproduce, and isolate the bug",
                    "aesthetic": "Follow the tracks through the haunted forest"
                },
                {
                    "name": "⚔️ Slay the Shadow Beast",
                    "description": "Implement the fix and verify",
                    "aesthetic": "Strike true at the heart of darkness"
                },
                {
                    "name": "🔦 Light the Torches",
                    "description": "Add tests to prevent regression",
                    "aesthetic": "Ensure the beast never returns"
                }
            ]
        },
        QuestType.FEATURE: {
            "demon_lord": "Guardian of {feature_name}",
            "sprints": [
                {
                    "name": "🗺️ Chart the Path",
                    "description": "Plan feature structure and architecture",
                    "aesthetic": "The map reveals the artifact's location"
                },
                {
                    "name": "🏔️ Brave the Perilous Journey",
                    "description": "Implement core feature functionality",
                    "aesthetic": "Through mountain and storm, the party advances"
                },
                {
                    "name": "💎 Claim the Lost Artifact",
                    "description": "Polish, test, and integrate the feature",
                    "aesthetic": "The legendary artifact is finally yours"
                }
            ]
        },
        QuestType.TESTING: {
            "demon_lord": "Siege of {system_name}",
            "sprints": [
                {
                    "name": "🏗️ Fortify the Castle Walls",
                    "description": "Write unit tests for core components",
                    "aesthetic": "Stone by stone, the defenses rise"
                },
                {
                    "name": "🏹 Man the Battlements",
                    "description": "Add integration and end-to-end tests",
                    "aesthetic": "Archers take position, ready for siege"
                },
                {
                    "name": "🎺 Sound the Victory Horn",
                    "description": "Achieve target coverage and confidence",
                    "aesthetic": "The castle stands impregnable"
                }
            ]
        }
    }

    def __init__(self, quest_type: QuestType, quest_goal: str):
        self.quest_type = quest_type
        self.quest_goal = quest_goal
        self.current_phase_index = 0
        self.phases: List[QuestPhase] = []
        self._build_journey()

    def _build_journey(self):
        """Build the complete hero's journey with campfires and sprints"""
        theme = self.QUEST_THEMES[self.quest_type]

        # Starting campfire - Planning
        self.phases.append(QuestPhase(
            phase_name="Gathering at the Tavern",
            phase_type="campfire",
            theme="🍺 The party meets to discuss the quest",
            objective="Understand the quest, form strategy, and prepare",
            success_criteria=[
                "Quest objective is clear",
                "All party members understand their roles",
                "Initial plan is agreed upon"
            ],
            max_duration_minutes=10
        ))

        # Sprints with campfires between
        sprints = theme["sprints"]
        for i, sprint in enumerate(sprints):
            # Sprint phase
            self.phases.append(QuestPhase(
                phase_name=sprint["name"],
                phase_type="sprint",
                theme=sprint["aesthetic"],
                objective=sprint["description"],
                success_criteria=[
                    "All tasks in sprint are completed",
                    "Tests pass",
                    "Budget is within limits"
                ],
                max_duration_minutes=30
            ))

            # Campfire after sprint (except after last sprint)
            if i < len(sprints) - 1:
                self.phases.append(QuestPhase(
                    phase_name="Resting at the Campfire",
                    phase_type="campfire",
                    theme=f"🏕️ The party gathers to review progress",
                    objective="Assess progress, discuss issues, and adjust strategy",
                    success_criteria=[
                        "Progress is reviewed",
                        "Issues are discussed",
                        "Next steps are clear"
                    ],
                    max_duration_minutes=5
                ))

        # Final victory campfire
        self.phases.append(QuestPhase(
            phase_name="Victory Celebration",
            phase_type="campfire",
            theme="🎉 The demon lord is defeated!",
            objective="Celebrate, document learnings, and export knowledge",
            success_criteria=[
                "Quest summary is created",
                "Lessons are documented",
                "Knowledge is exported to Obsidian"
            ],
            max_duration_minutes=5
        ))

    def get_current_phase(self) -> QuestPhase:
        """Get the current phase of the journey"""
        if self.current_phase_index >= len(self.phases):
            return self.phases[-1]  # Return victory phase if complete
        return self.phases[self.current_phase_index]

    def advance_phase(self) -> bool:
        """Move to the next phase. Returns False if journey is complete."""
        self.current_phase_index += 1
        return self.current_phase_index < len(self.phases)

    def is_complete(self) -> bool:
        """Check if the journey is complete"""
        return self.current_phase_index >= len(self.phases) - 1

    def get_progress_percentage(self) -> float:
        """Get journey completion percentage"""
        if not self.phases:
            return 0.0
        return (self.current_phase_index / len(self.phases)) * 100

    def get_journey_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire journey"""
        return {
            "quest_type": self.quest_type.value,
            "quest_goal": self.quest_goal,
            "total_phases": len(self.phases),
            "current_phase": self.current_phase_index,
            "progress_percentage": round(self.get_progress_percentage(), 1),
            "phases": [
                {
                    "name": phase.phase_name,
                    "type": phase.phase_type,
                    "theme": phase.theme,
                    "objective": phase.objective
                }
                for phase in self.phases
            ]
        }

    def get_ascii_journey_map(self) -> str:
        """Generate an ASCII art journey map"""
        lines = []
        lines.append("╔════════════════════════════════════════════════════════╗")
        lines.append("║           🗺️  THE HERO'S JOURNEY                       ║")
        lines.append("╠════════════════════════════════════════════════════════╣")

        for i, phase in enumerate(self.phases):
            marker = "🔥" if phase.phase_type == "campfire" else "⚔️"
            status = "✓" if i < self.current_phase_index else "○"
            current = "→" if i == self.current_phase_index else " "

            if phase.phase_type == "campfire":
                lines.append(f"║ {current} {status} {marker} {phase.phase_name:<45} ║")
            else:
                lines.append(f"║ {current} {status} {marker} {phase.phase_name:<45} ║")

        lines.append("╚════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    @classmethod
    def detect_quest_type(cls, quest_goal: str) -> QuestType:
        """
        Detect quest type from goal description

        Uses keyword matching to determine the most appropriate quest aesthetic
        """
        goal_lower = quest_goal.lower()

        # Authentication/Security
        if any(word in goal_lower for word in ["auth", "jwt", "login", "token", "security", "permission"]):
            return QuestType.AUTHENTICATION

        # Database
        if any(word in goal_lower for word in ["database", "schema", "migration", "sql", "query", "index"]):
            return QuestType.DATABASE

        # API
        if any(word in goal_lower for word in ["api", "endpoint", "rest", "graphql", "route"]):
            return QuestType.API_SERVICE

        # Refactor
        if any(word in goal_lower for word in ["refactor", "cleanup", "improve", "reorganize", "simplify"]):
            return QuestType.REFACTOR

        # Bug fix
        if any(word in goal_lower for word in ["bug", "fix", "error", "issue", "broken", "failing"]):
            return QuestType.BUG_FIX

        # Testing
        if any(word in goal_lower for word in ["test", "coverage", "verify", "validate"]):
            return QuestType.TESTING

        # Web App
        if any(word in goal_lower for word in ["app", "ui", "frontend", "component", "page", "interface"]):
            return QuestType.WEB_APP

        # Default to feature
        return QuestType.FEATURE


# Example usage
if __name__ == "__main__":
    # Example 1: JWT Authentication quest
    print("=" * 60)
    print("Quest 1: Implement JWT Authentication")
    print("=" * 60)

    journey1 = HeroesJourney(
        quest_type=QuestType.AUTHENTICATION,
        quest_goal="Implement JWT-based authentication for the API"
    )

    print(journey1.get_ascii_journey_map())
    print()
    print("Current Phase:", journey1.get_current_phase().phase_name)
    print("Theme:", journey1.get_current_phase().theme)
    print()

    # Example 2: Web app quest
    print("=" * 60)
    print("Quest 2: Build User Dashboard")
    print("=" * 60)

    journey2 = HeroesJourney(
        quest_type=QuestType.WEB_APP,
        quest_goal="Build a user dashboard with real-time updates"
    )

    print(journey2.get_ascii_journey_map())
    print()

    # Example 3: Auto-detect quest type
    print("=" * 60)
    print("Quest 3: Auto-detected quest type")
    print("=" * 60)

    goal = "Fix the memory leak in the caching service"
    detected_type = HeroesJourney.detect_quest_type(goal)
    print(f"Goal: {goal}")
    print(f"Detected Type: {detected_type.value}")

    journey3 = HeroesJourney(detected_type, goal)
    print()
    print(journey3.get_ascii_journey_map())
