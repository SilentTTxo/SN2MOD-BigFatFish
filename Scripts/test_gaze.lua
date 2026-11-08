local root = assert(arg[1])
local Gaze = dofile(root .. "/Runtime/BigFatFish/Scripts/gaze.lua")
local function fish()
    local anim = {IsValid = function() return true end, GetAddress = function() return 123 end}
    local mesh = {IsValid = function() return true end, GetAnimInstance = function() return anim end}
    return {actor = {SkeletalMeshComponent = mesh}, position = {X = 0, Y = 0, Z = 0}, yaw = 0}, anim
end
local ahead, behind = {X = 1000, Y = 300, Z = 100}, {X = -1000, Y = 0, Z = 0}
local results = {}
for _, fps in ipairs({30, 60, 144}) do
    local f, a = fish()
    for _ = 1, fps do assert(Gaze.update(f, ahead, 1 / fps)) end
    assert(a.HeadAlpha > 0.99 and a.EyeAlpha > 0.99 and a.NeckAlpha > 0.58)
    results[#results + 1] = a.HeadAlpha
    assert(a.GazeTargetWorld.X == ahead.X)
    for _ = 1, fps * 2 do Gaze.update(f, behind, 1 / fps) end
    assert(a.HeadAlpha < 0.0001 and a.EyeAlpha < 0.0001, "Rear dead angle must relax")
end
assert(math.abs(results[1] - results[3]) < 0.000001, "Frame independent blend")
local f, a = fish()
for _ = 1, 120 do Gaze.update(f, ahead, 1 / 60) end
Gaze.enabled = false
for _ = 1, 120 do Gaze.update(f, ahead, 1 / 60) end
assert(a.HeadAlpha < 0.0001, "Off smoothly returns to swim")
Gaze.enabled = true
for _ = 1, 120 do Gaze.update(f, {X = 6000, Y = 0, Z = 0}, 1 / 60) end
assert(a.EyeAlpha < 0.0001, "Far target relaxes")
assert(not Gaze.update({actor = {}}, ahead, 0.016), "Missing mesh is harmless")
local other, b = fish()
for _ = 1, 120 do Gaze.update(other, ahead, 1 / 60) end
assert(b.HeadAlpha > 0.99 and a.HeadAlpha < 0.0001, "Instances are independent")
print("PASS: actual runtime gaze; 30/60/144 FPS; rear/far relaxation; off blend; independent instances; unavailable mesh")
