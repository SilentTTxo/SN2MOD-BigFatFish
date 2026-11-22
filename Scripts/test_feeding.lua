-- World-drop lifecycle: no inventory use/debit, pickup cancellation, one fish.
local root=assert(arg[1]);local Feeding=dofile(root..'/Runtime/BigFatFish/Scripts/feeding.lua')
local clock,menu,allow=0,false,true
local function valid()return true end
local asset={IsValid=valid,GetMaterial=function()return {IsValid=valid}end}
function StaticFindObject()return asset end
local anim={IsValid=valid,pos=0,playing=false}
function anim:PlaySlotAnimationAsDynamicMontage()self.pos=0;self.playing=true;return asset end
function anim:Montage_GetPosition()return self.pos end
function anim:Montage_IsPlaying()return self.playing end
function anim:Montage_Stop()self.playing=false end
function anim:Montage_Pause()self.paused=true end
function anim:Montage_Resume()self.paused=false end
local world={IsValid=valid,GetAddress=function()return 7 end}
local props,fishs,items,removed={},{},{},0
function world:SpawnActor()
 local prop={live=true,EmptyMesh=asset,StaticMeshComponent={IsValid=valid,GetNumMaterials=function()return 2 end,SetMaterial=function()end,SetStaticMesh=function(_,m)assert(m==asset)end}}
 function prop:IsValid()return self.live end
 function prop:K2_DestroyActor()self.live=false end
 function prop:SetActorScale3D()end
 function prop:K2_SetActorLocation()end
 function prop:K2_SetActorRotation()end
 props[#props+1]=prop;return prop
end
local origin,rotation={X=0,Y=0,Z=0},{Yaw=0,Pitch=0}
local pawn={IsValid=valid,GetGameTimeSinceCreation=function()return clock end,K2_GetActorLocation=function()return origin end,HasAuthority=function()return true end}
-- Any access to native inventory in the new offering flow is a regression.
pawn.InventoryComponent=setmetatable({},{__index=function()error('Offering must never touch inventory')end})
local pc={GetControlRotation=function()return rotation end}
function FindAllOf()return items end
Feeding.configure({name=function(s)return s end,log=function()end,ready=function()return pc,pawn,world end,
 menuOpen=function()return menu end,canSpawn=function()return allow end,
 spawn=function(pos,yaw)
  local mesh={IsValid=valid,VisibilityBasedAnimTickOption=2,bEnableUpdateRateOptimizations=true,DoesSocketExist=function()return true end,GetAnimInstance=function()return anim end,
   GetSocketLocation=function(_,name)return {X=140,Y=name=='hand_L' and 20 or 30,Z=-20}end}
  local f={id=#fishs+1,size=1,position=pos,yaw=yaw,mode='follow',actor={IsValid=valid,SkeletalMeshComponent=mesh,FeedAnimation=asset,WasRecentlyRendered=function()return true end,SetActorHiddenInGame=function()end}}
  fishs[#fishs+1]=f;return f
 end,remove=function()removed=removed+1 end})
local function drop()
 local item={live=true,owned=false,address=#items+1}
 function item:IsValid()return self.live end
 function item:GetWorld()return world end
 function item:GetAddress()return self.address end
 function item:IsEquipped()return self.owned end
 function item:IsOwned()error('Native IsOwned crashes when a dropped item has Owner=nil; must never be called')end
 function item:IsHidden()return false end
 function item:GetAttachParentActor()end
 function item:K2_GetActorLocation()return {X=90,Y=0,Z=-25}end
 function item:K2_DestroyActor()self.live=false;self.consumed=(self.consumed or 0)+1 end
 items[#items+1]=item;return item
end
local function step(seconds)
 for i=1,math.floor(seconds/.05+.5) do
  clock=clock+.05
  if anim.playing and not anim.paused then anim.pos=anim.pos+.05*.7;if anim.pos>=4.8 then anim.playing=false end end
  Feeding.discover()
  local f=fishs[#fishs];if f then Feeding.update(f,.05,origin,rotation,world) end
 end
end
step(5);assert(#fishs==0,'Eating has no dropped actor and cannot summon')
local held=drop();held.Owner={IsValid=valid};step(4)
assert(#fishs==0,'An actor with an owner is not a world offering')
held.live=false
local a=drop();step(2.9);assert(#fishs==0)
a.owned=true;step(2);assert(#fishs==0,'Picked up before three seconds')
a.owned=false;step(3.2);assert(#fishs==1 and a.live)
step(14);assert(not a.live and a.consumed==1 and fishs[1].mode=='follow' and removed==0)
assert(Feeding.status()=='idle' and not props[1].live)
assert(fishs[1].actor.FeedEmptyMesh==asset and fishs[1].actor.FeedServingClass==asset,'Native actor retains loaded assets')
step(5);assert(#fishs==1,'A consumed actor cannot trigger twice')
local b=drop();step(3.3);assert(#fishs==2);b.owned=true;step(.1)
assert(b.live and removed==1 and Feeding.status()=='idle','Pickup during approach cancels without charging')
allow=false;local c=drop();step(5);assert(#fishs==2 and c.live)
allow=true;step(14);assert(#fishs==3 and c.consumed==1)
print('PASS: >3s continuous world drop, early/approach pickup cancellation, one source/one fish, native asset ownership, zero inventory calls, ordinary follow handoff')
