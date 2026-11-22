-- Big Fat Fish v0.6.1: view-relative wing formation and SaveId-scoped recovery.
local UEHelpers = require("UEHelpers")
local dir = debug.getinfo(1, "S").source:sub(2):match("^(.*[/\\])")
local config = dofile(dir .. "config.lua")
local Storage = dofile(dir .. "storage.lua")
local Save = dofile(dir .. "save_adapter.lua")
local Gaze = dofile(dir .. "gaze.lua")
local Face = dofile(dir .. "face.lua")
local Feeding = dofile(dir .. "feeding.lua")
local Interactions=dofile(dir .. "interactions.lua")
Face.configure(dofile(dir .. "face_morphs.lua"), UEHelpers.FindOrAddFName)
local saveDirectory = (os.getenv("LOCALAPPDATA") or "") .. "/Subnautica2/Saved/SaveGames/BigFatFish"
local state = {fish = {}, nextId = 1, paused = false, stable = 0}
local function log(message) print("[BigFatFish Big Fat Fish] " .. tostring(message) .. "\n") end
local function valid(o) return o ~= nil and o:IsValid() end
local function gameThread(callback)
    ExecuteInGameThread(function()
        local ok, err = pcall(callback)
        if not ok then log("Error: " .. tostring(err)) end
    end)
end
local function copy(v) return {X = v.X, Y = v.Y, Z = v.Z} end
local function playerContext()
    local pc = UEHelpers.GetPlayerController()
    if not valid(pc) or not valid(pc.Pawn) then return nil end
    local cls = StaticFindObject("/Script/Subnautica2.SN2PlayerCharacter")
    if not valid(cls) or not pc.Pawn:IsA(cls) then return nil end
    local world = pc.Pawn:GetWorld()
    if not valid(world) then return nil end
    return pc, pc.Pawn, world
end
local function destroyInstances()
    Feeding.cancel()
    for _, fish in ipairs(state.fish) do
        Interactions.cleanup(fish)
        if valid(fish.actor) then fish.actor:K2_DestroyActor() end
    end
    state.fish = {}; state.nextId = 1; state.paused = false
end
local function resetSession()
    destroyInstances()
    state.context = nil; state.worldAddress = nil; state.candidate = nil; state.stable = 0
end
local function loadClass()
    local cls = StaticFindObject(config.ClassPath)
    if valid(cls) then return cls end
    local helper = StaticFindObject("/Script/AssetRegistry.Default__AssetRegistryHelpers")
    if valid(helper) then
        cls = helper:GetAsset({PackageName = UEHelpers.FindOrAddFName("/Game/Mods/BigFatFish/BP_BigFatFish"),
            AssetName = UEHelpers.FindOrAddFName("BP_BigFatFish_C")})
    end
    return valid(cls) and cls or nil
