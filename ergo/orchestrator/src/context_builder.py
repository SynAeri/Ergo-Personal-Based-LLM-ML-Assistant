"""
Context builder for assembling relevant information for model prompts
Pulls from ephemeral, working, and long-term memory layers
"""

import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

from .config import settings

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds context from multiple memory layers"""

    def __init__(self):
        self.db_path = Path(settings.sqlite_path).expanduser()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))

    async def build_chat_context(self, project_id: Optional[str] = None) -> str:
        """
        Build full context for a chat request
        Combines ephemeral, working, and relevant long-term memory
        """
        parts = []

        # Add ephemeral context (last N minutes)
        ephemeral = await self.get_recent_context(
            settings.ephemeral_context_minutes
        )
        if ephemeral:
            parts.append("## Recent Activity\n" + ephemeral)

        # Add working memory (current session)
        working = await self.get_working_memory()
        if working:
            parts.append("## Current Session\n" + working)

        # Add relevant long-term memories
        if project_id:
            long_term = await self.get_project_memories(project_id)
            if long_term:
                parts.append("## Project Context\n" + long_term)

        return "\n\n".join(parts)

    async def get_recent_context(self, minutes: int) -> str:
        """
        Get ephemeral context - last N minutes of activity
        Returns formatted string of recent events
        """
        cutoff_ts = int((datetime.now() - timedelta(minutes=minutes)).timestamp())

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get recent events
            cursor.execute(
                """
                SELECT timestamp, source, event_type, payload_json
                FROM events
                WHERE timestamp > ? AND privacy_tag != '"ignore"'
                ORDER BY timestamp DESC
                LIMIT 50
                """,
                (cutoff_ts,),
            )

            events = cursor.fetchall()

            if not events:
                return ""

            # Format events into readable context
            lines = []
            for ts, source, event_type, payload_str in events:
                try:
                    payload = json.loads(payload_str)
                    dt = datetime.fromtimestamp(ts)
                    time_str = dt.strftime("%H:%M")

                    # Format based on event type
                    if "window.focus" in event_type:
                        lines.append(
                            f"[{time_str}] Switched to: {payload.get('window_title', 'unknown')}"
                        )
                    elif "nvim.buffer" in event_type:
                        lines.append(
                            f"[{time_str}] Editing: {payload.get('file_path', 'unknown')}"
                        )
                    elif "build" in event_type:
                        status = "succeeded" if payload.get("success") else "failed"
                        lines.append(
                            f"[{time_str}] Build {status}: {payload.get('build_type', 'unknown')}"
                        )
                    elif "git.status" in event_type:
                        lines.append(
                            f"[{time_str}] Git: {payload.get('branch', 'unknown')} ({payload.get('modified_files', 0)} modified)"
                        )

                except Exception as e:
                    logger.warning(f"Error formatting event: {e}")
                    continue

            return "\n".join(lines[:20])  # Limit to 20 most recent

        finally:
            conn.close()

    async def get_working_memory(self) -> str:
        """
        Get working memory - current session/task block
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get active session
            cursor.execute(
                """
                SELECT session_id, start_time, project_id
                FROM sessions
                WHERE end_time IS NULL
                ORDER BY start_time DESC
                LIMIT 1
                """
            )

            session = cursor.fetchone()
            if not session:
                return ""

            session_id, start_time, project_id = session
            start_dt = datetime.fromtimestamp(start_time)
            duration = datetime.now() - start_dt

            parts = [
                f"Active session: {duration.seconds // 60} minutes",
                f"Started at: {start_dt.strftime('%H:%M')}",
            ]

            if project_id:
                parts.append(f"Project: {project_id}")

            # Get session stats
            cursor.execute(
                """
                SELECT COUNT(*) as event_count,
                       COUNT(DISTINCT source) as unique_sources
                FROM events
                WHERE timestamp > ?
                """,
                (start_time,),
            )

            stats = cursor.fetchone()
            if stats:
                parts.append(
                    f"Activity: {stats[0]} events from {stats[1]} sources"
                )

            return "\n".join(parts)

        finally:
            conn.close()

    async def get_project_memories(self, project_id: str) -> str:
        """
        Get long-term memories relevant to a project
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT memory_type, key, value
                FROM memories
                WHERE project_id = ? OR project_id IS NULL
                ORDER BY access_count DESC, last_accessed DESC
                LIMIT 20
                """,
                (project_id,),
            )

            memories = cursor.fetchall()
            if not memories:
                return ""

            lines = []
            for mem_type, key, value in memories:
                lines.append(f"- {mem_type}.{key}: {value}")

            return "\n".join(lines)

        finally:
            conn.close()

    async def get_style_profile(self) -> Dict[str, Any]:
        """
        Get user's coding style profile
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT category, pattern, frequency
                FROM style_profiles
                ORDER BY frequency DESC
                LIMIT 50
                """
            )

            profiles = cursor.fetchall()
            if not profiles:
                return {}

            # Group by category
            style_dict = {}
            for category, pattern, frequency in profiles:
                if category not in style_dict:
                    style_dict[category] = []
                style_dict[category].append(
                    {"pattern": pattern, "frequency": frequency}
                )

            return style_dict

        finally:
            conn.close()

    async def get_recent_errors(self, limit: int = 10) -> List[str]:
        """
        Get recent build/test errors for debugging context
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT payload_json
                FROM events
                WHERE event_type = 'build.failed'
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )

            events = cursor.fetchall()
            errors = []

            for (payload_str,) in events:
                try:
                    payload = json.loads(payload_str)
                    error_list = payload.get("errors", [])
                    errors.extend(error_list)
                except:
                    continue

            return errors

        finally:
            conn.close()
