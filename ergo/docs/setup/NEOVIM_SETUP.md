# Ergo Neovim Plugin Setup for NixOS
# Integration with PrimaMateria-style configuration at /etc/nixos/neovimConfig/

## Overview
This guide shows how to integrate the Ergo Neovim plugin into your declarative NixOS Neovim setup at `/etc/nixos/neovimConfig/`.

The plugin gives Ergo authority to scan your editor context including:
- Current file path and language
- Cursor position and selections
- Diagnostics (errors/warnings)
- Visible code context
- Git status from within Neovim

## Installation Steps

### 1. Create a Local Nix Package for Ergo Plugin

First, we need to make the plugin available as a Nix package:

```bash
# Create a package definition in your neovimConfig
sudo mkdir -p /etc/nixos/neovimConfig/packages/ergo-nvim
```

Create `/etc/nixos/neovimConfig/packages/ergo-nvim/default.nix`:

```nix
{ pkgs, lib }:

pkgs.vimUtils.buildVimPlugin {
  pname = "ergo-nvim";
  version = "0.1.0";

  src = pkgs.fetchFromGitHub {
    owner = "yourusername";  # Update if you publish to GitHub
    repo = "ergo";
    rev = "main";
    sha256 = lib.fakeSha256;  # Will need to update after first build
  };

  # Or use local path during development:
  # src = /path/to/ergo/ergo/nvim-plugin;

  meta = with lib; {
    description = "Neovim plugin for Ergo AI assistant integration";
    homepage = "https://github.com/yourusername/ergo";
    license = licenses.mit;
  };
}
```

**For local development**, use the simpler approach - just reference the local directory.

### 2. Add Plugin to plugins.nix

Edit `/etc/nixos/neovimConfig/plugins.nix` and add:

```nix
{ pkgs }:
with pkgs.vimPlugins; [
  telescope-nvim
  plenary-nvim
  # ... existing plugins ...

  claudecode-nvim # AI HELP (already present)

  # Add Ergo plugin (local development version)
  (pkgs.vimUtils.buildVimPlugin {
    pname = "ergo-nvim";
    version = "dev";
    src = /path/to/ergo/ergo/nvim-plugin;
  })

  # ... rest of plugins ...
]
```

### 3. Create Lua Configuration

Create the file `/etc/nixos/neovimConfig/config/lua/nvim-ergo.lua`:

```lua
-- Ergo AI Assistant Plugin Configuration
-- Connects Neovim to the Ergo orchestrator for context-aware assistance

local status_ok, ergo = pcall(require, "ergo")
if not status_ok then
  vim.notify("Ergo plugin not found", vim.log.levels.WARN)
  return
end

-- Configure the plugin
ergo.setup({
  -- Unix socket path for communication with daemon
  socket_path = "/tmp/ergo-nvim.sock",

  -- Enable automatic context reporting
  enabled = true,

  -- How often to send context updates (milliseconds)
  auto_report_interval = 5000,  -- Every 5 seconds

  -- Send LSP diagnostics to Ergo
  send_diagnostics = true,

  -- Send visual selections to Ergo
  send_selections = true,
})

-- Set up keybindings
local opts = { noremap = true, silent = true }

-- Explain what you're currently working on
vim.keymap.set('n', '<leader>ee', '<cmd>ErgoExplainContext<CR>',
  vim.tbl_extend('force', opts, { desc = "Ergo: Explain context" }))

-- Summarize recent work
vim.keymap.set('n', '<leader>es', '<cmd>ErgoSummarizeWork<CR>',
  vim.tbl_extend('force', opts, { desc = "Ergo: Summarize work" }))

-- Review/judge current code
vim.keymap.set('n', '<leader>ej', '<cmd>ErgoJudgeThisCode<CR>',
  vim.tbl_extend('force', opts, { desc = "Ergo: Judge code" }))

-- Review git commit
vim.keymap.set('n', '<leader>ec', '<cmd>ErgoCommitReview<CR>',
  vim.tbl_extend('force', opts, { desc = "Ergo: Review commit" }))

-- Toggle Ergo monitoring on/off
vim.keymap.set('n', '<leader>et', '<cmd>ErgoToggle<CR>',
  vim.tbl_extend('force', opts, { desc = "Ergo: Toggle monitoring" }))

-- Visual mode: Send selection to Ergo for analysis
vim.keymap.set('v', '<leader>ea', function()
  -- Get selected text
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  local lines = vim.api.nvim_buf_get_lines(0, start_pos[2] - 1, end_pos[2], false)

  if #lines > 0 then
    local code = table.concat(lines, "\n")

    -- Send to Ergo for analysis
    local cmd = string.format(
      'curl -s -X POST http://127.0.0.1:8765/chat -H "Content-Type: application/json" -d \'{"message": "Analyze this code: %s", "include_context": true}\'',
      vim.fn.shellescape(code)
    )

    vim.notify("Asking Ergo about selection...", vim.log.levels.INFO)
    vim.fn.jobstart(cmd, {
      on_stdout = function(_, data)
        if data and #data > 0 then
          local response = table.concat(data, "\n")
          vim.notify("Ergo: " .. response, vim.log.levels.INFO)
        end
      end
    })
  end
end, vim.tbl_extend('force', opts, { desc = "Ergo: Analyze selection" }))

-- Status line integration (optional)
vim.api.nvim_create_autocmd({"BufEnter", "BufWritePost"}, {
  pattern = "*",
  callback = function()
    if ergo.config.enabled then
      vim.g.ergo_status = "󰚩 Ergo"  -- Nerd font icon
    else
      vim.g.ergo_status = "󰚩 Ergo (paused)"
    end
  end
})

print("Ergo integration loaded - Use <leader>e* for commands")
```

