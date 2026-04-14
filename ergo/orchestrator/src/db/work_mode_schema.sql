-- Ergo Work Mode Database Schema
-- Date: 2026-03-25
-- Purpose: Mission state machine, memory system, and agent coordination

-- ============================================================================
-- MISSIONS AND TASK MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS missions (
    mission_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    goal TEXT NOT NULL,
    mode TEXT NOT NULL, -- 'chat', 'deliberation', 'work'
    status TEXT NOT NULL, -- 'created', 'scoping', 'decomposed', 'waiting_for_approval', 'running', 'blocked', 'awaiting_input', 'review', 'completed', 'failed', 'archived'
    project_id TEXT,
    priority INTEGER DEFAULT 0,
    budget_limit REAL,
    total_cost REAL DEFAULT 0.0,
    token_limit INTEGER,
    max_iterations INTEGER DEFAULT 10,
    allowed_tools TEXT, -- JSON array of allowed tool names
    selected_roles TEXT, -- JSON array of role names
    acceptance_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_missions_project ON missions(project_id);
CREATE INDEX idx_missions_created ON missions(created_at DESC);

-- ============================================================================
-- MISSION STEPS (Individual agent actions within a mission)
-- ============================================================================

CREATE TABLE IF NOT EXISTS mission_steps (
    step_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL REFERENCES missions(mission_id) ON DELETE CASCADE,
    role_name TEXT NOT NULL, -- 'planner', 'mage', 'rogue', 'tank', 'support', 'healer'
    objective TEXT NOT NULL,
    status TEXT NOT NULL, -- 'pending', 'running', 'completed', 'failed', 'blocked'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    input_context TEXT, -- JSON object with context data
    output_summary TEXT,
    tool_calls TEXT, -- JSON array of tool calls made
    cost_estimate REAL DEFAULT 0.0,
    review_status TEXT -- 'pending', 'approved', 'rejected', 'needs_revision'
);

CREATE INDEX idx_mission_steps_mission ON mission_steps(mission_id);
CREATE INDEX idx_mission_steps_role ON mission_steps(role_name);
CREATE INDEX idx_mission_steps_status ON mission_steps(status);

-- ============================================================================
-- MEMORY SYSTEM
-- ============================================================================

CREATE TABLE IF NOT EXISTS memories (
    memory_id TEXT PRIMARY KEY,
    memory_type TEXT NOT NULL, -- 'episodic', 'semantic', 'procedural', 'personality'
    scope TEXT NOT NULL, -- 'user', 'project', 'session', 'global'
    project_id TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL DEFAULT 1.0, -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP
);

CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_scope ON memories(scope);
CREATE INDEX idx_memories_project ON memories(project_id);
CREATE INDEX idx_memories_updated ON memories(updated_at DESC);

-- ============================================================================
-- CODING STYLE PREFERENCES
-- ============================================================================

CREATE TABLE IF NOT EXISTS coding_style_preferences (
    pref_id TEXT PRIMARY KEY,
    language TEXT NOT NULL, -- 'python', 'rust', 'typescript', 'nix', 'lua', etc.
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    confidence REAL DEFAULT 0.5, -- 0.0 to 1.0, increases with evidence
    evidence_count INTEGER DEFAULT 1, -- Number of times this preference was observed
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, preference_key)
);

CREATE INDEX idx_coding_style_language ON coding_style_preferences(language);
CREATE INDEX idx_coding_style_confidence ON coding_style_preferences(confidence DESC);

-- ============================================================================
-- PERSONALITY PROFILES
-- ============================================================================

CREATE TABLE IF NOT EXISTS personality_profiles (
    profile_id TEXT PRIMARY KEY,
    mode_name TEXT NOT NULL UNIQUE, -- 'core', 'chat', 'work', 'code_review', 'quiet', 'mission'
    prompt_fragment TEXT NOT NULL,
    priority INTEGER DEFAULT 0, -- Higher priority fragments applied last
    enabled BOOLEAN DEFAULT 1
);

CREATE INDEX idx_personality_mode ON personality_profiles(mode_name);
CREATE INDEX idx_personality_priority ON personality_profiles(priority);

