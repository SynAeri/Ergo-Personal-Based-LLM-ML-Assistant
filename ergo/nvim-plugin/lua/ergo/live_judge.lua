-- Ergo Live Judge - Real-time code commentary
-- Provides snarky, helpful remarks as you write code
-- Triggers on specific events: function completion, imports, etc.

local M = {}
local async = require('ergo.async')
local ui = require('ergo.ui')

-- Configuration
M.config = {
  enabled = true,
  personality = 'verbose',  -- Uses the sass personality by default
  trigger_events = {
    function_complete = true,
    import_added = true,
    line_idle = true,  -- When you hover on a line for a while
  },
  idle_time = 2000,  -- 3 seconds of idle before checking
  min_lines_for_judgment = 3,  -- Minimum lines before judging
}

-- State tracking
M.state = {
  last_line_count = 0,
  last_cursor_pos = {0, 0},
  idle_timer = nil,
  last_judgment_line = 0,
  recently_judged = {},  -- Cache to avoid repeating same comments
}

--- Setup function
function M.setup(opts)
  opts = opts or {}
  M.config = vim.tbl_deep_extend('force', M.config, opts)
end

--- Start live judging
function M.start()
  if not M.config.enabled then
    return
  end

  -- Attach to buffer events
  vim.api.nvim_create_autocmd({'TextChanged', 'TextChangedI'}, {
    callback = function()
      M.on_text_changed()
    end,
  })

  vim.api.nvim_create_autocmd({'CursorHold', 'CursorHoldI'}, {
    callback = function()
      M.on_cursor_hold()
    end,
  })

  print('Ergo Live Judge: Watching your code...')
end

--- Stop live judging
function M.stop()
  M.config.enabled = false
  if M.state.idle_timer then
    M.state.idle_timer:stop()
    M.state.idle_timer = nil
  end
end

