"""
Supervisor Controller for Ergo Work Mode
Orchestrates missions, dispatches agents, enforces constraints
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from .mission_manager import MissionManager
from .memory_service import MemoryService
from .obsidian_bridge import ObsidianBridge


class Supervisor:
    """Main work mode supervisor - coordinates agents and manages missions"""

    WORK_MODE_ACTIVATION_PHRASES = [
        "let's get a job done",
        "start work mode",
        "begin mission",
        "let's work on",
        "help me build",
        "i need to implement"
    ]

    def __init__(
        self,
        db_path: str = "~/ergo/runtime/missions.db",
        obsidian_vault: str = None
    ):
        self.mission_manager = MissionManager(db_path)
        self.memory_service = MemoryService(db_path)

        # Use user's Obsidian vault at ~/Obsidian
        vault_path = obsidian_vault or os.getenv("OBSIDIAN_VAULT", "~/Obsidian")
        self.obsidian_bridge = ObsidianBridge(db_path, vault_path)

        self.current_mission_id = None

    def detect_work_mode_activation(self, user_message: str) -> bool:
        """Check if user is requesting work mode"""
        message_lower = user_message.lower()
        return any(phrase in message_lower for phrase in self.WORK_MODE_ACTIVATION_PHRASES)

    def create_mission_from_user_input(
        self,
        user_goal: str,
        project_id: Optional[str] = None,
        budget_limit: float = 10.0
    ) -> Dict[str, Any]:
        """Create a new mission from user request"""
        # Extract title from goal (first sentence or first 50 chars)
        title = user_goal.split('.')[0][:50]

        mission_id = self.mission_manager.create_mission(
            title=title,
            goal=user_goal,
            mode="work",
            project_id=project_id,
            budget_limit=budget_limit
        )

        self.current_mission_id = mission_id

        return {
            "mission_id": mission_id,
            "title": title,
            "status": "scoping",
            "next_action": "planning"
        }

    def plan_mission(self, mission_id: str, goal: str) -> Dict[str, Any]:
        """Create initial mission plan using Planner agent"""
        # This would dispatch to the Planner agent
        # For now, return a simple plan structure

        plan = {
            "analysis": f"Mission to: {goal}",
            "steps": [
                {
                    "step_number": 1,
                    "role": "planner",
                    "objective": "Decompose task into actionable steps",
                    "status": "pending"
                }
            ]
        }

        # Add steps to mission
        for step_plan in plan['steps']:
            self.mission_manager.add_mission_step(
                mission_id,
                step_plan['role'],
                step_plan['objective']
            )

        # Transition to decomposed state
        self.mission_manager.transition_state(mission_id, "decomposed")

        return plan

    def request_approval(self, mission_id: str) -> Dict[str, Any]:
        """Request user approval for mission plan"""
        status = self.mission_manager.get_mission_status(mission_id)
        mission = status['mission']
        steps = status['steps']

        # Transition to waiting_for_approval
        self.mission_manager.transition_state(mission_id, "waiting_for_approval")

        return {
            "mission_id": mission_id,
            "title": mission['title'],
            "goal": mission['goal'],
            "steps": len(steps),
            "estimated_cost": mission.get('budget_limit', 0),
            "requires_approval": True
        }

    def approve_mission(self, mission_id: str) -> bool:
        """User approves mission, transition to running"""
        self.mission_manager.transition_state(mission_id, "running")
        return True

    def execute_mission_step(self, step_id: str) -> Dict[str, Any]:
        """Execute a single mission step by dispatching to appropriate agent"""
        step = self.mission_manager.get_step(step_id)

        # Mark step as started
        self.mission_manager.start_mission_step(step_id)

        # This would dispatch to the actual agent based on step['role_name']
        # For now, simulate execution
        result = {
            "step_id": step_id,
            "role": step['role_name'],
            "status": "simulated",
            "output": f"Simulated execution of {step['role_name']} for: {step['objective']}"
        }

        # Mark step as completed
        self.mission_manager.complete_mission_step(
            step_id,
            output_summary=result['output'],
            cost=0.5  # Simulated cost
        )

        return result

    def execute_mission(self, mission_id: str) -> Dict[str, Any]:
        """Execute all steps in a mission sequentially"""
        steps = self.mission_manager.get_mission_steps(mission_id)

        results = []
        for step in steps:
            if step['status'] == 'pending':
                result = self.execute_mission_step(step['step_id'])
                results.append(result)

        # Transition to review
        self.mission_manager.transition_state(mission_id, "review")

        return {
            "mission_id": mission_id,
            "steps_executed": len(results),
            "results": results
        }

    def complete_mission(self, mission_id: str) -> Dict[str, Any]:
        """Mark mission as completed and export summary"""
        # Transition to completed
        self.mission_manager.transition_state(mission_id, "completed")

        # Get final status
        status = self.mission_manager.get_mission_status(mission_id)

        # Export to Obsidian vault
        vault_path = self.obsidian_bridge.export_mission_summary(mission_id)

        # Store episodic memory
        mission = status['mission']
        self.memory_service.store_memory(
            memory_type="episodic",
            scope="session",
            title=f"Mission: {mission['title']}",
            content=f"Completed mission with {len(status['steps'])} steps. Cost: ${mission['total_cost']:.2f}",
            project_id=mission.get('project_id'),
            confidence=1.0
        )

        return {
            "mission_id": mission_id,
            "status": "completed",
            "cost": mission['total_cost'],
            "steps": len(status['steps']),
            "vault_export": str(vault_path)
        }

    def handle_mission_failure(self, mission_id: str, reason: str) -> Dict[str, Any]:
        """Handle mission failure"""
        self.mission_manager.transition_state(mission_id, "failed")

        # Log failure event
        self.mission_manager.log_mission_event(
            mission_id,
            "supervisor",
            "mission_failed",
            {"reason": reason}
        )

        # Export failure analysis to vault
        vault_path = self.obsidian_bridge.export_mission_summary(mission_id)

        return {
            "mission_id": mission_id,
            "status": "failed",
            "reason": reason,
            "vault_export": str(vault_path)
        }

    def get_mission_progress(self, mission_id: str) -> Dict[str, Any]:
        """Get current mission progress"""
        status = self.mission_manager.get_mission_status(mission_id)

        return {
            "mission_id": mission_id,
            "title": status['mission']['title'],
            "status": status['mission']['status'],
            "progress_percentage": status['progress']['percentage'],
            "completed_steps": status['progress']['completed'],
            "total_steps": status['progress']['total_steps'],
            "cost_used": status['budget']['used'],
            "cost_limit": status['budget']['limit']
        }

    def enforce_budget_limits(self, mission_id: str) -> bool:
        """Check if mission is within budget limits"""
        status = self.mission_manager.get_mission_status(mission_id)

        if status['budget']['remaining'] < 0:
            self.handle_mission_failure(
                mission_id,
                f"Budget exceeded: ${status['budget']['used']:.2f} / ${status['budget']['limit']:.2f}"
            )
            return False

        # Warn if approaching limit (90%)
        if status['budget']['used'] / status['budget']['limit'] > 0.9:
            print(f"⚠️  Budget warning: {status['budget']['used']:.2f} / {status['budget']['limit']:.2f}")

        return True

    def close(self):
        """Close all service connections"""
        self.mission_manager.close()
        self.memory_service.close()
        self.obsidian_bridge.close()


# Example workflow
if __name__ == "__main__":
    supervisor = Supervisor()

    # Detect work mode activation
    user_input = "let's get a job done - implement JWT authentication"

    if supervisor.detect_work_mode_activation(user_input):
        print("✓ Work mode activated")

        # Create mission
        mission = supervisor.create_mission_from_user_input(
            user_goal="Implement JWT authentication for the API",
            project_id="ergo",
            budget_limit=5.0
        )

        print(f"✓ Mission created: {mission['mission_id']}")

        # Plan mission
        plan = supervisor.plan_mission(mission['mission_id'], mission['title'])
        print(f"✓ Plan created with {len(plan['steps'])} steps")

        # Request approval
        approval_request = supervisor.request_approval(mission['mission_id'])
        print(f"✓ Awaiting approval...")

        # Approve and execute (in real scenario, user would approve)
        supervisor.approve_mission(mission['mission_id'])
        print(f"✓ Mission approved")

        # Execute mission
        results = supervisor.execute_mission(mission['mission_id'])
        print(f"✓ Executed {results['steps_executed']} steps")

        # Complete mission
        completion = supervisor.complete_mission(mission['mission_id'])
        print(f"✓ Mission completed")
        print(f"  Cost: ${completion['cost']:.2f}")
        print(f"  Exported to: {completion['vault_export']}")

    supervisor.close()
