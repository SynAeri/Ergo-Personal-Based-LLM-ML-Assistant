"""
Mission Manager for Ergo Work Mode
Implements the mission state machine and manages mission lifecycle
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class MissionManager:
    """Manages mission lifecycle and state transitions"""

    VALID_STATES = [
        "created", "scoping", "decomposed", "waiting_for_approval",
        "running", "blocked", "awaiting_input", "review",
        "completed", "failed", "archived"
    ]

    VALID_TRANSITIONS = {
        "created": ["scoping", "archived"],
        "scoping": ["decomposed", "awaiting_input", "failed"],
        "decomposed": ["waiting_for_approval", "running", "failed"],
        "waiting_for_approval": ["running", "decomposed", "archived"],
        "running": ["blocked", "awaiting_input", "review", "failed"],
        "blocked": ["running", "awaiting_input", "failed", "archived"],
        "awaiting_input": ["running", "failed", "archived"],
        "review": ["completed", "running", "failed"],
        "completed": ["archived"],
        "failed": ["archived", "decomposed"],
        "archived": []
    }

    def __init__(self, db_path: str = "~/ergo/runtime/missions.db"):
        self.db_path = Path(db_path).expanduser()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def create_mission(
        self,
        title: str,
        goal: str,
        mode: str = "work",  # 'chat', 'deliberation', 'work'
        project_id: Optional[str] = None,
        budget_limit: float = 10.0,
        token_limit: int = 100000,
        max_iterations: int = 10
    ) -> str:
        """Create a new mission and return its ID"""
        mission_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO missions (
                mission_id, title, goal, mode, status, project_id,
                budget_limit, total_cost, token_limit, max_iterations,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mission_id, title, goal, mode, "created", project_id,
            budget_limit, 0.0, token_limit, max_iterations, now, now
        ))

        self.conn.commit()

        # Log creation event
        self.log_mission_event(mission_id, "supervisor", "mission_created", {
            "title": title,
            "mode": mode
        })

        # Auto-transition to scoping
        self.transition_state(mission_id, "scoping")

        return mission_id

    def transition_state(self, mission_id: str, new_state: str) -> bool:
        """Transition mission to new state if valid"""
        if new_state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {new_state}")

        # Get current state
        mission = self.get_mission(mission_id)
        current_state = mission['status']

        # Check if transition is valid
        if new_state not in self.VALID_TRANSITIONS[current_state]:
            raise ValueError(
                f"Invalid transition from {current_state} to {new_state}"
            )

        # Perform transition
        cursor = self.conn.cursor()
        update_data = {
            "status": new_state,
            "updated_at": datetime.now().isoformat()
        }

        # Set completed_at timestamp if completing or failing
        if new_state in ["completed", "failed"]:
            update_data["completed_at"] = datetime.now().isoformat()

        cursor.execute("""
            UPDATE missions
            SET status = ?, updated_at = ?, completed_at = ?
            WHERE mission_id = ?
        """, (
            update_data["status"],
            update_data["updated_at"],
            update_data.get("completed_at"),
            mission_id
        ))

        self.conn.commit()

        # Log transition event
        self.log_mission_event(mission_id, "supervisor", "state_transition", {
            "from": current_state,
            "to": new_state
        })

        return True

    def add_mission_step(
        self,
        mission_id: str,
        role: str,
        objective: str,
        input_context: Optional[Dict] = None
    ) -> str:
        """Add a step to a mission"""
        step_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mission_steps (
                step_id, mission_id, role_name, objective, status,
                input_context
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            step_id, mission_id, role, objective, "pending",
            json.dumps(input_context or {})
        ))

        self.conn.commit()

        return step_id

    def start_mission_step(self, step_id: str):
        """Mark a step as started"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mission_steps
            SET status = 'running', started_at = ?
            WHERE step_id = ?
        """, (datetime.now().isoformat(), step_id))

        self.conn.commit()

    def complete_mission_step(
        self,
        step_id: str,
        output_summary: str,
        cost: float = 0.0,
        tool_calls: Optional[List[Dict]] = None,
        review_status: str = "approved"
    ):
        """Mark a step as completed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mission_steps
            SET status = 'completed',
                completed_at = ?,
                output_summary = ?,
                cost_estimate = ?,
                tool_calls = ?,
                review_status = ?
            WHERE step_id = ?
        """, (
            datetime.now().isoformat(),
            output_summary,
            cost,
            json.dumps(tool_calls or []),
            review_status,
            step_id
        ))

        self.conn.commit()

        # Update mission total cost
        step = self.get_step(step_id)
        mission_id = step['mission_id']
        self._update_mission_cost(mission_id, cost)

    def fail_mission_step(self, step_id: str, error: str):
        """Mark a step as failed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mission_steps
            SET status = 'failed', completed_at = ?, output_summary = ?
            WHERE step_id = ?
        """, (datetime.now().isoformat(), f"ERROR: {error}", step_id))

        self.conn.commit()

    def _update_mission_cost(self, mission_id: str, additional_cost: float):
        """Update total cost for a mission"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE missions
            SET total_cost = total_cost + ?
            WHERE mission_id = ?
        """, (additional_cost, mission_id))

        self.conn.commit()

    def log_mission_event(
        self,
        mission_id: str,
        source: str,
        event_type: str,
        payload: Dict
    ):
        """Log an event for a mission"""
        event_id = str(uuid.uuid4())

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mission_events (event_id, mission_id, source, event_type, payload_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id, mission_id, source, event_type,
            json.dumps(payload), datetime.now().isoformat()
        ))

        self.conn.commit()

    def get_mission(self, mission_id: str) -> Dict[str, Any]:
        """Get mission by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Mission not found: {mission_id}")

        return dict(row)

    def get_step(self, step_id: str) -> Dict[str, Any]:
        """Get step by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mission_steps WHERE step_id = ?", (step_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Step not found: {step_id}")

        return dict(row)

    def get_mission_steps(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get all steps for a mission"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mission_steps WHERE mission_id = ? ORDER BY started_at",
            (mission_id,)
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_mission_events(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get all events for a mission"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM mission_events WHERE mission_id = ? ORDER BY timestamp",
            (mission_id,)
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_active_missions(self) -> List[Dict[str, Any]]:
        """Get all active (non-completed) missions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM missions
            WHERE status NOT IN ('completed', 'failed', 'archived')
            ORDER BY created_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get detailed mission status"""
        mission = self.get_mission(mission_id)
        steps = self.get_mission_steps(mission_id)

        total_steps = len(steps)
        completed_steps = len([s for s in steps if s['status'] == 'completed'])
        failed_steps = len([s for s in steps if s['status'] == 'failed'])

        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        return {
            "mission": mission,
            "steps": steps,
            "progress": {
                "total_steps": total_steps,
                "completed": completed_steps,
                "failed": failed_steps,
                "percentage": round(progress, 1)
            },
            "budget": {
                "used": mission['total_cost'],
                "limit": mission.get('budget_limit', 0),
                "remaining": mission.get('budget_limit', 0) - mission['total_cost']
            }
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    manager = MissionManager()

    # Create a mission
    mission_id = manager.create_mission(
        title="Implement JWT Authentication",
        goal="Add JWT-based authentication to the API",
        mode="work",
        project_id="ergo",
        budget_limit=5.0
    )

    print(f"Created mission: {mission_id}")

    # Add steps
    step1 = manager.add_mission_step(
        mission_id,
        "planner",
        "Decompose authentication requirements"
    )

    step2 = manager.add_mission_step(
        mission_id,
        "mage",
        "Design auth architecture"
    )

    print(f"Added {len(manager.get_mission_steps(mission_id))} steps")

    # Get status
    status = manager.get_mission_status(mission_id)
    print(f"Mission progress: {status['progress']['percentage']}%")

    manager.close()
