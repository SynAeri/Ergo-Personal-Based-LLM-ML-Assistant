-- Ergo Passive module - Background monitoring with personality
-- Provides passive insights and monitoring without being intrusive

local M = {}
local async = require('ergo.async')
local ui = require('ergo.ui')

-- Configuration
M.config = {
  enabled = true,
  check_interval = 60000,  -- Check every 60 seconds
  personality = 'standard',  -- quiet, standard, verbose
  min_idle_time = 120,  -- Min seconds before commenting on idle
  min_stuck_time = 300,  -- Min seconds before "stuck" detection
}

-- State tracking
M.state = {
  last_file = nil,
  last_file_change = 0,
  last_edit = 0,
  edit_count = 0,
  last_insight_time = 0,
  current_session_start = os.time(),
}

M.timer = nil

--- Setup passive monitoring
function M.setup(opts)
  M.config = vim.tbl_deep_extend('force', M.config, opts or {})
end

--- Start passive monitoring
function M.start()
  if M.timer then
    return
  end
  
  M.config.enabled = true
  M.state.current_session_start = os.time()
  
  -- Set up autocommands for activity tracking
  vim.api.nvim_create_augroup('ErgoPassive', {clear = true})
  
  -- Track file changes
  vim.api.nvim_create_autocmd({'BufEnter', 'BufWinEnter'}, {
    group = 'ErgoPassive',
    callback = function()
      M.on_buffer_enter()
    end,
  })
  
  -- Track edits
  vim.api.nvim_create_autocmd({'TextChanged', 'TextChangedI'}, {
    group = 'ErgoPassive',
    callback = function()
      M.on_text_changed()
    end,
  })
  
  -- Start periodic check timer
  M.timer = vim.loop.new_timer()
  M.timer:start(
    M.config.check_interval,
    M.config.check_interval,
    vim.schedule_wrap(function()
      M.periodic_check()
    end)
  )
  
  if M.config.personality ~= 'quiet' then
    ui.show_passive_insight('Monitoring active', M.config.personality)
  end
end

--- Stop passive monitoring
function M.stop()
  M.config.enabled = false
  
  if M.timer then
    M.timer:stop()
    M.timer = nil
  end
  
  vim.api.nvim_create_augroup('ErgoPassive', {clear = true})
  
  if M.config.personality ~= 'quiet' then
    ui.show_passive_insight('Monitoring paused', M.config.personality)
  end
end

--- Toggle passive monitoring
function M.toggle()
  if M.config.enabled then
    M.stop()
  else
    M.start()
  end
end

--- Handle buffer enter event
function M.on_buffer_enter()
  local current_file = vim.api.nvim_buf_get_name(0)
  local now = os.time()
  
  if current_file ~= M.state.last_file then
    M.state.last_file = current_file
    M.state.last_file_change = now
    M.state.edit_count = 0
  end
end

--- Handle text changed event
function M.on_text_changed()
  M.state.last_edit = os.time()
  M.state.edit_count = M.state.edit_count + 1
end

--- Periodic check for insights
function M.periodic_check()
  if not M.config.enabled then
    return
  end
  
  local now = os.time()
  
  -- Don't spam insights
  if now - M.state.last_insight_time < 180 then  -- Min 3 min between insights
    return
  end
  
  -- Check for various patterns
  M.check_stuck_pattern()
  M.check_idle_pattern()
  M.check_session_milestone()
end

--- Check if user appears stuck on same file/section
function M.check_stuck_pattern()
  local now = os.time()
  local time_on_file = now - M.state.last_file_change
  local time_since_edit = now - M.state.last_edit
  
  -- User has been on same file for a while with few edits
  if time_on_file > M.config.min_stuck_time and
     M.state.edit_count < 10 and
     time_since_edit < 60 then
    
    M.show_insight("Been on this file a while - need help understanding it?")
    M.state.last_insight_time = now
  end
end

--- Check if user has been idle
function M.check_idle_pattern()
  local now = os.time()
  local time_since_edit = now - M.state.last_edit
  
  if time_since_edit > M.config.min_idle_time and
     time_since_edit < M.config.min_idle_time + 60 then
    
    if M.config.personality == 'verbose' then
      M.show_insight("Taking a break? I'm here when you're ready.")
    end
    M.state.last_insight_time = now
  end
end

--- Check session milestones
function M.check_session_milestone()
  local now = os.time()
  local session_duration = now - M.state.current_session_start
  
  -- 1 hour milestone
  if session_duration > 3600 and session_duration < 3660 then
    if M.config.personality ~= 'quiet' then
      M.show_insight("You've been coding for an hour - good progress!")
      M.state.last_insight_time = now
    end
  end
  
  -- 2 hour milestone - suggest break
  if session_duration > 7200 and session_duration < 7260 then
    M.show_insight("2 hours in - consider a break?")
    M.state.last_insight_time = now
  end
end

--- Request context-aware insight from API
function M.request_contextual_insight()
  if not M.config.enabled then
    return
  end
  
  local bufnr = vim.api.nvim_get_current_buf()
  local file_path = vim.api.nvim_buf_get_name(bufnr)
  local filetype = vim.bo[bufnr].filetype
  
  -- Get visible code
  local start_line = vim.fn.line('w0') - 1
  local end_line = vim.fn.line('w$')
  local lines = vim.api.nvim_buf_get_lines(bufnr, start_line, end_line, false)
  local code_sample = table.concat(lines, '\n')
  
  local context_message = string.format(
    "Provide a brief insight about this %s code (max 1 sentence):\n\n%s",
    filetype,
    code_sample:sub(1, 500)  -- Limit to 500 chars
  )
  
  async.send_chat(context_message, false, function(response, err)
    if not err and response then
      M.show_insight(response)
      M.state.last_insight_time = os.time()
    end
  end)
end

--- Show insight to user
function M.show_insight(message)
  ui.show_passive_insight(message, M.config.personality)
end

--- Get activity summary
function M.get_activity_summary()
  local now = os.time()
  local session_duration = now - M.state.current_session_start
  local minutes = math.floor(session_duration / 60)
  
  return {
    session_duration_minutes = minutes,
    current_file = M.state.last_file,
    edit_count = M.state.edit_count,
    time_since_last_edit = now - M.state.last_edit,
  }
end

return M
