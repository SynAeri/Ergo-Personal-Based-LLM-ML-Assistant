-- Ergo Neovim Plugin v2.0
-- Local AI assistant with async commands, floating windows, and passive monitoring
-- Connects to orchestrator API for AI-powered code assistance

local M = {}

-- Load submodules
local ui = require('ergo.ui')
local async = require('ergo.async')
local passive = require('ergo.passive')

-- Configuration
M.config = {
  api_url = 'http://127.0.0.1:8765',
  enabled = true,
  personality = 'standard',  -- quiet, standard, verbose
  passive_monitoring = true,
  passive_check_interval = 60000,  -- 60 seconds
  auto_report_interval = 5000,     -- 5 seconds
  send_diagnostics = true,
  send_selections = true,
}

-- Internal state
local auto_report_timer = nil

--- Setup function called by user
-- @param opts table User configuration options
function M.setup(opts)
  opts = opts or {}
  M.config = vim.tbl_deep_extend('force', M.config, opts)
  
  -- Configure submodules
  async.api_base_url = M.config.api_url
  passive.setup({
    personality = M.config.personality,
    check_interval = M.config.passive_check_interval,
  })
  
  -- Create user commands
  M.create_commands()
  
  -- Start services if enabled
  if M.config.enabled then
    M.start_auto_report()
    
    if M.config.passive_monitoring then
      passive.start()
    end
  end
  
  print('Ergo plugin loaded (async mode)')
end

--- Create user commands
function M.create_commands()
  -- Main commands
  vim.api.nvim_create_user_command('ErgoExplainContext', function()
    M.explain_context()
  end, {desc = 'Ask Ergo to explain current context'})
  
  vim.api.nvim_create_user_command('ErgoSummarizeWork', function()
    M.summarize_work()
  end, {desc = 'Get summary of recent work'})
  
  vim.api.nvim_create_user_command('ErgoJudgeCode', function()
    M.judge_code()
  end, {desc = 'Get AI code review of visible code'})
  
  vim.api.nvim_create_user_command('ErgoCommitReview', function()
    M.commit_review()
  end, {desc = 'Review staged git changes'})
  
  vim.api.nvim_create_user_command('ErgoChat', function()
    M.open_chat()
  end, {desc = 'Open interactive chat buffer'})
  
  vim.api.nvim_create_user_command('ErgoInsight', function()
    M.request_insight()
  end, {desc = 'Request contextual insight'})
  
  -- Control commands
  vim.api.nvim_create_user_command('ErgoToggle', function()
    M.toggle()
  end, {desc = 'Toggle Ergo monitoring on/off'})
  
  vim.api.nvim_create_user_command('ErgoPassiveToggle', function()
    passive.toggle()
  end, {desc = 'Toggle passive monitoring'})
  
  vim.api.nvim_create_user_command('ErgoPersonality', function(opts)
    M.set_personality(opts.args)
  end, {
    nargs = 1,
    complete = function() return {'quiet', 'standard', 'verbose'} end,
    desc = 'Set Ergo personality'
  })
end

--- Start automatic context reporting
function M.start_auto_report()
  if auto_report_timer then
    return
  end
  
  auto_report_timer = vim.loop.new_timer()
  auto_report_timer:start(
    1000,  -- Start after 1s
    M.config.auto_report_interval,
    vim.schedule_wrap(function()
      M.send_buffer_context()
    end)
  )
end

--- Stop automatic reporting
function M.stop_auto_report()
  if auto_report_timer then
    auto_report_timer:stop()
    auto_report_timer = nil
  end
end

--- Toggle plugin on/off
function M.toggle()
  M.config.enabled = not M.config.enabled
  
  if M.config.enabled then
    M.start_auto_report()
    passive.start()
    ui.show_passive_insight('Monitoring enabled', M.config.personality)
  else
    M.stop_auto_report()
    passive.stop()
    ui.show_passive_insight('Monitoring disabled', M.config.personality)
  end
end

--- Set personality mode
-- @param mode string Personality mode (quiet/standard/verbose)
function M.set_personality(mode)
  if mode == 'quiet' or mode == 'standard' or mode == 'verbose' then
    M.config.personality = mode
    passive.config.personality = mode
    print('Ergo personality set to: ' .. mode)
  else
    print('Invalid personality. Use: quiet, standard, or verbose')
  end
end

