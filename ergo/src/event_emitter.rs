// Event emitter for publishing normalized events
// Handles IPC to orchestrator and local database storage

use crate::models::*;
use crate::database_v2::Database;
use anyhow::Result;
use log::{info, warn};
use std::sync::Arc;
use std::sync::mpsc;

pub struct EventEmitter {
    db: Arc<Database>,
    tx: mpsc::Sender<Event>,
}

impl EventEmitter {
    pub fn new(db: Arc<Database>) -> (Self, mpsc::Receiver<Event>) {
        let (tx, rx) = mpsc::channel();

        (EventEmitter { db, tx }, rx)
    }

    /// Emit a window focus event
    pub fn emit_window_focus(
        &self,
        window_title: String,
        process_name: String,
        duration: i64,
        privacy_tag: PrivacyTag,
    ) -> Result<()> {
        let payload = WindowFocusPayload {
            window_title,
            process_name,
            duration,
        };

        let event = Event::new(
            EventSource::Window,
            "window.focus.changed".to_string(),
            serde_json::to_value(&payload)?,
        )
        .with_privacy(privacy_tag);

        self.send_event(event)
    }

    /// Emit a shell command event
    pub fn emit_shell_command(
        &self,
        command: String,
        exit_code: i32,
        duration_ms: i64,
        working_dir: String,
    ) -> Result<()> {
        let payload = ShellCommandPayload {
            command,
            exit_code,
            duration_ms,
            working_dir,
        };

        let event = Event::new(
            EventSource::Shell,
            "shell.command.finished".to_string(),
            serde_json::to_value(&payload)?,
        );

        self.send_event(event)
    }

    /// Emit a git status event
    pub fn emit_git_status(
        &self,
        repo_path: String,
        branch: String,
        modified_files: usize,
        untracked_files: usize,
        is_dirty: bool,
        project_id: Option<String>,
    ) -> Result<()> {
        let payload = GitStatusPayload {
            repo_path,
            branch,
            modified_files,
            untracked_files,
            is_dirty,
        };

        let mut event = Event::new(
            EventSource::Git,
            "git.status.changed".to_string(),
            serde_json::to_value(&payload)?,
        );

        if let Some(pid) = project_id {
            event = event.with_project(pid);
        }

        self.send_event(event)
    }

    /// Emit a build event
    pub fn emit_build_event(
        &self,
        build_type: String,
        success: bool,
        duration_ms: i64,
        errors: Vec<String>,
    ) -> Result<()> {
        let event_type = if success {
            "build.succeeded"
        } else {
            "build.failed"
        };

        let payload = BuildEventPayload {
            build_type,
            success,
            duration_ms,
            errors,
        };

        let event = Event::new(
            EventSource::Build,
            event_type.to_string(),
            serde_json::to_value(&payload)?,
        );

        self.send_event(event)
    }

    /// Emit a browser tab event
    pub fn emit_browser_tab(
        &self,
        url: String,
        title: String,
        domain: String,
        privacy_tag: PrivacyTag,
    ) -> Result<()> {
        let payload = BrowserTabPayload {
            url,
            title,
            domain,
        };

        let event = Event::new(
            EventSource::Browser,
            "browser.tab.changed".to_string(),
            serde_json::to_value(&payload)?,
        )
        .with_privacy(privacy_tag);

        self.send_event(event)
    }

    /// Emit a Neovim buffer event
    pub fn emit_nvim_buffer(
        &self,
        file_path: String,
        language: String,
        cursor_line: usize,
        cursor_col: usize,
        diagnostics_count: usize,
    ) -> Result<()> {
        let payload = NvimBufferPayload {
            file_path,
            language,
            cursor_line,
            cursor_col,
            diagnostics_count,
        };

        let event = Event::new(
            EventSource::Nvim,
            "nvim.buffer.enter".to_string(),
            serde_json::to_value(&payload)?,
        );

        self.send_event(event)
    }

    /// Internal method to send event to both database and IPC channel
    fn send_event(&self, event: Event) -> Result<()> {
        // Store in database
        if let Err(e) = self.db.insert_event(&event) {
            warn!("Failed to store event in database: {}", e);
        }

        // Send to orchestrator via channel
        if let Err(e) = self.tx.send(event.clone()) {
            warn!("Failed to send event to orchestrator: {}", e);
        } else {
            info!("Event emitted: {:?} - {}", event.source, event.event_type);
        }

        Ok(())
    }

    /// Get a clone of the sender for use in other threads
    pub fn get_sender(&self) -> mpsc::Sender<Event> {
        self.tx.clone()
    }
}
