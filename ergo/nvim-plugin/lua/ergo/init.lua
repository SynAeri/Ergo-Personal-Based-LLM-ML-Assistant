-- Ergo Neovim Plugin
-- Streams editor context to the ergo-daemon over Unix socket
-- Provides commands for explicit code interactions

local M = {}

-- Configuration
M.config = {
  socket_path = "/tmp/ergo-nvim.sock",
  enabled = true,
  auto_report_interval = 5000, -- ms
  send_diagnostics = true,
  send_selections = true,
}

-- Internal state
local socket_client = nil
local auto_timer = nil

--- Setup function called by user
function M.setup(opts)
  opts = opts or {}
  M.config = vim.tbl_deep_extend("force", M.config, opts)

  -- Create user commands
  M.create_commands()

  -- Start auto-reporting if enabled
  if M.config.enabled then
    M.start_auto_report()
  end

  print("Ergo plugin loaded")
end

--- Create user commands
function M.create_commands()
  vim.api.nvim_create_user_command("ErgoExplainContext", function()
    M.explain_context()
  end, {})

  vim.api.nvim_create_user_command("ErgoSummarizeWork", function()
    M.summarize_work()
  end, {})

  vim.api.nvim_create_user_command("ErgoJudgeThisCode", function()
    M.judge_code()
  end, {})

  vim.api.nvim_create_user_command("ErgoCommitReview", function()
    M.commit_review()
  end, {})

  vim.api.nvim_create_user_command("ErgoToggle", function()
    M.toggle()
  end, {})
end

--- Start automatic context reporting
function M.start_auto_report()
  if auto_timer then
    return
  end

  auto_timer = vim.loop.new_timer()
  auto_timer:start(
    1000, -- Start after 1s
    M.config.auto_report_interval,
    vim.schedule_wrap(function()
      M.send_buffer_context()
    end)
  )
end

--- Stop automatic reporting
function M.stop_auto_report()
  if auto_timer then
    auto_timer:stop()
    auto_timer = nil
  end
end

--- Toggle plugin on/off
function M.toggle()
  M.config.enabled = not M.config.enabled

  if M.config.enabled then
    M.start_auto_report()
    print("Ergo monitoring enabled")
  else
    M.stop_auto_report()
    print("Ergo monitoring disabled")
  end
end

--- Get current buffer context
function M.get_buffer_context()
  local bufnr = vim.api.nvim_get_current_buf()
  local win = vim.api.nvim_get_current_win()

  -- Get file info
  local file_path = vim.api.nvim_buf_get_name(bufnr)
  local filetype = vim.bo[bufnr].filetype

  -- Get cursor position
  local cursor = vim.api.nvim_win_get_cursor(win)
  local line = cursor[1]
  local col = cursor[2]

  -- Get visible content
  local total_lines = vim.api.nvim_buf_line_count(bufnr)

  -- Get diagnostics
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

  -- Get visual selection if any
  local selection = nil
  if M.config.send_selections then
    local mode = vim.fn.mode()
    if mode == "v" or mode == "V" or mode == "\22" then
      local start_pos = vim.fn.getpos("v")
      local end_pos = vim.fn.getpos(".")
      selection = {
        start_line = start_pos[2],
        start_col = start_pos[3],
        end_line = end_pos[2],
        end_col = end_pos[3],
      }
    end
  end

  return {
    event_type = "nvim.buffer.enter",
    timestamp = os.time(),
    file_path = file_path,
    language = filetype,
    cursor = {
      line = line,
      col = col,
    },
    total_lines = total_lines,
    diagnostics = diagnostics,
    selection = selection,
  }
end

--- Send buffer context to daemon
function M.send_buffer_context()
  if not M.config.enabled then
    return
  end

  local context = M.get_buffer_context()

  -- For now, just write to a JSON file that the daemon can read
  -- In a full implementation, this would use a Unix socket
  local data_file = vim.fn.expand("~/.local/share/ergo/nvim_context.json")

  local ok, encoded = pcall(vim.json.encode, context)
  if ok then
    local file = io.open(data_file, "w")
    if file then
      file:write(encoded)
      file:close()
    end
  end
end

--- Command: Explain current context
function M.explain_context()
  M.send_buffer_context()

  -- Call orchestrator API
  local cmd = string.format(
    'curl -s -X POST http://127.0.0.1:8765/chat -H "Content-Type: application/json" -d \'{"message": "Explain what I\'\\\'\'m working on", "include_context": true}\' | jq -r .response'
  )

  local response = vim.fn.system(cmd)
  print("Ergo: " .. response)
end

--- Command: Summarize recent work
function M.summarize_work()
  local cmd = string.format(
    'curl -s http://127.0.0.1:8765/context/recent?minutes=60 | jq -r .context'
  )

  local response = vim.fn.system(cmd)
  print("Recent work:\n" .. response)
end

--- Command: Judge/review current code
function M.judge_code()
  local bufnr = vim.api.nvim_get_current_buf()

  -- Get visible lines
  local win = vim.api.nvim_get_current_win()
  local start_line = vim.fn.line("w0") - 1
  local end_line = vim.fn.line("w$")

  local lines = vim.api.nvim_buf_get_lines(bufnr, start_line, end_line, false)
  local code = table.concat(lines, "\n")

  local filetype = vim.bo[bufnr].filetype
  local file_path = vim.api.nvim_buf_get_name(bufnr)

  -- Escape for JSON
  code = code:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n')

  local cmd = string.format(
    'curl -s -X POST "http://127.0.0.1:8765/code-review?language=%s&file_path=%s" -H "Content-Type: text/plain" -d "%s" | jq -r .review',
    filetype,
    file_path,
    code
  )

  print("Requesting code review...")
  vim.fn.jobstart(cmd, {
    on_stdout = function(_, data)
      if data then
        local text = table.concat(data, "\n")
        if text and text ~= "" then
          print("Code Review:\n" .. text)
        end
      end
    end,
  })
end

--- Command: Review git commit
function M.commit_review()
  -- Get diff of staged changes
  local diff = vim.fn.system("git diff --cached")

  if diff == "" then
    print("No staged changes to review")
    return
  end

  print("Reviewing commit...")

  -- Escape for JSON
  diff = diff:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n')

  local prompt = string.format(
    "Review this git commit and suggest a commit message:\\n\\n%s",
    diff
  )

  local cmd = string.format(
    'curl -s -X POST http://127.0.0.1:8765/chat -H "Content-Type: application/json" -d \'{"message": "%s", "include_context": false}\' | jq -r .response',
    prompt
  )

  local response = vim.fn.system(cmd)
  print("Commit review:\n" .. response)
end

return M
