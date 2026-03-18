
Project Ergo
Full Architecture and Execution Specification
Local-first NixOS personal operator with developer context, memory, and persona-driven interaction
Purpose
A practical system architecture for building, testing, and evolving Project Ergo from prototype to stable local operator.


1. Executive summary
Project Ergo is a local-first AI assistant designed for NixOS. It observes workstation activity, understands code context, keeps memory across sessions, and responds through a sharp, work-focused persona.
The system should not be built as one giant all-seeing model. It should be split into five layers: capture, index, reason, act, and interact. This separation keeps the system debuggable, cheaper to run, and safer to evolve.
The initial version should favor ordinary structured storage over a dedicated vector database. Most early-value memory is factual and operational: active repo, open files, shell history, browser tab, recurring errors, daily patterns, and session summaries. Semantic retrieval can be added later with embeddings once the memory shape is proven.
The strongest near-term setup is a Rust daemon for system observation, a Python orchestration service for model routing and memory logic, a local relational database, a Neovim plugin for explicit editor context, and optional voice only when intentionally enabled.
2. Design goals
Remain local-first and usable even when external model services are unavailable.
Observe work context without relying on crude full-time screenshot scraping.
Understand code state through explicit editor and repository signals rather than screen pixels.
Build persistent structured memory of user workflows, style, and recurring blockers.
Support a strong persona without letting the persona corrupt planning or system policy.
Use premium hosted models only for high-value reasoning and code tasks.
Stay modular enough to swap models, storage backends, and interfaces over time.
3. Non-goals for v1
Not a full autonomous AGI-style operator.
Not a permanent always-listening voice assistant.
Not a complete browser surveillance engine with indiscriminate screenshot retention.
Not a giant all-purpose vector memory dump from day one.
Not a fake sentient companion product. The personality is presentation; the core is state, memory, and intervention.
4. System architecture overview
Project Ergo should be implemented as a set of cooperating local services rather than one monolith.
Layer
Primary role
Main technology
Notes
Capture
Collect system, editor, browser, shell, and repository signals
Rust
Long-running daemon and hooks
Index
Normalize events and store memory
SQLite/Postgres
Structured first, semantic later
Reason
Assemble context, route models, summarize, detect patterns
Python
Model-agnostic orchestration
Act
Notifications, interventions, commands, tool execution
Rust + Python
Clear policy boundaries
Interact
Chat UI, phone UI later, optional voice
Web/Tauri/FastAPI
Persona is applied here

5. Core services
ergo-daemon (Rust)
Tracks focused window, active application, browser tab metadata, shell command events, filesystem/repo events, and configured system signals.
Publishes normalized events over a local IPC channel or localhost API.
Owns privacy modes, kill switches, rate limiting, and source-specific collection policy.
ergo-orchestrator (Python)
Builds prompt context, routes requests to local or hosted models, generates summaries, updates memory, and runs retrieval.
Separates cognition, persona wrapping, and tool policy.
ergo-memory
Stores events, working memory, long-term memory, session summaries, style profiles, and retrieval metadata.
Starts with SQLite or Postgres. Add embeddings later if semantic retrieval becomes necessary.
ergo-ui
Local desktop chat interface with status panels, activity summaries, and intervention feed.
Future phone access should happen through an authenticated relay or private network such as Tailscale.
ergo-voice
Optional service that starts only when voice mode is intentionally enabled.
Supports push-to-talk first. Always-on listening should be postponed.
ergo-nvim plugin
Provides file path, language, cursor position, diagnostics, visible symbols, selected text, test/build actions, and code-context snapshots.
This is the most important source of coding awareness; do not replace it with OCR or screenshot analysis.
6. Data flow
1. The Rust daemon captures raw workstation events and emits normalized event records.
2. The memory layer stores those records and attaches metadata such as project, source, privacy tag, and confidence.
3. The Python orchestrator pulls recent context, relevant long-term memory, and explicit editor context when a user message or system trigger occurs.
4. The orchestrator decides whether a local model, Gemini, or Opus should handle the task.
5. The response is generated, persona-wrapped, shown in the UI, and optionally written back into memory as a summary or decision record.
6. Intervention rules can trigger proactive notifications when a threshold or recognized pattern is hit.
7. Event model
Ergo should use an event-based memory system instead of raw data dumping. Suggested event families:
window.focus.changed
browser.tab.changed
browser.page.visited
shell.command.finished
git.status.changed
build.failed / build.succeeded
nvim.buffer.enter
nvim.selection.changed
nvim.diagnostics.updated
session.summary.created
voice.session.started / ended
Suggested normalized event fields:
Field
Type
Purpose
Example
event_id
UUID
Unique identity
550e8400-e29b
timestamp
datetime
Ordering and retrieval
2026-03-17T09:14
source
enum
Emitter service
nvim, browser, shell
project_id
text
Repo/task grouping
project-ergo
privacy_tag
enum
Retention and visibility control
public, private, ignore
payload_json
json
Raw normalized content
{...}
confidence
float
Signal reliability
0.92

