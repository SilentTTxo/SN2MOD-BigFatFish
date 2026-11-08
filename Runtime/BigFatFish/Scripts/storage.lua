-- Versioned mod sidecars: one current record + one backup per game SaveId.
-- No native .sav files are edited. Windows rename keeps a recoverable backup.
local json = dofile(debug.getinfo(1, "S").source:sub(2):match("^(.*[/\\])") .. "json.lua")
local M = {}
local function finite(n) return type(n) == "number" and n == n and math.abs(n) < 1e12 end
local function vector(v)
    return type(v) == "table" and finite(v.X) and finite(v.Y) and finite(v.Z)
end
function M.validate(data, context)
    assert(type(data) == "table" and data.version == 1, "Unsupported mod save version")
    assert(type(data.checkpoint) == "string" and data.checkpoint:match("^%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d$"), "Invalid checkpoint stamp")
    assert(data.saveId == context.id and data.checkpoint == context.checkpoint, "Different game save/checkpoint")
    assert(type(data.fish) == "table" and #data.fish <= 64, "Invalid fish list")
    local count = 0
    for key in pairs(data.fish) do
        assert(type(key) == "number" and key % 1 == 0 and key >= 1 and key <= #data.fish, "Invalid fish array")
        count = count + 1
    end
    assert(count == #data.fish, "Sparse fish array")
    local seen = {}
    for _, f in ipairs(data.fish) do
        assert(type(f) == "table" and finite(f.id) and f.id >= 1 and f.id % 1 == 0 and not seen[f.id], "Invalid fish ID")
        seen[f.id] = true
        assert(f.size == nil or (finite(f.size) and f.size >= 0.5 and f.size <= 1.5), "Invalid fish size")
        assert(vector(f.position) and vector(f.center), "Invalid position")
        assert(finite(f.yaw) and finite(f.phase) and finite(f.startAngle), "Invalid movement state")
        assert(f.mode == "wander" or f.mode == "follow" or f.mode == "stay", "Invalid behavior")
    end
    return data
end
local function filename(directory, context)
    assert(context.id:match("^[%x%-]+$") and #context.id >= 32, "Unsafe SaveId")
    assert(context.checkpoint:match("^%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d$"), "Unsafe checkpoint")
    return directory .. "/" .. context.id .. "_current.json"
end
function M.load(directory, context)
    local current = filename(directory, context)
    local errors = {}
    -- LastModified on the in-memory ActiveSave is not a stable loaded-checkpoint
    -- identifier in SN2. The SaveId-scoped current record is authoritative.
    -- Old timestamp-only snapshots are preserved, but never guessed/migrated.
    for _, candidate in ipairs({current, current .. ".bak"}) do
        local file = io.open(candidate, "rb")
        if file then
            local bytes = file:read("*a"); file:close()
            local ok, data = pcall(function()
                assert(#bytes <= 1024 * 1024, "Oversized mod save")
                local decoded = json.decode(bytes)
                local expected = {id = context.id, checkpoint = decoded.checkpoint}
                return M.validate(decoded, expected)
            end)
            if ok then return data, candidate:sub(-4) == ".bak" and "backup" or nil end
            errors[#errors + 1] = tostring(data)
        end
    end
    if #errors > 0 then return nil, table.concat(errors, "; "), true end
    return nil
end
local function createSaveDirectory(directory)
    local root = assert(os.getenv("LOCALAPPDATA"), "LOCALAPPDATA is unavailable")
    local expected = (root .. "/Subnautica2/Saved/SaveGames/BigFatFish"):gsub("\\", "/"):gsub("/+$", "")
    assert(directory:gsub("\\", "/"):gsub("/+$", "") == expected, "Unexpected mod save directory")
    -- This command is entirely constant: cmd expands the native environment
    -- path, including spaces/Unicode. Never interpolate save IDs or user data.
    -- Windows mkdir also creates missing parent directories. Try only after an
    -- open failure, so ordinary autosaves do not launch another process.
    os.execute('mkdir "%LOCALAPPDATA%\\Subnautica2\\Saved\\SaveGames\\BigFatFish" >nul 2>&1')
end
local function writeAtomic(path, bytes, directory)
    local file, openError = io.open(path .. ".tmp", "wb")
    if not file then
        createSaveDirectory(directory)
        file, openError = io.open(path .. ".tmp", "wb")
    end
    assert(file, "Cannot write mod save: " .. tostring(openError))
    local written, err = file:write(bytes)
    if not written then file:close(); error(err or "Write failed") end
    assert(file:flush()); assert(file:close())
    local old = io.open(path, "rb")
    if old then
        old:close()
        os.remove(path .. ".bak")
        assert(os.rename(path, path .. ".bak"))
    end
    local renamed, renameError = os.rename(path .. ".tmp", path)
    if not renamed then
        os.rename(path .. ".bak", path)
        error(renameError or "Commit failed")
    end
end
function M.save(directory, context, fish)
    local path = filename(directory, context)
    local payload = {version = 1, saveId = context.id, slot = context.slot,
        checkpoint = context.checkpoint, fish = fish}
    M.validate(payload, context)
    local bytes = json.encode(payload)
    writeAtomic(path, bytes, directory)
    return path
end
return M
