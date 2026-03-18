// Enhanced SQLite database operations for Ergo
// Implements full memory architecture: events, sessions, memories, summaries, interventions

use rusqlite::{Connection, Result, params, OptionalExtension};
use std::path::PathBuf;
use chrono::Local;
use uuid::Uuid;
use crate::models::*;

pub struct Database {
    conn: Connection,
}

impl Database {
    /// Create or open database with full schema
    pub fn new(db_path: &PathBuf) -> Result<Self> {
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent)
                .expect("Failed to create database directory");
        }

        let conn = Connection::open(db_path)?;

        let db = Database { conn };
        db.initialize_schema()?;

        Ok(db)
    }

    /// Initialize all tables for the full memory architecture
    fn initialize_schema(&self) -> Result<()> {
        // Core events table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                project_id TEXT,
                privacy_tag TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )",
            [],
        )?;

        // Projects table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                repo_path TEXT,
                tags TEXT,
                last_active INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )",
            [],
        )?;

        // Sessions table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS sessions (
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
            )",
            [],
        )?;

        // Long-term structured memories table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS memories (
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
            )",
            [],
        )?;

        // Session summaries table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS summaries (
                summary_id TEXT PRIMARY KEY,
                session_id TEXT,
                summary_type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )",
            [],
        )?;

        // Style profiles table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS style_profiles (
                profile_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                pattern TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )",
            [],
        )?;

        // Interventions table
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS interventions (
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
            )",
            [],
        )?;

        // Artifacts table (screenshots, audio, etc.)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                artifact_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                event_id TEXT,
                session_id TEXT,
                metadata_json TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (event_id) REFERENCES events(event_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )",
            [],
        )?;

        // Legacy activity_log table for compatibility
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                window_title TEXT NOT NULL,
                process_name TEXT NOT NULL,
                duration INTEGER DEFAULT 0,
                ignored BOOLEAN DEFAULT 0
            )",
            [],
        )?;

        // Legacy patterns table for compatibility
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT,
                window_title TEXT,
                process_name TEXT
            )",
            [],
        )?;

        // Create indices
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_project ON events(project_id)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_start ON sessions(start_time)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_type_key ON memories(memory_type, key)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_interventions_timestamp ON interventions(timestamp)",
            [],
        )?;

        Ok(())
    }

    /// Get default database path
    pub fn default_path() -> PathBuf {
        let mut path = dirs::home_dir()
            .expect("Could not find home directory");
        path.push(".local/share/ergo");
        path.push("activity.db");
        path
    }

    // ========================================================================
    // EVENT OPERATIONS
    // ========================================================================

    /// Insert a normalized event
    pub fn insert_event(&self, event: &Event) -> Result<()> {
        self.conn.execute(
            "INSERT INTO events
             (event_id, timestamp, source, event_type, project_id, privacy_tag, payload_json, confidence)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                event.event_id.to_string(),
                event.timestamp,
                serde_json::to_string(&event.source).unwrap(),
                event.event_type,
                event.project_id,
                serde_json::to_string(&event.privacy_tag).unwrap(),
                serde_json::to_string(&event.payload).unwrap(),
                event.confidence,
            ],
        )?;
        Ok(())
    }

    /// Get recent events (ephemeral context)
    pub fn get_recent_events(&self, minutes: i64) -> Result<Vec<Event>> {
        let cutoff = Local::now().timestamp() - (minutes * 60);

        let mut stmt = self.conn.prepare(
            "SELECT event_id, timestamp, source, event_type, project_id, privacy_tag, payload_json, confidence
             FROM events
             WHERE timestamp > ?1 AND privacy_tag != '\"ignore\"'
             ORDER BY timestamp DESC"
        )?;

        let events = stmt.query_map(params![cutoff], |row| {
            Ok(Event {
                event_id: Uuid::parse_str(&row.get::<_, String>(0)?).unwrap(),
                timestamp: row.get(1)?,
                source: serde_json::from_str(&row.get::<_, String>(2)?).unwrap(),
                event_type: row.get(3)?,
                project_id: row.get(4)?,
                privacy_tag: serde_json::from_str(&row.get::<_, String>(5)?).unwrap(),
                payload: serde_json::from_str(&row.get::<_, String>(6)?).unwrap(),
                confidence: row.get(7)?,
            })
        })?;

        events.collect()
    }

    // ========================================================================
    // SESSION OPERATIONS
    // ========================================================================

    /// Create a new session
    pub fn create_session(&self, project_id: Option<String>) -> Result<Uuid> {
        let session_id = Uuid::new_v4();
        let now = Local::now().timestamp();

        self.conn.execute(
            "INSERT INTO sessions (session_id, start_time, project_id)
             VALUES (?1, ?2, ?3)",
            params![session_id.to_string(), now, project_id],
        )?;

        Ok(session_id)
    }

    /// End a session and add summary
    pub fn end_session(
        &self,
        session_id: Uuid,
        summary: SessionSummary,
    ) -> Result<()> {
        self.conn.execute(
            "UPDATE sessions
             SET end_time = ?1,
                 summary_text = ?2,
                 key_activities = ?3,
                 context_switches = ?4,
                 focus_time_seconds = ?5
             WHERE session_id = ?6",
            params![
                summary.end_time,
                summary.summary_text,
                serde_json::to_string(&summary.key_activities).unwrap(),
                summary.context_switches,
                summary.focus_time_seconds,
                session_id.to_string(),
            ],
        )?;

        Ok(())
    }

    /// Get current active session
    pub fn get_active_session(&self) -> Result<Option<Uuid>> {
        self.conn.query_row(
            "SELECT session_id FROM sessions
             WHERE end_time IS NULL
             ORDER BY start_time DESC
             LIMIT 1",
            [],
            |row| {
                let session_str: String = row.get(0)?;
                Ok(Uuid::parse_str(&session_str).unwrap())
            },
        ).optional()
    }

    // ========================================================================
    // MEMORY OPERATIONS
    // ========================================================================

    /// Store a long-term memory fact
    pub fn store_memory(
        &self,
        memory_type: &str,
        key: &str,
        value: &str,
        project_id: Option<String>,
    ) -> Result<()> {
        let memory_id = Uuid::new_v4();
        let now = Local::now().timestamp();

        self.conn.execute(
            "INSERT OR REPLACE INTO memories
             (memory_id, memory_type, key, value, project_id, last_accessed)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![memory_id.to_string(), memory_type, key, value, project_id, now],
        )?;

        Ok(())
    }

    /// Retrieve a memory by type and key
    pub fn get_memory(&self, memory_type: &str, key: &str) -> Result<Option<String>> {
        // Update access count and timestamp
        self.conn.execute(
            "UPDATE memories
             SET last_accessed = ?1,
                 access_count = access_count + 1
             WHERE memory_type = ?2 AND key = ?3",
            params![Local::now().timestamp(), memory_type, key],
        )?;

        self.conn.query_row(
            "SELECT value FROM memories
             WHERE memory_type = ?1 AND key = ?2",
            params![memory_type, key],
            |row| row.get(0),
        ).optional()
    }

    // ========================================================================
    // INTERVENTION OPERATIONS
    // ========================================================================

    /// Log an intervention
    pub fn log_intervention(&self, intervention: &Intervention) -> Result<()> {
        self.conn.execute(
            "INSERT INTO interventions
             (intervention_id, timestamp, intervention_type, description, severity, confidence, context_json, acknowledged)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                intervention.intervention_id.to_string(),
                intervention.timestamp,
                serde_json::to_string(&intervention.intervention_type).unwrap(),
                intervention.description,
                intervention.severity,
                intervention.confidence,
                serde_json::to_string(&intervention.context).unwrap(),
                intervention.acknowledged,
            ],
        )?;

        Ok(())
    }

    /// Get recent unacknowledged interventions
    pub fn get_pending_interventions(&self) -> Result<Vec<Intervention>> {
        let mut stmt = self.conn.prepare(
            "SELECT intervention_id, timestamp, intervention_type, description, severity, confidence, context_json, acknowledged
             FROM interventions
             WHERE acknowledged = 0
             ORDER BY timestamp DESC
             LIMIT 10"
        )?;

        let interventions = stmt.query_map([], |row| {
            Ok(Intervention {
                intervention_id: Uuid::parse_str(&row.get::<_, String>(0)?).unwrap(),
                timestamp: row.get(1)?,
                intervention_type: serde_json::from_str(&row.get::<_, String>(2)?).unwrap(),
                description: row.get(3)?,
                severity: row.get(4)?,
                confidence: row.get(5)?,
                context: serde_json::from_str(&row.get::<_, String>(6)?).unwrap(),
                acknowledged: row.get(7)?,
            })
        })?;

        interventions.collect()
    }

    // ========================================================================
    // LEGACY COMPATIBILITY
    // ========================================================================

    /// Log activity (legacy compatibility)
    pub fn log_activity(
        &self,
        window_title: &str,
        process_name: &str,
        ignored: bool,
    ) -> Result<i64> {
        let timestamp = Local::now().timestamp();

        self.conn.execute(
            "INSERT INTO activity_log
             (timestamp, window_title, process_name, ignored)
             VALUES (?1, ?2, ?3, ?4)",
            params![timestamp, window_title, process_name, ignored],
        )?;

        Ok(self.conn.last_insert_rowid())
    }

    /// Update duration for last activity entry (legacy)
    pub fn update_last_duration(&self, duration: i64) -> Result<()> {
        self.conn.execute(
            "UPDATE activity_log
             SET duration = ?1
             WHERE id = (SELECT MAX(id) FROM activity_log)",
            params![duration],
        )?;
        Ok(())
    }

    /// Get activity for last N hours (legacy)
    pub fn get_recent_activity(&self, hours: i64) -> Result<Vec<ActivityEntry>> {
        let cutoff = Local::now().timestamp() - (hours * 3600);

        let mut stmt = self.conn.prepare(
            "SELECT timestamp, window_title, process_name, duration, ignored
             FROM activity_log
             WHERE timestamp > ?1
             ORDER BY timestamp DESC"
        )?;

        let entries = stmt.query_map(params![cutoff], |row| {
            Ok(ActivityEntry {
                timestamp: row.get(0)?,
                window_title: row.get(1)?,
                process_name: row.get(2)?,
                duration: row.get(3)?,
                ignored: row.get(4)?,
            })
        })?;

        entries.collect()
    }

    /// Get today's statistics (legacy)
    pub fn get_today_stats(&self) -> Result<DailyStats> {
        let today_start = Local::now()
            .date_naive()
            .and_hms_opt(0, 0, 0)
            .unwrap()
            .and_local_timezone(Local)
            .unwrap()
            .timestamp();

        let total_seconds: i64 = self.conn.query_row(
            "SELECT COALESCE(SUM(duration), 0)
             FROM activity_log
             WHERE timestamp >= ?1 AND ignored = 0",
            params![today_start],
            |row| row.get(0),
        )?;

        let context_switches: i64 = self.conn.query_row(
            "SELECT COUNT(*)
             FROM activity_log
             WHERE timestamp >= ?1",
            params![today_start],
            |row| row.get(0),
        )?;

        let most_used_app: String = self.conn.query_row(
            "SELECT process_name
             FROM activity_log
             WHERE timestamp >= ?1 AND ignored = 0
             GROUP BY process_name
             ORDER BY SUM(duration) DESC
             LIMIT 1",
            params![today_start],
            |row| row.get(0),
        ).unwrap_or_else(|_| "none".to_string());

        Ok(DailyStats {
            total_seconds,
            context_switches,
            most_used_app,
        })
    }

    /// Detect stuck pattern (legacy)
    pub fn detect_stuck_pattern(&self, minutes: i64) -> Result<Option<String>> {
        let cutoff = Local::now().timestamp() - (minutes * 60);

        let count: i64 = self.conn.query_row(
            "SELECT COUNT(DISTINCT window_title)
             FROM activity_log
             WHERE timestamp > ?1 AND ignored = 0",
            params![cutoff],
            |row| row.get(0),
        )?;

        if count == 1 {
            let window: String = self.conn.query_row(
                "SELECT window_title
                 FROM activity_log
                 WHERE timestamp > ?1 AND ignored = 0
                 LIMIT 1",
                params![cutoff],
                |row| row.get(0),
            )?;

            Ok(Some(window))
        } else {
            Ok(None)
        }
    }

    /// Log pattern (legacy)
    pub fn log_pattern(
        &self,
        pattern_type: &str,
        description: &str,
        window_title: Option<&str>,
        process_name: Option<&str>,
    ) -> Result<()> {
        let timestamp = Local::now().timestamp();

        self.conn.execute(
            "INSERT INTO patterns
             (timestamp, pattern_type, description, window_title, process_name)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            params![
                timestamp,
                pattern_type,
                description,
                window_title,
                process_name
            ],
        )?;

        Ok(())
    }
}

// Legacy data structures for compatibility

#[derive(Debug)]
pub struct ActivityEntry {
    pub timestamp: i64,
    pub window_title: String,
    pub process_name: String,
    pub duration: i64,
    pub ignored: bool,
}

#[derive(Debug)]
pub struct DailyStats {
    pub total_seconds: i64,
    pub context_switches: i64,
    pub most_used_app: String,
}
