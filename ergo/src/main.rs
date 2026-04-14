// Ergo daemon - monitors active Hyprland window and posts events to orchestrator
// Connects to: http://127.0.0.1:8765/events (FastAPI orchestrator)
use std::env;
mod privacy;
mod window_monitor;
mod database;

use window_monitor::WindowMonitor;
use database::Database;
use std::time::{Duration, Instant};
use tokio::time::sleep;

const ORCHESTRATOR_URL: &str = "http://127.0.0.1:8765/events";
const CHECK_INTERVAL_SECS: u64 = 5;
const PATTERN_CHECK_SECS: u64 = 50;

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() > 1 && args[1] == "stats" {
        show_stats();
        return;
    }

    println!("Ergo Observer starting...");

    let db_path = Database::default_path();
    println!("Database: {}", db_path.display());

    let db = match Database::new(&db_path) {
        Ok(db) => { println!("Database initialized"); db }
        Err(e) => { eprintln!("Database error: {}", e); return; }
    };

    let ignore_patterns = vec![
        "password".to_string(), ".env".to_string(), "token".to_string(),
        "secret".to_string(), "bitwarden".to_string(), "keepass".to_string(),
    ];

    let monitor = match WindowMonitor::new() {
        Ok(m) => m,
        Err(e) => { eprintln!("Monitor error: {}", e); return; }
    };

    // HTTP client for posting to orchestrator - non-blocking, best-effort
    let http_client = reqwest::Client::builder()
        .timeout(Duration::from_secs(3))
        .build()
        .expect("Failed to build HTTP client");

    // Check if orchestrator is up
    let orchestrator_alive = http_client.get("http://127.0.0.1:8765/health")
        .send().await.is_ok();
    if orchestrator_alive {
        println!("Orchestrator connected at {}", ORCHESTRATOR_URL);
    } else {
        println!("Orchestrator not reachable — events will be DB-only until it starts");
    }

    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("Monitoring active window every {}s...", CHECK_INTERVAL_SECS);
    println!("Press Ctrl+C to stop");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    let mut last_pattern_check = Instant::now();
    let mut last_window_title: Option<String> = None;
    let mut window_start_time: Option<Instant> = None;

    loop {
        match monitor.get_active_window() {
            Ok(window) => {
                let ignored = window.should_ignore(&ignore_patterns);
                let title = window.title.clone();
                let window_changed = last_window_title.as_ref() != Some(&title);

                if window_changed {
                    // Update duration for the window we just left
                    if let Some(start) = window_start_time {
                        let duration = start.elapsed().as_secs() as i64;
                        if duration > 0 {
                            let _ = db.update_last_duration(duration);
                        }
                    }

                    // Log to local DB
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

                    // Post event to orchestrator (fire-and-forget, never blocks the loop)
                    if !ignored {
                        let payload = build_event_payload(
                            &window.title,
                            &window.process,
                            &window.class,
                            &window.workspace,
                        );
                        let client = http_client.clone();
                        tokio::spawn(async move {
                            let result = client
                                .post(ORCHESTRATOR_URL)
                                .json(&payload)
                                .send()
                                .await;
                            if let Err(e) = result {
                                // Orchestrator may not be running — silently skip
                                eprintln!("[event] Post failed (orchestrator down?): {}", e);
                            }
                        });
                    }

                    last_window_title = Some(title);
                    window_start_time = Some(Instant::now());
                }
            }
            Err(e) => eprintln!("Error getting window: {}", e),
        }

        // Pattern check every ~50 seconds
        if last_pattern_check.elapsed() >= Duration::from_secs(PATTERN_CHECK_SECS) {
            check_patterns(&db);
            last_pattern_check = Instant::now();
        }

        sleep(Duration::from_secs(CHECK_INTERVAL_SECS)).await;
    }
}

fn build_event_payload(
    title: &str,
    process: &str,
    class: &str,
    workspace: &str,
) -> serde_json::Value {
    // Matches the EventPayload schema in orchestrator/src/main.py
    serde_json::json!({
        "event_id": uuid::Uuid::new_v4().to_string(),
        "timestamp": std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs(),
        "source": "window",
        "event_type": "window.focus.changed",
        "project_id": null,
        "privacy_tag": "public",
        "payload": {
            "window_title": title,
            "process_name": process,
            "window_class": class,
            "workspace": workspace,
        },
        "confidence": 1.0
    })
}

fn check_patterns(db: &Database) {
    match db.detect_stuck_pattern(30) {
        Ok(Some(window)) => {
            println!("\n[PATTERN] Stuck on '{}' for 30+ minutes", window);
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
        Err(e) => { eprintln!("Database error: {}", e); return; }
    };

    println!("Ergo Statistics - Today");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

    match db.get_today_stats() {
        Ok(stats) => {
            println!("Total tracked: {}h {}m",
                stats.total_seconds / 3600,
                (stats.total_seconds % 3600) / 60);
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
                    println!("[{}] {} ({}) - {}s",
                        dt.format("%H:%M"),
                        entry.window_title,
                        entry.process_name,
                        entry.duration);
                }
            }
        }
        Err(e) => eprintln!("Error: {}", e),
    }
}
