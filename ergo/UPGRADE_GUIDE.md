# Ergo v2.0 Upgrade Guide

## What's New

### 1. Non-Blocking Async Commands
- All commands now use `jobstart()` instead of `system()`
- Neovim won't freeze during API calls
- Loading indicators show progress

### 2. Floating Window UI
- Responses appear in centered floating windows
- Press `q` or `Esc` to close
- Markdown syntax highlighting
- Professional, non-intrusive display

### 3. Passive Monitoring with Personality
- Background analysis of your coding patterns
- Occasional helpful insights (top-right notifications)
- Three personality modes:
  - **quiet**: Minimal notifications, brief messages
  - **standard**: Balanced, helpful insights  
  - **verbose**: More frequent, detailed feedback

### 4. Interactive Chat
- New `:ErgoChat` command opens chat buffer
- Type message and press Enter to send
- Chat history preserved in buffer
- Async communication (non-blocking)

## New Files Created

```
nvim-plugin/lua/ergo/
├── init.lua      # Main plugin (updated)
├── ui.lua        # Floating windows
├── async.lua     # Non-blocking API calls
└── passive.lua   # Background monitoring
```

## Updated Configuration

Edit `/etc/nixos/neovimConfig/config/lua/ergo-config.lua` with sudo:

```lua
  -- Ergo AI Assistant Configuration v2.0
  local status_ok, ergo = pcall(require, "ergo")
  if not status_ok then
    vim.notify("Ergo plugin not found", vim.log.levels.WARN)
    return
  end

  -- Configure the plugin with new features
  ergo.setup({
    api_url = "http://127.0.0.1:8765",
    enabled = true,
    personality = "standard",  -- Options: quiet, standard, verbose
    passive_monitoring = true,
    passive_check_interval = 60000,  -- Check every 60s
    auto_report_interval = 5000,
    send_diagnostics = true,
    send_selections = true,
  })

  -- Keybindings
  local opts = { noremap = true, silent = true }

  -- Main commands (async, non-blocking)
  vim.keymap.set('n', '<leader>ee', '<cmd>ErgoExplainContext<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Explain context" }))

  vim.keymap.set('n', '<leader>es', '<cmd>ErgoSummarizeWork<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Summarize work" }))

  vim.keymap.set('n', '<leader>ej', '<cmd>ErgoJudgeCode<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Judge code" }))

  vim.keymap.set('n', '<leader>ec', '<cmd>ErgoCommitReview<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Review commit" }))

  vim.keymap.set('n', '<leader>eC', '<cmd>ErgoChat<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Open chat" }))

  vim.keymap.set('n', '<leader>ei', '<cmd>ErgoInsight<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Request insight" }))

  -- Toggle commands
  vim.keymap.set('n', '<leader>et', '<cmd>ErgoToggle<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Toggle monitoring" }))

  vim.keymap.set('n', '<leader>ep', '<cmd>ErgoPassiveToggle<CR>',
    vim.tbl_extend('force', opts, { desc = "Ergo: Toggle passive monitoring" }))

  print("Ergo v2.0 configuration loaded (async + passive monitoring)")
```

## Installation Steps

1. **Commit local changes to GitHub:**
   ```bash
   cd ~/Documents/Github/Ergo/ergo
   git add nvim-plugin/lua/ergo/
   git commit -m "feat: v2.0 - async commands, floating UI, passive monitoring"
   git push origin main
   ```

2. **Update NixOS config sha256:**
   ```bash
   # Get new commit hash
   git rev-parse HEAD
   
   # Update /etc/nixos/neovimConfig/plugins.nix with:
   # - new rev = "your-new-commit-hash"
   # - Update sha256 (will fail first, use error message hash)
   ```

3. **Update ergo-config.lua:**
   ```bash
   sudo nano /etc/nixos/neovimConfig/config/lua/ergo-config.lua
   # Paste the new configuration from above
   ```

4. **Rebuild NixOS:**
   ```bash
   sudo nixos-rebuild switch
   ```

## New Commands

| Command | Keybinding | Description |
|---------|------------|-------------|
| `:ErgoExplainContext` | `<leader>ee` | Explain current context (async) |
| `:ErgoSummarizeWork` | `<leader>es` | Summarize recent work |
| `:ErgoJudgeCode` | `<leader>ej` | Review visible code |
| `:ErgoCommitReview` | `<leader>ec` | Review git commit |
| `:ErgoChat` | `<leader>eC` | Open interactive chat |
| `:ErgoInsight` | `<leader>ei` | Request contextual insight |
| `:ErgoToggle` | `<leader>et` | Toggle monitoring on/off |
| `:ErgoPassiveToggle` | `<leader>ep` | Toggle passive monitoring |
| `:ErgoPersonality {mode}` | - | Set personality (quiet/standard/verbose) |

## Passive Monitoring Features

When enabled, Ergo will:
- Track your coding patterns
- Detect when you're stuck on a file
- Notice idle time
- Celebrate milestones (1 hour, 2 hours)
- Suggest breaks
- Show insights in top-right corner

All notifications auto-dismiss and are non-intrusive.

## Testing

After installation:

1. **Test async commands:**
   ```vim
   :ErgoExplainContext
   " Should see loading indicator, then floating window
   " Neovim should NOT freeze
   ```

2. **Test chat:**
   ```vim
   :ErgoChat
   " Type a message, press Enter
   " Should see response without blocking
   ```

3. **Test passive monitoring:**
   ```vim
   :ErgoInsight
   " Should see notification in top-right
   " Wait 1-2 minutes for automatic insights
   ```

4. **Test personality:**
   ```vim
   :ErgoPersonality quiet
   :ErgoPersonality verbose
   ```

## Troubleshooting

**Commands not found:**
- Ensure orchestrator is running: `http://127.0.0.1:8765/health`
- Check plugin loaded: `:lua print(vim.inspect(require('ergo')))`

**Still blocking:**
- Verify you're using the new plugin version
- Check git commit is pulled in NixOS config

**No passive insights:**
- Check enabled: `:ErgoPassiveToggle`
- Set verbose: `:ErgoPersonality verbose`

**Module not found errors:**
- Rebuild NixOS after git push
- Verify all 4 files exist in nvim-plugin/lua/ergo/
