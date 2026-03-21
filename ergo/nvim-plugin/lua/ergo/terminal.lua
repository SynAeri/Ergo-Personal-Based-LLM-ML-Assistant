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

--- Create or toggle the Ergo chat-style terminal
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

  -- Create a chat buffer (not terminal buffer)
  M.state.buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(M.state.buf, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(M.state.buf, 'buftype', 'nofile')
  vim.api.nvim_buf_set_option(M.state.buf, 'filetype', 'markdown')

  -- Window configuration (minimalistic)
  local win_opts = {
    relative = 'editor',
    width = width,
    height = height,
    row = row,
    col = col,
    style = 'minimal',
    border = 'single',
    title = ' ergo ',
    title_pos = 'left',
  }

  -- Open the window
  M.state.win = vim.api.nvim_open_win(M.state.buf, true, win_opts)

  -- Set up chat-style interface
  local welcome_lines = {
    '',
    '  Ergo Assistant',
    '',
    '  Type your message below and press <C-CR> to send',
    '  Press <Esc> to close',
    '',
    '─────────────────────────────────────────────────────',
    '',
  }

  vim.api.nvim_buf_set_lines(M.state.buf, 0, -1, false, welcome_lines)
  vim.api.nvim_win_set_cursor(M.state.win, {#welcome_lines, 0})

  -- Enter insert mode automatically
  vim.cmd('startinsert')

  -- Set up keymaps for the chat buffer
  local opts = { buffer = M.state.buf, noremap = true, silent = true }

  -- <Esc> to close window
  vim.keymap.set('n', '<Esc>', function()
    if M.state.win and vim.api.nvim_win_is_valid(M.state.win) then
      vim.api.nvim_win_close(M.state.win, true)
      M.state.win = nil
    end
  end, opts)

  -- <C-CR> to send message (both insert and normal mode)
  vim.keymap.set('i', '<C-CR>', function()
    M.send_message()
  end, opts)

  vim.keymap.set('n', '<C-CR>', function()
    M.send_message()
  end, opts)

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

--- Send a message to Ergo
function M.send_message()
  if not M.state.buf or not vim.api.nvim_buf_is_valid(M.state.buf) then
    return
  end

  -- Get all lines in buffer
  local lines = vim.api.nvim_buf_get_lines(M.state.buf, 0, -1, false)

  -- Find the separator line (where user input starts)
  local separator_line = 0
  for i, line in ipairs(lines) do
    if line:match('^─+$') then
      separator_line = i
      break
    end
  end

  -- Get user message (everything after separator)
  local message_lines = {}
  for i = separator_line + 2, #lines do  -- +2 to skip separator and empty line
    table.insert(message_lines, lines[i])
  end

  local user_message = table.concat(message_lines, '\n'):gsub('^%s+', ''):gsub('%s+$', '')

  if user_message == '' then
    return
  end

  -- Add user message to chat
  vim.api.nvim_buf_set_option(M.state.buf, 'modifiable', true)
  local cursor_line = vim.api.nvim_buf_line_count(M.state.buf)

  vim.api.nvim_buf_set_lines(M.state.buf, separator_line, -1, false, {
    '─────────────────────────────────────────────────────',
    '',
    '  You: ' .. user_message,
    '',
    '  Ergo: thinking...',
    '',
  })

  -- Load async module and send to Ergo
  local async = require('ergo.async')
  async.send_chat(user_message, true, 'standard', function(response, err)
    if not M.state.buf or not vim.api.nvim_buf_is_valid(M.state.buf) then
      return
    end

    vim.schedule(function()
      -- Replace "thinking..." with actual response
      local current_lines = vim.api.nvim_buf_get_lines(M.state.buf, 0, -1, false)
      local thinking_line = 0

      for i, line in ipairs(current_lines) do
        if line:match('thinking%.%.%.') then
          thinking_line = i
          break
        end
      end

      if thinking_line > 0 then
        local response_text = err and ('Error: ' .. err) or response

        -- Word wrap the response
        local wrapped_lines = {}
        for para in response_text:gmatch('[^\n]+') do
          local words = {}
          for word in para:gmatch('%S+') do
            table.insert(words, word)
          end

          local current_line = '  '
          for _, word in ipairs(words) do
            if #current_line + #word + 1 <= 60 then
              current_line = current_line .. ' ' .. word
            else
              table.insert(wrapped_lines, current_line)
              current_line = '  ' .. word
            end
          end
          if current_line ~= '  ' then
            table.insert(wrapped_lines, current_line)
          end
        end

        vim.api.nvim_buf_set_lines(M.state.buf, thinking_line - 1, thinking_line, false, wrapped_lines)

        -- Add input prompt for next message
        local line_count = vim.api.nvim_buf_line_count(M.state.buf)
        vim.api.nvim_buf_set_lines(M.state.buf, line_count, line_count, false, {
          '',
          '─────────────────────────────────────────────────────',
          '',
        })

        -- Move cursor to end
        vim.api.nvim_win_set_cursor(M.state.win, {vim.api.nvim_buf_line_count(M.state.buf), 0})
      end
    end)
  end)
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
