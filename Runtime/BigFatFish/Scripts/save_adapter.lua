-- Symbols verified against Subnautica2 CL-131439's reflection map (UE 5.6.1).
-- Do not fall back to a guessed "default" slot or the newest file on disk.
local M = {}
local function valid(o) return o ~= nil and o:IsValid() end
local function stringValue(value)
    return type(value) == "string" and value or value:ToString()
end
local function stamp(date)
    local mathlib = StaticFindObject("/Script/Engine.Default__KismetMathLibrary")
    assert(valid(mathlib), "DateTime helper unavailable")
    return string.format("%04d%02d%02d%02d%02d%02d%03d", mathlib:GetYear(date),
        mathlib:GetMonth(date), mathlib:GetDay(date), mathlib:GetHour(date),
        mathlib:GetMinute(date), mathlib:GetSecond(date), mathlib:GetMillisecond(date))
end
function M.context()
    local subsystem = FindFirstOf("UWESaveGameSubsystem")
    if not valid(subsystem) then return nil end
    local active = subsystem.SaveContext.ActiveSave
    if not valid(active) then return nil end
    local metadata = active.MetaData
    -- Collection identity survives checkpoint rotation; a checkpoint's metadata
    -- is still the authority for its own LastModified timestamp.
    local collection = subsystem.SaveContext.SaveGameCollection
    local saveId = valid(collection) and collection.ContainerInfo.SaveId or metadata.SaveId
    local guidlib = StaticFindObject("/Script/Engine.Default__KismetGuidLibrary")
    assert(valid(guidlib), "Guid helper unavailable")
    local id = stringValue(guidlib:Conv_GuidToString(saveId)):lower()
    if not id:match("^[%x%-]+$") or id:gsub("[0%-]", "") == "" then return nil end
    local checkpoint = stamp(metadata.LastModified)
    if checkpoint:sub(1,4) < "2020" then return nil end
    return {id = id, slot = stringValue(active:GetSlotName()), checkpoint = checkpoint,
        discStamp = stamp(subsystem:GetLastSaveToDiscTimeStamp())}
end
function M.registerSaveCompleted(callback, log)
    for _, name in ipairs({"AsyncSaveGameCompleted", "AutoSaveCompleted"}) do
        local path = "/Script/UWESaveSystem.UWESaveCommunicationComponent:" .. name
        local ok, err = pcall(RegisterHook, path, function() end, function(_, result)
            if result:get() == true then callback() end
        end)
        log(ok and ("Save completion hook registered: " .. name) or ("Save hook unavailable: " .. tostring(err)))
    end
end
return M