-- ============================================================================
-- MISSION EVENTS (Detailed event log for missions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS mission_events (
    event_id TEXT PRIMARY KEY,
    mission_id TEXT REFERENCES missions(mission_id) ON DELETE CASCADE,
    source TEXT NOT NULL, -- 'supervisor', 'planner', 'mage', 'rogue', 'tank', 'support', 'healer', 'user'
    event_type TEXT NOT NULL, -- 'started', 'step_completed', 'tool_called', 'blocked', 'resumed', 'completed', 'failed'
    payload_json TEXT NOT NULL, -- JSON object with event details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mission_events_mission ON mission_events(mission_id);
CREATE INDEX idx_mission_events_source ON mission_events(source);
CREATE INDEX idx_mission_events_timestamp ON mission_events(timestamp DESC);

-- ============================================================================
-- VAULT EXPORTS (Track what has been exported to Obsidian)
-- ============================================================================

CREATE TABLE IF NOT EXISTS vault_exports (
    export_id TEXT PRIMARY KEY,
    mission_id TEXT REFERENCES missions(mission_id) ON DELETE CASCADE,
    path TEXT NOT NULL, -- Relative path within vault
    export_type TEXT NOT NULL, -- 'mission_summary', 'session_summary', 'project_update', 'style_profile'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vault_exports_mission ON vault_exports(mission_id);
CREATE INDEX idx_vault_exports_type ON vault_exports(export_type);

-- ============================================================================
-- ROLE DEFINITIONS (Agent role configurations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS role_definitions (
    role_id TEXT PRIMARY KEY,
    role_name TEXT NOT NULL UNIQUE, -- 'planner', 'mage', 'rogue', 'tank', 'support', 'healer'
    system_prompt_path TEXT NOT NULL, -- Path to prompt file in models/prompts/
    allowed_tools TEXT NOT NULL, -- JSON array of allowed tools
    allowed_memory_scopes TEXT NOT NULL, -- JSON array of allowed memory scopes
    preferred_models TEXT NOT NULL, -- JSON array of preferred model names in priority order
    max_iterations INTEGER DEFAULT 3,
    escalation_rules TEXT, -- JSON object defining escalation conditions
    enabled BOOLEAN DEFAULT 1
);

CREATE INDEX idx_role_definitions_name ON role_definitions(role_name);

-- ============================================================================
-- PROJECT TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    repo_path TEXT,
    primary_language TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_projects_active ON projects(active);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_missions_timestamp
AFTER UPDATE ON missions
BEGIN
    UPDATE missions SET updated_at = CURRENT_TIMESTAMP WHERE mission_id = NEW.mission_id;
END;

CREATE TRIGGER IF NOT EXISTS update_memories_timestamp
AFTER UPDATE ON memories
BEGIN
    UPDATE memories SET updated_at = CURRENT_TIMESTAMP WHERE memory_id = NEW.memory_id;
END;

CREATE TRIGGER IF NOT EXISTS update_coding_style_timestamp
AFTER UPDATE ON coding_style_preferences
BEGIN
    UPDATE coding_style_preferences SET updated_at = CURRENT_TIMESTAMP WHERE pref_id = NEW.pref_id;
END;

CREATE TRIGGER IF NOT EXISTS update_projects_timestamp
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE project_id = NEW.project_id;
END;

-- ============================================================================
-- INITIAL DATA: ROLE DEFINITIONS
-- ============================================================================

INSERT OR IGNORE INTO role_definitions (role_id, role_name, system_prompt_path, allowed_tools, allowed_memory_scopes, preferred_models, max_iterations, enabled) VALUES
('role-planner', 'planner', 'models/prompts/planner.md', '["read_memory", "read_repo_tree", "list_files"]', '["user", "project", "session"]', '["gemini-2.5-flash", "gemini-pro"]', 3, 1),
('role-mage', 'mage', 'models/prompts/mage.md', '["read_code", "analyze_architecture", "read_memory"]', '["user", "project", "session", "global"]', '["claude-opus", "claude-sonnet"]', 5, 1),
('role-rogue', 'rogue', 'models/prompts/rogue.md', '["read_file", "write_file", "edit_file", "shell_limited", "git_commands"]', '["project", "session"]', '["claude-sonnet", "claude-opus"]', 10, 1),
('role-tank', 'tank', 'models/prompts/tank.md', '["run_tests", "inspect_diff", "verify_constraints"]', '["project", "session"]', '["claude-sonnet", "gemini-pro"]', 3, 1),
('role-support', 'support', 'models/prompts/support.md', '["read_vault", "write_summary", "search_memory", "retrieve_context"]', '["user", "project", "session", "global"]', '["gemini-2.5-flash", "gemini-pro"]', 2, 1),
('role-healer', 'healer', 'models/prompts/healer.md', '["read_mission_state", "write_summary", "generate_recovery_plan"]', '["user", "project", "session"]', '["gemini-2.5-flash"]', 2, 1);

-- ============================================================================
-- INITIAL DATA: PERSONALITY PROFILES
-- ============================================================================

INSERT OR IGNORE INTO personality_profiles (profile_id, mode_name, prompt_fragment, priority, enabled) VALUES
('persona-core', 'core', 'You are Ergo, a local-first NixOS-native work supervisor. You are direct, technically precise, and focused on getting real work done.', 0, 1),
('persona-chat', 'chat', 'In chat mode, be conversational but concise. Provide helpful context without over-explaining.', 1, 1),
('persona-work', 'work', 'In work mode, be mission-focused and systematic. Break down tasks clearly, coordinate agents efficiently, and keep the user informed of progress.', 1, 1),
('persona-code-review', 'code_review', 'In code review mode, be thorough and direct. Point out issues clearly, suggest improvements, and explain the reasoning behind recommendations.', 1, 1),
('persona-quiet', 'quiet', 'In quiet mode, minimize output. Be brief, skip pleasantries, and focus only on essential information.', 1, 1),
('persona-mission', 'mission', 'In mission mode, act as a supervisor coordinating a team. Be clear about assignments, track progress, and synthesize results.', 1, 1);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

CREATE VIEW IF NOT EXISTS active_missions AS
SELECT * FROM missions
WHERE status IN ('scoping', 'decomposed', 'waiting_for_approval', 'running', 'blocked', 'awaiting_input', 'review')
ORDER BY priority DESC, created_at ASC;

CREATE VIEW IF NOT EXISTS recent_memories AS
SELECT * FROM memories
WHERE updated_at > datetime('now', '-30 days')
ORDER BY updated_at DESC;

CREATE VIEW IF NOT EXISTS high_confidence_preferences AS
SELECT * FROM coding_style_preferences
WHERE confidence >= 0.7
ORDER BY confidence DESC, evidence_count DESC;
