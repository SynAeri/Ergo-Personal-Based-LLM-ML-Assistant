"""
Quest - Main goal representation with progressive difficulty sprints
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from ..coordination.sprint_difficulty import Sprint, SprintGenerator, DifficultyRank


class QuestStatus(Enum):
    """Current status of the quest"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Quest:
    """
    A quest represents the main goal with 6 difficulty-scaled sprints

    Example:
        Main Goal: "Build a banking app"
        Demon King: "VOID LORD OF FINANCES"
        Sprints:
            1. D-RANK: "Stave Away the Crocodiles" (setup)
            2. C-RANK: "Clear the Goblin Den" (basic features)
            3. B-RANK: "Slay the Dragon Fafnir" (core features)
            4. A-RANK: "Defeat the Elder Vampire" (security)
            5. S-RANK: "Conquer the Ancient Fortress" (testing)
            6. SSS-RANK: "SLAY THE DEMON KING" (deployment)
    """

    def __init__(
        self,
        goal: str,
        quest_type: Optional[str] = None,
        budget: float = 10.0,
        max_tokens: int = 100_000,
        party_size: int = 6
    ):
        self.id = str(uuid.uuid4())
        self.goal = goal
        self.quest_type = quest_type or self._detect_quest_type(goal)
        self.budget = budget
        self.max_tokens = max_tokens
        self.party_size = party_size

        # Generate 6 progressive difficulty sprints
        self.sprints: List[Sprint] = SprintGenerator.generate_sprints(
            quest_goal=goal,
            quest_type=self.quest_type,
            total_budget=budget
        )

        # The final boss (SSS-RANK enemy)
        self.demon_king = self.sprints[-1].enemy_type

        # Quest state
        self.status = QuestStatus.CREATED
        self.current_sprint_index = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Tracking
        self.budget_used = 0.0
        self.tokens_used = 0
        self.sprints_completed = 0
        self.campfires_held = 0

        # Results
        self.lessons_learned: List[str] = []
        self.party_members: List[str] = []

    def _detect_quest_type(self, goal: str) -> str:
        """Auto-detect quest type from goal description"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["auth", "jwt", "login", "security"]):
            return "authentication"
        elif any(word in goal_lower for word in ["database", "schema", "sql"]):
            return "database"
        elif any(word in goal_lower for word in ["api", "endpoint", "rest", "graphql"]):
            return "api_service"
        elif any(word in goal_lower for word in ["app", "ui", "frontend", "web"]):
            return "web_app"
        else:
            return "web_app"  # Default

    def start(self):
        """Start the quest"""
        self.status = QuestStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def get_current_sprint(self) -> Optional[Sprint]:
        """Get the currently active sprint"""
        if self.current_sprint_index >= len(self.sprints):
            return None
        return self.sprints[self.current_sprint_index]

    def complete_sprint(self, success: bool, cost: float, tokens: int):
        """Mark current sprint as complete and move to next"""
        if success:
            self.sprints_completed += 1

        self.budget_used += cost
        self.tokens_used += tokens
        self.current_sprint_index += 1

    def is_complete(self) -> bool:
        """Check if all sprints are done"""
        return self.current_sprint_index >= len(self.sprints)

    def complete(self):
        """Mark quest as complete"""
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.now()

    def fail(self, reason: str):
        """Mark quest as failed"""
        self.status = QuestStatus.FAILED
        self.completed_at = datetime.now()
        self.lessons_learned.append(f"Quest failed: {reason}")

    def get_progress_percentage(self) -> float:
        """Get quest completion percentage"""
        return (self.sprints_completed / len(self.sprints)) * 100

    def get_budget_percentage(self) -> float:
        """Get budget usage percentage"""
        return (self.budget_used / self.budget) * 100

    def get_token_percentage(self) -> float:
        """Get token usage percentage"""
        return (self.tokens_used / self.max_tokens) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary"""
        return {
            "id": self.id,
            "goal": self.goal,
            "quest_type": self.quest_type,
            "demon_king": self.demon_king,
            "status": self.status.value,
            "current_sprint": self.current_sprint_index + 1,
            "total_sprints": len(self.sprints),
            "sprints_completed": self.sprints_completed,
            "progress_percentage": round(self.get_progress_percentage(), 1),
            "budget": {
                "total": self.budget,
                "used": round(self.budget_used, 2),
                "remaining": round(self.budget - self.budget_used, 2),
                "percentage": round(self.get_budget_percentage(), 1)
            },
            "tokens": {
                "total": self.max_tokens,
                "used": self.tokens_used,
                "remaining": self.max_tokens - self.tokens_used,
                "percentage": round(self.get_token_percentage(), 1)
            },
            "sprints": [
                {
                    "number": i + 1,
                    "rank": sprint.rank.value,
                    "name": sprint.name,
                    "enemy": sprint.enemy_type,
                    "description": sprint.description,
                    "aesthetic": sprint.aesthetic,
                    "estimated_cost": sprint.estimated_cost,
                    "completed": i < self.current_sprint_index
                }
                for i, sprint in enumerate(self.sprints)
            ],
            "party_members": self.party_members,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def get_ascii_quest_board(self) -> str:
        """Generate ASCII art quest board"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append("║                     📜 QUEST BOARD 📜                        ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  Goal: {self.goal:<50} ║")
        lines.append(f"║  Demon King: {self.demon_king:<44} ║")
        lines.append(f"║  Status: {self.status.value.upper():<48} ║")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append("║  SPRINTS:                                                    ║")
        lines.append("╟──────────────────────────────────────────────────────────────╢")

        for i, sprint in enumerate(self.sprints):
            completed = i < self.current_sprint_index
            current = i == self.current_sprint_index
            status_icon = "✓" if completed else ("→" if current else "○")
            rank_badge = f"[{sprint.rank.value:^4}]"

            lines.append(f"║  {status_icon} {rank_badge} {sprint.name:<45} ║")

        lines.append("╟──────────────────────────────────────────────────────────────╢")
        lines.append(f"║  Budget: ${self.budget_used:.2f} / ${self.budget:.2f} ({self.get_budget_percentage():.0f}%){'':>20} ║")
        lines.append(f"║  Progress: {self.sprints_completed}/{len(self.sprints)} sprints ({self.get_progress_percentage():.0f}%){'':>25} ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Create a quest
    quest = Quest(
        goal="Build a banking app",
        budget=10.0,
        max_tokens=100_000
    )

    print(quest.get_ascii_quest_board())
    print()
    print("DEMON KING:", quest.demon_king)
    print()
    print("Sprint Details:")
    for i, sprint in enumerate(quest.sprints, 1):
        print(f"\n{i}. {sprint.rank.value}-RANK: {sprint.name}")
        print(f"   Enemy: {sprint.enemy_type}")
        print(f"   {sprint.aesthetic}")
        print(f"   Estimated Cost: ${sprint.estimated_cost:.2f}")

    # Simulate quest progress
    print("\n" + "=" * 60)
    print("Simulating Quest Progress...")
    print("=" * 60)

    quest.start()

    # Complete first 2 sprints
    quest.complete_sprint(success=True, cost=1.0, tokens=10000)
    quest.complete_sprint(success=True, cost=1.5, tokens=15000)

    print("\nAfter 2 sprints:")
    print(quest.get_ascii_quest_board())

    print("\nQuest Data:")
    import json
    print(json.dumps(quest.to_dict(), indent=2))
