"""
Sprint Difficulty System - Progressive challenge scaling
Each quest has 6 sprints that scale in difficulty like an RPG
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random


class DifficultyRank(Enum):
    """RPG-style difficulty rankings"""
    D_RANK = "D"  # Beginner - Setup tasks
    C_RANK = "C"  # Easy - Basic features
    B_RANK = "B"  # Medium - Core functionality
    A_RANK = "A"  # Hard - Complex integrations
    S_RANK = "S"  # Very Hard - Critical systems
    SS_RANK = "SS"  # Expert - Final challenges
    SSS_RANK = "SSS"  # Legendary - The Demon King


@dataclass
class Sprint:
    """A single sprint in the quest"""
    rank: DifficultyRank
    name: str  # "Stave Away the Crocodiles"
    description: str  # What this sprint accomplishes
    aesthetic: str  # Thematic flavor text
    estimated_cost: float  # Expected budget usage
    enemy_type: str  # Type of challenge (e.g., "Minor Beasts", "Dragon", "Demon King")
    success_criteria: List[str]


class SprintGenerator:
    """
    Generates 6 difficulty-scaled sprints for any quest goal

    The sprints follow RPG progression:
    D → C → B → A → S → SSS (Final Boss)
    """

    # Enemy types by difficulty
    ENEMY_TYPES = {
        DifficultyRank.D_RANK: ["Slimes", "Crocodiles", "Wild Boars", "Giant Rats"],
        DifficultyRank.C_RANK: ["Goblins", "Wolves", "Bandits", "Skeleton Warriors"],
        DifficultyRank.B_RANK: ["Dragons", "Wyverns", "Minotaurs", "Golems"],
        DifficultyRank.A_RANK: ["Vampires", "Liches", "Demon Lords", "Ancient Beasts"],
        DifficultyRank.S_RANK: ["Titans", "Elder Dragons", "Archmages", "Fortress Lords"],
        DifficultyRank.SSS_RANK: ["DEMON KING", "GOD OF CHAOS", "VOID LORD", "PRIMORDIAL EVIL"]
    }

    # Cost multipliers by difficulty (relative to total budget)
    COST_MULTIPLIERS = {
        DifficultyRank.D_RANK: 0.10,  # 10% of budget
        DifficultyRank.C_RANK: 0.15,  # 15% of budget
        DifficultyRank.B_RANK: 0.20,  # 20% of budget
        DifficultyRank.A_RANK: 0.20,  # 20% of budget
        DifficultyRank.S_RANK: 0.20,  # 20% of budget
        DifficultyRank.SSS_RANK: 0.15  # 15% of budget (final sprint is optimization)
    }

    @classmethod
    def generate_sprints(
        cls,
        quest_goal: str,
        quest_type: str,
        total_budget: float = 10.0
    ) -> List[Sprint]:
        """
        Generate 6 progressive difficulty sprints for a quest

        Args:
            quest_goal: Main goal (e.g., "Build a banking app")
            quest_type: Type of quest (web_app, api, database, etc.)
            total_budget: Total budget for the quest

        Returns:
            List of 6 sprints, D-rank through SSS-rank
        """
        sprints = []

        # Get quest-specific sprint templates
        templates = cls._get_templates_for_quest_type(quest_type)

        # Generate 6 sprints with increasing difficulty
        ranks = [
            DifficultyRank.D_RANK,
            DifficultyRank.C_RANK,
            DifficultyRank.B_RANK,
            DifficultyRank.A_RANK,
            DifficultyRank.S_RANK,
            DifficultyRank.SSS_RANK
        ]

        for i, rank in enumerate(ranks):
            template = templates[i]
            enemy = random.choice(cls.ENEMY_TYPES[rank])

            sprint = Sprint(
                rank=rank,
                name=template["name"].format(enemy=enemy),
                description=template["description"],
                aesthetic=template["aesthetic"].format(enemy=enemy),
                estimated_cost=total_budget * cls.COST_MULTIPLIERS[rank],
                enemy_type=enemy,
                success_criteria=template["success_criteria"]
            )
            sprints.append(sprint)

        return sprints

    @classmethod
    def _get_templates_for_quest_type(cls, quest_type: str) -> List[Dict]:
        """Get sprint templates based on quest type"""
        templates = {
            "web_app": [
                {  # D-Rank
                    "name": "🦎 Stave Away the {enemy}",
                    "description": "Set up project structure, routing, and basic components",
                    "aesthetic": "Beginner adventurers clear the path. The {enemy} are numerous but weak.",
                    "success_criteria": [
                        "Project scaffolding complete",
                        "Basic routing working",
                        "Component structure established"
                    ]
                },
                {  # C-Rank
                    "name": "⚔️ Clear the {enemy} Den",
                    "description": "Implement core UI components and basic state management",
                    "aesthetic": "The {enemy} nest in the shadows. They fight in packs.",
                    "success_criteria": [
                        "Main components implemented",
                        "State management working",
                        "Basic styling complete"
                    ]
                },
                {  # B-Rank
                    "name": "🐉 Slay the {enemy}",
                    "description": "Integrate APIs, handle complex data flows, advanced features",
                    "aesthetic": "The {enemy} guards the mountain pass. Its scales are like iron.",
                    "success_criteria": [
                        "API integration complete",
                        "Data flows working",
                        "Advanced features implemented"
                    ]
                },
                {  # A-Rank
                    "name": "🧛 Defeat the Elder {enemy}",
                    "description": "Implement authentication, security, and error handling",
                    "aesthetic": "The {enemy} has ruled the capital for centuries. It thirsts for blood.",
                    "success_criteria": [
                        "Authentication implemented",
                        "Security hardened",
                        "Error handling robust"
                    ]
                },
                {  # S-Rank
                    "name": "🏰 Conquer the {enemy} Fortress",
                    "description": "Testing, performance optimization, edge case handling",
                    "aesthetic": "The {enemy} commands legions from its impregnable fortress.",
                    "success_criteria": [
                        "Test coverage >80%",
                        "Performance optimized",
                        "Edge cases handled"
                    ]
                },
                {  # SSS-Rank
                    "name": "👹 SLAY THE {enemy}",
                    "description": "Final polish, deployment, documentation, victory",
                    "aesthetic": "The {enemy} emerges from the void. Reality warps in its presence. THIS IS THE FINAL BATTLE.",
                    "success_criteria": [
                        "Application deployed",
                        "Documentation complete",
                        "All systems operational"
                    ]
                }
            ],
            "api_service": [
                {  # D-Rank
                    "name": "🦎 Ward Off the {enemy}",
                    "description": "Project setup, basic API structure, initial endpoints",
                    "aesthetic": "The {enemy} infest the forge. Clear them out to begin work.",
                    "success_criteria": [
                        "API framework setup",
                        "Basic endpoints created",
                        "Project structure defined"
                    ]
                },
                {  # C-Rank
                    "name": "⚔️ Drive Back the {enemy}",
                    "description": "Core business logic, database models, validation",
                    "aesthetic": "The {enemy} raid the smithy. Defend your work.",
                    "success_criteria": [
                        "Database models complete",
                        "Core logic implemented",
                        "Input validation working"
                    ]
                },
                {  # B-Rank
                    "name": "🐉 Forge in {enemy} Fire",
                    "description": "Advanced features, integrations, complex queries",
                    "aesthetic": "Only the flames of a {enemy} can temper the sacred blade.",
                    "success_criteria": [
                        "Advanced features working",
                        "Third-party integrations done",
                        "Complex queries optimized"
                    ]
                },
                {  # A-Rank
                    "name": "🧛 Protect from the {enemy}",
                    "description": "Authentication, authorization, security hardening",
                    "aesthetic": "The {enemy} seeks to corrupt your creation. Defend it.",
                    "success_criteria": [
                        "Auth/authz complete",
                        "Security audit passed",
                        "Rate limiting implemented"
                    ]
                },
                {  # S-Rank
                    "name": "🏰 Test Against {enemy} Siege",
                    "description": "Load testing, performance tuning, monitoring",
                    "aesthetic": "The {enemy} army tests your defenses. Will they hold?",
                    "success_criteria": [
                        "Load testing passed",
                        "Performance targets met",
                        "Monitoring configured"
                    ]
                },
                {  # SSS-Rank
                    "name": "👹 DEPLOY TO SLAY {enemy}",
                    "description": "Production deployment, documentation, final victory",
                    "aesthetic": "The {enemy} awaits in the void. Your API is the weapon that will end it.",
                    "success_criteria": [
                        "Production deployment successful",
                        "API documentation complete",
                        "All endpoints operational"
                    ]
                }
            ],
            "database": [
                {  # D-Rank
                    "name": "🦎 Clear the {enemy} from the Entrance",
                    "description": "Initial schema design, basic tables, setup",
                    "aesthetic": "The catacombs are infested with {enemy}. Clear the way.",
                    "success_criteria": [
                        "Database setup complete",
                        "Basic tables created",
                        "Migrations working"
                    ]
                },
                {  # C-Rank
                    "name": "⚔️ Fight Through the {enemy}",
                    "description": "Core models, relationships, basic queries",
                    "aesthetic": "The {enemy} patrol the deeper chambers. Press forward.",
                    "success_criteria": [
                        "Core models implemented",
                        "Relationships defined",
                        "Basic queries working"
                    ]
                },
                {  # B-Rank
                    "name": "🐉 Brave the {enemy} Chamber",
                    "description": "Complex queries, indexes, optimization",
                    "aesthetic": "The {enemy} nests in the treasure room. Its hoard glitters in the dark.",
                    "success_criteria": [
                        "Complex queries optimized",
                        "Indexes created",
                        "Query performance acceptable"
                    ]
                },
                {  # A-Rank
                    "name": "🧛 Banish the {enemy}",
                    "description": "Transactions, constraints, data integrity",
                    "aesthetic": "The undead {enemy} corrupts all data it touches. Purify the database.",
                    "success_criteria": [
                        "Transactions implemented",
                        "Constraints enforced",
                        "Data integrity ensured"
                    ]
                },
                {  # S-Rank
                    "name": "🏰 Fortify Against {enemy}",
                    "description": "Backups, replication, disaster recovery",
                    "aesthetic": "The {enemy} army approaches. Your data must survive.",
                    "success_criteria": [
                        "Backup system configured",
                        "Replication working",
                        "DR plan tested"
                    ]
                },
                {  # SSS-Rank
                    "name": "👹 SEAL THE {enemy}",
                    "description": "Final optimization, documentation, production deployment",
                    "aesthetic": "The {enemy} seeks to devour all data. Seal it away forever.",
                    "success_criteria": [
                        "Database deployed",
                        "Documentation complete",
                        "All migrations applied"
                    ]
                }
            ],
            "authentication": [
                {  # D-Rank
                    "name": "🦎 Patrol Against {enemy}",
                    "description": "Basic auth structure, user models, setup",
                    "aesthetic": "Minor {enemy} probe the defenses. Establish watch.",
                    "success_criteria": [
                        "Auth framework setup",
                        "User models created",
                        "Basic structure in place"
                    ]
                },
                {  # C-Rank
                    "name": "⚔️ Guard Against {enemy} Raiders",
                    "description": "Login/logout, session management, basic tokens",
                    "aesthetic": "The {enemy} test the walls. Hold the line.",
                    "success_criteria": [
                        "Login/logout working",
                        "Session management implemented",
                        "Basic token flow complete"
                    ]
                },
                {  # B-Rank
                    "name": "🐉 Withstand the {enemy} Assault",
                    "description": "JWT implementation, refresh tokens, middleware",
                    "aesthetic": "A {enemy} leads the assault. The walls shake.",
                    "success_criteria": [
                        "JWT fully implemented",
                        "Refresh tokens working",
                        "Auth middleware complete"
                    ]
                },
                {  # A-Rank
                    "name": "🧛 Defend the Seal from {enemy}",
                    "description": "Authorization, permissions, role-based access",
                    "aesthetic": "The {enemy} seeks the royal seal. It must not fall.",
                    "success_criteria": [
                        "Authorization implemented",
                        "Permissions system working",
                        "Role-based access complete"
                    ]
                },
                {  # S-Rank
                    "name": "🏰 Fortify Against {enemy} Magic",
                    "description": "Security hardening, rate limiting, 2FA",
                    "aesthetic": "The {enemy} wields dark magic. Strengthen all defenses.",
                    "success_criteria": [
                        "Security audit passed",
                        "Rate limiting active",
                        "2FA implemented"
                    ]
                },
                {  # SSS-Rank
                    "name": "👹 BANISH THE {enemy}",
                    "description": "Final security review, deployment, monitoring",
                    "aesthetic": "The {enemy} arrives. Your authentication system is the final barrier.",
                    "success_criteria": [
                        "Security review passed",
                        "Auth deployed to production",
                        "Monitoring configured"
                    ]
                }
            ]
        }

        # Default template if quest type not found
        return templates.get(quest_type, templates["web_app"])

    @classmethod
    def get_difficulty_badge_color(cls, rank: DifficultyRank) -> str:
        """Get CSS color for difficulty badge"""
        colors = {
            DifficultyRank.D_RANK: "#8B8B8B",  # Gray
            DifficultyRank.C_RANK: "#4CAF50",  # Green
            DifficultyRank.B_RANK: "#2196F3",  # Blue
            DifficultyRank.A_RANK: "#9C27B0",  # Purple
            DifficultyRank.S_RANK: "#FF9800",  # Orange
            DifficultyRank.SSS_RANK: "#F44336"  # Red
        }
        return colors[rank]

    @classmethod
    def get_difficulty_description(cls, rank: DifficultyRank) -> str:
        """Get human-readable difficulty description"""
        descriptions = {
            DifficultyRank.D_RANK: "Beginner Quest - Setup & Scaffolding",
            DifficultyRank.C_RANK: "Easy Quest - Basic Features",
            DifficultyRank.B_RANK: "Medium Quest - Core Functionality",
            DifficultyRank.A_RANK: "Hard Quest - Complex Systems",
            DifficultyRank.S_RANK: "Very Hard - Critical Infrastructure",
            DifficultyRank.SSS_RANK: "LEGENDARY - THE FINAL BOSS"
        }
        return descriptions[rank]


# Example usage
if __name__ == "__main__":
    print("🎮 QUEST: Build a Banking App")
    print("=" * 60)
    print()

    sprints = SprintGenerator.generate_sprints(
        quest_goal="Build a banking app",
        quest_type="web_app",
        total_budget=10.0
    )

    for i, sprint in enumerate(sprints, 1):
        print(f"Sprint {i}: {sprint.rank.value}-RANK")
        print(f"  Name: {sprint.name}")
        print(f"  Enemy: {sprint.enemy_type}")
        print(f"  Description: {sprint.description}")
        print(f"  Aesthetic: {sprint.aesthetic}")
        print(f"  Estimated Cost: ${sprint.estimated_cost:.2f}")
        print(f"  Success Criteria:")
        for criterion in sprint.success_criteria:
            print(f"    - {criterion}")
        print()

    print("=" * 60)
    print("TOTAL BUDGET: $10.00")
    print(f"FINAL BOSS: {sprints[-1].enemy_type}")
