-- Ergo UI module - Floating windows and visual display
-- Handles all UI components for displaying AI responses

local M = {}

-- Store active windows
M.active_windows = {}

--- Create a centered floating window
-- @param opts table Options: width, height, title, filetype
-- @return bufnr, winid
function M.create_float(opts)
  opts = opts or {}
  local width = opts.width or math.floor(vim.o.columns * 0.6)
  local height = opts.height or math.floor(vim.o.lines * 0.6)
  
  -- Calculate center position
  local row = math.floor((vim.o.lines - height) / 2)
  local col = math.floor((vim.o.columns - width) / 2)
  
  -- Create buffer
  local bufnr = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(bufnr, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(bufnr, 'filetype', opts.filetype or 'markdown')
  
  -- Window configuration
  local win_opts = {
    relative = 'editor',
    width = width,
    height = height,
    row = row,
    col = col,
    style = 'minimal',
    border = 'rounded',
    title = opts.title or 'Ergo',
    title_pos = 'center',
  }
  
  -- Create window
  local winid = vim.api.nvim_open_win(bufnr, true, win_opts)
  
  -- Set window options
  vim.api.nvim_win_set_option(winid, 'wrap', true)
  vim.api.nvim_win_set_option(winid, 'linebreak', true)
  vim.api.nvim_win_set_option(winid, 'cursorline', true)
  
  -- Add keymaps to close window
  local close_keys = {'q', '<Esc>'}
  for _, key in ipairs(close_keys) do
    vim.api.nvim_buf_set_keymap(bufnr, 'n', key,
      ':close<CR>',
      {nowait = true, noremap = true, silent = true})
  end
  
  return bufnr, winid
end

--- Show response in floating window
-- @param content string|table Content to display
-- @param opts table Options: title, filetype
function M.show_response(content, opts)
  opts = opts or {}
  
  -- Convert to lines if string
  local lines
  if type(content) == 'string' then
    lines = vim.split(content, '\n')
  else
    lines = content
  end
  
  -- Create floating window
  local bufnr, winid = M.create_float(opts)
  
  -- Set content
  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, lines)
  vim.api.nvim_buf_set_option(bufnr, 'modifiable', false)
  
  -- Store window
  table.insert(M.active_windows, {bufnr = bufnr, winid = winid})
  
  return bufnr, winid
end

--- Show loading indicator
-- @param message string Loading message
function M.show_loading(message)
  message = message or 'Loading...'
  
  local lines = {
    '',
    '  ' .. message,
    '',
    '  [Press q to cancel]',
  }
  
  local bufnr, winid = M.create_float({
    width = 40,
    height = 6,
    title = 'Ergo',
  })
  
  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, lines)
  vim.api.nvim_buf_set_option(bufnr, 'modifiable', false)
  
  return bufnr, winid
end