### 4. Add to Neovim Initialization

Edit `/etc/nixos/neovimConfig/config/lua/nvim-0-init.lua` (or your main init file) and add:

```lua
-- Load Ergo integration
require('nvim-ergo')
```

Or if you have a separate plugins configuration loader, add it there.

### 5. Rebuild NixOS Configuration

```bash
# Rebuild to apply changes
sudo nixos-rebuild switch --flake /etc/nixos#
```

**Note:** Based on your CLAUDE.md rules, I'm NOT running this command automatically. You should review the changes and run it yourself.

## Verifying Installation

### 1. Check Plugin Loaded

Open Neovim and run:
```vim
:lua print(vim.inspect(require('ergo')))
```

Should show the Ergo module table.

### 2. Check Commands Available

```vim
:ErgoToggle
:ErgoExplainContext
:ErgoSummarizeWork
```

### 3. Check Context File Being Written

The plugin writes context to a JSON file:
```bash
cat ~/.local/share/ergo/nvim_context.json | jq
```

Should show something like:
```json
{
  "event_type": "nvim.buffer.enter",
  "timestamp": 1710789456,
  "file_path": "/path/to/ergo/ergo/src/main.rs",
  "language": "rust",
  "cursor": {
    "line": 42,
    "col": 10
  },
  "total_lines": 200,
  "diagnostics": {
    "error_count": 0,
    "warning_count": 2,
    "total_count": 2
  }
}
```

## Permission Controls

### What the Plugin Can Access

The plugin has permission to read:
-  Current buffer file path
-  Cursor position
-  Language/filetype
-  LSP diagnostics
-  Visual selections (when you select text)
-  Line counts

The plugin **CANNOT** read:
-  File contents (unless you explicitly send them via commands)
-  Other buffers (only the active one)
-  Files outside Neovim
-  Your filesystem

### Controlling Access

**Disable monitoring temporarily:**
```vim
:ErgoToggle
```

**Disable permanently in config:**
```lua
ergo.setup({
  enabled = false,  -- Don't send automatic context
  send_diagnostics = false,  -- Don't send errors/warnings
  send_selections = false,   -- Don't track selections
})
```

**Per-project control** - Add to `.nvim.lua` in project root:
```lua
-- Disable Ergo for this project
if pcall(require, 'ergo') then
  require('ergo').config.enabled = false
end
```

## Keybindings Reference

