// WindowStruct - extended with Hyprland-native fields

pub struct WindowInfo {
    pub title: String,
    pub process: String,
    pub class: String,
    pub workspace: String,
    pub timestamp: i64,
}

impl WindowInfo {
    pub fn new(title: String, process: String) -> Self {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;

        WindowInfo { title, process, class: String::new(), workspace: String::new(), timestamp }
    }

    pub fn new_hypr(title: String, process: String, class: String, workspace: String) -> Self {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() as i64;

        WindowInfo { title, process, class, workspace, timestamp }
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
        println!("[{}] {} ({}) [ws:{}]", self.timestamp, self.title, self.process, self.workspace);
    }
}
