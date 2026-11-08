local root=assert(arg[1])
local Face=dofile(root.."/Runtime/BigFatFish/Scripts/face.lua")
Face.configure({blink="blink",mouthOpen="open",mouthRound="round"},function(s) return s end)
local function fish()
    local weights={}
    local mesh={IsValid=function() return true end,SetMorphTarget=function(_,name,value) weights[name]=value end}
    return {actor={SkeletalMeshComponent=mesh}},weights
end
math.randomseed(400)
local a,wa=fish()
local b,wb=fish()
local blinks,mouth,independent=0,false,false
local previous=0
for _=1,60*40 do
    assert(Face.update(a,1/60));assert(Face.update(b,1/60))
    assert(wa.blink>=0 and wa.blink<=1)
    assert(wa.open>=0 and wa.open<=0.3 and wa.round<=0.075)
    if wa.blink>=0.99 and previous<0.99 then blinks=blinks+1 end
    if wa.open>0.1 then mouth=true end
    if math.abs(wa.blink-wb.blink)>0.2 then independent=true end
    previous=wa.blink
end
assert(blinks>=4 and blinks<=15,"Natural random blink interval")
assert(mouth and independent,"Mouth activity and independent blink schedules")
-- Both envelopes reach neutral without leaving a stuck facial expression.
a.face.nextBlink=math.huge;a.face.nextMouth=math.huge
for _=1,120 do Face.update(a,1/60) end
assert(wa.blink==0 and wa.open==0 and wa.round==0)
assert(not Face.update({actor={}},0.016))
print("PASS: random independent blinks; complete closure/reopening; gentle intermittent mouth; bounded weights; neutral recovery")
