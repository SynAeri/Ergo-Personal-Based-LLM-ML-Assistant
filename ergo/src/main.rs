use std::env; 
mod privacy;
mod window_monitor;
mod database;  
// mod context;

use window_monitor::WindowMonitor;
use database::Database; 
use std::thread;
use std::time::{Duration, Instant};

fn main() {
    println!("Ergo Observer starting...");

    // Check for commands have been used
    let args: Vec<String> = env::args().collect();
    
    if args.len() > 1 && args[1] == "stats" {
        show_stats();
        return;
    }

    // Initialize database
    let db_path = Database::default_path();
    println!("Database: {}", db_path.display());
    
    let db = match Database::new(&db_path) {
        Ok(db) => {
            println!("Database initialized");
            db
        }
        Err(e) => {
            eprintln!("Database error: {}", e);
            return;
        }
    };
    
    // Privacy patterns to ignore
    let ignore_patterns = vec![
        "password".to_string(),
        ".env".to_string(),
        "token".to_string(),
        "secret".to_string(),
        "bitwarden".to_string(),
        "keepass".to_string(),
    ];
    
    // Create window monitorer thingy 
    let monitor = match WindowMonitor::new() {
        Ok(m) => m,
        Err(e) => {
            eprintln!("Error: {}", e);
            return;
        }
    };
    
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Monitoring active window every 5 seconds...");
    println!("📊 Run with 'stats' arg for statistics");
    println!("Press Ctrl+C to stop"); 
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    let check_interval = Duration::from_secs(5);
    let mut last_check = Instant::now();
    let mut last_window_title: Option<String> = None;
    let mut window_start_time: Option<Instant> = None;
    
    // Main observation loop
    loop {
        // Get current window
        match monitor.get_active_window() {
            Ok(window) => {
                let ignored = window.should_ignore(&ignore_patterns);
                
                // Check if window changed
                let title = window.title.clone();
                let window_changed = last_window_title.as_ref() != Some(&title);
                
                if window_changed {
                    // Update duration for previous window
                    if let Some(start) = window_start_time {
                        let duration = start.elapsed().as_secs() as i64;
                        if duration > 0 {
                            let _ = db.update_last_duration(duration);
                        }
                    }
                    
                    // Log new window
                    match db.log_activity(&window.title, &window.process, ignored) {
                        Ok(_) => {
                            if ignored {
                                println!("[IGNORED] Privacy filter triggered");
                            } else {
                                window.display();
                            }
                        }
                        Err(e) => eprintln!("Database error: {}", e),
                    }
                    
                    // Update tracking vars
                    last_window_title = Some(title);
                    window_start_time = Some(Instant::now());
                }
            }
            Err(e) => {
                eprintln!("Error getting window: {}", e);
            }
        }
        
        // Check for patterns every 10 checks (50 seconds)
        if last_check.elapsed() >= Duration::from_secs(50) {
            check_patterns(&db);
            last_check = Instant::now();
        }
        
        thread::sleep(check_interval);
    }
}

fn check_patterns(db: &Database) {
    // Check if stuck on same window for 30+ minutes
    match db.detect_stuck_pattern(30) {
        Ok(Some(window)) => {
            println!("\nYou've been on '{}' for 30+ minutes", window);
            let _ = db.log_pattern(
                "stuck",
                &format!("30+ minutes on same window: {}", window),
                Some(&window),
                None,
            );
        }
        Ok(None) => {}
        Err(e) => eprintln!("Pattern detection error: {}", e),
    }
}

fn show_stats() {
    let db_path = Database::default_path();
    let db = match Database::new(&db_path) {
        Ok(db) => db,
        Err(e) => {
            eprintln!("Database error: {}", e);
            return;
        }
    };
    
    println!("Ergo Statistics - Today");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    
    match db.get_today_stats() {
        Ok(stats) => {
            let hours = stats.total_seconds / 3600;
            let minutes = (stats.total_seconds % 3600) / 60;
            
            println!("Total tracked: {}h {}m", hours, minutes);
            println!("Context switches: {}", stats.context_switches);
            println!("Most used: {}", stats.most_used_app);
        }
        Err(e) => eprintln!("Error: {}", e),
    }
    
    println!("\nRecent activity (last 2 hours):");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    
    match db.get_recent_activity(2) {
        Ok(entries) => {
            for entry in entries.iter().take(10) {
                if !entry.ignored {
                    let dt = chrono::DateTime::from_timestamp(entry.timestamp, 0)
                        .unwrap()
                        .with_timezone(&chrono::Local);
                    
                    println!(
                        "[{}] {} ({}) - {}s",
                        dt.format("%H:%M"),
                        entry.window_title,
                        entry.process_name,
                        entry.duration
                    );
                }
            }
        }
        Err(e) => eprintln!("Error: {}", e),
    }
}