end
local function instantiate(record, world, cls)
    local actor = world:SpawnActor(cls, record.position, {Pitch = 0, Yaw = record.yaw, Roll = 0})
    assert(valid(actor), "SpawnActor failed")
    record.size = record.size or 1.0 -- Existing saves retain their original size.
    local scale = config.Scale * record.size
    actor:SetActorScale3D({X = scale, Y = scale, Z = scale})
    record.actor = actor; record.lastTime = actor:GetGameTimeSinceCreation()
    record.velocity = {X = 0, Y = 0, Z = 0}
    state.fish[#state.fish + 1] = record
    state.nextId = math.max(state.nextId, record.id + 1)
    return record
end
local function snapshot()
    local records = {}
    for _, f in ipairs(state.fish) do
        if valid(f.actor) and not Feeding.isUnpaid(f) then
            records[#records + 1] = {id = f.id, position = copy(f.position), center = copy(f.center),
                yaw = f.yaw, phase = f.phase, startAngle = f.startAngle, mode = f.mode, size = f.size, basinMode=f.basinMode==true}
        end
    end
    return records
end
local function saveCompleted(context)
    local _, _, world = playerContext()
    if not world or not state.context or state.context.id ~= context.id
        or state.worldAddress ~= world:GetAddress() then return end
    if state.readOnly then log("Unreadable mod data preserved; saving skipped."); return end
    local records = snapshot()
    if #records ~= #state.fish then
        log("Actors are unloading/invalid; preserving previous mod save instead of writing a partial list.")
        return
    end
    local path = Storage.save(saveDirectory, context, records)
    state.context = context
    state.lastDiscStamp = context.discStamp
    log("Saved " .. #state.fish .. " fish with game slot " .. context.slot .. ", checkpoint " .. context.checkpoint .. ": " .. path)
end
local function poll()
    local _, _, world = playerContext()
    if not world then
        if state.context then resetSession(); log("Left game world; instances released.") end
        return
    end
    local context = Save.context()
    if not context then return end
    local session = tostring(world:GetAddress()) .. ":" .. context.id
    if state.context and (state.worldAddress ~= world:GetAddress() or state.context.id ~= context.id) then resetSession() end
    if not state.context then
        if state.candidate ~= session then state.candidate = session; state.stable = 0 end
        state.stable = state.stable + 1
        if state.stable < 3 then return end
        local data, warning, corrupt = Storage.load(saveDirectory, context)
        local cls = loadClass()
        if not cls then return end -- Retry after the resource container becomes ready.
        -- Restore all or none. A partial restore must not later overwrite the save.
        local ok, err = pcall(function()
            for _, record in ipairs(data and data.fish or {}) do instantiate(record, world, cls) end
        end)
        if not ok then destroyInstances(); error("Restore failed; retrying: " .. tostring(err)) end
        state.context = context; state.worldAddress = world:GetAddress()
        state.lastDiscStamp = context.discStamp; state.readOnly = corrupt == true
        if warning then log("Mod save notice: " .. warning) end
        log("Game slot ready: " .. context.slot .. "; restored " .. #state.fish .. " fish; SaveId=" .. context.id
            .. "; activeCheckpoint=" .. context.checkpoint .. "; dataCheckpoint=" .. (data and data.checkpoint or "none"))
    elseif context.discStamp ~= state.lastDiscStamp then
        -- Fallback for missed completion notifications: use the native last
        -- SUCCESSFUL disk-save timestamp, never just the file's modification time.
        saveCompleted(context)
    end
end
local function ready(quiet)
    local pc, pawn, world = playerContext()
    if not state.context or not world or world:GetAddress() ~= state.worldAddress then
        if not quiet then log("Load a game save and wait for Game slot ready before using this command.") end
        return nil
    end
    return pc, pawn, world
end
local function spawn(count)
    local pc, pawn, world = ready()
    if not pc then return end
    count = count or 1
    assert(count >= 1 and count % 1 == 0 and #state.fish + count <= config.MaxFish,
        "Count must be an integer; maximum " .. config.MaxFish .. " fish")
    local cls = assert(loadClass(), "BigFatFish cooked blueprint is unavailable")
    local yaw = math.rad(pc:GetControlRotation().Yaw)
    local origin = pawn:K2_GetActorLocation()
    for i = 1, count do
        local lanes = {0, -1, 1, -2, 2}
        local lateral = lanes[#state.fish % 5 + 1] * config.FollowSpacingCm
        local forward = config.SpawnDistanceCm + math.floor(#state.fish / 5) * config.FollowSpacingCm
        local position = {X = origin.X + math.cos(yaw) * forward - math.sin(yaw) * lateral,
            Y = origin.Y + math.sin(yaw) * forward + math.cos(yaw) * lateral, Z = origin.Z}
        local angle = yaw - math.pi / 2
        instantiate({id = state.nextId, size = 0.5 + math.random(), position = position, yaw = math.deg(yaw) + config.MeshYawOffsetDegrees,
            center = {X = position.X - config.PatrolRadiusCm * math.cos(angle),
                Y = position.Y - config.PatrolRadiusCm * math.sin(angle), Z = position.Z},
            startAngle = angle, phase = 0, mode = "wander"}, world, cls)
    end
    log("Spawned " .. count .. " Big Fat Fish; total=" .. #state.fish .. ". Use bigfatfish_follow to follow; save the GAME to persist.")
end
local function behavior(mode)
    if not ready() then return end
    for _, fish in ipairs(state.fish) do
        if mode == "wander" then
            fish.phase = 0
            fish.startAngle = math.rad(fish.yaw - config.MeshYawOffsetDegrees) - math.pi / 2
            fish.center = {X = fish.position.X - config.PatrolRadiusCm * math.cos(fish.startAngle),
                Y = fish.position.Y - config.PatrolRadiusCm * math.sin(fish.startAngle), Z = fish.position.Z}
        end
        fish.mode = mode; fish.velocity = {X = 0, Y = 0, Z = 0}
    end
    state.paused = false
    log("All " .. #state.fish .. " Big Fat Fish: " .. mode .. ". Save the game to persist.")
end
local function moveFollow(f, index, dt, viewOrigin, viewRotation)
    local yaw, pitch = math.rad(viewRotation.Yaw), math.rad(viewRotation.Pitch or 0)
    local row = math.floor((index - 1) / 2)
    local side = index % 2 == 1 and -1 or 1
    f.phase = f.phase + dt * 0.45
    local forward = config.FormationForwardCm + row * config.FormationRowSpacingCm
    local lateral = side * (config.FormationLateralCm + row * 70)
        + config.FormationDriftCm * math.sin(f.phase + index)
    local vertical = config.FormationBobCm * math.sin(f.phase * 1.3 + index * 1.7)
    local cp, sp, cy, sy = math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
    local dx = viewOrigin.X + cp * cy * forward - sy * lateral - sp * cy * vertical - f.position.X
    local dy = viewOrigin.Y + cp * sy * forward + cy * lateral - sp * sy * vertical - f.position.Y
    local dz = viewOrigin.Z + sp * forward + cp * vertical - f.position.Z
    local distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    local speed = math.min(config.FollowMaxSpeedCmPerSecond, math.max(0, distance - 30) * 1.5)
    local factor = 1 - math.exp(-config.FollowResponse * dt)
    local desiredScale = distance > 0.001 and speed / distance or 0
    for axis, delta in pairs({X = dx, Y = dy, Z = dz}) do
        f.velocity[axis] = f.velocity[axis] + (delta * desiredScale - f.velocity[axis]) * factor
        f.position[axis] = f.position[axis] + f.velocity[axis] * dt
    end
    if f.velocity.X ^ 2 + f.velocity.Y ^ 2 > 4 then
        local yaw = math.deg(math.atan(f.velocity.Y, f.velocity.X)) + config.MeshYawOffsetDegrees
        local difference = (yaw - f.yaw + 180) % 360 - 180
        local turn = config.TurnDegreesPerSecond * dt
        f.yaw = f.yaw + math.max(-turn, math.min(turn, difference))
    end
end
local function update()
    Feeding.poll()
    if not state.context or #state.fish == 0 then return end
    local pc, pawn, world = playerContext()
    if not world or world:GetAddress() ~= state.worldAddress then resetSession(); return end
    local targetOrigin = pawn:K2_GetActorLocation()
    local viewRotation = pc:GetControlRotation()
    local camera = pc.PlayerCameraManager
    if valid(camera) then
        targetOrigin = camera:GetCameraLocation()
        viewRotation = camera:GetCameraRotation()
    end
    local followIndex=0
    for index, f in ipairs(state.fish) do
        if valid(f.actor) then
            if f.mode=='follow' then followIndex=followIndex+1 end
            local now = f.actor:GetGameTimeSinceCreation()
            local dt = math.max(0, math.min(now - f.lastTime, 0.2)); f.lastTime = now
            if not state.paused or Feeding.isActive(f) then
                local feeding=Feeding.update(f,dt,targetOrigin,viewRotation,world)
                if not valid(f.actor) then goto nextFish end
                if feeding then
                    -- Feeding supplies the position/yaw during the short arrival.
                elseif f.mode == "wander" then
                    f.phase = f.phase + dt * config.SwimSpeedCmPerSecond / config.PatrolRadiusCm
                    local angle = f.startAngle + f.phase
                    f.position = {X = f.center.X + config.PatrolRadiusCm * math.cos(angle),
                        Y = f.center.Y + config.PatrolRadiusCm * math.sin(angle),
                        Z = f.center.Z + config.VerticalBobCm * math.sin(2 * f.phase)}
                    f.yaw = math.deg(angle + math.pi / 2) + config.MeshYawOffsetDegrees
                elseif f.mode == "follow" then moveFollow(f, followIndex, dt, targetOrigin, viewRotation) end
                f.actor:K2_SetActorLocation(f.position, false, {}, false)
                f.actor:K2_SetActorRotation({Pitch = 0, Yaw = f.yaw, Roll = 0}, false)
            end
            local interactionOK,interactionError=pcall(Interactions.update,f,dt,world,Feeding.isActive(f))
            if not interactionOK and tostring(interactionError)~=f.interactionError then f.interactionError=tostring(interactionError);log(f.interactionError) end
            local faceOk, faceError = pcall(Face.update, f, dt)
            if not faceOk and tostring(faceError) ~= f.faceError then
                f.faceError = tostring(faceError); log("Face ID=" .. f.id .. ": " .. f.faceError)
            end
            local ok, active = pcall(Gaze.update, f, targetOrigin, dt)
            f.gazeActive = ok and active == true
            if not ok and tostring(active) ~= f.gazeError then
                f.gazeError = tostring(active); log("Gaze ID=" .. f.id .. ": " .. f.gazeError)
            end
        end
        ::nextFish::
    end
end
local function guarded(callback)
    local lastError
    return function()
        local ok, err = pcall(callback)
        if not ok and tostring(err) ~= lastError then log(err); lastError = tostring(err) end
        if ok then lastError = nil end
    end
end
local function offeringMenuOpen(pc)
    if pc.bShowMouseCursor or pc:IsLookInputIgnored() then return true end
    local common=StaticFindObject('/Script/CommonUI.CommonActivatableWidget')
    if valid(common) then
        for _,name in ipairs({'WBP_PDAScreen_C','WBP_Inventory_C'}) do
            for _,widget in ipairs(FindAllOf(name) or {}) do
                if valid(widget) and widget:IsA(common) and widget:IsActivated() and widget:IsVisible() then return true end
            end
        end
    end
    return false
end
Feeding.configure({ready=function() return ready(true) end,name=UEHelpers.FindOrAddFName,log=log,menuOpen=offeringMenuOpen,
    canSpawn=function() return #state.fish<config.MaxFish and not state.readOnly end,
    spawn=function(position,yaw)
        local _,_,world=ready();assert(world,'Game world is not ready')
        return instantiate({id=state.nextId,size=.5+math.random(),position=position,yaw=yaw,
            center=copy(position),startAngle=0,phase=0,mode='follow'},world,assert(loadClass(),'Fish class is unavailable'))
    end,
    remove=function(fish)
        Interactions.cleanup(fish)
        if valid(fish.actor) then fish.actor:K2_DestroyActor() end
        for i,f in ipairs(state.fish) do if f==fish then table.remove(state.fish,i);break end end
    end})
Interactions.configure({ready=function() return ready(true) end,fish=function() return state.fish end,
    config=config,name=UEHelpers.FindOrAddFName,log=log,defer=gameThread})
LoopInGameThreadAfterFrames(1, guarded(update))
LoopInGameThreadWithDelay(500, guarded(function() poll();Interactions.installHooks();Feeding.discover() end))
Save.registerSaveCompleted(function()
    gameThread(function()
        local context = Save.context()
        if context then saveCompleted(context) end
    end)
end, log)
local callbacks = {
    bigfatfish_spawn = function(parts)
        local value = parts and parts[1]
        spawn(value and assert(tonumber(value), "Usage: bigfatfish_spawn [count]") or 1)
    end,
    bigfatfish_follow = function() behavior("follow") end,
    bigfatfish_stay = function() behavior("stay") end,
    bigfatfish_wander = function() behavior("wander") end,
    bigfatfish_remove = function() if ready() then destroyInstances(); log("Removed all Big Fat Fish. Save the game to persist removal.") end end,
    bigfatfish_pause = function() state.paused = not state.paused; log("Movement paused=" .. tostring(state.paused)) end,
    bigfatfish_gaze = function(parts)
        local mode = parts and parts[1]
        assert(mode == "on" or mode == "off", "Usage: bigfatfish_gaze on|off")
        Gaze.enabled = mode == "on"; log("Head/eye tracking=" .. tostring(Gaze.enabled))
    end,
    bigfatfish_status = function()
        log("v0.6.1; total=" .. #state.fish .. "; slot=" .. (state.context and state.context.slot or "NOT READY") .. '; feeding=' .. Feeding.status())
        for _, f in ipairs(state.fish) do log("ID=" .. f.id .. " size=" .. string.format("%.2fx", f.size) .. " mode=" .. f.mode .. " gaze=" .. tostring(f.gazeActive == true) .. " valid=" .. tostring(valid(f.actor))) end
    end,
}
for name, callback in pairs(callbacks) do
    local command = callback
    RegisterConsoleCommandHandler(name, function(_, parts)
        -- CommandParts contains arguments only in this UE4SS build.
        gameThread(function() command(parts or {}) end)
        return true
    end)
end
log("Big Fat Fish v0.6.1 loaded. Commands: bigfatfish_spawn [count], bigfatfish_follow, bigfatfish_stay, bigfatfish_wander, bigfatfish_remove, bigfatfish_gaze on|off, bigfatfish_status.")
