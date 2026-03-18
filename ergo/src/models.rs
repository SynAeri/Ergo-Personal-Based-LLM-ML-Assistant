// Data models for Ergo event system and memory architecture
// These structs represent the normalized event format and memory layers

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Privacy tag for events and memory retention
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum PrivacyTag {
    Public,
    Private,
    Ignore,
}

/// Event source identifier
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum EventSource {
    Window,
    Browser,
    Shell,
    Git,
    Build,
    Nvim,
    Voice,
    System,
}

/// Normalized event structure matching the architecture spec
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub event_id: Uuid,
    pub timestamp: i64,
    pub source: EventSource,
    pub event_type: String,
    pub project_id: Option<String>,
    pub privacy_tag: PrivacyTag,
    pub payload: serde_json::Value,
    pub confidence: f64,
}

impl Event {
    pub fn new(
        source: EventSource,
        event_type: String,
        payload: serde_json::Value,
    ) -> Self {
        Event {
            event_id: Uuid::new_v4(),
            timestamp: chrono::Local::now().timestamp(),
            source,
            event_type,
            project_id: None,
            privacy_tag: PrivacyTag::Public,
            payload,
            confidence: 1.0,
        }
    }

    pub fn with_privacy(mut self, tag: PrivacyTag) -> Self {
        self.privacy_tag = tag;
        self
    }

    pub fn with_project(mut self, project_id: String) -> Self {
        self.project_id = Some(project_id);
        self
    }

    pub fn with_confidence(mut self, confidence: f64) -> Self {
        self.confidence = confidence;
        self
    }
}

/// Window focus event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowFocusPayload {
    pub window_title: String,
    pub process_name: String,
    pub duration: i64,
}

/// Browser tab event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrowserTabPayload {
    pub url: String,
    pub title: String,
    pub domain: String,
}

/// Shell command event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShellCommandPayload {
    pub command: String,
    pub exit_code: i32,
    pub duration_ms: i64,
    pub working_dir: String,
}

/// Git status event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GitStatusPayload {
    pub repo_path: String,
    pub branch: String,
    pub modified_files: usize,
    pub untracked_files: usize,
    pub is_dirty: bool,
}

/// Build event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BuildEventPayload {
    pub build_type: String, // "test", "build", "run"
    pub success: bool,
    pub duration_ms: i64,
    pub errors: Vec<String>,
}

/// Neovim buffer event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NvimBufferPayload {
    pub file_path: String,
    pub language: String,
    pub cursor_line: usize,
    pub cursor_col: usize,
    pub diagnostics_count: usize,
}

/// Session summary
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionSummary {
    pub session_id: Uuid,
    pub start_time: i64,
    pub end_time: i64,
    pub project_id: Option<String>,
    pub summary_text: String,
    pub key_activities: Vec<String>,
    pub context_switches: i64,
    pub focus_time_seconds: i64,
}

/// Intervention types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum InterventionType {
    StuckPattern,
    ExcessiveContextSwitch,
    DistractionDetected,
    RecurringError,
    BuildAvoidance,
    FocusReminder,
}

/// Intervention record
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intervention {
    pub intervention_id: Uuid,
    pub timestamp: i64,
    pub intervention_type: InterventionType,
    pub description: String,
    pub severity: f64,
    pub confidence: f64,
    pub context: serde_json::Value,
    pub acknowledged: bool,
}
