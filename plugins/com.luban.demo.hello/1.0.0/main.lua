local M = {}

function M.activate(ctx)
  luban.log("info", "DEMO_HELLO_ACTIVATE version=" .. ctx.plugin.version)
end

function M.run(ctx)
  local dir = luban.data_dir()
  if not dir then
    luban.log("error", "DEMO_HELLO_NO_DATA_DIR")
    return
  end

  local path = dir .. "/runs.txt"
  local text = luban.fs.read(path) or ""
  local count = 0
  for _ in text:gmatch("[^\n]+") do
    count = count + 1
  end
  count = count + 1

  local ok, err = luban.fs.write(
    path,
    text .. "run " .. count .. " version " .. ctx.plugin.version .. "\n"
  )
  if not ok then
    luban.log("error", "DEMO_HELLO_WRITE_FAILED " .. tostring(err))
    return
  end

  luban.log("info", "DEMO_HELLO_RAN count=" .. count .. " version=" .. ctx.plugin.version)
  luban.notify("Hello demo: run " .. count)
  luban.insert_text(luban.settings.get("greeting") .. "\n")
end

return M
