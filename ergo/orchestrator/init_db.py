"""
Initialize the Ergo SQLite database with required schema
Run this once before starting the orchestrator for the first time
"""

import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from src.config import settings


def initialize_database():
    """Create all required tables and indices"""

    db_path = Path(settings.sqlite_path).expanduser()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Core events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                project_id TEXT,
                privacy_tag TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                repo_path TEXT,
                tags TEXT,
                last_active INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time INTEGER NOT NULL,
                end_time INTEGER,
                project_id TEXT,
                summary_text TEXT,
                key_activities TEXT,
                context_switches INTEGER DEFAULT 0,
                focus_time_seconds INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        # Long-term structured memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                project_id TEXT,
                confidence REAL DEFAULT 1.0,
                last_accessed INTEGER,
                access_count INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)

        # Session summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                summary_id TEXT PRIMARY KEY,
                session_id TEXT,
                summary_type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Style profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS style_profiles (
                profile_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                pattern TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)

        # Interventions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                intervention_id TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                intervention_type TEXT NOT NULL,
                description TEXT NOT NULL,
                severity REAL NOT NULL,
                confidence REAL NOT NULL,
                context_json TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                outcome TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)

        # Artifacts table (screenshots, audio, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                artifact_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                event_id TEXT,
                session_id TEXT,
                metadata_json TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (event_id) REFERENCES events(event_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Create indices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_project ON events(project_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions(start_time)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_type_key ON memories(memory_type, key)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interventions_timestamp ON interventions(timestamp)"
        )

        conn.commit()
        print("✓ Database initialized successfully")

        # Verify tables exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Created {len(tables)} tables: {', '.join(tables)}")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
