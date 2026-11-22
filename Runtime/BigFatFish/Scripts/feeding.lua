-- One native inventory use -> one behind-player arrival -> one paid meal.
local Feeding = {}
local D, active
local function valid(o) return o ~= nil and o:IsValid() end
local function mix(a,b,t) return {X=a.X+(b.X-a.X)*t,Y=a.Y+(b.Y-a.Y)*t,Z=a.Z+(b.Z-a.Z)*t} end
local function smooth(t) t=math.max(0,math.min(1,t));return t*t*(3-2*t) end
local function point(o,v,forward,right,up)
    local yaw,pitch=math.rad(v.Yaw),math.rad(v.Pitch or 0)
    local cy,sy,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch)
    return {X=o.X+cy*cp*forward-sy*right-cy*sp*up,
        Y=o.Y+sy*cp*forward+cy*right-sy*sp*up,Z=o.Z+sp*forward+cp*up}
end
local function asset(package,name)
    local obj=StaticFindObject(package..'.'..name)
    if valid(obj) then return obj end
    local helper=StaticFindObject('/Script/AssetRegistry.Default__AssetRegistryHelpers')
    if valid(helper) then obj=helper:GetAsset({PackageName=D.name(package),AssetName=D.name(name)}) end
    return valid(obj) and obj or nil
end
local function view(pc,pawn)
    local camera=pc.PlayerCameraManager
    if valid(camera) then return camera:GetCameraLocation(),camera:GetCameraRotation() end
    return pawn:K2_GetActorLocation(),pc:GetControlRotation()
end
function Feeding.configure(deps) D=deps end
function Feeding.isActive(fish) return active and active.fish==fish end
function Feeding.status() return active and string.format('%.2fs; rice_spent=%s',active.time,tostring(active.paid)) or 'idle' end
function Feeding.isUnpaid(fish) return active and active.fish==fish and not active.paid end
function Feeding.cancel()
    local meal=active;active=nil
    if not meal then return end
    if valid(meal.prop) then meal.prop:K2_DestroyActor() end
    meal.fish.feedMouth=nil
    if not meal.paid then D.remove(meal.fish) end
end
function Feeding.request(avatar)
    if active then return false,'A fish is already taking the rice; no extra rice was spent.' end
    local pc,pawn,world=D.ready()
    if not pc then return false,'Load a save and wait for the fish save session.' end
    if not valid(avatar) or avatar:GetAddress()~=pawn:GetAddress() then return false,'Ignoring non-local rice use.' end
    if not D.canSpawn() then return false,'Fish limit reached; rice was not spent.' end
    local item=asset('/BigFatFishRice/Data/DA_BFF_CookedRice_ItemType','DA_BFF_CookedRice_ItemType')
    local serving=asset('/BigFatFishRice/Blueprints/BP_BFF_RiceServing','BP_BFF_RiceServing_C')
    local animation=asset('/Game/Mods/BigFatFish/Character/AN_BigFatFish_GrabEat','AN_BigFatFish_GrabEat')
    local empty=asset('/BigFatFishRice/Meshes/SM_BFF_EmptyRiceBowl','SM_BFF_EmptyRiceBowl')
    if not item or not serving or not animation or not empty then return false,'Rice/feeding content is missing; rice was not spent.' end
    local inventory=pawn.InventoryComponent
    if not valid(inventory) or inventory:GetItemCountByType(item)<1 then return false,'No Steamed Rice in the local inventory.' end
    local origin,rotation=view(pc,pawn)
    local start=point(origin,rotation,-320,85,-25)
    local prop=world:SpawnActor(serving,point(origin,rotation,70,25,-25),{Pitch=0,Yaw=rotation.Yaw,Roll=0})
    if not valid(prop) then return false,'Could not show the rice bowl; rice was not spent.' end
    prop:SetActorScale3D({X=1.7,Y=1.7,Z=1.7})
    local ok,fish=pcall(D.spawn,start,rotation.Yaw)
    if not ok then prop:K2_DestroyActor();return false,tostring(fish) end
    active={fish=fish,prop=prop,inventory=inventory,item=item,empty=empty,time=0,paid=false,
        start=start,control1=point(origin,rotation,-170,360,-20),world=world:GetAddress()}
    local success,err=pcall(function()
        local anim=fish.actor.SkeletalMeshComponent:GetAnimInstance();assert(valid(anim),'Animation instance is not ready')
        local montage=anim:PlaySlotAnimationAsDynamicMontage(animation,D.name('DefaultSlot'),0.18,0.25,1,1,-1,0)
        assert(valid(montage),'Grab/eat montage failed')
    end)
    if not success then Feeding.cancel();return false,tostring(err) end
    D.log('Rice offered: fish is approaching from behind; rice is deducted on the grab.')
    return true
end
function Feeding.update(fish,dt,origin,rotation,world)
    local m=active
    if not m or m.fish~=fish then return false end
    if not valid(m.prop) or world:GetAddress()~=m.world then Feeding.cancel();return false end
    m.time=m.time+math.max(0,math.min(dt,0.2))
    local held=point(origin,rotation,70,25,-25)
    local goal=point(origin,rotation,175,55,-20)
    if m.time<1.6 then
        local t=smooth(m.time/1.6)
        local c2=point(origin,rotation,160,250,-10)
        local a=mix(m.start,m.control1,t);local b=mix(m.control1,c2,t);local c=mix(c2,goal,t)
        fish.position=mix(mix(a,b,t),mix(b,c,t),t)
        fish.yaw=rotation.Yaw+180*smooth((m.time-.65)/.95)
        m.prop:K2_SetActorLocation(held,false,{},false)
    else
        if not m.paid then
            if not valid(m.inventory) or m.inventory:GetItemCountByType(m.item)<1 or not m.inventory:RemoveItemByType(m.item,1) then
                D.log('Rice disappeared before the grab; arrival cancelled without spending rice.')
                Feeding.cancel();return true
            end
            m.paid=true;D.log('Fish grabbed exactly one Steamed Rice.')
        end
        fish.position=mix(fish.position,goal,1-math.exp(-4*dt))
        local diff=(rotation.Yaw+180-fish.yaw+180)%360-180
        fish.yaw=fish.yaw+diff*(1-math.exp(-4*dt))
        local mesh=fish.actor.SkeletalMeshComponent
        local left=mesh:GetSocketLocation(D.name('hand_L'))
        local right=mesh:GetSocketLocation(D.name('hand_R'))
        local hands=mix(left,right,.5);hands.Z=hands.Z-3*fish.size
        local bowl=mix(held,hands,smooth((m.time-1.6)/.3))
        m.prop:K2_SetActorLocation(bowl,false,{},false)
        m.prop:K2_SetActorRotation({Pitch=0,Yaw=fish.yaw,Roll=0},false)
        fish.feedMouth=(.20+.35*math.sin((m.time-1.6)*math.pi*3.5)^2)*(1-smooth((m.time-3.9)/.4))
        if m.time>=3.9 and not m.emptied then
            m.prop.StaticMeshComponent:SetStaticMesh(m.empty);m.emptied=true
        end
    end
    if m.time>=4.8 then
        m.prop:K2_DestroyActor();active=nil;fish.feedMouth=nil
        fish.mode='follow';fish.velocity={X=0,Y=0,Z=0}
        D.log('Rice finished; the new Big Fat Fish is following. Save the game to keep it.')
    end
    return true
end
return Feeding
