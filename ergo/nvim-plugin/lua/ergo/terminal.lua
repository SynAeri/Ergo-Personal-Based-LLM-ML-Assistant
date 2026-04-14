-- Ergo Terminal - Two-pane chat interface connecting to orchestrator at 127.0.0.1:8765
-- Top pane: read-only history. Bottom pane: input line. Enter sends, Esc closes.

local M = {}

-- State: two buffers, two windows
M.state = {
  history_buf = nil,
  input_buf = nil,
  history_win = nil,
  input_win = nil,
  waiting = false,  -- block double-sends while response pending
}

-- Personality from init.lua config (can be overridden by :ErgoPersonality)
M.personality = 'standard'

local SEPARATOR = string.rep('─', 58)

--- Append lines to history buffer and scroll to bottom
local function history_append(lines)
  if not M.state.history_buf or not vim.api.nvim_buf_is_valid(M.state.history_buf) then
    return
  end
  vim.api.nvim_buf_set_option(M.state.history_buf, 'modifiable', true)
  local count = vim.api.nvim_buf_line_count(M.state.history_buf)
  vim.api.nvim_buf_set_lines(M.state.history_buf, count, count, false, lines)
  vim.api.nvim_buf_set_option(M.state.history_buf, 'modifiable', false)

  -- Scroll history window to bottom
  if M.state.history_win and vim.api.nvim_win_is_valid(M.state.history_win) then
    local new_count = vim.api.nvim_buf_line_count(M.state.history_buf)
    vim.api.nvim_win_set_cursor(M.state.history_win, { new_count, 0 })
  end
end

--- Replace last line in history (used to swap "thinking..." with actual response)
local function history_replace_last(lines)
  if not M.state.history_buf or not vim.api.nvim_buf_is_valid(M.state.history_buf) then
    return
  end
  vim.api.nvim_buf_set_option(M.state.history_buf, 'modifiable', true)
  local count = vim.api.nvim_buf_line_count(M.state.history_buf)
  -- Replace the last line (the "thinking..." line)
  vim.api.nvim_buf_set_lines(M.state.history_buf, count - 1, count, false, lines)
  vim.api.nvim_buf_set_option(M.state.history_buf, 'modifiable', false)

  if M.state.history_win and vim.api.nvim_win_is_valid(M.state.history_win) then
    local new_count = vim.api.nvim_buf_line_count(M.state.history_buf)
    vim.api.nvim_win_set_cursor(M.state.history_win, { new_count, 0 })
  end
end

--- Close all chat windows
local function close_all()
  if M.state.history_win and vim.api.nvim_win_is_valid(M.state.history_win) then
    vim.api.nvim_win_close(M.state.history_win, true)
  end
  if M.state.input_win and vim.api.nvim_win_is_valid(M.state.input_win) then
    vim.api.nvim_win_close(M.state.input_win, true)
  end
  M.state.history_win = nil
  M.state.input_win = nil
  M.state.history_buf = nil
  M.state.input_buf = nil
  M.state.waiting = false
end

--- Word-wrap a string into lines with a prefix, respecting max_width
local function wrap_text(text, prefix, max_width)
  local result = {}
  for para in (text .. '\n'):gmatch('([^\n]*)\n') do
    if para == '' then
      table.insert(result, '')
    else
      local line = prefix
      for word in para:gmatch('%S+') do
        if #line + 1 + #word > max_width and line ~= prefix then
          table.insert(result, line)
          line = prefix .. word
        else
          line = (line == prefix) and (prefix .. word) or (line .. ' ' .. word)
        end
      end
      if line ~= prefix then
        table.insert(result, line)
      end
    end
  end
  return result
end

--- Send the current input line to Ergo
function M.send_message()
  if M.state.waiting then return end
  if not M.state.input_buf or not vim.api.nvim_buf_is_valid(M.state.input_buf) then
    return
  end

  local lines = vim.api.nvim_buf_get_lines(M.state.input_buf, 0, -1, false)
  local message = vim.trim(table.concat(lines, ' '))

  if message == '' then return end

  -- Clear input
  vim.api.nvim_buf_set_option(M.state.input_buf, 'modifiable', true)
  vim.api.nvim_buf_set_lines(M.state.input_buf, 0, -1, false, { '' })
  vim.api.nvim_buf_set_option(M.state.input_buf, 'modifiable', false)

  -- Re-enable input modifiable for typing (it gets locked above, re-enable now)
  vim.api.nvim_buf_set_option(M.state.input_buf, 'modifiable', true)

  M.state.waiting = true

  local width = vim.api.nvim_win_get_width(M.state.history_win or 0)
  local max_w = math.max(40, width - 4)

  -- Append user turn to history
  local user_lines = wrap_text(message, '  you  │ ', max_w)
  history_append({ SEPARATOR })
  history_append(user_lines)
  history_append({ '' })
  -- Placeholder for Ergo response (will be replaced)
  history_append({ ' ergo  │ thinking...' })

  local async = require('ergo.async')
  async.send_chat(message, true, M.personality, function(response, err)
    vim.schedule(function()
      M.state.waiting = false

      local response_text = err and ('Error: ' .. err) or response
      local ergo_lines = wrap_text(response_text, ' ergo  │ ', max_w)

      -- Replace the "thinking..." placeholder
      history_replace_last(ergo_lines)
      history_append({ '' })

      -- Focus input and enter insert mode
      if M.state.input_win and vim.api.nvim_win_is_valid(M.state.input_win) then
        vim.api.nvim_set_current_win(M.state.input_win)
        vim.cmd('startinsert')
      end
    end)
  end)
