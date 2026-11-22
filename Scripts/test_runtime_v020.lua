function RegisterCustomEvent() end
-- Exercises the real runtime, save adapter and storage with mocked UE/disk APIs.
local root = assert(arg[1], "Pass project directory")
local dir = root .. "/Runtime/BigFatFish/Scripts/"
local clock, spawned, files, logs = 0, {}, {}, {}
local commands, loops, queue, hooks = {}, {}, {}, {}
local worldAddress, assetsReady, saveReady, playerReady = 101, true, true, false
local origin = {X = 100, Y = 200, Z = -1000}
local guid = "12345678123456781234567812345678"
local checkpoint, discStamp = 10, 10
local failRename, failWrite = false, false
local directoryReady, mkdirCalls, denyDirectory = false, 0, false
local originalPrint = print
function print(message) logs[#logs + 1] = tostring(message) end
os.getenv = function() return "TEST" end
io.open = function(path, mode)
    mode = mode or "r"
    if mode:sub(1,1) == "r" and not files[path] then return nil end
    if mode:sub(1,1)=="w" and not directoryReady then return nil,"directory missing" end
    local buffer = files[path] or ""
    return {
        read = function() return buffer end,
        write = function(_, bytes) if failWrite then return nil, "disk full" end; buffer = bytes; return true end,
        flush = function() return true end,
        close = function() if mode:sub(1,1) == "w" then files[path] = buffer end; return true end,
    }
end
os.execute = function(command)
    assert(command == 'mkdir "%LOCALAPPDATA%\\Subnautica2\\Saved\\SaveGames\\BigFatFish" >nul 2>&1', "Constant mkdir command")
    mkdirCalls = mkdirCalls + 1
    directoryReady = not denyDirectory
    return directoryReady
end
os.remove = function(path) files[path] = nil; return true end
os.rename = function(from, to)
    if failRename and from:sub(-4) == ".tmp" then return nil, "locked" end
    if files[from] == nil or files[to] ~= nil then return nil, "cannot rename" end
    files[to] = files[from]; files[from] = nil; return true
end
local valid = function() return true end
local world = {IsValid = valid, GetAddress = function() return worldAddress end}
local pawn = {IsValid = valid, IsA = function() return true end,
    GetWorld = function() return world end, K2_GetActorLocation = function() return origin end}
local controller = {IsValid = valid, GetControlRotation = function() return {Yaw = 30} end}
local cls = {IsValid = valid}
local registry = {IsValid = valid, GetAsset = function(_, data)
    assert(data.PackageName == "/Game/Mods/BigFatFish/BP_BigFatFish")
    assert(data.AssetName == "BP_BigFatFish_C")
    return assetsReady and cls or nil
end}
local mathlib = {IsValid = valid, GetYear = function() return 2026 end,
    GetMonth = function() return 11 end, GetDay = function() return 1 end,
    GetHour = function() return 20 end, GetMinute = function() return 1 end,
    GetSecond = function(_, date) return date end, GetMillisecond = function() return 0 end}
local guidlib = {IsValid = valid, Conv_GuidToString = function(_, g) return g end}
local active = {IsValid = valid, GetSlotName = function() return "savegame_0" end}
local subsystem = {IsValid = valid, SaveContext = {ActiveSave = active},
    GetLastSaveToDiscTimeStamp = function() return discStamp end}
function FindFirstOf(name)
    assert(name == "UWESaveGameSubsystem")
    active.MetaData = {SaveId = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", LastModified = checkpoint}
    subsystem.SaveContext.SaveGameCollection = {IsValid = valid, ContainerInfo = {SaveId = guid}}
    return saveReady and subsystem or nil
end
function StaticFindObject(path)
    if path == "/Script/AssetRegistry.Default__AssetRegistryHelpers" then return registry end
    if path == "/Script/Subnautica2.SN2PlayerCharacter" then return cls end
    if path == "/Script/Engine.Default__KismetMathLibrary" then return mathlib end
    if path == "/Script/Engine.Default__KismetGuidLibrary" then return guidlib end
end
package.preload.UEHelpers = function() return {
    GetPlayerController = function() controller.Pawn = playerReady and pawn or nil; return controller end,
    FindOrAddFName = function(s) return s end,
} end
function world:SpawnActor(_, location, rotation)
    local a = {alive = true, born = clock, location = {X=location.X,Y=location.Y,Z=location.Z}, rotation = rotation}
    a.anim={IsValid=valid,GetAddress=function() return #spawned+1000 end}
    a.morphs={}
    a.SkeletalMeshComponent={IsValid=valid,GetAnimInstance=function() return a.anim end,
        SetMorphTarget=function(_,name,value) a.morphs[name]=value end}
    function a:IsValid() return self.alive end
    function a:K2_DestroyActor() self.alive = false end
    function a:SetActorScale3D(scale) self.scale = scale end
    function a:GetGameTimeSinceCreation() return clock - self.born end
    function a:K2_SetActorLocation(location) self.location = {X=location.X,Y=location.Y,Z=location.Z} end
    function a:K2_SetActorRotation(rotation) self.rotation = rotation end
    spawned[#spawned + 1] = a; return a
end
function ExecuteInGameThread(fn) queue[#queue + 1] = fn end
function LoopInGameThreadAfterFrames(frames, fn) assert(frames == 1); loops.frame = fn end
function LoopInGameThreadWithDelay(ms, fn) assert(ms == 500); loops.poll = fn end
function RegisterHook(path, pre, post) hooks[path] = post; return 1, 2 end
function RegisterConsoleCommandHandler(name, fn) commands[name] = fn end
local function drain()
    local pending = queue; queue = {}
    for _, fn in ipairs(pending) do fn() end
end
local function command(name, argument)
    assert(commands[name], name); commands[name](name, argument and {argument} or {}); drain()
end
local function tick(dt) clock = clock + (dt or 1/60); loops.frame(); drain() end
local function loadWorld() for _=1,3 do loops.poll(); drain() end end
local function nativeSave(success, second)
    if success then checkpoint = second; discStamp = second end
    hooks["/Script/UWESaveSystem.UWESaveCommunicationComponent:AsyncSaveGameCompleted"](nil, {get = function() return success end})
    drain()
end
local function countFiles()
    local n = 0; for path in pairs(files) do if path:sub(-5) == ".json" then n = n + 1 end end; return n
end
local function distance(a,b) return math.sqrt((a.X-b.X)^2+(a.Y-b.Y)^2+(a.Z-b.Z)^2) end
dofile(dir .. "main.lua")
assert(commands.whale_spawn == nil and commands.whale_remove == nil and commands.whale_pause == nil, "Legacy aliases removed")
command("bigfatfish_spawn"); assert(#spawned == 0, "Menu guard")
playerReady = true; saveReady = false; loadWorld()
command("bigfatfish_spawn"); assert(#spawned == 0, "Unknown slot must not use default")
saveReady = true; assetsReady = false; loadWorld()
command("bigfatfish_spawn"); assert(#spawned == 0, "Missing assets")
assetsReady = true; loadWorld()
command("bigfatfish_spawn"); command("bigfatfish_spawn", "2")
assert(#spawned == 3 and spawned[1].alive and spawned[2].alive, "Repeated spawn must ADD fish")
for _,a in ipairs(spawned) do assert(a.scale.X>=1 and a.scale.X<=3,"Random size is 0.5 to 1.5 times base 2") end
assert(spawned[1].scale.X~=spawned[2].scale.X,"Each fish gets its own size")
command("bigfatfish_spawn", "-1"); command("bigfatfish_spawn", "oops")
assert(#spawned == 3, "Invalid counts must not spawn")
for _, fps in ipairs({30,60,144}) do
    local travelled = 0
    for _=1,fps do local previous = spawned[1].location; tick(1/fps); travelled=travelled+distance(previous,spawned[1].location) end
    assert(math.abs(travelled-50) < .15, "Patrol speed frame independence")
end
assert(spawned[1].anim.GazeTargetWorld, "Frame update writes public AnimBP target")
assert(spawned[1].morphs.BFF_Blink~=nil and spawned[1].morphs.BFF_MouthOpen~=nil,"Actual runtime updates face morphs")
command("bigfatfish_gaze","off")
for _=1,120 do tick() end
assert(spawned[1].anim.HeadAlpha<0.0001,"Runtime off command reaches AnimBP")
command("bigfatfish_gaze","on")
command("bigfatfish_follow")
local initialDistance = distance(spawned[1].location, origin)
for _=1,600 do
    local previous = spawned[1].location; tick()
    assert(distance(previous, spawned[1].location) <= 950/60+.001, "Follow speed cap and smooth updates")
end
assert(distance(spawned[1].location,origin) < initialDistance, "Follow approaches the player")
assert(distance(spawned[1].location,spawned[2].location)>100, "Followers spread out")
assert(distance(spawned[1].location,origin)>800, "Wingmates keep their distance")
local cameraYaw=math.rad(30)
local vx=spawned[1].location.X-origin.X
local vy=spawned[1].location.Y-origin.Y
local ahead=vx*math.cos(cameraYaw)+vy*math.sin(cameraYaw)
local side=-vx*math.sin(cameraYaw)+vy*math.cos(cameraYaw)
assert(ahead>800 and math.abs(math.deg(math.atan(side,ahead)))<32, "Wingmate remains ahead within view")
command("bigfatfish_stay")
local stopped = spawned[1].location; for _=1,60 do tick() end
assert(distance(stopped,spawned[1].location) == 0, "Stay freezes movement")
command("bigfatfish_wander"); tick()
assert(distance(stopped,spawned[1].location) < 1, "Wander restarts without teleport")
command("bigfatfish_follow")
nativeSave(false); assert(countFiles() == 0, "Failed game saves must not commit mod data")
nativeSave(true,11); assert(countFiles()==1, "Successful game save writes sidecar")
assert(directoryReady and mkdirCalls==1,"Missing save directory created automatically")
spawned[1].alive=false;nativeSave(true,16)
assert(countFiles()==1, "Unloading actors must not replace saved fish with an empty/partial list")
spawned[1].alive=true;checkpoint=11;discStamp=11
local savedPosition = spawned[1].location
local savedScale = spawned[1].scale.X
playerReady = false; loops.poll(); assert(not spawned[1].alive, "Menu clears instances")
playerReady = true; worldAddress = 202; checkpoint = 15; loadWorld()
assert(#spawned == 6 and spawned[4].alive, "Changed in-memory LastModified still restores three fish exactly once")
assert(distance(savedPosition, spawned[4].location)<.01, "Position round trip")
assert(math.abs(spawned[4].scale.X-savedScale)<1e-9,"Random size survives JSON numeric round trip without reroll: "..spawned[4].scale.X.." / "..savedScale)
for _=1,5 do loops.poll() end; assert(#spawned==6, "Repeated ready polls must not duplicate")
tick(); assert(distance(savedPosition,spawned[4].location)>0, "Follow state restored")
command("bigfatfish_remove"); nativeSave(true,12)
assert(countFiles()==1 and not spawned[4].alive, "Persist explicit removal")
playerReady=false;loops.poll(); playerReady=true;worldAddress=303;loadWorld()
assert(#spawned==6, "Removed fish stay removed")
playerReady=false;loops.poll(); playerReady=true;worldAddress=404;checkpoint=11;loadWorld()
assert(#spawned==6, "Current SaveId record remains authoritative across checkpoint timestamp changes")
playerReady=false;loops.poll();playerReady=true;worldAddress=505;guid="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";loadWorld()
assert(#spawned==6, "Different save must not inherit fish")
command("bigfatfish_spawn"); nativeSave(true,13)
assert(countFiles()==2, "Independent save identity")
command("bigfatfish_spawn")
checkpoint=14;discStamp=14;loops.poll()
assert(countFiles()==2, "Checkpoint changes update the current file without accumulating JSON")
playerReady=false;loops.poll();playerReady=true;worldAddress=606
local beforeRestart=#spawned
dofile(dir.."main.lua");loadWorld()
assert(#spawned==beforeRestart+2, "Fresh runtime reconstructs the native saved checkpoint")
assert(spawned[7].scale.X>=1 and spawned[7].scale.X<=3)
local Storage=dofile(dir.."storage.lua")
local json=dofile(dir.."json.lua")
local context={id=guid,slot="savegame_1",checkpoint="20261101200113000"}
local directory="TEST/Subnautica2/Saved/SaveGames/BigFatFish"
local data=assert(Storage.load(directory,context))
local savedSize=data.fish[1].size
assert(savedSize and savedSize>=0.5 and savedSize<=1.5,"Size serialized into native-save sidecar")
local validationContext={id=guid,checkpoint=data.checkpoint}
local invalid=json.decode(json.encode(data));invalid.fish[1].size=2
assert(not pcall(Storage.validate,invalid,validationContext),"Reject invalid saved scale")
local legacy=json.decode(json.encode(data));legacy.fish[1].size=nil
assert(Storage.validate(legacy,validationContext),"Existing fish without size remain readable")
local path=Storage.save(directory,context,data.fish)
files[path]="truncated"
local recovered,why=Storage.load(directory,context)
assert(recovered and why=="backup", "Corrupt current file falls back to good backup")
files[path]=json.encode(data);failRename=true
assert(not pcall(Storage.save,directory,context,{}), "Failed commit reported")
failRename=false;assert(Storage.load(directory,context), "Old save survives failed commit")
failWrite=true;assert(not pcall(Storage.save,directory,context,{}));failWrite=false
assert(Storage.load(directory,context), "Old save survives disk full")
assert(mkdirCalls==1,"Existing directory does not launch mkdir on normal saves")
local beforeCount=countFiles()
for _=1,50 do Storage.save(directory,context,data.fish) end
assert(countFiles()==beforeCount,"Repeated saves do not accumulate JSON")
local backupCount=0
for name in pairs(files) do if name:sub(-4)==".bak" then backupCount=backupCount+1 end end
assert(backupCount==2,"Only one backup per SaveId")
directoryReady=false;denyDirectory=true
assert(not pcall(Storage.save,directory,context,data.fish),"Directory creation failure is reported")
assert(Storage.load(directory,context),"Failed directory creation preserves existing data")
denyDirectory=false
Storage.save(directory,context,data.fish)
assert(directoryReady,"Deleted directory is recreated on retry")
data.version=999;assert(not pcall(Storage.validate,data,context), "Reject future schema")
data.version=1;data.saveId="wrong";assert(not pcall(Storage.validate,data,context), "Reject wrong SaveId")
data.saveId=guid;data.checkpoint="20261101200112000";assert(not pcall(Storage.validate,data,context), "Reject wrong checkpoint")
-- Regression from the real save: 55 wanderers must not reserve 55 wing slots.
local mixed={}
for i=1,56 do
    local record=json.decode(json.encode(data.fish[1]))
    record.id=i;record.mode=i==56 and "follow" or "wander";mixed[i]=record
end
Storage.save(directory,context,mixed)
worldAddress=worldAddress+1;loadWorld()
local loneFollower=spawned[#spawned]
for _=1,1500 do tick() end
assert(distance(loneFollower.location,origin)<1500,"55 wanderers must not push one follower 80 metres away")

for _, line in ipairs(logs) do originalPrint(line) end
originalPrint("PASS: removed legacy aliases; multiple spawn; 30/60/144 FPS; front wing formation/distance/view; native save success/failure; LastModified change regression; restore once; slot isolation; persisted deletion; backup recovery; Windows commit failure; disk full; schema validation; random independent sizes; size save/load; legacy default size; bounded face morph weights; automatic directory creation/retry; bounded current+backup files; 55-wanderer/one-follower regression")
