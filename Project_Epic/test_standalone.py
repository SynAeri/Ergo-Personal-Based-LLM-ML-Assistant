#!/usr/bin/env python3
"""
Project Epic - Standalone Testing Script
Test the quest system without Ergo integration
"""

import asyncio
import os
from pathlib import Path

# Add epic package to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from epic.core.quest import Quest
from epic.core.party import Party
from epic.coordination.campfire import Campfire, CampfireAgenda
from epic.coordination.sprint_difficulty import SprintGenerator


async def test_quest_creation():
    """Test creating a quest with difficulty-scaled sprints"""
    print("=" * 70)
    print("TEST 1: Quest Creation with Progressive Difficulty")
    print("=" * 70)
    print()

    quest = Quest(
        goal="Build a banking app",
        budget=10.0,
        max_tokens=100_000
    )

    print(quest.get_ascii_quest_board())
    print()
    print(f"Demon King: {quest.demon_king}")
    print(f"Quest Type: {quest.quest_type}")
    print()

    print("Sprint Details:")
    for i, sprint in enumerate(quest.sprints, 1):
        print(f"\n{i}. {sprint.rank.value}-RANK: {sprint.name}")
        print(f"   Enemy: {sprint.enemy_type}")
        print(f"   {sprint.aesthetic}")
        print(f"   Estimated Cost: ${sprint.estimated_cost:.2f}")

    return quest


async def test_party_assembly():
    """Test assembling a party of 4 members"""
    print("\n" + "=" * 70)
    print("TEST 2: Party Assembly (4 Members)")
    print("=" * 70)
    print()

    party = Party.assemble(roles=["planner", "mage", "rogue", "tank"], simulation_mode=True)

    print("🎭 Party Assembled!")
    print()
    print("Roster:")
    for member in party.get_party_roster():
        print(f"  {member['role'].upper():12} - {member['model']}")

    print()
    print("Permissions Check:")
    rogue = party.get_member("rogue")
    tank = party.get_member("tank")

    print(f"  Rogue can write files: {rogue.check_permission('write_file')}")
    print(f"  Rogue can run commands: {rogue.check_permission('run_command')}")
    print(f"  Tank can write files: {tank.check_permission('write_file')}")
    print(f"  Tank can run tests: {tank.check_permission('run_tests')}")

    return party


async def test_campfire():
    """Test campfire business checkpoint"""
    print("\n" + "=" * 70)
    print("TEST 3: Campfire Business Checkpoint")
    print("=" * 70)
    print()

    quest = Quest("Build a banking app", budget=10.0)
    party = Party.assemble(roles=["planner", "mage", "rogue", "tank"], simulation_mode=True)
    campfire = Campfire(quest.goal, quest.budget, quest.max_tokens)

    # Simulate progress
    quest.start()
    quest.complete_sprint(success=True, cost=1.0, tokens=10000)
    quest.complete_sprint(success=True, cost=1.5, tokens=15000)

    # Mock agent stats
    class MockAgent:
        def __init__(self, role, tools, cost):
            self.role_name = role
            self._tools = tools
            self._cost = cost
        def get_stats(self):
            return {"tools_used": self._tools, "total_cost": self._cost, "total_tokens": 10000}

    mock_party = [
        MockAgent("planner", 3, 0.50),
        MockAgent("mage", 2, 0.80),
        MockAgent("rogue", 8, 1.20),
        MockAgent("tank", 5, 0.90)
    ]

    report = await campfire.gather_party(
        agenda=CampfireAgenda.SPRINT_REVIEW,
        sprint_number=2,
        sprint_success=True,
        party_agents=mock_party,
        budget_used=2.5,
        tokens_used=25000
    )

    print(campfire.format_report(report))


