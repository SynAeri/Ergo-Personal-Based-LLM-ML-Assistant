// WindowStruct 

pub struct WindowInfo {
    pub title: String,
    pub process: String,
    pub timestamp: i64,
}

impl WindowInfo {
    pub fn new(title: String, process: String) -> Self {
        // Get current timestamp
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;
        
        WindowInfo { title, process, timestamp }
    }
    
    pub fn should_ignore(&self, patterns: &[String]) -> bool {
        let title_lower = self.title.to_lowercase();
        let process_lower = self.process.to_lowercase();
        
        for pattern in patterns {
            let pattern_lower = pattern.to_lowercase();
            if title_lower.contains(&pattern_lower) || 
               process_lower.contains(&pattern_lower) {
                return true;
            }
        }
        
        false
    }
    
    pub fn display(&self) {
        println!("[{}] {} ({})", self.timestamp, self.title, self.process);
    }
}
