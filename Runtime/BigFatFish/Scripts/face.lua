-- Authored morph targets: intermittent soft mouth motion and independent blinks.
local Face = {}
local names
function Face.configure(morphs, makeName)
    names = {}
    for key, value in pairs(morphs) do names[key] = makeName(value) end
end
local function smooth(t) return t * t * (3 - 2 * t) end
function Face.update(fish, dt)
    local mesh = fish.actor.SkeletalMeshComponent
    if not mesh or not mesh:IsValid() then return false end
    if not fish.face then
        fish.face = {time = 0, nextBlink = 1.5 + math.random() * 4,
            nextMouth = 1 + math.random() * 5, mouthAmplitude = 0}
    end
    local f = fish.face
    f.time = f.time + math.max(0, math.min(dt, 0.2))
    if f.time >= f.nextBlink then
        f.blinkStart = f.time
        f.nextBlink = f.time + 2.5 + math.random() * 4.5
    end
    local blink = 0
    if f.blinkStart then
        local t = f.time - f.blinkStart
        if t < 0.07 then blink = smooth(t / 0.07)
        elseif t < 0.10 then blink = 1
        elseif t < 0.24 then blink = 1 - smooth((t - 0.10) / 0.14)
        else f.blinkStart = nil end
    end
    if f.time >= f.nextMouth then
        f.mouthStart = f.time
        f.mouthDuration = 1.0 + math.random() * 0.8
        f.mouthAmplitude = 0.12 + math.random() * 0.18
        f.nextMouth = f.time + f.mouthDuration + 2 + math.random() * 4
    end
    local mouth = 0
    if f.mouthStart then
        local t = (f.time - f.mouthStart) / f.mouthDuration
        if t <= 1 then mouth = f.mouthAmplitude * math.sin(math.pi * t) ^ 2
        else f.mouthStart = nil end
    end
    mesh:SetMorphTarget(names.blink, blink, true)
    mesh:SetMorphTarget(names.mouthOpen, mouth, true)
    mesh:SetMorphTarget(names.mouthRound, mouth * 0.25, true)
    return true
end
return Face
