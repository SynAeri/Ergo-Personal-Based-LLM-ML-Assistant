-- Ergo Terminal - Floating terminal with Ergo branding
-- Mimics Claude's terminal style but with Ergo's identity

local M = {}

-- Terminal state
M.state = {
  buf = nil,
  win = nil,
  term_chan = nil,
}

--- Create fancy Ergo logo banner
local function get_ergo_banner()
  return {
    "╔═══════════════════════════════════════════════════════════╗",
    "║                                                           ║",
    "║     ███████╗ ██████╗  ██████╗  ██████╗                   ║",
    "║     ██╔════╝ ██╔══██╗ ██╔════╝ ██╔═══██╗                 ║",
    "║     █████╗   ██████╔╝ ██║  ███╗██║   ██║                 ║",
    "║     ██╔══╝   ██╔══██╗ ██║   ██║██║   ██║                 ║",
    "║     ███████╗ ██║  ██║ ╚██████╔╝╚██████╔╝                 ║",
    "║     ╚══════╝ ╚═╝  ╚═╝  ╚═════╝  ╚═════╝                  ║",
    "║                                                           ║",
    "║              Your Local AI Assistant                     ║",
    "║                                                           ║",
    "╚═══════════════════════════════════════════════════════════╝",
    "",
    "  Type 'exit' or press <Esc> to close",
    "  Press 'i' to start typing commands",
    "",
  }
end

--- Create or toggle the Ergo floating terminal
function M.toggle()
  -- If terminal is open, close it
  if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
    vim.api.nvim_win_close(M.state.win, true)
    M.state.win = nil
    return
  end

  -- Calculate dimensions (80% of screen)
  local width = math.floor(vim.o.columns * 0.8)
  local height = math.floor(vim.o.lines * 0.8)

  -- Calculate center position
  local row = math.floor((vim.o.lines - height) / 2)
  local col = math.floor((vim.o.columns - width) / 2)

  -- Create or reuse buffer
  if not M.state.buf or not vim.api.nvim_buf_is_valid(M.state.buf) then
    M.state.buf = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_option(M.state.buf, 'bufhidden', 'hide')
    vim.api.nvim_buf_set_option(M.state.buf, 'filetype', 'ergo-terminal')
  end

  -- Window configuration
  local win_opts = {
    relative = 'editor',
    width = width,
    height = height,
    row = row,
    col = col,
    style = 'minimal',
    border = 'rounded',
    title = ' Ergo Terminal ',
    title_pos = 'center',
  }

  -- Open the window
  M.state.win = vim.api.nvim_open_win(M.state.buf, true, win_opts)

  -- Set window options
  vim.api.nvim_win_set_option(M.state.win, 'winblend', 0)
  vim.api.nvim_win_set_option(M.state.win, 'winhighlight', 'Normal:Normal,FloatBorder:FloatBorder')

  -- If terminal channel doesn't exist, create it
  if not M.state.term_chan then
    -- Show banner first
    local banner = get_ergo_banner()
    vim.api.nvim_buf_set_lines(M.state.buf, 0, -1, false, banner)

    -- Wait a moment then start terminal
    vim.defer_fn(function()
      if vim.api.nvim_buf_is_valid(M.state.buf) then
        -- Clear banner and start terminal
        vim.api.nvim_buf_set_lines(M.state.buf, 0, -1, false, {})

        -- Start terminal
        vim.fn.termopen(vim.o.shell, {
          on_exit = function()
            M.state.term_chan = nil
            if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
              vim.api.nvim_win_close(M.state.win, true)
              M.state.win = nil
            end
          end,
        })

        M.state.term_chan = vim.b.terminal_job_id

        -- Enter insert mode automatically
        vim.cmd('startinsert')
      end
    end, 800)  -- Show banner for 800ms
  else
    -- Terminal already exists, just enter insert mode
    vim.cmd('startinsert')
  end

  -- Set up keymaps for the terminal buffer
  local opts = { buffer = M.state.buf, noremap = true, silent = true }

  -- <Esc> to close terminal
  vim.keymap.set('t', '<Esc>', function()
    if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
      vim.api.nvim_win_close(M.state.win, true)
      M.state.win = nil
    end
  end, opts)

  -- <C-h/j/k/l> for window navigation from terminal
  vim.keymap.set('t', '<C-h>', '<C-\\><C-n><C-w>h', opts)
  vim.keymap.set('t', '<C-j>', '<C-\\><C-n><C-w>j', opts)
  vim.keymap.set('t', '<C-k>', '<C-\\><C-n><C-w>k', opts)
  vim.keymap.set('t', '<C-l>', '<C-\\><C-n><C-w>l', opts)

  -- Auto-close when leaving buffer
  vim.api.nvim_create_autocmd('BufLeave', {
    buffer = M.state.buf,
    callback = function()
      if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
        vim.api.nvim_win_close(M.state.win, true)
        M.state.win = nil
      end
    end,
    once = true,
  })
end

--- Send a command to the terminal
function M.send_command(cmd)
  if M.state.term_chan then
    vim.fn.chansend(M.state.term_chan, cmd .. '\n')
  end
end

--- Create a minimal version (no banner, instant open)
function M.quick_toggle()
  -- If terminal is open, close it
  if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
    vim.api.nvim_win_close(M.state.win, true)
    M.state.win = nil
    return
  end

  -- Calculate dimensions
  local width = math.floor(vim.o.columns * 0.8)
  local height = math.floor(vim.o.lines * 0.8)
  local row = math.floor((vim.o.lines - height) / 2)
  local col = math.floor((vim.o.columns - width) / 2)

  -- Create buffer if needed
  if not M.state.buf or not vim.api.nvim_buf_is_valid(M.state.buf) then
    M.state.buf = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_option(M.state.buf, 'bufhidden', 'hide')
  end

  -- Open window
  local win_opts = {
    relative = 'editor',
    width = width,
    height = height,
    row = row,
    col = col,
    style = 'minimal',
    border = 'rounded',
    title = ' Ergo Terminal ',
    title_pos = 'center',
  }

  M.state.win = vim.api.nvim_open_win(M.state.buf, true, win_opts)

  -- Start terminal if not already running
  if not M.state.term_chan then
    vim.fn.termopen(vim.o.shell)
    M.state.term_chan = vim.b.terminal_job_id
  end

  vim.cmd('startinsert')
end

return M
