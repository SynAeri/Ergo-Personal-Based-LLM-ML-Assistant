"""
Party - Coordinates multiple Claude agents working together
"""

from typing import List, Dict, Any, Optional
from .claude_agent import ClaudeAgent
from ..coordination.campfire import Campfire, CampfireAgenda, CampfireReport


class Party:
    """
    A party of Claude agents working together on a quest

    The party consists of 6 members:
    - Planner: Task decomposition (Gemini Flash)
    - Mage: Architecture & reasoning (Claude Opus)
    - Rogue: Code execution (Claude Sonnet)
    - Tank: Testing & verification (Claude Sonnet)
    - Support: Memory & context retrieval (Gemini Flash)
    - Healer: Summarization & documentation (Gemini Flash)
    """

    # Default party composition
    DEFAULT_ROLES = ["planner", "mage", "rogue", "tank", "support", "healer"]

    # Model assignments per role
    ROLE_MODELS = {
        "planner": "gemini-2.0-flash",  # Fast planning
        "mage": "claude-sonnet-3.5",    # Deep reasoning (use Opus for complex quests)
        "rogue": "claude-sonnet-3.5",   # Balanced code execution
        "tank": "claude-sonnet-3.5",    # Rigorous testing
        "support": "gemini-2.0-flash",  # Cheap lookups
        "healer": "gemini-2.0-flash"    # Cheap summarization
    }

    # Permissions per role
    ROLE_PERMISSIONS = {
        "planner": {
            "can_read_files": True,
            "can_write_files": False,
            "can_execute_shell": False,
            "allowed_tools": ["read_file", "search_code", "create_plan", "search_memory"]
        },
        "mage": {
            "can_read_files": True,
            "can_write_files": False,  # Can only suggest
            "can_execute_shell": False,
            "allowed_tools": ["read_file", "search_code", "search_memory"]
        },
        "rogue": {
            "can_read_files": True,
            "can_write_files": True,
            "can_execute_shell": True,
            "shell_allowlist": ["git", "cargo", "npm", "pytest", "go", "make"],
            "allowed_tools": ["read_file", "write_file", "search_code", "run_command"]
        },
        "tank": {
            "can_read_files": True,
            "can_write_files": False,
            "can_execute_shell": True,
            "shell_allowlist": ["cargo test", "npm test", "pytest", "go test", "make test"],
            "allowed_tools": ["read_file", "search_code", "run_tests", "run_command"]
        },
        "support": {
            "can_read_files": True,
            "can_write_files": False,
            "can_execute_shell": False,
            "allowed_tools": ["read_file", "search_code", "search_memory"]
        },
        "healer": {
            "can_read_files": True,
            "can_write_files": True,  # Can write summaries/docs
            "can_execute_shell": False,
            "file_scope": "docs/",  # Only write to docs
            "allowed_tools": ["read_file", "write_file", "search_memory"]
        }
    }

    def __init__(self, roles: Optional[List[str]] = None, simulation_mode: bool = False):
        """
        Initialize party with specified roles

        Args:
            roles: List of role names. Defaults to all 6 roles.
            simulation_mode: If True, create agents without API connections (testing mode)
        """
        self.roles = roles or self.DEFAULT_ROLES
        self.members: Dict[str, ClaudeAgent] = {}
        self.simulation_mode = simulation_mode

        # Assemble the party
        for role in self.roles:
            self.members[role] = self._create_agent(role)

    @classmethod
    def assemble(cls, roles: Optional[List[str]] = None, simulation_mode: bool = False) -> "Party":
        """Factory method to assemble a party"""
        return cls(roles, simulation_mode)

    def _create_agent(self, role: str) -> ClaudeAgent:
        """Create a Claude agent for a specific role"""
        model = self.ROLE_MODELS.get(role, "claude-sonnet-3.5")
        permissions = self.ROLE_PERMISSIONS.get(role, {})
        personality_file = f"{role}.md"

        return ClaudeAgent(
            role_name=role,
            personality_file=personality_file,
            model=model,
            permissions=permissions,
            simulation_mode=self.simulation_mode
        )

    def get_member(self, role: str) -> Optional[ClaudeAgent]:
        """Get a specific party member"""
        return self.members.get(role)

    def get_all_members(self) -> List[ClaudeAgent]:
        """Get all party members"""
        return list(self.members.values())

    async def coordinate_action(
        self,
        primary_role: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        supporting_roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate an action with primary and supporting agents

        Args:
            primary_role: The agent taking primary action
            action: What to do
            context: Additional context
            supporting_roles: Roles that should provide input first

        Returns:
            Combined results from all agents
        """
        results = {
            "primary": None,
            "supporting": []
        }

        # Get supporting input first
        if supporting_roles:
            for role in supporting_roles:
                agent = self.get_member(role)
                if agent:
                    support_result = await agent.send_message(
                        f"Provide input for: {action}",
                        context=context
                    )
                    results["supporting"].append({
                        "role": role,
                        "response": support_result["response"],
                        "cost": support_result["cost"]
                    })

        # Primary agent takes action
        primary_agent = self.get_member(primary_role)
        if primary_agent:
            # Add supporting input to context
            if results["supporting"]:
                context = context or {}
                context["party_input"] = [s["response"] for s in results["supporting"]]

            primary_result = await primary_agent.send_message(action, context=context)
            results["primary"] = {
                "role": primary_role,
                "response": primary_result["response"],
                "tool_calls": primary_result["tool_calls"],
                "cost": primary_result["cost"],
                "tokens": primary_result["tokens"]
            }

        return results

    def get_party_stats(self) -> Dict[str, Any]:
        """Get statistics for all party members"""
        stats = {}
        total_cost = 0.0
        total_tokens = 0

        for role, agent in self.members.items():
            agent_stats = agent.get_stats()
            stats[role] = agent_stats
            total_cost += agent_stats["total_cost"]
            total_tokens += agent_stats["total_tokens"]

        return {
            "members": stats,
            "total_cost": round(total_cost, 2),
            "total_tokens": total_tokens,
            "party_size": len(self.members)
        }

    async def gather_at_campfire(
        self,
        campfire: Campfire,
        agenda: CampfireAgenda,
        sprint_number: Optional[int],
        sprint_success: bool,
        budget_used: float,
        tokens_used: int
    ) -> CampfireReport:
        """
        Gather all party members at campfire for business checkpoint

        Args:
            campfire: Campfire instance
            agenda: What this campfire is about
            sprint_number: Which sprint was just completed
            sprint_success: Did the sprint succeed
            budget_used: Total budget used so far
            tokens_used: Total tokens used so far

        Returns:
            Campfire report with assessment and recommendations
        """
        return await campfire.gather_party(
            agenda=agenda,
            sprint_number=sprint_number,
            sprint_success=sprint_success,
            party_agents=self.get_all_members(),
            budget_used=budget_used,
            tokens_used=tokens_used
        )

    def compress_all_histories(self, keep_recent: int = 5):
        """Compress conversation history for all agents"""
        for agent in self.get_all_members():
            agent.compress_history(keep_recent=keep_recent)

    def reset_all_conversations(self):
        """Reset conversation history for all agents"""
        for agent in self.get_all_members():
            agent.reset_conversation()

    def get_party_roster(self) -> List[Dict[str, str]]:
        """Get party roster with roles and models"""
        return [
            {
                "role": role,
                "model": agent.model,
                "personality": f"{role}.md"
            }
            for role, agent in self.members.items()
        ]

    def __repr__(self) -> str:
        return f"Party(members={list(self.members.keys())})"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_party():
        print("🎮 Assembling the party...")
        party = Party.assemble()

        print(f"\nParty assembled: {party}")
        print("\nRoster:")
        for member in party.get_party_roster():
            print(f"  {member['role'].title()}: {member['model']}")

        print("\n📋 Planning Phase - Coordinated Action")
        print("=" * 60)

        # Coordinate planning with support from multiple agents
        result = await party.coordinate_action(
            primary_role="planner",
            action="Create a plan to implement JWT authentication",
            supporting_roles=["support", "mage"]  # Support provides context, Mage provides arch advice
        )

        print(f"\nSupporting input from {len(result['supporting'])} agents:")
        for support in result["supporting"]:
            print(f"  {support['role'].title()}: ${support['cost']:.4f}")

        if result["primary"]:
            print(f"\nPrimary action by {result['primary']['role'].title()}:")
            print(f"  Cost: ${result['primary']['cost']:.4f}")
            print(f"  Tokens: {result['primary']['tokens']}")
            print(f"  Response: {result['primary']['response'][:200]}...")

        print("\n📊 Party Statistics")
        print("=" * 60)
        stats = party.get_party_stats()
        print(f"Total Cost: ${stats['total_cost']:.2f}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"\nPer-Agent Breakdown:")
        for role, agent_stats in stats["members"].items():
            print(f"  {role.title()}: ${agent_stats['total_cost']:.2f} ({agent_stats['total_tokens']:,} tokens)")

    asyncio.run(test_party())
