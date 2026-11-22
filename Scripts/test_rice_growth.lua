-- Saved and newly spawned panicles stay at a rotated/scaled plant's crown.
local root=assert(arg[1]);local delayed,frame
local valid=function()return true end
local world={IsValid=valid,GetAddress=function()return 9 end}
local pawn={IsValid=valid,GetWorld=function()return world end}
package.preload.UEHelpers=function()return {GetPlayerController=function()return {IsValid=valid,Pawn=pawn}end}end
function RegisterConsoleCommandHandler()end
function LoopInGameThreadWithDelay(_,callback)delayed=callback end
function LoopInGameThreadAfterFrames(_,callback)frame=callback end
local moved,droppedMoved=0,0
local seed={IsValid=valid,K2_SetActorLocation=function(self,p)self.position=p;moved=moved+1 end}
local dropped={IsValid=valid,K2_SetActorLocation=function()droppedMoved=droppedMoved+1 end}
local plant={IsValid=valid,GetWorld=function()return world end,K2_GetActorLocation=function()return {X=100,Y=200,Z=300}end,
    GetActorUpVector=function()return {X=0,Y=.6,Z=.8}end,GetActorScale3D=function()return {X=2,Y=2,Z=2}end}
plant.RiceSeedGrower={IsValid=valid,HasSeed=function()return true end,GetSeedActor=function()return seed end}
local picked={IsValid=valid,GetWorld=function()return world end,RiceSeedGrower={IsValid=valid,HasSeed=function()return false end,GetSeedActor=function()return dropped end}}
function FindAllOf()return {plant,picked}end
dofile(root..'/Runtime/BigFatFishRice/Scripts/main.lua')
delayed();frame();assert(moved==1 and droppedMoved==0)
assert(seed.position.X==100 and math.abs(seed.position.Y-286.4)<.001 and math.abs(seed.position.Z-415.2)<.001)
-- Native growth or a saved transform can move the seed back to soil; the next
-- frame restores the crown, without changing seed scale, ripeness or inventory.
seed.position={X=100,Y=200,Z=300};frame();assert(moved==2 and seed.position.Z>400)
plant.RiceSeedGrower.HasSeed=function()return false end;frame();assert(moved==2)
print('PASS: translated/rotated/scaled crown, saved soil-origin correction, mature/young ownership path, harvested/dropped items left alone')