async def test_sprint_difficulty():
    """Test sprint difficulty generation for different quest types"""
    print("\n" + "=" * 70)
    print("TEST 4: Sprint Difficulty Scaling")
    print("=" * 70)
    print()

    quest_types = ["web_app", "api_service", "database", "authentication"]

    for quest_type in quest_types:
        sprints = SprintGenerator.generate_sprints(
            quest_goal=f"Test {quest_type} project",
            quest_type=quest_type,
            total_budget=10.0
        )

        print(f"\n{quest_type.upper()} Quest:")
        print("─" * 70)
        for sprint in sprints:
            print(f"  {sprint.rank.value:4} | {sprint.name}")


async def test_full_quest_flow():
    """Test a complete quest flow"""
    print("\n" + "=" * 70)
    print("TEST 5: Complete Quest Flow")
    print("=" * 70)
    print()

    # Create quest
    quest = Quest("Build a JWT auth system", budget=5.0, max_tokens=50000)
    party = Party.assemble(roles=["planner", "rogue", "tank"], simulation_mode=True)
    campfire = Campfire(quest.goal, quest.budget, quest.max_tokens)

    print(f"🎮 Quest: {quest.goal}")
    print(f"👹 Demon King: {quest.demon_king}")
    print(f"🎭 Party: {', '.join(party.roles)}")
    print()

    quest.start()

    # Simulate 3 sprints
    for i in range(3):
        sprint = quest.get_current_sprint()
        if not sprint:
            break

        print(f"\n⚔️  SPRINT {i+1}: {sprint.rank.value}-RANK - {sprint.name}")
        print(f"   Enemy: {sprint.enemy_type}")
        print(f"   {sprint.aesthetic}")

        # Simulate execution
        await asyncio.sleep(0.5)

        # Complete sprint
        quest.complete_sprint(
            success=True,
            cost=sprint.estimated_cost,
            tokens=10000
        )

        print(f"   ✓ Complete! Cost: ${sprint.estimated_cost:.2f}")

        # Campfire after each sprint
        if i < 2:  # Not after last sprint for this demo
            print(f"\n🏕️  Campfire Gathering...")

            # Mock stats
            mock_party = [
                MockAgent("planner", i+1, 0.30),
                MockAgent("rogue", (i+1)*2, 0.60),
                MockAgent("tank", i+1, 0.40)
            ]

            report = await campfire.gather_party(
                agenda=CampfireAgenda.SPRINT_REVIEW,
                sprint_number=i+1,
                sprint_success=True,
                party_agents=mock_party,
                budget_used=quest.budget_used,
                tokens_used=quest.tokens_used
            )

            print(f"   Progress: {quest.get_progress_percentage():.0f}%")
            print(f"   Budget: ${quest.budget_used:.2f} / ${quest.budget:.2f}")
            print(f"   On Track: {'YES ✓' if report.on_track else 'NO ✗'}")
            print(f"   Morale: {report.overall_morale}")

    print(f"\n🎉 Quest Progress: {quest.get_progress_percentage():.0f}%")
    print(quest.get_ascii_quest_board())


class MockAgent:
    def __init__(self, role, tools, cost):
        self.role_name = role
        self._tools = tools
        self._cost = cost
    def get_stats(self):
        return {"tools_used": self._tools, "total_cost": self._cost, "total_tokens": 10000}


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PROJECT EPIC - STANDALONE TESTS" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    await test_quest_creation()
    await asyncio.sleep(1)

    await test_party_assembly()
    await asyncio.sleep(1)

    await test_campfire()
    await asyncio.sleep(1)

    await test_sprint_difficulty()
    await asyncio.sleep(1)

    await test_full_quest_flow()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
    print()
    print("To test the web interface:")
    print("  1. Set API keys: export ANTHROPIC_API_KEY='...'")
    print("  2. Install deps: pip install -r requirements.txt")
    print("  3. Start server: python -m epic.api.server")
    print("  4. Open browser: http://localhost:8766")
    print()


if __name__ == "__main__":
    asyncio.run(main())
