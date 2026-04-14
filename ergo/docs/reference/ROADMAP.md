# Ergo Development Roadmap

Based on the architecture specification in `proj_ergo_arch.md`.

##  Phase 0: Skeleton (COMPLETE)

**Goal:** Basic structure and proof of concept

- [x] Nix flake for reproducible environment
- [x] Rust daemon basic structure
- [x] Python orchestrator setup
- [x] SQLite database
- [x] Simple chat interface
- [x] Basic prompt path with current context

## [X] Phase 1: Developer Awareness (90% COMPLETE)

**Goal:** Deep integration with developer workflow

### Completed
- [x] Neovim plugin with context streaming
- [x] Session tracking and management
- [x] Daily session summaries
- [x] Window and application monitoring
- [x] Privacy filters
- [x] Code review via Opus
- [x] Full database schema

### Remaining
- [ ] Shell event ingestion
  - [ ] Add bash/zsh hook script to capture commands
  - [ ] Emit shell.command.finished events
  - [ ] Store in database
  - [ ] Display in recent context

- [ ] Git status tracking
  - [ ] Implement git2 wrapper
  - [ ] Watch for repository changes
  - [ ] Emit git.status.changed events
  - [ ] Detect branch switches

- [ ] Build/test hooks
  - [ ] Watch for cargo/npm/pytest runs
  - [ ] Capture build output
  - [ ] Emit build.succeeded/failed events
  - [ ] Track recurring errors

**Estimated Time:** 2-3 days for remaining items

## 📋 Phase 2: Memory (40% COMPLETE)

**Goal:** Persistent understanding of user workflows

### Completed
- [x] Structured long-term memory tables
- [x] Memory storage and retrieval with access tracking
- [x] Project tracking
- [x] Session summaries generation
- [x] Context builder with memory layers

### Remaining
- [ ] Style profile extraction
  - [ ] Analyze code patterns from Neovim events
  - [ ] Track preferred libraries and tools
  - [ ] Learn common workflows
  - [ ] Auto-populate coding preferences

- [ ] Pinned preferences
  - [ ] UI for setting preferences
  - [ ] Preference application in responses
  - [ ] Per-project preferences

- [ ] Enhanced summary jobs
  - [ ] Automatic daily summaries
  - [ ] Weekly retrospectives
  - [ ] Project milestone tracking

- [ ] Retrieval over prior sessions
  - [ ] "What was I doing Tuesday?"
  - [ ] "Last time I worked on this module?"
  - [ ] Similar session finding

**Estimated Time:** 1 week

## [X] Phase 3: Intervention (Foundation Ready)

**Goal:** Proactive nudges and pattern detection

### Completed (Infrastructure)
- [x] Intervention data model
- [x] Interventions database table
- [x] Intervention storage and retrieval
- [x] UI panel for interventions

### To Implement
- [ ] Pattern detection engine
  - [ ] Stuck pattern (already exists in legacy, needs migration)
  - [ ] Excessive context switching
  - [ ] Distraction detection (browser drift)
  - [ ] Build avoidance detection
  - [ ] Recurring error patterns

- [ ] Intervention triggers
  - [ ] Confidence threshold checks
  - [ ] Quiet hours enforcement
  - [ ] Per-project intervention rules
  - [ ] Severity-based filtering

- [ ] Notification system
  - [ ] Desktop notifications (libnotify)
  - [ ] In-UI alerts
  - [ ] Sound notifications (optional)
  - [ ] Intervention history view

- [ ] Outcome tracking
  - [ ] User acknowledgment
  - [ ] Effectiveness metrics
  - [ ] Intervention tuning based on outcomes

**Estimated Time:** 1 week

## 🔮 Phase 4: Remote and Voice (Planned)

**Goal:** Access beyond the desktop

### Remote Access
- [ ] Tailscale integration
  - [ ] Secure tunnel setup
  - [ ] Authentication layer
  - [ ] Rate limiting
  - [ ] Mobile-optimized UI

- [ ] Phone interface
  - [ ] Mobile web UI
  - [ ] Context-aware responses
  - [ ] Quick actions
  - [ ] Push notifications

### Voice Interface
- [ ] STT integration
  - [ ] Whisper model integration
  - [ ] Push-to-talk activation
  - [ ] Audio device gating

- [ ] TTS output (optional)
  - [ ] Response audio
  - [ ] Intervention announcements

- [ ] Voice sessions
  - [ ] Session recording
  - [ ] Transcript storage
  - [ ] Context from voice

**Estimated Time:** 2 weeks

