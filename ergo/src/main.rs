// src/main.rs
mod privacy;
mod window_monitor;
use window_monitor::WindowMonitor;
use std::thread;
use std::time::Duration;

fn main() {
    println!("Ergo Observer starting...");
    
    // Privacy patterns to ignore
    let ignore_patterns = vec![
        "password".to_string(),
        ".env".to_string(),
        "token".to_string(),
        "secret".to_string(),
        "bitwarden".to_string(),
        "keepass".to_string(),
    ];
    
    // Create window monitor
    let monitor = match WindowMonitor::new() {
        Ok(m) => m,
        Err(e) => {
            eprintln!("Error: {}", e);
            eprintln!("Make sure you're running in nix-shell!");
            return;
        }
    };
    
    println!("Monitoring active window every 5 seconds...");
    println!("Press Ctrl+C to stop\n");
    
    // Main observation loop
    loop {
        match monitor.get_active_window() {
            Ok(window) => {
                if window.should_ignore(&ignore_patterns) {
                    println!("[IGNORED] Privacy filter triggered");
                } else {
                    window.display();
                }
            }
            Err(e) => {
                eprintln!("Error getting window: {}", e);
            }
        }
        
        // Check every 5 seconds
        thread::sleep(Duration::from_secs(5));
    }
}
