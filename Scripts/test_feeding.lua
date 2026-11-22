-- Check the inventory transaction and transient arrival lifecycle, not rendering.
local root=assert(arg[1])
local Feeding=dofile(root..'/Runtime/BigFatFish/Scripts/feeding.lua')
local valid=function() return true end
local pawn={IsValid=valid,GetAddress=function() return 11 end}
local other={IsValid=valid,GetAddress=function() return 12 end}
local origin={X=0,Y=0,Z=0};local rot={Yaw=0,Pitch=0}
local pc={PlayerCameraManager={IsValid=valid,GetCameraLocation=function() return origin end,GetCameraRotation=function() return rot end}}
local item={IsValid=valid};local asset={IsValid=valid};local count,spent=2,0
local inventory={IsValid=valid,GetItemCountByType=function() return count end,
    RemoveItemByType=function(_,_,n) assert(n==1);if count<1 then return false end;count=count-1;spent=spent+1;return true end}
pawn.InventoryComponent=inventory
function StaticFindObject(path) if path:find('CookedRice_ItemType',1,true) then return item end;return asset end
local world={IsValid=valid,GetAddress=function() return 7 end}
local props={}
function world:SpawnActor()
    local p={live=true,StaticMeshComponent={SetStaticMesh=function(self,m) self.mesh=m end}}
    function p:IsValid()return self.live end
    function p:K2_DestroyActor()self.live=false end
    function p:SetActorScale3D()end
    function p:K2_SetActorLocation(pos)self.position=pos end
    function p:K2_SetActorRotation()end
    props[#props+1]=p;return p
end
local fish,removed,allow,failMontage=nil,0,true,false
Feeding.configure({name=function(s)return s end,log=function()end,
    ready=function()return pc,pawn,world end,canSpawn=function()return allow end,
    spawn=function(pos,yaw)
        fish={size=1,position=pos,yaw=yaw,mode='follow'}
        local anim={IsValid=valid,PlaySlotAnimationAsDynamicMontage=function() if failMontage then return nil end;return asset end}
        fish.actor={IsValid=valid,SkeletalMeshComponent={GetAnimInstance=function()return anim end,
            GetSocketLocation=function(_,name) return {X=150,Y=name=='hand_L' and 20 or 30,Z=-20} end}}
        return fish
    end,remove=function(f)assert(f==fish);removed=removed+1 end})
assert(not Feeding.request(other));assert(spent==0)
allow=false;assert(not Feeding.request(pawn));assert(spent==0);allow=true
count=0;assert(not Feeding.request(pawn));count=2
failMontage=true;assert(not Feeding.request(pawn));assert(removed==1 and spent==0);failMontage=false
assert(Feeding.request(pawn));assert(Feeding.isUnpaid(fish));assert(spent==0)
assert(not Feeding.request(pawn));assert(count==2)
for i=1,7 do assert(Feeding.update(fish,.2,origin,rot,world)) end
assert(spent==0)
for i=1,4 do Feeding.update(fish,.2,origin,rot,world) end
assert(spent==1 and count==1 and not Feeding.isUnpaid(fish))
for i=1,16 do Feeding.update(fish,.2,origin,rot,world) end
assert(spent==1 and fish.mode=='follow' and fish.feedMouth==nil)
assert(not props[#props]:IsValid())
assert(Feeding.request(pawn));Feeding.cancel();assert(count==1 and spent==1 and removed==2)
assert(Feeding.request(pawn));count=0
for i=1,10 do Feeding.update(fish,.2,origin,rot,world) end
assert(spent==1 and removed==3)
print('PASS: local-use guard, capacity, no-food, montage rollback, duplicate-use guard, delayed exactly-once rice payment, follow handoff and cancellation')