**Priority:** Low (nice-to-have, not core value)

##  Phase 5: Semantic Retrieval (Future)

**Goal:** Fuzzy recall and similarity search

### Prerequisites
- Complete Phase 2 (memory foundation)
- Stable summary generation
- Enough historical data

### Implementation
- [ ] Embedding generation
  - [ ] Choose embedding model (local vs API)
  - [ ] Generate embeddings for summaries
  - [ ] Store in summaries.embedding column

- [ ] Vector search
  - [ ] Evaluate: pgvector vs Qdrant vs Chroma
  - [ ] Implement similarity search
  - [ ] Hybrid search (keywords + semantic)

- [ ] Use cases
  - [ ] "Find similar debugging sessions"
  - [ ] "What did I learn about X?"
  - [ ] Related decision recall

**Estimated Time:** 1-2 weeks

**Priority:** Low until memory proves valuable

## ️ Ongoing: Polish and Quality

### Testing
- [ ] Unit tests for Rust modules
  - [ ] Database operations
  - [ ] Event emitters
  - [ ] Privacy filters

- [ ] Python tests
  - [ ] Model router logic
  - [ ] Context builder
  - [ ] Memory manager

- [ ] Integration tests
  - [ ] API endpoint tests
  - [ ] Database migrations
  - [ ] Full flow tests

### Performance
- [ ] Profile daemon
  - [ ] Optimize database queries
  - [ ] Reduce memory usage
  - [ ] Minimize context switching overhead

- [ ] Profile orchestrator
  - [ ] Cache context assembly
  - [ ] Async optimizations
  - [ ] Rate limiting

### UI/UX
- [ ] Better error states
- [ ] Loading indicators
- [ ] Keyboard shortcuts
- [ ] Dark/light theme toggle
- [ ] Export session data
- [ ] Settings panel

### Security
- [ ] API authentication
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] SQL injection protection
- [ ] XSS prevention

### Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Architecture diagrams
- [ ] Developer guide for contributors
- [ ] Deployment guide
- [ ] Security audit

##  Release Plan

### v0.1.0 - MVP (Target: 2 weeks)
- Complete Phase 1 remaining items
- Basic Phase 2 features
- Intervention engine activation
- Documentation polish
- Basic testing

### v0.2.0 - Memory Focus (Target: 4 weeks)
- Full Phase 2 completion
- Enhanced summaries
- Style profiles
- Better retrieval

### v0.3.0 - Interventions (Target: 6 weeks)
- Full Phase 3 completion
- Pattern detection
- Notification system
- Outcome tracking

### v0.4.0 - Extended Access (Target: 10 weeks)
- Phase 4 remote access
- Optional voice
- Mobile UI

### v1.0.0 - Production (Target: 12 weeks)
- All core features complete
- Full test coverage
- Performance optimized
- Security hardened
- Documentation complete

##  Current Status (March 2026)

**Phase 0:**  100% Complete
**Phase 1:** [X] 90% Complete
**Phase 2:** [X] 40% Complete
**Phase 3:** 📋 20% Complete (infrastructure only)
**Phase 4:** 📋 0% (planned)
**Phase 5:** 📋 0% (planned)

**Overall Progress:** ~60% to MVP, ~30% to v1.0

##  Immediate Next Steps (This Week)

1. **Git Integration** (Priority: High)
   - Implement git status watcher
   - Test with multiple repos
   - Verify event emission

2. **Shell Tracking** (Priority: High)
   - Create bash/zsh hook script
   - Test command capture
   - Privacy filter shell commands

3. **Intervention Activation** (Priority: Medium)
   - Port stuck pattern detection to new architecture
   - Add context switch detection
   - Test notification delivery

4. **Testing** (Priority: Medium)
   - Write basic unit tests
   - API integration tests
   - E2E smoke test

## 📝 Notes

- **Philosophy:** Build iteratively, test with real use, evolve based on actual value
- **Avoid:** Over-engineering before proving utility
- **Focus:** Developer workflow integration first, fancy features second
- **Measure:** Does it actually help? Does it save time? Is it less annoying than helpful?

## 🤝 Contributing

Want to help? Pick an item from Phase 1 or Phase 2 remaining tasks. See [BUILD_STATUS.md](BUILD_STATUS.md) for implementation details.

Focus areas where help would be valuable:
1. Git integration (Rust + git2)
2. Shell command tracking (bash/zsh scripting)
3. Testing (any language)
4. UI polish (HTML/CSS/JS)
5. Documentation improvements

---

This roadmap will be updated as development progresses. Last updated: March 17, 2026
