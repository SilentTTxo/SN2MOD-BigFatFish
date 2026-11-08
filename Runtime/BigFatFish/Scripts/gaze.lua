-- Public AnimBP inputs only; the native LookAt nodes apply the bone limits.
local Gaze = {enabled = true}
local function valid(object) return object ~= nil and object:IsValid() end
local function clamp(value, low, high) return math.max(low, math.min(high, value)) end
local function blend(current, target, response, dt)
    return current + (target - current) * (1 - math.exp(-response * dt))
end
function Gaze.update(fish, target, dt)
    local mesh = fish.actor.SkeletalMeshComponent
    if not valid(mesh) then return false end
    local anim = mesh:GetAnimInstance()
    if not valid(anim) then return false end
    local g = fish.gaze
    if not g or g.address ~= anim:GetAddress() then
        g = {address = anim:GetAddress(), target = {X = target.X, Y = target.Y, Z = target.Z}, neck = 0, head = 0, eyes = 0}
        fish.gaze = g
    end
    dt = clamp(dt, 0, 0.2)
    for _, axis in ipairs({"X", "Y", "Z"}) do
        g.target[axis] = blend(g.target[axis], target[axis], 8, dt)
    end
    local dx, dy, dz = target.X - fish.position.X, target.Y - fish.position.Y, target.Z - fish.position.Z
    local distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    local yaw = math.rad(fish.yaw)
    local forward = (dx * math.cos(yaw) + dy * math.sin(yaw)) / math.max(distance, 1)
    local angle = math.deg(math.acos(clamp(forward, -1, 1)))
    -- Fade near the rear dead angle to prevent left/right snapping at 180 degrees.
    local weight = Gaze.enabled and clamp((175 - angle) / 40, 0, 1) * clamp((5000 - distance) / 1500, 0, 1) or 0
    if distance < 50 then weight = 0 end
    g.neck = blend(g.neck, weight * 0.6, 4, dt)
    g.head = blend(g.head, weight, 6, dt)
    g.eyes = blend(g.eyes, weight, 12, dt)
    anim.GazeTargetWorld = {X = g.target.X, Y = g.target.Y, Z = g.target.Z}
    anim.NeckAlpha = g.neck
    anim.HeadAlpha = g.head
    anim.EyeAlpha = g.eyes
    return true
end
return Gaze
