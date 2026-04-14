"""
Project Epic - Fantasy Quest Agent System
Where Software Development Meets High Fantasy
"""

from .core.claude_agent import ClaudeAgent
from .core.party import Party
from .core.quest import Quest
from .coordination.heroes_journey import HeroesJourney, QuestType

__version__ = "0.1.0"
__all__ = ["ClaudeAgent", "Party", "Quest", "HeroesJourney", "QuestType"]