--- Show inline notification (like LSP hover)
-- @param content string Content to show
-- @param row number Row position (0-indexed)
-- @param col number Column position (0-indexed)
function M.show_inline_notification(content, row, col)
  local lines = vim.split(content, '\n')
  
  -- Calculate dimensions
  local width = 0
  for _, line in ipairs(lines) do
    width = math.max(width, #line)
  end
  width = math.min(width + 4, 60)
  local height = math.min(#lines + 2, 10)
  
  -- Create buffer
  local bufnr = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(bufnr, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(bufnr, 'filetype', 'markdown')
  
  -- Pad lines
  local padded_lines = {}
  table.insert(padded_lines, '')
  for _, line in ipairs(lines) do
    table.insert(padded_lines, '  ' .. line)
  end
  table.insert(padded_lines, '')
  
  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, padded_lines)
  
  -- Window configuration
  local win_opts = {
    relative = 'cursor',
    width = width,
    height = height,
    row = 1,
    col = 0,
    style = 'minimal',
    border = 'rounded',
  }
  
  -- Create window
  local winid = vim.api.nvim_open_win(bufnr, false, win_opts)
  vim.api.nvim_win_set_option(winid, 'wrap', true)
  
  -- Auto-close after 5 seconds
  vim.defer_fn(function()
    if vim.api.nvim_win_is_valid(winid) then
      vim.api.nvim_win_close(winid, true)
    end
  end, 5000)
  
  return bufnr, winid
end

--- Show passive insight notification (top-left corner)
-- @param message string Insight message
-- @param personality string Personality type (quiet, standard, verbose)
function M.show_passive_insight(message, personality)
  personality = personality or 'standard'

  -- Format message based on personality
  local prefix = ''
  if personality == 'quiet' then
    prefix = '[Ergo] '
  elseif personality == 'standard' then
    prefix = '[Ergo] 💡 '
  else
    prefix = '[Ergo Assistant] 💡 '
  end

  local full_message = prefix .. message
  local lines = vim.split(full_message, '\n')

  -- Calculate dimensions
  local width = 0
  for _, line in ipairs(lines) do
    width = math.max(width, #line)
  end
  width = math.min(width + 4, 50)
  local height = #lines + 2

  -- Create buffer
  local bufnr = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(bufnr, 'bufhidden', 'wipe')

  -- Pad lines
  local padded_lines = {}
  table.insert(padded_lines, '')
  for _, line in ipairs(lines) do
    table.insert(padded_lines, '  ' .. line)
  end
  table.insert(padded_lines, '')

  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, padded_lines)
  vim.api.nvim_buf_set_option(bufnr, 'modifiable', false)

  -- Check for neo-tree or other sidebars and adjust column position
  local col_offset = 2

  -- Check all windows for neo-tree
  for _, win in ipairs(vim.api.nvim_list_wins()) do
    local buf = vim.api.nvim_win_get_buf(win)
    local ft = vim.api.nvim_buf_get_option(buf, 'filetype')

    -- If neo-tree is on the left, offset our window
    if ft == 'neo-tree' then
      local win_config = vim.api.nvim_win_get_config(win)
      if win_config.relative == '' then  -- It's a regular window, not floating
        local win_width = vim.api.nvim_win_get_width(win)
        col_offset = win_width + 4  -- Position after neo-tree with margin
        break
      end
    end
  end

  -- Window configuration (TOP-LEFT corner, respecting sidebars)
  local win_opts = {
    relative = 'editor',
    width = width,
    height = height,
    row = 2,  -- Below the top line
    col = col_offset,  -- Adjusted for sidebars
    style = 'minimal',
    border = 'rounded',
    focusable = false,  -- Can't focus with Tab or click
    zindex = 50,  -- Stay on top but not too high
  }

  -- Create window
  local winid = vim.api.nvim_open_win(bufnr, false, win_opts)

  -- Auto-close after duration based on personality
  local duration = personality == 'quiet' and 3000 or 8000
  vim.defer_fn(function()
    if vim.api.nvim_win_is_valid(winid) then
      vim.api.nvim_win_close(winid, true)
    end
  end, duration)

  return bufnr, winid
end

--- Create chat buffer
function M.create_chat_buffer()
  -- Create or reuse chat buffer
  local existing_buf = nil
  for _, buf in ipairs(vim.api.nvim_list_bufs()) do
    if vim.api.nvim_buf_get_name(buf):match('ergo%-chat') then
      existing_buf = buf
      break
    end
  end
  
  local bufnr = existing_buf or vim.api.nvim_create_buf(false, true)
  
  if not existing_buf then
    vim.api.nvim_buf_set_name(bufnr, 'ergo-chat')
    vim.api.nvim_buf_set_option(bufnr, 'buftype', 'nofile')
    vim.api.nvim_buf_set_option(bufnr, 'filetype', 'markdown')
    
    -- Add welcome message
    local welcome = {
      '# Ergo Chat',
      '',
      'Type your message below and press <CR> to send.',
      'Type `:ErgoChat` to close.',
      '',
      '---',
      '',
    }
    vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, welcome)
  end
  
  -- Open in split
  vim.cmd('botright split')
  vim.cmd('resize 15')
  vim.api.nvim_win_set_buf(0, bufnr)
  
  -- Set up chat keybindings
  vim.api.nvim_buf_set_keymap(bufnr, 'i', '<CR>',
    '<Esc>:lua require("ergo.async").send_chat_message()<CR>',
    {noremap = true, silent = true})
  
  return bufnr
end

--- Close all Ergo windows
function M.close_all()
  for _, win_info in ipairs(M.active_windows) do
    if vim.api.nvim_win_is_valid(win_info.winid) then
      vim.api.nvim_win_close(win_info.winid, true)
    end
  end
  M.active_windows = {}
end

return M
