-- Model the native backpack debit as well as the visual state machine.
local root=assert(arg[1]);local Feeding=dofile(root..'/Runtime/BigFatFish/Scripts/feeding.lua')
local clock,count,nativeSpent,refunds,extraDebits=0,3,0,0,0
local menu,rendered,allow=true,true,true
local valid=function()return true end
local item={IsValid=valid,GetFullName=function()return 'UWEItemType /BigFatFishRice/Data/DA_BFF_CookedRice_ItemType.DA_BFF_CookedRice_ItemType' end}
local generic={IsValid=valid,GetMaterial=function()return item end}
function StaticFindObject(path)if path:find('CookedRice_ItemType',1,true) then return item end;return generic end
local world={IsValid=valid,GetAddress=function()return 7 end}
local inventory={IsValid=valid,GetItemCountByType=function()return count end,
    RemoveItemByType=function()extraDebits=extraDebits+1;error('The native use already paid!')end,
    AddItemTypeToInventory=function(_,_,n)assert(n==1);count=count+n;refunds=refunds+1;return true end}
local pawn={IsValid=valid,GetAddress=function()return 11 end,InventoryComponent=inventory,GetGameTimeSinceCreation=function()return clock end}
local origin,rot={X=0,Y=0,Z=0},{Yaw=0,Pitch=0}
local pc={PlayerCameraManager={IsValid=valid,GetCameraLocation=function()return origin end,GetCameraRotation=function()return rot end}}
local vm={IsValid=valid,GetItemType=function()return item end,GetAddress=function()return 31 end}
local props,fishs,plays,removed={},{},0,0
function world:SpawnActor()
 local p={live=true,StaticMeshComponent={GetNumMaterials=function()return 3 end,SetMaterial=function()end,
  SetStaticMesh=function(self,m)self.mesh=m end}}
 function p:IsValid()return self.live end
 function p:K2_DestroyActor()self.live=false end
 function p:SetActorScale3D()end
 function p:K2_SetActorLocation(pos)self.position=pos end
 function p:K2_SetActorRotation()end
 props[#props+1]=p;return p
end
local anim={IsValid=valid,pos=0,playing=false,paused=false}
function anim:PlaySlotAnimationAsDynamicMontage(_,_,_,_,rate)plays=plays+1;self.pos=0;self.playing=true;self.rate=rate;return generic end
function anim:Montage_GetPosition()return self.playing and self.pos or 0 end
function anim:Montage_IsPlaying()return self.playing end
function anim:Montage_Pause()self.paused=true end
function anim:Montage_Resume()self.paused=false end
Feeding.configure({name=function(s)return s end,log=function()end,ready=function()return pc,pawn,world end,
 menuOpen=function()return menu end,canSpawn=function()return allow end,
 spawn=function(pos,yaw)
  local f={id=#fishs+1,size=1,position=pos,yaw=yaw,mode='follow'}
  f.actor={IsValid=valid,SetActorHiddenInGame=function(self,x)self.hidden=x end,K2_SetActorLocation=function()end,
   WasRecentlyRendered=function()return rendered end,SkeletalMeshComponent={IsValid=valid,VisibilityBasedAnimTickOption=2,bEnableUpdateRateOptimizations=true,
    DoesSocketExist=function()return true end,GetAnimInstance=function()return anim end,
    GetSocketLocation=function(_,name)return {X=150,Y=name=='hand_L' and 20 or 30,Z=-20}end}}
  fishs[#fishs+1]=f;return f
 end,remove=function()removed=removed+1 end})
local function ability()return {IsValid=valid,ended=0,K2_EndAbility=function(self)self.ended=self.ended+1 end}end
local function use(a,beforeCallback)
 Feeding.beginInventoryUse(vm)
 if not beforeCallback then count=count-1;nativeSpent=nativeSpent+1 end
 local receipt=Feeding.claimReceipt(pawn)
 local ok=Feeding.request(pawn,a,receipt)
 if beforeCallback then count=count-1;nativeSpent=nativeSpent+1 end
 Feeding.endInventoryUse(vm);Feeding.poll();return ok
end
local function step(n)
 for i=1,n do
  clock=clock+.05
  if anim.playing and not anim.paused then anim.pos=anim.pos+.05*anim.rate;if anim.pos>=4.8 then anim.playing=false end end
  local f=fishs[#fishs];if f then Feeding.update(f,.05,origin,rot,world) end
  Feeding.poll()
 end
end
local a=ability();assert(use(a,true));assert(count==2 and nativeSpent==1 and extraDebits==0)
step(80);assert(#props==0 and plays==0 and fishs[1].actor.hidden)
local b=ability();assert(not use(b));assert(count==2 and refunds==1 and #fishs==1)
menu=false;rendered=false;step(100)
assert(#props==1 and plays==0 and Feeding.status():find('visible_pose',1,true))
rendered=true;step(10);assert(plays==1 and anim.pos<.3)
step(30);assert(Feeding.status():find('reaching',1,true));assert(extraDebits==0)
menu=true;step(1);local frozen=anim.pos;step(60);assert(anim.pos==frozen and anim.paused)
menu=false;step(160)
assert(a.ended==1 and fishs[1].mode=='follow' and removed==0 and extraDebits==0)
assert(not props[1]:IsValid() and Feeding.status()=='idle')
assert(fishs[1].actor.SkeletalMeshComponent.VisibilityBasedAnimTickOption==2)
-- The last native-paid serving leaves zero items before the Lua callback.
count=1;menu=true;local c=ability();assert(use(c));assert(count==0)
menu=false;step(230);assert(c.ended==1 and Feeding.status()=='idle' and count==0 and #fishs==2)
-- A rejected offering refunds only the one debit proven by a native receipt.
count=1;allow=false;assert(not use(ability()));assert(count==1 and refunds==2 and #fishs==2)
assert(extraDebits==0)
print('PASS: native-before/native-after use timing; exactly one total debit; last serving; busy refund; backpack/visibility gating; delayed montage; paused UI; new fish retained in follow; no extra mod removals')
