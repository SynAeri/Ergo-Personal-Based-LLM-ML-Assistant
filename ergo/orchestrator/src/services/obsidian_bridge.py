"""
Obsidian Bridge for Ergo Work Mode
Exports memories and mission summaries to Obsidian vault
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json


class ObsidianBridge:
    """Manages exports from database to Obsidian vault"""

    def __init__(
        self,
        db_path: str = "~/ergo/runtime/missions.db",
        vault_path: str = "~/ergo/vault"
    ):
        self.db_path = Path(db_path).expanduser()
        self.vault_path = Path(vault_path).expanduser()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def export_mission_summary(self, mission_id: str) -> Path:
        """Export mission summary to vault/missions/"""
        cursor = self.conn.cursor()

        # Get mission data
        cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
        mission = dict(cursor.fetchone())

        # Get mission steps
        cursor.execute(
            "SELECT * FROM mission_steps WHERE mission_id = ? ORDER BY started_at",
            (mission_id,)
        )
        steps = [dict(row) for row in cursor.fetchall()]

        # Generate markdown
        md = self._generate_mission_markdown(mission, steps)

        # Write to vault
        missions_dir = self.vault_path / "missions"
        missions_dir.mkdir(exist_ok=True)

        file_path = missions_dir / f"mission-{mission_id[:8]}.md"
        file_path.write_text(md)

        # Track export in database
        self._track_export(mission_id, str(file_path), "mission_summary")

        return file_path

    def _generate_mission_markdown(self, mission: Dict, steps: list) -> str:
        """Generate markdown for mission summary"""
        md = f"""# Mission: {mission['title']}

**ID**: {mission['mission_id']}
**Status**: {mission['status']}
**Created**: {mission['created_at']}
**Completed**: {mission.get('completed_at', 'In Progress')}
**Cost**: ${mission.get('total_cost', 0):.2f}

## Objective

{mission['goal']}

## Approach

Mode: {mission['mode']}
Budget Limit: ${mission.get('budget_limit', 0):.2f}
Token Limit: {mission.get('token_limit', 'N/A')}

## Steps Executed

"""
        for i, step in enumerate(steps, 1):
            md += f"""### Step {i}: {step['role_name'].title()}
**Objective**: {step['objective']}
**Status**: {step['status']}
**Started**: {step.get('started_at', 'N/A')}
**Completed**: {step.get('completed_at', 'N/A')}

"""
            if step.get('output_summary'):
                md += f"{step['output_summary']}\n\n"

        md += f"""## Results

**Status**: {mission['status']}
**Total Cost**: ${mission.get('total_cost', 0):.2f}

## Tags

#mission #{mission['mode']} #status-{mission['status']}
"""

        if mission.get('project_id'):
            md += f"#project-{mission['project_id']}\n"

        return md

    def export_session_summary(self, date: str, content: str) -> Path:
        """Export session summary to vault/sessions/"""
        sessions_dir = self.vault_path / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        file_path = sessions_dir / f"{date}.md"
        file_path.write_text(content)

        return file_path

    def export_memory_to_vault(self, memory_id: str) -> Optional[Path]:
        """Export a memory to appropriate vault location"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,))

        row = cursor.fetchone()
        if not row:
            return None

        memory = dict(row)

        # Determine export location based on memory type
        if memory['memory_type'] == 'semantic' and memory['scope'] == 'project':
            return self._export_to_project_notes(memory)
        elif memory['memory_type'] == 'procedural':
            return self._export_to_procedures(memory)
        elif memory['memory_type'] == 'personality':
            return self._export_to_personality(memory)
        else:
            return self._export_to_general(memory)

    def _export_to_project_notes(self, memory: Dict) -> Path:
        """Export to projects/{project_id}/"""
        project_id = memory.get('project_id', 'unknown')
        project_dir = self.vault_path / "projects" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        file_path = project_dir / f"{memory['title'].lower().replace(' ', '-')}.md"

        md = f"""# {memory['title']}

**Type**: {memory['memory_type']}
**Confidence**: {memory['confidence']}
**Last Updated**: {memory['updated_at']}

## Content

{memory['content']}

## Metadata

- Created: {memory['created_at']}
- Accessed: {memory.get('accessed_count', 0)} times
- Last Access: {memory.get('last_accessed', 'Never')}

#memory #{memory['memory_type']} #project-{project_id}
"""

        file_path.write_text(md)
        return file_path

    def _export_to_procedures(self, memory: Dict) -> Path:
        """Export to procedures/"""
        procedures_dir = self.vault_path / "procedures"
        procedures_dir.mkdir(exist_ok=True)

        file_path = procedures_dir / f"{memory['title'].lower().replace(' ', '-')}.md"

        md = f"""# {memory['title']}

**Type**: Procedural Memory
**Confidence**: {memory['confidence']}

## Rule

{memory['content']}

## Metadata

- Created: {memory['created_at']}
- Updated: {memory['updated_at']}

#procedure #rule
"""

        file_path.write_text(md)
        return file_path

    def _export_to_personality(self, memory: Dict) -> Path:
        """Export to personality/"""
        personality_dir = self.vault_path / "personality"
        personality_dir.mkdir(exist_ok=True)

        file_path = personality_dir / f"{memory['title'].lower().replace(' ', '-')}.md"
        file_path.write_text(memory['content'])
        return file_path

    def _export_to_general(self, memory: Dict) -> Path:
        """Export to general/"""
        general_dir = self.vault_path / "general"
        general_dir.mkdir(exist_ok=True)

        file_path = general_dir / f"{memory['title'].lower().replace(' ', '-')}.md"

        md = f"""# {memory['title']}

{memory['content']}

---
*Type: {memory['memory_type']} | Confidence: {memory['confidence']}*
"""

        file_path.write_text(md)
        return file_path

    def _track_export(self, mission_id: str, path: str, export_type: str):
        """Track export in database"""
        export_id = f"export-{datetime.now().timestamp()}"
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO vault_exports (export_id, mission_id, path, export_type, created_at, last_synced)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            export_id,
            mission_id,
            path,
            export_type,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        self.conn.commit()

    def sync_all_pending(self):
        """Sync all completed missions that haven't been exported"""
        cursor = self.conn.cursor()

        # Find completed missions without exports
        cursor.execute("""
            SELECT m.mission_id
            FROM missions m
            LEFT JOIN vault_exports ve ON m.mission_id = ve.mission_id
            WHERE m.status IN ('completed', 'failed')
              AND ve.export_id IS NULL
        """)

        mission_ids = [row['mission_id'] for row in cursor.fetchall()]

        exported = []
        for mission_id in mission_ids:
            try:
                path = self.export_mission_summary(mission_id)
                exported.append(str(path))
            except Exception as e:
                print(f"Failed to export {mission_id}: {e}")

        return exported

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    bridge = ObsidianBridge()

    # Sync all pending exports
    exported = bridge.sync_all_pending()
    print(f"Exported {len(exported)} missions to vault")

    bridge.close()