--- Detect what kind of code event just happened
function M.detect_code_event()
  local bufnr = vim.api.nvim_get_current_buf()
  local cursor = vim.api.nvim_win_get_cursor(0)
  local current_line_num = cursor[1]

  -- Get current line (being typed) AND previous few lines
  local lines = vim.api.nvim_buf_get_lines(bufnr, math.max(0, current_line_num - 5), current_line_num + 1, false)
  local current_line = lines[#lines] or ''  -- The line cursor is on
  local previous_line = #lines > 1 and lines[#lines - 1] or ''  -- Line just completed

  -- Check both current line (being typed) and previous line (just completed)
  local check_lines = {current_line, previous_line}
  local full_context = table.concat(lines, '\n')

  for _, line in ipairs(check_lines) do
    -- Detect import statement (with optional leading whitespace)
    if line:match('^%s*import%s+') or line:match('^%s*from%s+.*import') or
       line:match('^%s*use%s+') or line:match('^%s*#include') or
       line:match('^%s*require%(') then
      return 'import', full_context
    end

    -- Detect function definition completion
    if line:match('def%s+%w+%(.*%)%s*:') or  -- Python
       line:match('function%s+%w+%(.*%)') or  -- JS/Lua
       line:match('^%s*}%s*$') or  -- Closing brace
       line:match('fn%s+%w+%(.*%)') then  -- Rust
      return 'function_def', full_context
    end

    -- Detect variable declaration
    if line:match('%w+%s*=%s*function') or
       line:match('const%s+%w+%s*=') or
       line:match('let%s+%w+%s*=') or
       line:match('var%s+%w+%s*=') then
      return 'variable_def', full_context
    end
  end

  return nil, nil
end

--- Called when text changes
function M.on_text_changed()
  local bufnr = vim.api.nvim_get_current_buf()
  local line_count = vim.api.nvim_buf_line_count(bufnr)
  local cursor = vim.api.nvim_win_get_cursor(0)

  -- Check if we just completed a line (moved to new line)
  if line_count > M.state.last_line_count then
    local event_type, context = M.detect_code_event()

    if event_type and M.config.trigger_events[event_type] then
      M.request_judgment(event_type, context)
    end
  end

  M.state.last_line_count = line_count
  M.state.last_cursor_pos = cursor
end

--- Called when cursor is idle
function M.on_cursor_hold()
  if not M.config.trigger_events.line_idle then
    return
  end

  local cursor = vim.api.nvim_win_get_cursor(0)
  local current_line = cursor[1]

  -- Don't judge the same line repeatedly
  if current_line == M.state.last_judgment_line then
    return
  end

  -- Get context around current line
  local bufnr = vim.api.nvim_get_current_buf()
  local start_line = math.max(0, current_line - 10)
  local end_line = math.min(vim.api.nvim_buf_line_count(bufnr), current_line + 10)
  local lines = vim.api.nvim_buf_get_lines(bufnr, start_line, end_line, false)
  local context = table.concat(lines, '\n')

  M.request_judgment('line_hover', context, current_line)
end

--- Request a judgment from the AI
function M.request_judgment(event_type, context, line_num)
  -- Check cache to avoid repeating
  local cache_key = event_type .. ':' .. vim.fn.sha256(context)
  if M.state.recently_judged[cache_key] then
    return
  end

  local filetype = vim.bo.filetype
  local file_path = vim.api.nvim_buf_get_name(0)

  -- Build prompt for snarky commentary
  local prompt = string.format(
    "You're judging code as it's being written. Event: %s. Language: %s\n\n" ..
    "Code context:\n```\n%s\n```\n\n" ..
    "Give a ONE-LINE or TWO-LINE snarky but helpful remark. Examples:\n" ..
    "- 'url maker with 2 variables? ehhh are you sure about that, I'd use 3 imo...'\n" ..
    "- 'importing pandas again? another statistics thing? you're so predictable...'\n" ..
    "- 'hmm that function name could be clearer, but you do you I guess'\n\n" ..
    "Keep it SHORT (under 80 chars), slightly judgy, but ultimately helpful.",
    event_type, filetype, context
  )

  -- Send to AI with verbose personality (the sassy one)
  async.send_chat(prompt, false, 'verbose', function(response, err)
    if err then
      return  -- Silent failure for live judge
    end

    -- Clean up response (remove quotes, extra whitespace)
    response = response:gsub('^["\']', ''):gsub('["\']$', ''):gsub('^%s+', ''):gsub('%s+$', '')

    -- Show as inline notification
    if response and response ~= '' then
      M.show_judgment(response)
      M.state.recently_judged[cache_key] = true
      M.state.last_judgment_line = line_num or 0

      -- Clear cache after 30 seconds
      vim.defer_fn(function()
        M.state.recently_judged[cache_key] = nil
      end, 30000)
    end
  end)
end

--- Show judgment as inline notification
function M.show_judgment(message)
  -- Split message into lines if needed for better display
  local msg_lines = {}
  local max_width = 60

  -- Word wrap the message
  local words = {}
  for word in message:gmatch('%S+') do
    table.insert(words, word)
  end

  local current_line = ''
  for _, word in ipairs(words) do
    if #current_line + #word + 1 <= max_width then
      current_line = current_line == '' and word or current_line .. ' ' .. word
    else
      if current_line ~= '' then
        table.insert(msg_lines, current_line)
      end
      current_line = word
    end
  end
  if current_line ~= '' then
    table.insert(msg_lines, current_line)
  end

  -- Calculate dimensions
  local width = max_width + 4
  local height = #msg_lines + 2

  local bufnr = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(bufnr, 'bufhidden', 'wipe')

  -- Format message with prefix
  local display_lines = {''}
  for _, line in ipairs(msg_lines) do
    table.insert(display_lines, '  💬 ' .. line)
  end
  table.insert(display_lines, '')

  vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, display_lines)
  vim.api.nvim_buf_set_option(bufnr, 'modifiable', false)

  -- Window configuration (relative to cursor, below and to the right)
  local win_opts = {
    relative = 'cursor',
    width = width,
    height = height,
    row = 1,  -- 1 line below cursor
    col = 0,  -- Aligned with cursor column
    style = 'minimal',
    border = 'rounded',
    focusable = false,
    zindex = 50,
  }

  local winid = vim.api.nvim_open_win(bufnr, false, win_opts)

  -- Auto-close after 12 seconds (longer to read)
  vim.defer_fn(function()
    if vim.api.nvim_win_is_valid(winid) then
      vim.api.nvim_win_close(winid, true)
    end
  end, 12000)
end

--- Toggle live judge on/off
function M.toggle()
  M.config.enabled = not M.config.enabled

  if M.config.enabled then
    M.start()
  else
    M.stop()
  end
end

return M