8. Memory architecture
Memory should be split into layers rather than stored as one blended context pool.
Layer
Purpose
Typical content
Ephemeral context
Last 30 to 90 minutes of actions. Used for immediate replies.
Open files, active window, current shell output, latest diagnostics.
Working memory
Current day or current task block.
Open goals, blockers, current branch, recent changes, unresolved issues.
Long-term structured memory
Stable, queryable user and project facts.
Coding style preferences, common commands, repo metadata, recurring schedules.
Long-term semantic memory
Compressed fuzzy-retrieval layer added later.
Session summaries, solved-problem summaries, decision records, project retrospectives.

9. Storage strategy
Start with local storage on the laptop for prototyping. This is enough for early development, especially if retention is selective.
Use a relational database first. SQLite is sufficient for single-user prototyping; Postgres becomes worth it when you want concurrent services, stronger querying, and future pgvector support.
Use filesystem object storage for heavy assets such as screenshots, voice transcripts, archived logs, and exported summaries.
Add a vector layer only when semantic retrieval clearly outgrows keyword-plus-metadata retrieval.
10. Do you need a vector database?
Not at the beginning. Most early-value memory is structured and should live in ordinary tables.
A vector database becomes useful when you want fuzzy recall such as finding similar past debugging sessions, session summaries, or design decisions.
The clean path is: relational storage first, embeddings second, dedicated vector engine only if retrieval needs justify it.
Recommended progression:
v1: SQLite or Postgres only
v2: Add embeddings for summaries, notes, and selected code chunks
v3: If needed, use pgvector inside Postgres or adopt a dedicated vector engine such as Qdrant
11. Model routing strategy
Ergo should be model-agnostic. Different model classes should handle different workloads.
Workload
Preferred model type
Initial routing
Reason
Event tagging
Small local model or rules
Local
Cheap and frequent
Session summaries
Small/medium local model
Local first
Runs often
General chat
Gemini
Hosted
Covered by current access plan
Code review / hard debugging
Opus
Hosted
Reserved for expensive reasoning
Embeddings
Embedding model
Local or cheap hosted
Indexing only
Voice transcription
Local STT if possible
Local first
Avoid realtime cloud cost