end

--- Open or close the chat interface
function M.toggle()
  -- Close if already open
  if M.state.history_win and vim.api.nvim_win_is_valid(M.state.history_win) then
    close_all()
    return
  end

  local total_w = math.floor(vim.o.columns * 0.82)
  local total_h = math.floor(vim.o.lines * 0.82)
  local row = math.floor((vim.o.lines - total_h) / 2)
  local col = math.floor((vim.o.columns - total_w) / 2)

  local input_h = 3  -- border top + 1 line + border bottom
  local history_h = total_h - input_h - 1  -- 1 gap between panes

  -- ── History buffer (read-only) ──────────────────────────────────────
  M.state.history_buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(M.state.history_buf, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(M.state.history_buf, 'buftype', 'nofile')
  vim.api.nvim_buf_set_option(M.state.history_buf, 'filetype', 'ergo-chat')
  vim.api.nvim_buf_set_option(M.state.history_buf, 'modifiable', false)

  M.state.history_win = vim.api.nvim_open_win(M.state.history_buf, false, {
    relative = 'editor',
    width = total_w,
    height = history_h,
    row = row,
    col = col,
    style = 'minimal',
    border = 'rounded',
    title = '  ergo ',
    title_pos = 'left',
  })

  vim.api.nvim_win_set_option(M.state.history_win, 'wrap', true)
  vim.api.nvim_win_set_option(M.state.history_win, 'cursorline', false)
  vim.api.nvim_win_set_option(M.state.history_win, 'scrolloff', 3)

  -- Seed history with greeting
  history_append({
    '',
    ' ergo  │ Hey. What do you need?',
    '',
  })

  -- ── Input buffer ────────────────────────────────────────────────────
  M.state.input_buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(M.state.input_buf, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(M.state.input_buf, 'buftype', 'nofile')
  vim.api.nvim_buf_set_option(M.state.input_buf, 'filetype', 'ergo-input')

  M.state.input_win = vim.api.nvim_open_win(M.state.input_buf, true, {
    relative = 'editor',
    width = total_w,
    height = 1,
    row = row + history_h + 1,
    col = col,
    style = 'minimal',
    border = 'rounded',
    title = '  message ',
    title_pos = 'left',
    footer = '  <CR> send   <Esc> close ',
    footer_pos = 'right',
  })

  vim.api.nvim_win_set_option(M.state.input_win, 'wrap', false)

  -- ── Keymaps ─────────────────────────────────────────────────────────
  local function mk(buf, mode, key, fn)
    vim.keymap.set(mode, key, fn, { buffer = buf, noremap = true, silent = true })
  end

  -- Input keymaps
  mk(M.state.input_buf, 'i', '<CR>', function() M.send_message() end)
  mk(M.state.input_buf, 'n', '<CR>', function() M.send_message() end)
  mk(M.state.input_buf, 'i', '<Esc>', function()
    vim.cmd('stopinsert')
    close_all()
  end)
  mk(M.state.input_buf, 'n', '<Esc>', close_all)
  -- Allow multi-line input with S-CR (shift-enter inserts newline)
  mk(M.state.input_buf, 'i', '<S-CR>', function()
    vim.api.nvim_buf_set_option(M.state.input_buf, 'modifiable', true)
    vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes('<CR>', true, false, true), 'n', false)
  end)

  -- History keymaps (navigate but can't edit)
  mk(M.state.history_buf, 'n', '<Esc>', close_all)
  mk(M.state.history_buf, 'n', 'q', close_all)
  -- Tab to jump between panes
  mk(M.state.history_buf, 'n', '<Tab>', function()
    if M.state.input_win and vim.api.nvim_win_is_valid(M.state.input_win) then
      vim.api.nvim_set_current_win(M.state.input_win)
      vim.cmd('startinsert')
    end
  end)
  mk(M.state.input_buf, 'n', '<Tab>', function()
    if M.state.history_win and vim.api.nvim_win_is_valid(M.state.history_win) then
      vim.api.nvim_set_current_win(M.state.history_win)
    end
  end)

  -- Auto-close if either window loses focus via BufLeave
  vim.api.nvim_create_autocmd('BufLeave', {
    buffer = M.state.input_buf,
    callback = function()
      vim.schedule(function()
        -- Only close if focus went outside both panes
        local cur_win = vim.api.nvim_get_current_win()
        if cur_win ~= M.state.history_win and cur_win ~= M.state.input_win then
          close_all()
        end
      end)
    end,
    once = true,
  })

  -- Start in insert mode on the input pane
  vim.cmd('startinsert')
end

return M
