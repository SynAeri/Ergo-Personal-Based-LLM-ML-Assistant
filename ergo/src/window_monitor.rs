// Window monitoring via hyprctl activewindow (Hyprland/Wayland native)
// Replaces xdotool which cannot read window titles under XWayland
use std::process::Command;
use crate::privacy::WindowInfo;

pub struct WindowMonitor;

impl WindowMonitor {
    pub fn new() -> Result<Self, String> {
        match Command::new("hyprctl").arg("version").output() {
            Ok(_) => Ok(WindowMonitor),
            Err(_) => Err("hyprctl not found. Is Hyprland running?".to_string()),
        }
    }

    pub fn get_active_window(&self) -> Result<WindowInfo, String> {
        let output = Command::new("hyprctl")
            .args(&["activewindow"])
            .output()
            .map_err(|e| format!("Failed to run hyprctl: {}", e))?;

        if !output.status.success() {
            return Err("hyprctl activewindow failed".to_string());
        }

        let text = String::from_utf8_lossy(&output.stdout);
        Ok(parse_hyprctl_output(&text))
    }
}

// Parse the key: value lines from `hyprctl activewindow`
fn parse_hyprctl_output(text: &str) -> WindowInfo {
    let mut title = String::from("unknown");
    let mut class = String::from("unknown");
    let mut workspace = String::from("unknown");
    let mut pid = String::new();

    for line in text.lines() {
        let line = line.trim();
        if let Some(val) = line.strip_prefix("title:") {
            title = val.trim().to_string();
        } else if let Some(val) = line.strip_prefix("class:") {
            class = val.trim().to_string();
        } else if let Some(val) = line.strip_prefix("workspace:") {
            // format: "4 (4)" — take just the name/number
            workspace = val.trim().split_whitespace().next().unwrap_or("?").to_string();
        } else if let Some(val) = line.strip_prefix("pid:") {
            pid = val.trim().to_string();
        }
    }

    // Use pid to get process name from /proc
    let process = if !pid.is_empty() {
        std::fs::read_to_string(format!("/proc/{}/comm", pid))
            .map(|s| s.trim().to_string())
            .unwrap_or_else(|_| class.clone())
    } else {
        class.clone()
    };

    WindowInfo::new_hypr(title, process, class, workspace)
}
