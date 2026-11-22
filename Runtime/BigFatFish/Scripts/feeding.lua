-- Backpack use owns the item cost. This module never removes another serving.
local Feeding={}
local D,active
local receipts,openUses,refunds={},{},{}
local ITEM='/BigFatFishRice/Data/DA_BFF_CookedRice_ItemType.DA_BFF_CookedRice_ItemType'
local function valid(o) return o~=nil and o:IsValid() end
local function mix(a,b,t) return {X=a.X+(b.X-a.X)*t,Y=a.Y+(b.Y-a.Y)*t,Z=a.Z+(b.Z-a.Z)*t} end
local function smooth(t) t=math.max(0,math.min(1,t));return t*t*(3-2*t) end
local function point(o,v,forward,right,up)
    local y,p=math.rad(v.Yaw),math.rad(v.Pitch or 0)
    local cy,sy,cp,sp=math.cos(y),math.sin(y),math.cos(p),math.sin(p)
    return {X=o.X+cy*cp*forward-sy*right-cy*sp*up,Y=o.Y+sy*cp*forward+cy*right-sy*sp*up,Z=o.Z+sp*forward+cp*up}
end
local function asset(package,name)
    local o=StaticFindObject(package..'.'..name)
    if valid(o) then return o end
    local helper=StaticFindObject('/Script/AssetRegistry.Default__AssetRegistryHelpers')
    if valid(helper) then o=helper:GetAsset({PackageName=D.name(package),AssetName=D.name(name)}) end
    return valid(o) and o or nil
end
local function view(pc,pawn)
    local camera=pc.PlayerCameraManager
    if valid(camera) then return camera:GetCameraLocation(),camera:GetCameraRotation() end
    return pawn:K2_GetActorLocation(),pc:GetControlRotation()
end
local function endAbility(ability)
    if valid(ability) then pcall(function() ability:K2_EndAbility() end) end
