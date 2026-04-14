"""
Heroes Journey - Quest Type System
Defines different quest types and their characteristics
"""

from enum import Enum


class QuestType(Enum):
    """Types of quests available in Project Epic"""
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    DATABASE = "database"
    AUTH_SYSTEM = "auth_system"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    GENERAL = "general"


class HeroesJourney:
    """
    Maps software development goals to RPG quest types

    This determines:
    - Quest type classification
    - Sprint naming themes
    - Enemy types
    - Success criteria patterns
    """

    QUEST_TYPE_KEYWORDS = {
        QuestType.WEB_APP: [
            "web", "frontend", "ui", "interface", "react", "vue", "angular",
            "website", "webapp", "app", "dashboard", "portal"
        ],
        QuestType.API_SERVICE: [
            "api", "rest", "graphql", "endpoint", "service", "backend",
            "server", "http", "websocket"
        ],
        QuestType.DATABASE: [
            "database", "db", "postgres", "mysql", "mongodb", "redis",
            "schema", "migration", "orm", "sql"
        ],
        QuestType.AUTH_SYSTEM: [
            "auth", "authentication", "authorization", "login", "signup",
            "jwt", "oauth", "session", "user", "password"
        ],
        QuestType.CLI_TOOL: [
            "cli", "command", "tool", "script", "terminal", "console",
            "executable", "binary"
        ],
        QuestType.LIBRARY: [
            "library", "package", "module", "sdk", "framework",
            "npm", "pip", "cargo", "gem"
        ],
        QuestType.MICROSERVICE: [
            "microservice", "service", "worker", "queue", "job",
            "background", "async", "task"
        ]
    }

    @classmethod
    def classify_quest(cls, goal: str) -> QuestType:
        """
        Classify a quest goal into a quest type

        Args:
            goal: User's quest goal (e.g., "Build a banking app")

        Returns:
            QuestType enum value
        """
        goal_lower = goal.lower()

        # Count keyword matches for each quest type
        scores = {}
        for quest_type, keywords in cls.QUEST_TYPE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in goal_lower)
            if score > 0:
                scores[quest_type] = score

        # Return quest type with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        # Default to general if no matches
        return QuestType.GENERAL

    @classmethod
    def get_quest_description(cls, quest_type: QuestType) -> str:
        """Get a thematic description for a quest type"""
        descriptions = {
            QuestType.WEB_APP: "A journey to craft a grand portal for the realm",
            QuestType.API_SERVICE: "Forging the mystical conduits of communication",
            QuestType.DATABASE: "Delving into the ancient vaults of knowledge",
            QuestType.AUTH_SYSTEM: "Guarding the gates with enchanted seals",
            QuestType.CLI_TOOL: "Smithing a legendary tool of power",
            QuestType.LIBRARY: "Writing the sacred tome of arcane functions",
            QuestType.MICROSERVICE: "Summoning a loyal servant to the realm",
            QuestType.GENERAL: "A grand quest across unknown lands"
        }
        return descriptions.get(quest_type, descriptions[QuestType.GENERAL])

    @classmethod
    def get_demon_king_title(cls, quest_type: QuestType, goal: str) -> str:
        """
        Generate the Demon King title for the final sprint

        Args:
            quest_type: Type of quest
            goal: Original quest goal

        Returns:
            Demon King title (e.g., "Elder Vampire Lord of Banking")
        """
        # Extract key feature from goal
        goal_words = goal.lower().split()

        # Remove common words
        stop_words = {"a", "an", "the", "for", "to", "of", "with", "build", "create", "make", "develop"}
        feature_words = [w for w in goal_words if w not in stop_words and len(w) > 3]

        # Get main feature (first significant word)
        feature = feature_words[0].capitalize() if feature_words else "Code"

        # Demon King titles by quest type
        titles = {
            QuestType.WEB_APP: f"Elder Vampire Lord of {feature}",
            QuestType.API_SERVICE: f"Demon King of {feature} Services",
            QuestType.DATABASE: f"Ancient Dragon of {feature} Vaults",
            QuestType.AUTH_SYSTEM: f"Dark Lord of {feature} Gates",
            QuestType.CLI_TOOL: f"Titan of {feature} Execution",
            QuestType.LIBRARY: f"Archlich of {feature} Knowledge",
            QuestType.MICROSERVICE: f"Chaos God of {feature} Workers",
            QuestType.GENERAL: f"Demon King of {feature}"
        }

        return titles.get(quest_type, titles[QuestType.GENERAL])


# Example usage
if __name__ == "__main__":
    # Test quest classification
    test_goals = [
        "Build a banking web app",
        "Create a REST API for user management",
        "Design a PostgreSQL database schema",
        "Implement JWT authentication",
        "Write a CLI tool for deployment",
        "Build a payment processing microservice"
    ]

    print("Quest Classification Examples:\n")
    for goal in test_goals:
        quest_type = HeroesJourney.classify_quest(goal)
        description = HeroesJourney.get_quest_description(quest_type)
        demon_king = HeroesJourney.get_demon_king_title(quest_type, goal)

        print(f"Goal: {goal}")
        print(f"  Type: {quest_type.value}")
        print(f"  Description: {description}")
        print(f"  Final Boss: {demon_king}")
        print()
