local root=assert(arg[1]);local M=dofile(root..'/Runtime/BigFatFishRice/Scripts/wild_rice.lua')
local valid=function()return true end
local time,worldId,saveId=0,7,'saveA';local nativeSaved,actors={},{}
local world={IsValid=valid,GetAddress=function()return worldId end}
local pawn={IsValid=valid,GetWorld=function()return world end,HasAuthority=function()return true end,GetGameTimeSinceCreation=function()return time end,K2_GetActorLocation=function()return {X=0,Y=0,Z=0}end}
local pc={IsValid=valid,Pawn=pawn}
local function text(g)if type(g)=='string' then return g end;return g.A..':'..g.B..':'..g.C..':'..g.D end
local guidlib={IsValid=valid,Conv_GuidToString=function(_,g)return text(g)end}
local saves={IsValid=valid,SaveContext={ActiveSave={IsValid=valid,MetaData={SaveId=saveId}}}}
function FindFirstOf()return saves end
local map={ForEach=function(_,callback)for key in pairs(nativeSaved) do callback({get=function()return key end})end end}
local empty={ForEach=function()end}
local manager={IsValid=valid,GetWorld=function()return world end,DynamicItemsSave={DynamicItems=map},ActiveActorsByID=empty}
function manager:SpawnActorAndRegisterWithoutDropping(_,transform,guid)
 local key=text(guid);assert(not nativeSaved[key],'Native GUID must never be spawned twice')
 assert(transform.Translation.Z==-998 and transform.Scale3D.X==1)
 nativeSaved[key]=true;actors[#actors+1]=key;return {IsValid=valid}
end
function manager:SetRemoveIfOutOfRange(_,flag)assert(flag==false)end
local pod={IsValid=valid,GetWorld=function()return world end,K2_GetActorLocation=function()return {X=0,Y=0,Z=0}end}
local terrain=true
local system={IsValid=valid,LineTraceSingleForObjects=function(_,_,start,finish,types,_,_,_,hit)
 assert(types[1]==0,'Only WorldStatic terrain')
 if not terrain then return false end
 hit.ImpactNormal={Z=1};hit.ImpactPoint={X=start.X,Y=start.Y,Z=-1000};return true
end}
function StaticFindObject(path)if path:find('GuidLibrary',1,true)then return guidlib end;if path:find('SystemLibrary',1,true)then return system end;return {IsValid=valid}end
function FindAllOf(name)if name=='UWEDynamicItemsManager'then return {manager}end;if name=='BP_StaticLifepod_Underwater_C'then return {pod}end;return {}end
M.configure({player=function()return pc end,name=function(s)return s end,log=function()end})
local function poll(n)for i=1,n do time=time+.5;M.poll()end end
terrain=false;poll(25);assert(#actors==0,'Never place a wild crop without a seabed hit')
terrain=true;poll(20);assert(#actors==8)
poll(30);assert(#actors==8)
worldId=8;poll(40);assert(#actors==8,'Reload native saved GUIDs without respawning ripe plants')
saveId='saveB';saves.SaveContext.ActiveSave.MetaData.SaveId=saveId;poll(40);assert(#actors==16,'World-specific population')
print('PASS: native dynamic registration, stable world GUIDs, no reload duplication, terrain required, finite eight-plant population')