end
local function queueRefund(receipt)
    if receipt and not receipt.refundQueued then receipt.refundQueued=true;refunds[#refunds+1]=receipt end
end
local function refundNativeUse(r)
    if not r.finished then return false end
    if r.refunded or r.before-r.after~=1 then return true end
    local _,pawn,world=D.ready()
    if not pawn or world:GetAddress()~=r.world or pawn:GetAddress()~=r.avatar then return true end
    if valid(r.inventory) and r.inventory:AddItemTypeToInventory(r.item,1) then
        r.refunded=true;D.log('Returned exactly one native-spent rice after an unused/cancelled offering.');return true
    end
    return false
end
function Feeding.configure(deps) D=deps end
function Feeding.beginInventoryUse(vm)
    if not valid(vm) then return end
    local item=vm:GetItemType()
    if not valid(item) or item:GetFullName():sub(-#ITEM)~=ITEM then return end
    local _,pawn,world=D.ready();if not pawn then return end
    local inventory=pawn.InventoryComponent;if not valid(inventory) then return end
    local r={model=vm:GetAddress(),avatar=pawn:GetAddress(),world=world:GetAddress(),item=item,
        inventory=inventory,before=inventory:GetItemCountByType(item),started=pawn:GetGameTimeSinceCreation()}
    openUses[r.model]=r;receipts[#receipts+1]=r
    if #receipts>16 then table.remove(receipts,1) end
end
function Feeding.endInventoryUse(vm)
    if not valid(vm) then return end
    local r=openUses[vm:GetAddress()];if not r then return end
    openUses[r.model]=nil;r.after=r.inventory:GetItemCountByType(r.item);r.finished=true
    D.log('Native backpack rice use: before='..r.before..'; after='..r.after..'; extra mod debit=0.')
    if active and not r.claimed then queueRefund(r) end
end
function Feeding.claimReceipt(pawn)
    if not valid(pawn) then return end
    local now=pawn:GetGameTimeSinceCreation()
    for i=#receipts,1,-1 do
        local r=receipts[i]
        if not r.claimed and not r.refundQueued and not r.refunded and r.avatar==pawn:GetAddress() and now-r.started<3 then r.claimed=true;return r end
    end
end
function Feeding.isActive(f) return active and active.fish==f end
function Feeding.isUnpaid() return false end -- Native inventory use is the sole cost owner.
function Feeding.status()
    return active and (active.stage..'; clip='..string.format('%.2f',active.clipTime or 0)..'; extra_debit=0') or 'idle'
end
local function restoreTick(m)
    if valid(m.fish.actor) then
        local mesh=m.fish.actor.SkeletalMeshComponent
        if valid(mesh) and m.tick then
            mesh.VisibilityBasedAnimTickOption=m.tick.visibility
            mesh.bEnableUpdateRateOptimizations=m.tick.optimized
        end
    end
end
function Feeding.cancel(refund)
    local m=active;active=nil;if not m then return end
    endAbility(m.ability)
    if valid(m.prop) then m.prop:K2_DestroyActor() end
    restoreTick(m);m.fish.feedMouth=nil
    if refund then queueRefund(m.receipt);D.remove(m.fish) end
end
function Feeding.poll()
    for i=#refunds,1,-1 do if refundNativeUse(refunds[i]) then table.remove(refunds,i) end end
end
function Feeding.request(pawn,ability,receipt)
    local function reject(reason)
        if not active or active.ability~=ability then endAbility(ability) end
        queueRefund(receipt);return false,reason
    end
    if active then return reject('A rice offering is already active; no extra mod debit.') end
    local pc,localPawn,world=D.ready()
    if not pc or not valid(pawn) or pawn:GetAddress()~=localPawn:GetAddress() then return reject('Ignoring non-local/unready rice use.') end
    if not receipt and not D.menuOpen(pc) then return reject('Offer rice from the backpack.') end
    if receipt and receipt.before<1 then return reject('Native inventory had no rice before use.') end
    if not D.canSpawn() then return reject('Fish limit reached; the native use will be returned when its debit is confirmed.') end
    local serving=asset('/BigFatFishRice/Blueprints/BP_BFF_RiceServing','BP_BFF_RiceServing_C')
    local full=asset('/BigFatFishRice/Meshes/SM_BFF_CookedRice','SM_BFF_CookedRice')
    local empty=asset('/BigFatFishRice/Meshes/SM_BFF_EmptyRiceBowl','SM_BFF_EmptyRiceBowl')
    local animation=asset('/Game/Mods/BigFatFish/Character/AN_BigFatFish_GrabEat','AN_BigFatFish_GrabEat')
    if not serving or not full or not empty or not animation then return reject('Offering content is missing; cancelling the native use.') end
    local o,r=view(pc,pawn);local start=point(o,r,-320,85,-25)
    local ok,fish=pcall(D.spawn,start,r.Yaw)
    if not ok then return reject(tostring(fish)) end
    fish.actor:SetActorHiddenInGame(true)
    active={fish=fish,ability=ability,receipt=receipt,serving=serving,full=full,empty=empty,animation=animation,
        world=world:GetAddress(),stage='waiting_for_backpack_close',closedFor=0,time=0,clipTime=0}
    D.log('Created new fish ID='..fish.id..'; waiting for backpack close; native use owns the single rice cost.')
    return true
end
local function setMesh(prop,mesh)
    local component=prop.StaticMeshComponent;component:SetStaticMesh(mesh)
    for i=0,component:GetNumMaterials()-1 do
        local material=mesh:GetMaterial(i)
        if valid(material) then component:SetMaterial(i,material) end
    end
end
local function startApproach(m,world,o,r)
    m.start=point(o,r,-320,85,-25);m.control1=point(o,r,-170,340,-20);m.time=0
    m.fish.position=m.start;m.fish.yaw=r.Yaw
    m.fish.actor:K2_SetActorLocation(m.start,false,{},false)
    m.fish.actor:SetActorHiddenInGame(false)
    m.prop=world:SpawnActor(m.serving,point(o,r,75,25,-25),{Pitch=0,Yaw=r.Yaw,Roll=0})
    assert(valid(m.prop),'Could not spawn the rice serving')
    setMesh(m.prop,m.full);m.prop:SetActorScale3D({X=1.7,Y=1.7,Z=1.7})
    local mesh=m.fish.actor.SkeletalMeshComponent
    m.tick={visibility=mesh.VisibilityBasedAnimTickOption,optimized=mesh.bEnableUpdateRateOptimizations}
    mesh.VisibilityBasedAnimTickOption=0;mesh.bEnableUpdateRateOptimizations=false
    m.stage='approaching';D.log('Backpack closed: fish is swimming from behind; bowl is explicitly full.')
end
local function startGesture(m)
    local mesh=m.fish.actor.SkeletalMeshComponent
    local anim=mesh:GetAnimInstance();assert(valid(anim),'Animation instance is not ready')
    assert(mesh:DoesSocketExist(D.name('hand_L')) and mesh:DoesSocketExist(D.name('hand_R')),'Hand bones are not available')
    m.anim=anim
    m.montage=anim:PlaySlotAnimationAsDynamicMontage(m.animation,D.name('DefaultSlot'),.2,.3,.7,1,-1,0)
    assert(valid(m.montage),'Grab/eat montage failed')
    m.stage='reaching';m.clipTime=0;m.gestureTime=0
    D.log('Visible fish reached the bowl; starting the reach/grab/eat montage now.')
end
function Feeding.update(f,dt,o,r,world)
    local m=active;if not m or m.fish~=f then return false end
    local function advance()
        assert(world:GetAddress()==m.world,'Offering world changed')
        local pc=D.ready();assert(pc,'Player is no longer ready')
        if D.menuOpen(pc) then
            m.closedFor=0
            if valid(m.montage) and not m.menuPaused then m.anim:Montage_Pause(m.montage);m.menuPaused=true end
            return
        end
        if m.menuPaused then m.anim:Montage_Resume(m.montage);m.menuPaused=false end
        dt=math.max(0,math.min(dt,.2))
        if m.stage=='waiting_for_backpack_close' then
            m.closedFor=m.closedFor+dt
            if m.closedFor>=.3 and (not m.receipt or m.receipt.finished) then startApproach(m,world,o,r) end
            return
        end
        assert(valid(m.prop),'Rice serving disappeared')
        local held=point(o,r,75,25,-25);local goal=point(o,r,190,65,-15)
        if m.stage=='approaching' then
            m.time=m.time+dt;local t=smooth(m.time/2.8)
            local c2=point(o,r,170,250,-10)
            local a,b,c=mix(m.start,m.control1,t),mix(m.control1,c2,t),mix(c2,goal,t)
            f.position=mix(mix(a,b,t),mix(b,c,t),t)
            f.yaw=r.Yaw+180*smooth((m.time-1.4)/1.4)
            m.prop:K2_SetActorLocation(held,false,{},false)
            if m.time>=2.8 then m.stage='waiting_for_visible_pose';m.visibleFor=0 end
            return
        end
        if m.stage~='reaching' then f.position=mix(f.position,goal,1-math.exp(-3*dt)) end
        f.yaw=f.yaw+((r.Yaw+180-f.yaw+180)%360-180)*(1-math.exp(-4*dt))
        if m.stage=='waiting_for_visible_pose' then
            m.prop:K2_SetActorLocation(held,false,{},false)
            if f.actor:WasRecentlyRendered(.3) then m.visibleFor=m.visibleFor+dt else m.visibleFor=0 end
            if m.visibleFor>=.25 then startGesture(m) end
            return
        end
        m.gestureTime=m.gestureTime+dt
        local clip=m.anim:Montage_GetPosition(m.montage)
        m.clipTime=math.max(m.clipTime,clip)
        assert(m.gestureTime<2 or m.clipTime>.1,'The feeding montage did not advance')
        local mesh=f.actor.SkeletalMeshComponent
        local hands=mix(mesh:GetSocketLocation(D.name('hand_L')),mesh:GetSocketLocation(D.name('hand_R')),.5)
        hands.Z=hands.Z-3*f.size
        if m.clipTime<1.6 then
            -- Move the hands to the offered bowl; do not teleport a full bowl
            -- away from the player while the arms are still reaching.
            local delta={X=held.X-hands.X,Y=held.Y-hands.Y,Z=held.Z-hands.Z}
            f.position={X=f.position.X+delta.X*(1-math.exp(-5*dt)),Y=f.position.Y+delta.Y*(1-math.exp(-5*dt)),Z=f.position.Z+delta.Z*(1-math.exp(-5*dt))}
            m.prop:K2_SetActorLocation(held,false,{},false)
        else
            if not m.grabbed then m.grabbed=true;D.log('Hands grabbed the full rice bowl; extra inventory removals=0.') end
            m.stage='eating'
            local bowl=mix(held,hands,smooth((m.clipTime-1.6)/.3))
            m.prop:K2_SetActorLocation(bowl,false,{},false)
            m.prop:K2_SetActorRotation({Pitch=0,Yaw=f.yaw,Roll=0},false)
            f.feedMouth=(.20+.35*math.sin((m.clipTime-1.6)*math.pi*3.5)^2)*(1-smooth((m.clipTime-3.9)/.4))
            if m.clipTime>=3.9 and not m.emptied then
                setMesh(m.prop,m.empty);m.emptied=true;m.emptyTime=0
                D.log('Rice eaten; showing an empty bowl before putting it away.')
            end
        end
        if m.emptied then m.emptyTime=m.emptyTime+dt end
        local finished=not m.anim:Montage_IsPlaying(m.montage) and m.clipTime>=4.4
        if m.emptied and m.emptyTime>=.8 and (m.clipTime>=4.75 or finished) then
            m.prop:K2_DestroyActor();restoreTick(m);endAbility(m.ability)
            f.feedMouth=nil;f.mode='follow';f.velocity={X=0,Y=0,Z=0};active=nil
            D.log('New fish ID='..f.id..' finished feeding; handed back to the normal companion follow routine.')
        end
    end
    local ok,err=pcall(advance)
    if not ok then D.log('Offering cancelled: '..tostring(err));Feeding.cancel(true) end
    return true
end
return Feeding
