-- Ergo Async module - Non-blocking API calls
-- Handles all communication with orchestrator API without freezing Neovim

local M = {}
local ui = require('ergo.ui')

M.api_base_url = 'http://127.0.0.1:8765'
M.pending_requests = {}

--- Make async API call using jobstart
-- @param endpoint string API endpoint (e.g., '/chat')
-- @param method string HTTP method (GET, POST)
-- @param data table|nil Request body for POST
-- @param callback function(response) Callback with parsed response
function M.api_call(endpoint, method, data, callback)
  method = method or 'GET'
  
  local url = M.api_base_url .. endpoint
  local cmd
  
  if method == 'POST' and data then
    -- Escape JSON data for shell
    local json_data = vim.fn.json_encode(data)
    json_data = json_data:gsub("'", "'\\''")  -- Escape single quotes
    
    cmd = string.format(
      "curl -s -X POST '%s' -H 'Content-Type: application/json' -d '%s'",
      url, json_data
    )
  else
    cmd = string.format("curl -s '%s'", url)
  end
  
  local output = {}
  local job_id = vim.fn.jobstart(cmd, {
    on_stdout = function(_, data_lines)
      for _, line in ipairs(data_lines) do
        if line and line ~= '' then
          table.insert(output, line)
        end
      end
    end,
    on_exit = function(_, exit_code)
      if exit_code == 0 then
        local response_text = table.concat(output, '\n')
        local ok, response = pcall(vim.fn.json_decode, response_text)
        
        if ok and response then
          vim.schedule(function()
            callback(response, nil)
          end)
        else
          vim.schedule(function()
            callback(nil, 'Failed to parse response: ' .. response_text)
          end)
        end
      else
        vim.schedule(function()
          callback(nil, 'API call failed with exit code: ' .. exit_code)
        end)
      end
    end,
  })
  
  table.insert(M.pending_requests, job_id)
  return job_id
end

--- Send chat message
-- @param message string User message
-- @param include_context boolean Include context
-- @param callback function(response) Callback with response
function M.send_chat(message, include_context, callback)
  local data = {
    message = message,
    include_context = include_context or false,
  }
  
  M.api_call('/chat', 'POST', data, function(response, err)
    if err then
      callback(nil, err)
    elseif response and response.response then
      callback(response.response, nil)
    else
      callback(nil, 'Invalid response from server')
    end
  end)
end

--- Get recent context
-- @param minutes number Minutes of history
-- @param callback function(context) Callback with context
function M.get_recent_context(minutes, callback)
  local endpoint = string.format('/context/recent?minutes=%d', minutes)
  
  M.api_call(endpoint, 'GET', nil, function(response, err)
    if err then
      callback(nil, err)
    elseif response and response.context then
      callback(response.context, nil)
    else
      callback(nil, 'Invalid response from server')
    end
  end)
end

--- Request code review
-- @param code string Code to review
-- @param language string Programming language
-- @param file_path string File path
-- @param callback function(review) Callback with review
function M.request_code_review(code, language, file_path, callback)
  local endpoint = string.format(
    '/code-review?language=%s&file_path=%s',
    language or 'unknown',
    file_path or 'unknown'
  )
  
  -- For code review, send as plain text
  local cmd = string.format(
    "curl -s -X POST '%s%s' -H 'Content-Type: text/plain' --data-binary @-",
    M.api_base_url, endpoint
  )
  
  local output = {}
  local job_id = vim.fn.jobstart(cmd, {
    on_stdin = function(_, _stdin)
      vim.fn.chansend(_stdin, code)
      vim.fn.chanclose(_stdin, 'stdin')
    end,
    on_stdout = function(_, data_lines)
      for _, line in ipairs(data_lines) do
        if line and line ~= '' then
          table.insert(output, line)
        end
      end
    end,
    on_exit = function(_, exit_code)
      if exit_code == 0 then
        local response_text = table.concat(output, '\n')
        local ok, response = pcall(vim.fn.json_decode, response_text)
        
        if ok and response and response.review then
          vim.schedule(function()
            callback(response.review, nil)
          end)
        else
          vim.schedule(function()
            callback(nil, 'Failed to parse review response')
          end)
        end
      else
        vim.schedule(function()
          callback(nil, 'Code review failed')
        end)
      end
    end,
  })
  
  return job_id
end

--- Send chat message from chat buffer
function M.send_chat_message()
  local bufnr = vim.api.nvim_get_current_buf()
  
  -- Get last line (user's message)
  local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
  local message = lines[#lines]
  
  if not message or message == '' or message == '---' then
    print('Ergo: Please type a message first')
    return
  end
  
  -- Add message to buffer
  vim.api.nvim_buf_set_lines(bufnr, -1, -1, false, {
    '',
    '**You:** ' .. message,
    '',
    '**Ergo:** _thinking..._',
    '',
  })
  
  -- Clear input line
  vim.api.nvim_buf_set_lines(bufnr, -1, -1, false, {''})
  
  -- Send to API
  M.send_chat(message, true, function(response, err)
    if err then
      -- Update last message with error
      local line_count = vim.api.nvim_buf_line_count(bufnr)
      vim.api.nvim_buf_set_lines(bufnr, line_count - 3, line_count - 2, false, {
        '**Ergo:** _Error: ' .. err .. '_'
      })
    else
      -- Update last message with response
      local line_count = vim.api.nvim_buf_line_count(bufnr)
      vim.api.nvim_buf_set_lines(bufnr, line_count - 3, line_count - 2, false, {
        '**Ergo:** ' .. response
      })
    end
    
    -- Scroll to bottom
    vim.cmd('normal! G')
  end)
end

--- Cancel all pending requests
function M.cancel_all()
  for _, job_id in ipairs(M.pending_requests) do
    vim.fn.jobstop(job_id)
  end
  M.pending_requests = {}
end

return M