--- Get current buffer context
-- @return table Context data
function M.get_buffer_context()
  local bufnr = vim.api.nvim_get_current_buf()
  local win = vim.api.nvim_get_current_win()
  
  local file_path = vim.api.nvim_buf_get_name(bufnr)
  local filetype = vim.bo[bufnr].filetype
  
  local cursor = vim.api.nvim_win_get_cursor(win)
  local total_lines = vim.api.nvim_buf_line_count(bufnr)
  
  local diagnostics = {}
  if M.config.send_diagnostics then
    local diag = vim.diagnostic.get(bufnr)
    diagnostics = {
      error_count = 0,
      warning_count = 0,
      total_count = #diag,
    }
    
    for _, d in ipairs(diag) do
      if d.severity == vim.diagnostic.severity.ERROR then
        diagnostics.error_count = diagnostics.error_count + 1
      elseif d.severity == vim.diagnostic.severity.WARN then
        diagnostics.warning_count = diagnostics.warning_count + 1
      end
    end
  end
  
  return {
    event_type = 'nvim.buffer.context',
    timestamp = os.time(),
    file_path = file_path,
    language = filetype,
    cursor = {line = cursor[1], col = cursor[2]},
    total_lines = total_lines,
    diagnostics = diagnostics,
  }
end

--- Send buffer context to file (for daemon to read)
function M.send_buffer_context()
  if not M.config.enabled then
    return
  end
  
  local context = M.get_buffer_context()
  local data_file = vim.fn.expand('~/.local/share/ergo/nvim_context.json')
  
  local ok, encoded = pcall(vim.fn.json_encode, context)
  if ok then
    local file = io.open(data_file, 'w')
    if file then
      file:write(encoded)
      file:close()
    end
  end
end

--- Command: Explain current context
function M.explain_context()
  M.send_buffer_context()
  
  -- Show loading indicator
  local loading_buf, loading_win = ui.show_loading('Analyzing context...')
  
  -- Make async API call
  async.send_chat("Explain what I'm working on", true, function(response, err)
    -- Close loading window
    if vim.api.nvim_win_is_valid(loading_win) then
      vim.api.nvim_win_close(loading_win, true)
    end
    
    if err then
      ui.show_response('Error: ' .. err, {title = 'Ergo - Error'})
    else
      ui.show_response(response, {title = 'Ergo - Context Explanation'})
    end
  end)
end

--- Command: Summarize recent work
function M.summarize_work()
  local loading_buf, loading_win = ui.show_loading('Fetching work summary...')
  
  async.get_recent_context(60, function(context, err)
    if vim.api.nvim_win_is_valid(loading_win) then
      vim.api.nvim_win_close(loading_win, true)
    end
    
    if err then
      ui.show_response('Error: ' .. err, {title = 'Ergo - Error'})
    elseif not context or context == '' then
      ui.show_response('No recent activity found.', {title = 'Ergo - Recent Work'})
    else
      ui.show_response(context, {title = 'Ergo - Recent Work (Last Hour)'})
    end
  end)
end

--- Command: Judge/review current code
function M.judge_code()
  local bufnr = vim.api.nvim_get_current_buf()
  
  -- Get visible lines
  local start_line = vim.fn.line('w0') - 1
  local end_line = vim.fn.line('w$')
  local lines = vim.api.nvim_buf_get_lines(bufnr, start_line, end_line, false)
  local code = table.concat(lines, '\n')
  
  if code == '' then
    print('No visible code to review')
    return
  end
  
  local filetype = vim.bo[bufnr].filetype
  local file_path = vim.api.nvim_buf_get_name(bufnr)
  
  local loading_buf, loading_win = ui.show_loading('Reviewing code...')
  
  async.request_code_review(code, filetype, file_path, function(review, err)
    if vim.api.nvim_win_is_valid(loading_win) then
      vim.api.nvim_win_close(loading_win, true)
    end
    
    if err then
      ui.show_response('Error: ' .. err, {title = 'Ergo - Error'})
    else
      ui.show_response(review, {title = 'Ergo - Code Review'})
    end
  end)
end

--- Command: Review git commit
function M.commit_review()
  local diff = vim.fn.system('git diff --cached')
  
  if diff == '' then
    print('No staged changes to review')
    return
  end
  
  local loading_buf, loading_win = ui.show_loading('Reviewing commit...')
  
  local prompt = 'Review this git commit and suggest a commit message:\n\n' .. diff
  
  async.send_chat(prompt, false, function(response, err)
    if vim.api.nvim_win_is_valid(loading_win) then
      vim.api.nvim_win_close(loading_win, true)
    end
    
    if err then
      ui.show_response('Error: ' .. err, {title = 'Ergo - Error'})
    else
      ui.show_response(response, {title = 'Ergo - Commit Review'})
    end
  end)
end

--- Command: Open chat interface
function M.open_chat()
  ui.create_chat_buffer()
end

--- Command: Request contextual insight
function M.request_insight()
  passive.request_contextual_insight()
end

return M
