# Running Ergo Without Nix Shell

**Problem:** The `nix-shell` in this project fails during build due to test failures in Django and psycopg2cffi dependencies that Ergo doesn't actually need.

**Solution:** Run Ergo directly using your system's Python and Cargo, bypassing the broken nix-shell.

## Prerequisites

You already have these installed:
-  Python 3.13.11
-  Cargo 1.91.0
-  Git
-  xdotool (for window monitoring)

## Setup (One-Time)

### 1. Create Python Virtual Environment

```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
python3 -m venv venv
```

### 2. Install Python Dependencies

```bash
source venv/bin/activate
pip install fastapi 'uvicorn[standard]' pydantic pydantic-settings \
            python-dotenv sqlalchemy httpx aiofiles anthropic \
            google-generativeai openai python-json-logger tenacity
```

### 3. Configure Environment

Your `.env` file is already configured with:
- Anthropic API key (for Opus/code review)
- Google AI API key (for Gemini/chat)
- Database settings (SQLite)
- Permission settings

## Running Ergo

### Method 1: Use the Startup Script

```bash
cd ~/Documents/Github/Ergo/ergo
./run-orchestrator-simple.sh
```

### Method 2: Manual Startup

```bash
cd ~/Documents/Github/Ergo/ergo

# Set library path for grpc
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH

# Activate venv and run
source orchestrator/venv/bin/activate
python -m orchestrator.src.main
```

## Verifying It Works

### 1. Check Health Endpoint

```bash
curl http://127.0.0.1:8765/health | jq
```

Should return:
```json
{
  "status": "healthy",
  "anthropic_configured": true,
  "gemini_configured": true,
  "openai_configured": false,
  "database_type": "sqlite"
}
```

### 2. Test Chat Endpoint

```bash
curl -X POST http://127.0.0.1:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you help me with?", "include_context": false}' | jq
```

### 3. Check Recent Context

```bash
curl http://127.0.0.1:8765/context/recent?minutes=30 | jq
```

## Running the Full Stack

To run the complete Ergo system, you need three terminals:

### Terminal 1: Orchestrator (Python)

```bash
cd ~/Documents/Github/Ergo/ergo
./run-orchestrator-simple.sh
```

### Terminal 2: Daemon (Rust) - Optional

The daemon monitors windows and processes. Currently not built yet, so this is optional:

```bash
cd ~/Documents/Github/Ergo/ergo
cargo run --bin ergo-daemon
```

### Terminal 3: UI (Python) - Optional

The web UI for chatting with Ergo. Not required for Neovim integration:

```bash
cd ~/Documents/Github/Ergo/ergo/ui
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH
python src/server.py
```

Then open: http://localhost:3000

## Using Ergo from Neovim

Once the orchestrator is running (Terminal 1), you can use Ergo from Neovim.

### Prerequisites

1. Orchestrator must be running
2. Neovim plugin must be installed (see `docs/setup/NEOVIM_SETUP.md`)

### Test from Neovim

In Neovim, run:

```vim
:ErgoExplainContext
```

Should show what you're currently working on based on file/cursor context.

## Troubleshooting

### "ImportError: libstdc++.so.6"

This happens if LD_LIBRARY_PATH isn't set. Solution:

```bash
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH
```

### "ModuleNotFoundError: No module named 'orchestrator'"

Run from the `ergo/` directory (not `orchestrator/`):

```bash
cd ~/Documents/Github/Ergo/ergo  # NOT ergo/orchestrator
python -m orchestrator.src.main
```

### "Connection refused" on port 8765

Orchestrator isn't running. Start it first (see above).

### "FutureWarning: google.generativeai package deprecated"

This is just a warning. Google is moving to a new package (`google.genai`), but the old one still works. You can ignore this warning for now.

### Virtual environment not activating

Make sure you're in the correct directory:

```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
ls venv/bin/activate  # Should exist
source venv/bin/activate
```

## What's Working

 **Orchestrator API** - FastAPI server on port 8765
 **Chat endpoint** - Send messages and get AI responses
 **Health checks** - Verify service status
 **Context assembly** - Recent activity context
 **Model routing** - Gemini for chat, Opus for code review
 **SQLite database** - Activity storage at ~/.local/share/ergo/activity.db

## What's Not Built Yet

️ **Rust daemon** - Window/process monitoring (needs `cargo build`)
️ **Web UI** - Chat interface (needs separate server)
️ **Neovim plugin** - Editor integration (needs installation)
️ **Memory manager** - Long-term memory (API exists but storage needs implementation)

## Next Steps

1. ** Orchestrator running** - You're here now!
2. **Install Neovim plugin** - See `docs/setup/NEOVIM_SETUP.md`
3. **Build Rust daemon** (optional) - `cargo build --release`
4. **Test from Neovim** - `:ErgoExplainContext`

## Why Not Use Nix Shell?

The `nix-shell` build fails because:

1. **Django test failures** - XML serialization performance test fails
2. **psycopg2cffi test failures** - PostgreSQL async notification test fails
3. **Cascade failures** - 4 packages fail due to Django/psycopg2 failures

These are **test-time failures** in dependencies Ergo doesn't even need (it uses SQLite, not PostgreSQL by default).

The Python venv approach:
-  Faster (no 40-minute builds)
-  Works reliably
-  Uses only needed dependencies
-  Easier to debug

## File Locations

```
~/Documents/Github/Ergo/ergo/
├── orchestrator/
│   ├── venv/                      # Python virtual environment
│   ├── src/
│   │   ├── main.py               # FastAPI server
│   │   ├── config.py             # Settings
│   │   ├── model_router.py       # AI model routing
│   │   └── ...
│   └── requirements.txt          # Python dependencies
├── .env                          # Configuration (API keys, etc)
├── run-orchestrator-simple.sh   # Startup script (use this!)
└── docs/                         # Documentation

Logs and data:
~/.local/share/ergo/
├── ergo.log                      # Application logs
├── activity.db                   # SQLite database
├── events/                       # Event storage
└── session_summaries/            # Session summaries
```

## Getting Help

- **Permission issues:** Run `./scripts/check-permissions.sh`
- **Neovim setup:** See `docs/setup/NEOVIM_SETUP.md`
- **Full docs:** See `docs/README.md`

---

**Status:**  Orchestrator running successfully
**Last tested:** 2026-03-18
**Python:** 3.13.11
**Cargo:** 1.91.0
