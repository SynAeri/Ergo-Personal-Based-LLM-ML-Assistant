"""
Memory Service for Ergo Work Mode
Handles CRUD operations for the four-category memory system
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path


class MemoryService:
    """Manages episodic, semantic, procedural, and personality memories"""

    def __init__(self, db_path: str = "~/ergo/runtime/missions.db"):
        self.db_path = Path(db_path).expanduser()
        self._init_connection()

    def _init_connection(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows

    def store_memory(
        self,
        memory_type: str,  # 'episodic', 'semantic', 'procedural', 'personality'
        scope: str,  # 'user', 'project', 'session', 'global'
        title: str,
        content: str,
        project_id: Optional[str] = None,
        confidence: float = 1.0
    ) -> str:
        """Store a memory and return its ID"""
        memory_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO memories
            (memory_id, memory_type, scope, project_id, title, content, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (memory_id, memory_type, scope, project_id, title, content, confidence, now, now))

        self.conn.commit()
        return memory_id

    def retrieve_memory(
        self,
        memory_type: Optional[str] = None,
        scope: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 10,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Retrieve memories matching criteria"""
        query = "SELECT * FROM memories WHERE confidence >= ?"
        params = [min_confidence]

        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)

        if scope:
            query += " AND scope = ?"
            params.append(scope)

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        # Convert rows to dicts and update access tracking
        memories = [dict(row) for row in cursor.fetchall()]

        # Update access count and timestamp
        for memory in memories:
            self._update_access(memory['memory_id'])

        return memories

    def update_memory_confidence(self, memory_id: str, new_confidence: float):
        """Update confidence score for a memory"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memories
            SET confidence = ?, updated_at = ?
            WHERE memory_id = ?
        """, (new_confidence, datetime.now().isoformat(), memory_id))

        self.conn.commit()

    def _update_access(self, memory_id: str):
        """Update access tracking for a memory"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE memories
            SET accessed_count = accessed_count + 1,
                last_accessed = ?
            WHERE memory_id = ?
        """, (datetime.now().isoformat(), memory_id))

        self.conn.commit()

    def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Full-text search across memories"""
        sql = """
            SELECT * FROM memories
            WHERE (title LIKE ? OR content LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]

        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)

        sql += " ORDER BY confidence DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(sql, params)

        return [dict(row) for row in cursor.fetchall()]

    def get_recent_memories(
        self,
        window_minutes: int = 90,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get memories from recent time window (ephemeral context)"""
        cutoff = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()

        query = "SELECT * FROM memories WHERE updated_at >= ?"
        params = [cutoff]

        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)

        query += " ORDER BY updated_at DESC"

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def delete_memory(self, memory_id: str):
        """Delete a memory (use sparingly)"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
        self.conn.commit()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        cursor = self.conn.cursor()

        stats = {}

        # Count by type
        cursor.execute("""
            SELECT memory_type, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM memories
            GROUP BY memory_type
        """)
        stats['by_type'] = [dict(row) for row in cursor.fetchall()]

        # Count by scope
        cursor.execute("""
            SELECT scope, COUNT(*) as count
            FROM memories
            GROUP BY scope
        """)
        stats['by_scope'] = [dict(row) for row in cursor.fetchall()]

        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM memories")
        stats['total'] = cursor.fetchone()['total']

        return stats

    def decay_confidence(self, decay_rate: float = 0.01):
        """Apply confidence decay to old memories (run periodically)"""
        cursor = self.conn.cursor()

        # Decay confidence for memories not accessed in last month
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()

        cursor.execute("""
            UPDATE memories
            SET confidence = MAX(0.1, confidence - ?),
                updated_at = ?
            WHERE last_accessed < ? OR last_accessed IS NULL
        """, (decay_rate, datetime.now().isoformat(), cutoff))

        self.conn.commit()

        return cursor.rowcount

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    service = MemoryService()

    # Store a semantic memory
    memory_id = service.store_memory(
        memory_type="semantic",
        scope="project",
        title="JWT Authentication Pattern",
        content="Uses jsonwebtoken crate with 15min access tokens and 7-day refresh tokens",
        project_id="ergo",
        confidence=0.95
    )

    print(f"Stored memory: {memory_id}")

    # Retrieve project memories
    memories = service.retrieve_memory(
        memory_type="semantic",
        scope="project",
        project_id="ergo"
    )

    print(f"Found {len(memories)} memories")

    # Get stats
    stats = service.get_memory_stats()
    print(f"Memory stats: {stats}")

    service.close()
