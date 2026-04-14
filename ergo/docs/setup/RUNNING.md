# Running Ergo

This guide shows you how to run the Ergo orchestrator and services.

## Prerequisites

- Python 3.13+ (you have 3.13.11)
- Cargo/Rust (you have 1.91.0)
- Git, xdotool
- API keys configured in `.env`

## One-Time Setup

### 1. Create Python Virtual Environment

```bash
cd ~/Documents/Github/Ergo/ergo/orchestrator
python3 -m venv venv
```

### 2. Install Dependencies

```bash
source venv/bin/activate
pip install fastapi 'uvicorn[standard]' pydantic pydantic-settings \
            python-dotenv sqlalchemy httpx aiofiles anthropic \
            google-generativeai openai python-json-logger tenacity
```

## Running the Orchestrator

The orchestrator is the core service that routes AI requests and manages context.

```bash
cd ~/Documents/Github/Ergo/ergo

# Set library path for grpc
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH

# Activate venv
source orchestrator/venv/bin/activate

# Run orchestrator
python -m orchestrator.src.main
```

You should see:
```
INFO - Starting Ergo Orchestrator
INFO - Database: sqlite
INFO - Listening on 127.0.0.1:8765
```

## Verify It's Running

```bash
# In another terminal
curl http://127.0.0.1:8765/health | jq
```

Should return:
```json
{
  "status": "healthy",
  "anthropic_configured": true,
  "gemini_configured": true,
  "database_type": "sqlite"
}
```

## Using from Neovim

Once the orchestrator is running, you can use Ergo from Neovim (after installing the plugin - see [NEOVIM_SETUP.md](NEOVIM_SETUP.md)):

```vim
:ErgoExplainContext
:ErgoSummarizeWork
:ErgoJudgeThisCode
```

## Stopping Ergo

Press `Ctrl+C` in the terminal where the orchestrator is running.

## Logs

Application logs are written to:
```
~/.local/share/ergo/ergo.log
```

View logs:
```bash
tail -f ~/.local/share/ergo/ergo.log
```

## Troubleshooting

### "ImportError: libstdc++.so.6"

Set the library path:
```bash
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH
```

### "ModuleNotFoundError: No module named 'orchestrator'"

Run from the `ergo/` directory (not `orchestrator/`):
```bash
cd ~/Documents/Github/Ergo/ergo
python -m orchestrator.src.main
```

### "Connection refused" on port 8765

Orchestrator isn't running. Start it using the commands above.

## Next Steps

- **Install Neovim plugin:** See [NEOVIM_SETUP.md](NEOVIM_SETUP.md)
- **Check permissions:** Run `../scripts/check-permissions.sh`
- **Test API:** Try the curl commands above

## Advanced: Running Other Services (Optional)

### Rust Daemon (Window Monitoring)

Not required for Neovim integration, but monitors windows and processes:

```bash
cd ~/Documents/Github/Ergo/ergo
cargo run --release
```

### Web UI (Chat Interface)

Optional web interface:

```bash
cd ~/Documents/Github/Ergo/ergo/ui
export LD_LIBRARY_PATH=/nix/store/gnpwfj9gpk8ll7dhf65a6r5gjbs4qbap-gcc-14.3.0-lib/lib:$LD_LIBRARY_PATH
python src/server.py
```

Then open: http://localhost:3000

---

For troubleshooting the nix-shell issues, see [RUNNING_WITHOUT_NIX.md](RUNNING_WITHOUT_NIX.md)
