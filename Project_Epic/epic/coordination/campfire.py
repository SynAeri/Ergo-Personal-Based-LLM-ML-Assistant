"""
Campfire System - Business Alignment & Recon Checkpoint
Where the party pauses to assess, align, and pivot
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CampfireAgenda(Enum):
    """What the campfire discussion focuses on"""
    INITIAL_PLANNING = "initial_planning"  # Before first sprint
    SPRINT_REVIEW = "sprint_review"        # After each sprint
    PIVOT_DECISION = "pivot_decision"      # When strategy needs to change
    FINAL_VICTORY = "final_victory"        # After final boss


@dataclass
class AgentStatus:
    """Status of a single agent at campfire"""
    role: str
    hp_percentage: float  # 0-100, based on budget remaining
    mp_percentage: float  # 0-100, based on tokens remaining
    morale: str  # "High", "Good", "Concerned", "Exhausted"
    concerns: List[str]  # What this agent is worried about
    achievements: List[str]  # What this agent accomplished
    recommendations: List[str]  # What this agent suggests


@dataclass
class CampfireReport:
    """Output from a campfire discussion"""
    agenda: CampfireAgenda
    timestamp: datetime
    sprint_completed: Optional[int]  # Which sprint just finished (1-6)
    sprint_success: bool  # Did we meet success criteria?

    # Business Alignment
    goal_progress: float  # 0-100, how close to main goal
    on_track: bool  # Are we on track to complete within budget/time?
    pivot_needed: bool  # Do we need to change strategy?

    # Agent Recon
    party_status: List[AgentStatus]
    overall_morale: str  # "High", "Good", "Concerned", "Critical"

    # Decisions
    continue_as_planned: bool
    strategy_changes: List[str]  # What will we do differently
    next_sprint_focus: Optional[str]  # Focus for next sprint

    # Resources
    budget_used: float
    budget_remaining: float
    tokens_used: int
    tokens_remaining: int


class Campfire:
    """
    Campfire discussion system

    Purpose:
    1. Assess: Did we accomplish sprint goals?
    2. Align: Are we on track for main quest?
    3. Pivot: Do we need to adjust strategy?
    4. Recon: How are agents doing?
    """

    def __init__(self, quest_goal: str, total_budget: float, total_tokens: int):
        self.quest_goal = quest_goal
        self.total_budget = total_budget
        self.total_tokens = total_tokens
        self.campfire_history: List[CampfireReport] = []

    async def gather_party(
        self,
        agenda: CampfireAgenda,
        sprint_number: Optional[int],
        sprint_success: bool,
        party_agents: List[Any],  # List of ClaudeAgent instances
        budget_used: float,
        tokens_used: int
    ) -> CampfireReport:
        """
        Gather the party at the campfire for discussion

        This is a business checkpoint, not a full AI discussion.
        We assess status and make strategic decisions.
        """
        # Calculate resources
        budget_remaining = self.total_budget - budget_used
        tokens_remaining = self.total_tokens - tokens_used

        # Gather agent statuses
        party_status = []
        for agent in party_agents:
            status = self._assess_agent(
                agent,
                budget_used,
                tokens_used,
                budget_remaining,
                tokens_remaining
            )
            party_status.append(status)

        # Determine overall morale
        overall_morale = self._calculate_overall_morale(party_status, budget_remaining)

        # Assess progress toward main goal
        goal_progress = self._assess_goal_progress(sprint_number, sprint_success)

        # Determine if on track
        on_track = self._check_on_track(
            sprint_number,
            budget_used,
            budget_remaining,
            goal_progress
        )

        # Determine if pivot needed
        pivot_needed = self._check_pivot_needed(
            on_track,
            budget_remaining,
            overall_morale,
            sprint_success
        )

        # Strategy changes
        strategy_changes = []
        if pivot_needed:
            strategy_changes = self._generate_strategy_changes(
                party_status,
                budget_remaining,
                sprint_success
            )

        # Next sprint focus
        next_sprint_focus = self._determine_next_focus(
            sprint_number,
            strategy_changes,
            party_status
        )

        # Create report
        report = CampfireReport(
            agenda=agenda,
            timestamp=datetime.now(),
            sprint_completed=sprint_number,
            sprint_success=sprint_success,
            goal_progress=goal_progress,
            on_track=on_track,
            pivot_needed=pivot_needed,
            party_status=party_status,
            overall_morale=overall_morale,
            continue_as_planned=(not pivot_needed),
            strategy_changes=strategy_changes,
            next_sprint_focus=next_sprint_focus,
            budget_used=budget_used,
            budget_remaining=budget_remaining,
            tokens_used=tokens_used,
            tokens_remaining=tokens_remaining
        )

        self.campfire_history.append(report)
        return report

    def _assess_agent(
        self,
        agent: Any,
        budget_used: float,
        tokens_used: int,
        budget_remaining: float,
        tokens_remaining: int
    ) -> AgentStatus:
        """Assess a single agent's status"""
        # Get agent stats
        stats = agent.get_stats()

        # Calculate HP (based on budget)
        hp_percentage = (budget_remaining / self.total_budget) * 100

        # Calculate MP (based on tokens)
        mp_percentage = (tokens_remaining / self.total_tokens) * 100

        # Determine morale
        morale = "High"
        if hp_percentage < 30 or mp_percentage < 30:
            morale = "Exhausted"
        elif hp_percentage < 50 or mp_percentage < 50:
            morale = "Concerned"
        elif hp_percentage < 70:
            morale = "Good"

        # Generate concerns
        concerns = []
        if hp_percentage < 40:
            concerns.append(f"Budget running low ({hp_percentage:.0f}% remaining)")
        if mp_percentage < 40:
            concerns.append(f"Token limit approaching ({mp_percentage:.0f}% remaining)")
        if stats["tools_used"] == 0:
            concerns.append("Haven't contributed yet")

        # Generate achievements
        achievements = []
        if stats["tools_used"] > 0:
            achievements.append(f"Used {stats['tools_used']} skills successfully")
        if stats["total_cost"] > 0:
            achievements.append(f"Contributed ${stats['total_cost']:.2f} worth of work")

        # Generate recommendations
        recommendations = []
        if morale == "Exhausted":
            recommendations.append("Need to conserve resources")
        if len(concerns) > 0:
            recommendations.append("Should reassess strategy")

        return AgentStatus(
            role=agent.role_name,
            hp_percentage=hp_percentage,
            mp_percentage=mp_percentage,
            morale=morale,
            concerns=concerns,
            achievements=achievements,
            recommendations=recommendations
        )

    def _calculate_overall_morale(
        self,
        party_status: List[AgentStatus],
        budget_remaining: float
    ) -> str:
        """Calculate overall party morale"""
        morale_scores = {
            "High": 4,
            "Good": 3,
            "Concerned": 2,
            "Exhausted": 1
        }

        avg_score = sum(morale_scores[a.morale] for a in party_status) / len(party_status)

        if avg_score >= 3.5:
            return "High"
        elif avg_score >= 2.5:
            return "Good"
        elif avg_score >= 1.5:
            return "Concerned"
        else:
            return "Critical"

    def _assess_goal_progress(self, sprint_number: Optional[int], sprint_success: bool) -> float:
        """Calculate progress toward main goal (0-100)"""
        if sprint_number is None:
            return 0.0

        # Each sprint is worth ~16.7% (100/6)
        base_progress = (sprint_number / 6) * 100

        # Penalize if sprint failed
        if not sprint_success:
            base_progress -= 10

        return max(0, min(100, base_progress))

    def _check_on_track(
        self,
        sprint_number: Optional[int],
        budget_used: float,
        budget_remaining: float,
        goal_progress: float
    ) -> bool:
        """Determine if we're on track to complete within constraints"""
        if sprint_number is None:
            return True

        # Check budget burn rate
        expected_budget_used = (sprint_number / 6) * self.total_budget
        budget_over = budget_used > (expected_budget_used * 1.2)  # 20% tolerance

        # Check progress
        expected_progress = (sprint_number / 6) * 100
        progress_behind = goal_progress < (expected_progress * 0.8)  # 20% tolerance

        return not (budget_over or progress_behind)

    def _check_pivot_needed(
        self,
        on_track: bool,
        budget_remaining: float,
        overall_morale: str,
        sprint_success: bool
    ) -> bool:
        """Determine if a strategic pivot is needed"""
        # Pivot if way off track
        if not on_track and budget_remaining < (self.total_budget * 0.3):
            return True

        # Pivot if morale critical
        if overall_morale == "Critical":
            return True

        # Pivot if multiple sprint failures
        recent_failures = sum(
            1 for report in self.campfire_history[-3:]
            if not report.sprint_success
        )
        if recent_failures >= 2:
            return True

        return False

    def _generate_strategy_changes(
        self,
        party_status: List[AgentStatus],
        budget_remaining: float,
        sprint_success: bool
    ) -> List[str]:
        """Generate strategic changes if pivot needed"""
        changes = []

        if budget_remaining < (self.total_budget * 0.3):
            changes.append("Reduce scope - focus on MVP only")
            changes.append("Use cheaper models where possible (Gemini Flash)")

        if not sprint_success:
            changes.append("Allocate more time to testing before next sprint")
            changes.append("Increase coordination between agents")

        exhausted_agents = [a for a in party_status if a.morale == "Exhausted"]
        if exhausted_agents:
            changes.append(f"Reduce workload for: {', '.join(a.role for a in exhausted_agents)}")

        return changes

    def _determine_next_focus(
        self,
        sprint_number: Optional[int],
        strategy_changes: List[str],
        party_status: List[AgentStatus]
    ) -> Optional[str]:
        """Determine focus area for next sprint"""
        if sprint_number is None or sprint_number >= 6:
            return None

        # If pivoting, focus on risk mitigation
        if strategy_changes:
            return "Risk mitigation and scope reduction"

        # If agents have concerns, address them
        all_concerns = [c for agent in party_status for c in agent.concerns]
        if all_concerns:
            return f"Address: {all_concerns[0]}"

        # Normal progression
        return "Continue as planned"

    def format_report(self, report: CampfireReport) -> str:
        """Format campfire report as text"""
        lines = []
        lines.append("🏕️  ═══════════════════════════════════════════════════")
        lines.append("              CAMPFIRE - BUSINESS CHECKPOINT")
        lines.append("   ═══════════════════════════════════════════════════ 🏕️")
        lines.append("")
        lines.append(f"Quest: {self.quest_goal}")
        lines.append(f"Agenda: {report.agenda.value.replace('_', ' ').title()}")
        lines.append(f"Time: {report.timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        if report.sprint_completed:
            status_icon = "✓" if report.sprint_success else "✗"
            lines.append(f"Sprint {report.sprint_completed}: {status_icon} {'SUCCESS' if report.sprint_success else 'INCOMPLETE'}")
            lines.append("")

        lines.append("─────────────────────────────────────────────────────")
        lines.append("PROGRESS ASSESSMENT")
        lines.append("─────────────────────────────────────────────────────")
        lines.append(f"Goal Progress: {report.goal_progress:.0f}%")
        lines.append(f"On Track: {'YES ✓' if report.on_track else 'NO ✗'}")
        lines.append(f"Pivot Needed: {'YES ⚠️' if report.pivot_needed else 'NO'}")
        lines.append("")

        lines.append("─────────────────────────────────────────────────────")
        lines.append("PARTY RECON")
        lines.append("─────────────────────────────────────────────────────")
        lines.append(f"Overall Morale: {report.overall_morale}")
        lines.append("")

        for agent in report.party_status:
            lines.append(f"{agent.role.upper()}:")
            lines.append(f"  HP: {agent.hp_percentage:.0f}% | MP: {agent.mp_percentage:.0f}%")
            lines.append(f"  Morale: {agent.morale}")
            if agent.achievements:
                lines.append(f"  Achievements: {', '.join(agent.achievements)}")
            if agent.concerns:
                lines.append(f"  Concerns: {', '.join(agent.concerns)}")
            lines.append("")

        lines.append("─────────────────────────────────────────────────────")
        lines.append("RESOURCES")
        lines.append("─────────────────────────────────────────────────────")
        lines.append(f"Budget: ${report.budget_used:.2f} / ${report.budget_used + report.budget_remaining:.2f}")
        lines.append(f"Remaining: ${report.budget_remaining:.2f} ({report.budget_remaining/(report.budget_used+report.budget_remaining)*100:.0f}%)")
        lines.append(f"Tokens: {report.tokens_used:,} / {report.tokens_used + report.tokens_remaining:,}")
        lines.append("")

        if report.strategy_changes:
            lines.append("─────────────────────────────────────────────────────")
            lines.append("STRATEGY CHANGES")
            lines.append("─────────────────────────────────────────────────────")
            for change in report.strategy_changes:
                lines.append(f"  • {change}")
            lines.append("")

        if report.next_sprint_focus:
            lines.append("─────────────────────────────────────────────────────")
            lines.append(f"NEXT SPRINT FOCUS: {report.next_sprint_focus}")
            lines.append("─────────────────────────────────────────────────────")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════")

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    from ..core.claude_agent import ClaudeAgent

    # Mock scenario
    print("=" * 60)
    print("QUEST: Build a Banking App")
    print("=" * 60)
    print()

    campfire = Campfire(
        quest_goal="Build a banking app",
        total_budget=10.0,
        total_tokens=100_000
    )

    # Simulate sprint 2 completion
    print("Sprint 2 (C-RANK) Complete - Campfire Gathering...")
    print()

    # Mock party agents
    class MockAgent:
        def __init__(self, role, tools_used, cost):
            self.role_name = role
            self._tools_used = tools_used
            self._cost = cost

        def get_stats(self):
            return {
                "tools_used": self._tools_used,
                "total_cost": self._cost
            }

    mock_party = [
        MockAgent("planner", 3, 0.50),
        MockAgent("mage", 2, 0.80),
        MockAgent("rogue", 8, 1.20),
        MockAgent("tank", 5, 0.90)
    ]

    report = campfire.gather_party(
        agenda=CampfireAgenda.SPRINT_REVIEW,
        sprint_number=2,
        sprint_success=True,
        party_agents=mock_party,
        budget_used=3.40,
        tokens_used=35_000
    )

    print(campfire.format_report(report))
