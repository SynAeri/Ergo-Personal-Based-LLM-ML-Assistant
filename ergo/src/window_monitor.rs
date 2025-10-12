// Simple approach using xdotool 
use std::process::Command;
use crate::privacy::WindowInfo;

pub struct WindowMonitor;

impl WindowMonitor {
    pub fn new() -> Result<Self, String> {
        // Check if xdotool is available
        match Command::new("xdotool").arg("--version").output() {
            Ok(_) => Ok(WindowMonitor),
            Err(_) => Err("xdotool not found. Make sure you're in nix-shell!".to_string()),
        }
    }
    
    pub fn get_active_window(&self) -> Result<WindowInfo, String> {
        // Get active window ID
        let window_id_output = Command::new("xdotool")
            .arg("getactivewindow")
            .output()
            .map_err(|e| format!("Failed to get active window: {}", e))?;
        
        if !window_id_output.status.success() {
            return Err("xdotool failed to get active window".to_string());
        }
        
        let window_id = String::from_utf8_lossy(&window_id_output.stdout)
            .trim()
            .to_string();
        
        // Get window title
        let title_output = Command::new("xdotool")
            .args(&["getwindowname", &window_id])
            .output()
            .map_err(|e| format!("Failed to get window name: {}", e))?;
        
        let title = if title_output.status.success() {
            String::from_utf8_lossy(&title_output.stdout)
                .trim()
                .to_string()
        } else {
            "Unknown Window".to_string()
        };
        
        // Get process name from PID
        let pid_output = Command::new("xdotool")
            .args(&["getwindowpid", &window_id])
            .output();
        
        let process = if let Ok(output) = pid_output {
            if output.status.success() {
                let pid = String::from_utf8_lossy(&output.stdout)
                    .trim()
                    .to_string();
                self.get_process_name_from_pid(&pid)
            } else {
                "unknown".to_string()
            }
        } else {
            "unknown".to_string()
        };
        
        Ok(WindowInfo::new(title, process))
    }
    
    fn get_process_name_from_pid(&self, pid: &str) -> String {
        // Read from pid 
        match std::fs::read_to_string(format!("/proc/{}/comm", pid)) {
            Ok(name) => name.trim().to_string(),
            Err(_) => "unknown".to_string(),
        }
    }
}