All commands use the `<leader>e` prefix (by default `<leader>` is `\` or `Space`):

| Key | Command | Description |
|-----|---------|-------------|
| `<leader>ee` | ErgoExplainContext | Explain what you're working on |
| `<leader>es` | ErgoSummarizeWork | Summarize last hour of work |
| `<leader>ej` | ErgoJudgeThisCode | Code review of visible code |
| `<leader>ec` | ErgoCommitReview | Review staged git changes |
| `<leader>et` | ErgoToggle | Toggle monitoring on/off |
| `<leader>ea` | (visual mode) | Analyze selected code |

## Customizing Keybindings

If you prefer different keys, edit `/etc/nixos/neovimConfig/config/lua/nvim-ergo.lua`:

```lua
-- Example: Use <leader>a instead of <leader>e
vim.keymap.set('n', '<leader>ax', '<cmd>ErgoExplainContext<CR>', opts)
vim.keymap.set('n', '<leader>as', '<cmd>ErgoSummarizeWork<CR>', opts)
-- etc...
```

Or use function keys:
```lua
vim.keymap.set('n', '<F9>', '<cmd>ErgoExplainContext<CR>', opts)
```

## Integration with Which-Key

If you use which-key (which you have installed), add to your which-key config:

```lua
local wk = require("which-key")
wk.register({
  e = {
    name = "Ergo AI",
    e = "Explain context",
    s = "Summarize work",
    j = "Judge code",
    c = "Review commit",
    t = "Toggle monitoring",
  },
}, { prefix = "<leader>" })
```

## Troubleshooting

### Plugin not loading

**Check if plugin is in runtimepath:**
```vim
:echo &runtimepath
```

Should include a path with `ergo-nvim`.

**Check for Lua errors:**
```vim
:messages
```

### Commands not working

**Verify Ergo orchestrator is running:**
```bash
curl http://127.0.0.1:8765/health
```

Should return JSON with status.

**Check socket path:**
```bash
ls -la /tmp/ergo-nvim.sock
```

### Context not being sent

**Check the context file:**
```bash
watch -n 1 cat ~/.local/share/ergo/nvim_context.json
```

Should update every 5 seconds when Neovim is focused.

**Enable debug logging in plugin:**
```lua
ergo.setup({
  -- ... other options ...
  debug = true,  -- Add this
})
```

## Advanced: Real Unix Socket Implementation

The current plugin writes to a JSON file. For better performance, implement real Unix socket communication:

```lua
-- In nvim-ergo.lua, replace the send_buffer_context function:

function M.send_buffer_context()
  if not M.config.enabled then return end

  local context = M.get_buffer_context()
  local ok, encoded = pcall(vim.json.encode, context)

  if not ok then return end

  -- Use Neovim's built-in socket support
  local socket = vim.loop.new_tcp()
  socket:connect("/tmp/ergo-nvim.sock", function(err)
    if err then
      vim.notify("Ergo: " .. err, vim.log.levels.WARN)
      return
    end

    socket:write(encoded .. "\n", function(err)
      if err then
        vim.notify("Ergo: Failed to send context", vim.log.levels.WARN)
      end
      socket:close()
    end)
  end)
end
```

## Privacy & Security

### What Gets Sent to Ergo

**Automatic (every 5 seconds):**
- File path you're editing
- Language/filetype
- Cursor position
- Line count
- Diagnostic counts (number of errors/warnings, not messages)

**Manual (only when you run commands):**
- Visible code (for `:ErgoJudgeThisCode`)
- Selected text (for visual mode analysis)
- Git diff (for `:ErgoCommitReview`)

### What Never Gets Sent

- File contents (automatically)
- Closed buffers
- Other windows/tabs
- Filesystem outside Neovim
- Sensitive files (filtered by privacy patterns in .env)

### Respecting Privacy Filters

The Ergo daemon will filter out files matching:
```bash
# From your .env
PRIVACY_IGNORE_PATTERNS=password,token,secret,.env,bitwarden,keepass,vault,credentials
```

Even if Neovim sends context for these files, the daemon will ignore them.

## Next Steps

1.  Install plugin via plugins.nix
2.  Create nvim-ergo.lua configuration
3.  Rebuild NixOS: `sudo nixos-rebuild switch`
4.  Start Neovim and test `:ErgoToggle`
5.  Ensure orchestrator is running: `python3 orchestrator/src/main.py`
6.  Try a command: `:ErgoExplainContext`

For more information, see:
- `PERMISSIONS.md` - Full permission documentation
- `SETUP_PERMISSIONS.md` - Quick setup guide
- `RUNNING.md` - How to run all Ergo services
