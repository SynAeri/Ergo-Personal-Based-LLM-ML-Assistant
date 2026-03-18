// SQLite database operations for Ergo

use rusqlite::{Connection, Result, params};
use std::path::PathBuf;
use chrono::{Local};

pub struct Database {
    conn: Connection,
}

impl Database {
    /// Create or open database at specified path
    pub fn new(db_path: &PathBuf) -> Result<Self> {
        // Ensure parent dir existant
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent)
                .expect("Failed to create database directory");
        }
        
        let conn = Connection::open(db_path)?;
        
        // Create tables if they don't exist
        conn.execute(
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
        
        conn.execute(
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
        
        // Create index for faster queries
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp 
             ON activity_log(timestamp)",
            [],
        )?;
        
        Ok(Database { conn })
    }
    
    /// Get default database path
    pub fn default_path() -> PathBuf {
        let mut path = dirs::home_dir()
            .expect("Could not find home directory");
        path.push(".local/share/ergo");
        path.push("activity.db");
        path
    }
    
    /// Log a window observation
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
    
    /// Update duration for the last activity entry
    pub fn update_last_duration(&self, duration: i64) -> Result<()> {
        self.conn.execute(
            "UPDATE activity_log 
             SET duration = ?1
             WHERE id = (SELECT MAX(id) FROM activity_log)",
            params![duration],
        )?;
        Ok(())
    }
    
    /// Get activity for the last N hours
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
    
    /// Get statistics for today
    pub fn get_today_stats(&self) -> Result<DailyStats> {
        let today_start = Local::now()
            .date_naive()
            .and_hms_opt(0, 0, 0)
            .unwrap()
            .and_local_timezone(Local)
            .unwrap()
            .timestamp();
        
        // Total tracked time
        let total_seconds: i64 = self.conn.query_row(
            "SELECT COALESCE(SUM(duration), 0)
             FROM activity_log
             WHERE timestamp >= ?1 AND ignored = 0",
            params![today_start],
            |row| row.get(0),
        )?;
        
        // Number of context switches
        let context_switches: i64 = self.conn.query_row(
            "SELECT COUNT(*)
             FROM activity_log
             WHERE timestamp >= ?1",
            params![today_start],
            |row| row.get(0),
        )?;
        
        // Most used app
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
    
    /// Detect if user is stuck on same window
    pub fn detect_stuck_pattern(&self, minutes: i64) -> Result<Option<String>> {
        let cutoff = Local::now().timestamp() - (minutes * 60);
        
        // Get recent entries for same window
        // ToDo: Add Potentially more checks for these tables
        let count: i64 = self.conn.query_row(
            "SELECT COUNT(DISTINCT window_title)
             FROM activity_log
             WHERE timestamp > ?1 AND ignored = 0",
            params![cutoff],
            |row| row.get(0),
        )?;
        
        // If only 1 unique window in last N minutes = stuck
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
    
    /// Log a detected pattern
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

// Data structures for query results

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
