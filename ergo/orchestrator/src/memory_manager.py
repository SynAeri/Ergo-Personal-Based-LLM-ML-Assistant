"""
Memory manager for Ergo orchestrator
Handles storage and retrieval of events, memories, and summaries
"""

import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import logging
import uuid

from .config import settings

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages long-term structured memory and event processing"""

    def __init__(self):
        self.db_path = Path(settings.sqlite_path).expanduser()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))

    async def process_event(self, event: Dict[str, Any]):
        """
        Process an incoming event
        Store it and update relevant memories
        """
        # Event is already stored by daemon
        # Here we extract higher-level patterns and update memories

        event_type = event.get("event_type", "")
        source = event.get("source", "")
        payload = event.get("payload", {})

        # Update style profiles based on events
        if source == "nvim" and "buffer" in event_type:
            await self._update_style_profile(payload)

        # Update project activity
        if event.get("project_id"):
            await self._update_project_activity(event.get("project_id"))

    async def _update_style_profile(self, nvim_payload: Dict[str, Any]):
        """
        Update coding style profile based on Neovim events
        """
        # Extract language, patterns, etc.
        language = nvim_payload.get("language")
        if not language:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Increment frequency for this language
            cursor.execute(
                """
                INSERT INTO style_profiles (profile_id, category, pattern, frequency, last_seen)
                VALUES (?, 'language', ?, 1, ?)
                ON CONFLICT(profile_id) DO UPDATE SET
                    frequency = frequency + 1,
                    last_seen = ?
                """,
                (
                    str(uuid.uuid4()),
                    language,
                    int(datetime.now().timestamp()),
                    int(datetime.now().timestamp()),
                ),
            )

            conn.commit()

        except Exception as e:
            logger.error(f"Error updating style profile: {e}")
        finally:
            conn.close()

    async def _update_project_activity(self, project_id: str):
        """
        Update last active timestamp for a project
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE projects
                SET last_active = ?
                WHERE project_id = ?
                """,
                (int(datetime.now().timestamp()), project_id),
            )

            conn.commit()

        except Exception as e:
            logger.error(f"Error updating project activity: {e}")
        finally:
            conn.close()

    async def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a session
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get session start time
            cursor.execute(
                "SELECT start_time FROM sessions WHERE session_id = ?",
                (session_id,),
            )

            row = cursor.fetchone()
            if not row:
                return []

            start_time = row[0]

            # Get events since session start
            cursor.execute(
                """
                SELECT event_id, timestamp, source, event_type, payload_json
                FROM events
                WHERE timestamp >= ? AND privacy_tag != '"ignore"'
                ORDER BY timestamp ASC
                """,
                (start_time,),
            )

            events = []
            for event_id, ts, source, event_type, payload_str in cursor.fetchall():
                try:
                    events.append(
                        {
                            "event_id": event_id,
                            "timestamp": datetime.fromtimestamp(ts).strftime(
                                "%H:%M:%S"
                            ),
                            "source": json.loads(source),
                            "event_type": event_type,
                            "payload": json.loads(payload_str),
                        }
                    )
                except:
                    continue

            return events

        finally:
            conn.close()

    async def store_summary(self, session_id: str, summary_text: str):
        """
        Store a session summary
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            summary_id = str(uuid.uuid4())

            cursor.execute(
                """
                INSERT INTO summaries (summary_id, session_id, summary_type, content)
                VALUES (?, ?, 'session', ?)
                """,
                (summary_id, session_id, summary_text),
            )

            # Also update the session record
            cursor.execute(
                """
                UPDATE sessions
                SET summary_text = ?
                WHERE session_id = ?
                """,
                (summary_text, session_id),
            )

            conn.commit()
            logger.info(f"Stored summary for session {session_id}")

        except Exception as e:
            logger.error(f"Error storing summary: {e}")
            raise
        finally:
            conn.close()

    async def get_memory(
        self, memory_type: str, key: str
    ) -> Optional[str]:
        """
        Retrieve a memory by type and key
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Update access tracking
            now_ts = int(datetime.now().timestamp())

            cursor.execute(
                """
                UPDATE memories
                SET last_accessed = ?,
                    access_count = access_count + 1
                WHERE memory_type = ? AND key = ?
                """,
                (now_ts, memory_type, key),
            )

            conn.commit()

            # Retrieve value
            cursor.execute(
                """
                SELECT value
                FROM memories
                WHERE memory_type = ? AND key = ?
                """,
                (memory_type, key),
            )

            row = cursor.fetchone()
            return row[0] if row else None

        finally:
            conn.close()

    async def store_memory(
        self,
        memory_type: str,
        key: str,
        value: str,
        project_id: Optional[str] = None,
    ):
        """
        Store a long-term memory fact
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            memory_id = str(uuid.uuid4())
            now_ts = int(datetime.now().timestamp())

            cursor.execute(
                """
                INSERT OR REPLACE INTO memories
                (memory_id, memory_type, key, value, project_id, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (memory_id, memory_type, key, value, project_id, now_ts),
            )

            conn.commit()
            logger.info(f"Stored memory: {memory_type}.{key}")

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
        finally:
            conn.close()

    async def get_pending_interventions(self) -> List[Dict[str, Any]]:
        """
        Get unacknowledged interventions
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT intervention_id, timestamp, intervention_type,
                       description, severity, confidence, context_json
                FROM interventions
                WHERE acknowledged = 0
                ORDER BY timestamp DESC
                LIMIT 10
                """
            )

            interventions = []
            for row in cursor.fetchall():
                try:
                    interventions.append(
                        {
                            "intervention_id": row[0],
                            "timestamp": datetime.fromtimestamp(row[1]).isoformat(),
                            "type": json.loads(row[2]),
                            "description": row[3],
                            "severity": row[4],
                            "confidence": row[5],
                            "context": json.loads(row[6]),
                        }
                    )
                except:
                    continue

            return interventions

        finally:
            conn.close()

    async def acknowledge_intervention(self, intervention_id: str, outcome: Optional[str] = None):
        """
        Mark an intervention as acknowledged
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE interventions
                SET acknowledged = 1,
                    outcome = ?
                WHERE intervention_id = ?
                """,
                (outcome, intervention_id),
            )

            conn.commit()
            logger.info(f"Acknowledged intervention {intervention_id}")

        except Exception as e:
            logger.error(f"Error acknowledging intervention: {e}")
            raise
        finally:
            conn.close()
