local root=assert(arg[1]);local M=dofile(root..'/Runtime/BigFatFish/Scripts/interactions.lua')
local time=0;local f={position={X=0,Y=0,Z=0},yaw=0,mode='wander',actor={IsValid=function()return true end}}
local far={position={X=10000,Y=0,Z=0},actor=f.actor}
local pawn={GetGameTimeSinceCreation=function()return time end,K2_GetActorLocation=function()return f.position end}
M.configure({ready=function()return {},pawn end,fish=function()return {f,far}end,config={MeshYawOffsetDegrees=0,PatrolRadiusCm=300},log=function()end})
assert(M.identify('DA_Emote1ThumbDown')=='angry')
assert(M.identify('DA_Emote2ThumbUp')=='happy')
assert(M.identify('Animation.Emote.Expressive')=='sad')
assert(M.identify('Animation.Emote.Clap')=='basin')
assert(M.identify('Animation.Emote.Wave')=='movement')
assert(M.identify('Animation.Swim')==nil)
M.react('basin');M.react('basin');assert(f.basinMode and not far.basinMode,'Duplicate native hooks toggle only once')
time=2;M.react('basin');assert(not f.basinMode)
time=4;M.react('movement');assert(f.mode=='follow')
time=6;M.react('movement');assert(f.mode=='wander' and f.center)
for _,kind in ipairs({'happy','sad','angry'}) do time=time+2;M.react(kind);assert(f.emotion.kind==kind and not far.emotion) end
print('PASS: five native emotes, deduplication, nearby reactions, formation toggle, emotions')