12. Persona design
The system persona should be separated from reasoning. The underlying planner should stay accurate, calm, and tool-aware. The persona layer should wrap the final output style.
Maintain at least three distinct prompt layers: cognition prompt, persona prompt, and policy prompt.
Support mode switches such as quiet mode, hard-focus mode, and standard assistant mode. That prevents the persona from becoming exhausting.
13. Screen monitoring policy
Do not default to continuous screenshot ingestion. It is expensive, noisy, and usually worse than explicit signals.
Prefer event-level observation: active window, tab title and URL where permitted, shell output, file path, diagnostics, git state, and editor context.
Allow screenshots only under controlled conditions: explicit user request, hotkey capture, repeated failure states, or coarse opt-in checkpoints.
14. Neovim integration
Implement a Neovim plugin in Lua that streams editor context to the local daemon over a Unix socket or locked localhost endpoint.
Send: current file, language, cursor position, selected text, visible symbols, diagnostics, and build/test actions.
Expose commands such as :ErgoExplainContext, :ErgoSummarizeWork, :ErgoJudgeThisCode, and :ErgoCommitReview.
This explicit integration is the main path for code understanding.
15. Voice and messaging
Voice should be optional and intentional. Start with push-to-talk and audio-device-gated activation.
A future phone interface should be a secure remote client, not raw SMS command injection.
Remote access should use authenticated networking such as Tailscale or a hardened relay rather than exposing the assistant publicly.
16. Intervention engine
The key proactive feature is not constant chatting; it is timely intervention.
Excessive context switching in a short period
Repeated recurrence of a known error class
Divergence from a stated daily objective
Compiling or testing avoidance after multiple edits
Known distraction pattern such as browser drift after a work block
Interventions should include severity, confidence, quiet-hours handling, and per-project rules.
17. Privacy, safety, and control
Every collector needs a kill switch.
Support privacy modes such as pause collection, exclude app, exclude site, and no-retention mode.
Retain summaries longer than raw captures where possible.
Separate private memory from general work memory in storage and retrieval policy.
Do not give the assistant uncontrolled shell execution by default.
18. Recommended local file layout
/data/ergo/events/
/data/ergo/session_summaries/
/data/ergo/screenshots/
/data/ergo/audio/
/data/ergo/repo_snapshots/
/data/ergo/models/
/data/ergo/config/
/data/ergo/backups/
19. Suggested database entities
Entity
Purpose
users
Single-user now, but keep schema future-safe
projects
Repo definitions and tags
events
Normalized workstation events
sessions
Work blocks and daily sessions
memories
Structured long-term facts
summaries
Session and project summaries
style_profiles
User coding style and communication patterns
interventions
Triggered nudges and outcomes
artifacts
Linked files, screenshots, and transcripts

20. Execution plan
Phase 0: skeleton
Create a Nix flake or equivalent setup for daemon, orchestrator, and UI.
Stand up local storage, config, and simple chat interface.
Implement a basic prompt path using current context only.
Phase 1: developer awareness
Add Neovim plugin, shell event ingestion, git status tracking, and build/test hooks.
Store and display current-task context and daily session summaries.
Phase 2: memory
Add structured long-term memory, pinned preferences, and style profile extraction.
Create summary jobs and retrieval over prior sessions.
Phase 3: intervention
Implement pattern detection, drift alerts, recurring-error recall, and focus nudges.
Add confidence thresholds and quiet-hours policy.
Phase 4: remote and voice
Ship secure phone access and optional voice mode.
Keep voice off unless explicitly activated.
Phase 5: semantic retrieval
Add embeddings and vector retrieval only after memory patterns are stable and useful.
21. MVP cut
The minimum credible version of Ergo should include:
Rust daemon capturing app focus, shell commands, and project events
Python orchestrator with Gemini for general assistance and Opus reserved for code-heavy tasks
Local relational storage
Neovim integration
Desktop chat interface
Daily summary generation
Basic intervention rules
The MVP should exclude:
Always-on screenshot ingestion
Always-on voice
Phone messaging as a primary interface
Large-scale vector infrastructure
Autonomous shell actions without review
22. Technical stack recommendation
Rust: daemon, event collection, IPC, policy enforcement
Python: orchestration, model routing, memory updates, summarization, embeddings
SQLite first, Postgres when service boundaries mature
FastAPI: local API for UI and plugin integration
Lua: Neovim plugin
Tauri or local web UI for desktop interaction
Tailscale for future remote access
23. Final recommendation
Build Ergo as a local work operator with memory and intervention first, and only then add the heavier character features.
The core value is not that it pretends to be a person. The core value is that it remembers your patterns, sees your working context, and intervenes at the right time.
The right v1 is a disciplined local platform with a strong persona skin. The wrong v1 is an overbuilt pseudo-sentient companion that tries to do everything at once.
