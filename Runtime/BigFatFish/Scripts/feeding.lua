-- A real world serving is the sole cost owner. Inventory use stays native food.
local Feeding={}
local D,active
local dropped={}
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
local function eligible(item,world)
 return valid(item) and valid(item:GetWorld()) and item:GetWorld():GetAddress()==world:GetAddress()
  -- CL-131439 IsOwned dereferences Actor.Owner without a null guard. A real
  -- dropped item has Owner=nil, so never call that native query here.
  and not valid(item.Owner) and not item:IsEquipped() and not item.bHidden
  and not valid(item:GetAttachParentActor())
end
function Feeding.configure(deps) D=deps end
function Feeding.isActive(f) return active and active.fish==f end
function Feeding.isUnpaid(f) return active and active.fish==f and not active.grabbed end
function Feeding.status() return active and (active.stage..'; clip='..string.format('%.2f',active.clipTime)) or 'idle' end
local function restoreTick(m)
 if valid(m.fish.actor) then
  local mesh=m.fish.actor.SkeletalMeshComponent
  if valid(mesh) and m.tick then mesh.VisibilityBasedAnimTickOption=m.tick.visibility;mesh.bEnableUpdateRateOptimizations=m.tick.optimized end
 end
end
function Feeding.cancel(remove)
 local m=active;active=nil;dropped={};if not m then return end
 if valid(m.fish.actor) then
  local anim=m.fish.actor.SkeletalMeshComponent:GetAnimInstance()
  if valid(anim) and valid(m.fish.actor.FeedMontage) then anim:Montage_Stop(.2,m.fish.actor.FeedMontage) end
  m.fish.actor:SetActorHiddenInGame(false)
 end
 if valid(m.prop) then m.prop:K2_DestroyActor() end
 restoreTick(m);m.fish.feedMouth=nil
 if remove and not m.grabbed then D.remove(m.fish) end
end
function Feeding.poll() end
function Feeding.discover()
 local pc,pawn,world=D.ready();if not pc then dropped={};return end
 if not pawn:HasAuthority() then return end
 local now=pawn:GetGameTimeSinceCreation();local seen={}
 for _,item in ipairs(FindAllOf('BP_BFF_CookedRice_C') or {}) do
  if eligible(item,world) then
   local key=item:GetAddress();seen[key]=true
   local p=item:K2_GetActorLocation();local q=pawn:K2_GetActorLocation()
   if (p.X-q.X)^2+(p.Y-q.Y)^2+(p.Z-q.Z)^2<2500^2 then
    local r=dropped[key]
    if not r then r={actor=item,since=now};dropped[key]=r end
    if not active and not r.claimed and now-r.since>3 and D.canSpawn() then
     local ok,err=Feeding.request(item,pc,pawn,world)
     if ok then r.claimed=true else r.since=now;D.log('Dropped rice: '..tostring(err)) end
    end
   else dropped[key]=nil end
  end
 end
 for key in pairs(dropped) do if not seen[key] then dropped[key]=nil end end
end
function Feeding.request(source,pc,pawn,world)
 if active or not eligible(source,world) then return false,'Serving no longer dropped' end
 local serving=asset('/BigFatFishRice/Blueprints/BP_BFF_RiceServing','BP_BFF_RiceServing_C')
 if not serving then return false,'Rice serving content unavailable' end
 local camera=pc.PlayerCameraManager
 local o,r=pawn:K2_GetActorLocation(),pc:GetControlRotation()
 if valid(camera) then o,r=camera:GetCameraLocation(),camera:GetCameraRotation() end
 local start=point(o,r,-320,85,-25)
 local fish=D.spawn(start,r.Yaw)
 local actor=fish.actor
 -- Native UPROPERTYs own loaded resources through GC, including the empty mesh.
 actor.FeedServingClass=serving
 actor.FeedFullMesh=asset('/BigFatFishRice/Meshes/SM_BFF_CookedRice','SM_BFF_CookedRice')
 actor.FeedEmptyMesh=asset('/BigFatFishRice/Meshes/SM_BFF_EmptyRiceBowl','SM_BFF_EmptyRiceBowl')
 if not valid(actor.FeedFullMesh) or not valid(actor.FeedEmptyMesh) or not valid(actor.FeedAnimation) then D.remove(fish);return false,'Offering resources unavailable' end
 local mesh=actor.SkeletalMeshComponent
 active={fish=fish,source=source,world=world:GetAddress(),stage='approaching',time=0,clipTime=0,
  start=start,control1=point(o,r,-170,340,-20),tick={visibility=mesh.VisibilityBasedAnimTickOption,optimized=mesh.bEnableUpdateRateOptimizations}}
 mesh.VisibilityBasedAnimTickOption=0;mesh.bEnableUpdateRateOptimizations=false
 D.log('Dropped rice waited >3s; created new fish ID='..fish.id..'; no inventory debit.')
 return true
end
local function startGesture(m)
 local actor=m.fish.actor;local mesh=actor.SkeletalMeshComponent;local anim=mesh:GetAnimInstance()
 assert(valid(anim) and valid(actor.FeedAnimation),'Feeding animation not ready')
 assert(mesh:DoesSocketExist(D.name('hand_L')) and mesh:DoesSocketExist(D.name('hand_R')),'Missing hand bones')
 actor.FeedMontage=anim:PlaySlotAnimationAsDynamicMontage(actor.FeedAnimation,D.name('DefaultSlot'),.2,.3,.7,1,-1,0)
 assert(valid(actor.FeedMontage),'Grab/eat montage failed')
 m.stage='reaching';m.gestureTime=0
end
function Feeding.update(f,dt,o,r,world)
 local m=active;if not m or m.fish~=f then return false end
 local function advance()
  assert(world:GetAddress()==m.world and valid(f.actor),'Offering world changed')
  local pc=D.ready();assert(pc,'Player not ready')
  local mesh=f.actor.SkeletalMeshComponent;local anim=mesh:GetAnimInstance();local montage=f.actor.FeedMontage
  if D.menuOpen(pc) then
   if valid(montage) and valid(anim) and not m.menuPaused then anim:Montage_Pause(montage);m.menuPaused=true end
   return
  end
  if m.menuPaused and valid(montage) and valid(anim) then anim:Montage_Resume(montage);m.menuPaused=false end
  if not m.grabbed then assert(eligible(m.source,world),'Rice picked up before the grab') end
  dt=math.max(0,math.min(dt,.2));m.time=m.time+dt
  assert(m.time<35,'Offering timed out')
  local held=m.grabbed and m.grabPosition or m.source:K2_GetActorLocation()
  local goal=point(held,r,130,40,25)
  if m.stage=='approaching' then
   local t=smooth(m.time/2.8);local c2=point(held,r,170,250,25)
   local a,b,c=mix(m.start,m.control1,t),mix(m.control1,c2,t),mix(c2,goal,t)
   f.position=mix(mix(a,b,t),mix(b,c,t),t)
   f.yaw=r.Yaw+180*smooth((m.time-1.4)/1.4)
   if m.time>=2.8 then m.stage='waiting_for_visible_pose';m.visibleFor=0 end
   return
  end
  f.yaw=f.yaw+((r.Yaw+180-f.yaw+180)%360-180)*(1-math.exp(-4*dt))
  if m.stage=='waiting_for_visible_pose' then
   if f.actor:WasRecentlyRendered(.3) then m.visibleFor=m.visibleFor+dt else m.visibleFor=0 end
   if m.visibleFor>=.25 then startGesture(m) end
   return
  end
  assert(valid(anim) and valid(montage),'Feeding montage lost')
  m.gestureTime=m.gestureTime+dt;m.clipTime=math.max(m.clipTime,anim:Montage_GetPosition(montage))
  assert(m.gestureTime<2 or m.clipTime>.1,'Feeding montage did not advance')
  local hands=mix(mesh:GetSocketLocation(D.name('hand_L')),mesh:GetSocketLocation(D.name('hand_R')),.5)
  hands.Z=hands.Z-3*f.size
  if m.clipTime<1.6 then
   local delta={X=held.X-hands.X,Y=held.Y-hands.Y,Z=held.Z-hands.Z}
   for _,axis in ipairs({'X','Y','Z'}) do f.position[axis]=f.position[axis]+delta[axis]*(1-math.exp(-5*dt)) end
  else
   if not m.grabbed then
    assert(eligible(m.source,world),'Rice was picked up')
    m.prop=world:SpawnActor(f.actor.FeedServingClass,held,{Pitch=0,Yaw=f.yaw,Roll=0});assert(valid(m.prop),'Serving spawn failed')
    m.prop:SetActorScale3D({X=1.7,Y=1.7,Z=1.7})
    m.grabPosition={X=held.X,Y=held.Y,Z=held.Z}
    m.source:K2_DestroyActor();m.grabbed=true;D.log('Grabbed one dropped serving; inventory removals=0.')
   end
   assert(valid(m.prop),'Held serving disappeared');m.stage='eating'
   m.prop:K2_SetActorLocation(mix(held,hands,smooth((m.clipTime-1.6)/.3)),false,{},false)
   m.prop:K2_SetActorRotation({Pitch=0,Yaw=f.yaw,Roll=0},false)
   f.feedMouth=(.20+.35*math.sin((m.clipTime-1.6)*math.pi*3.5)^2)*(1-smooth((m.clipTime-3.9)/.4))
   if m.clipTime>=3.9 and not m.emptied then
    -- Both this native prop and the fish retain the empty mesh through GC.
    local empty=m.prop.EmptyMesh;assert(valid(empty),'Empty mesh unavailable')
    local component=m.prop.StaticMeshComponent;assert(valid(component),'Serving component unavailable')
    component:SetStaticMesh(empty)
    for i=0,component:GetNumMaterials()-1 do local mat=empty:GetMaterial(i);if valid(mat) then component:SetMaterial(i,mat) end end
    m.emptied=true;m.emptyTime=0
   end
  end
  if m.emptied then m.emptyTime=m.emptyTime+dt end
  local finished=not anim:Montage_IsPlaying(montage) and m.clipTime>=4.4
  if m.emptied and m.emptyTime>=.8 and (m.clipTime>=4.75 or finished) then
   m.prop:K2_DestroyActor();restoreTick(m);f.feedMouth=nil;f.mode='follow';f.velocity={X=0,Y=0,Z=0};active=nil
   D.log('New fish ID='..f.id..' finished eating; normal companion follow resumed.')
  end
 end
 local ok,err=pcall(advance)
 if not ok then D.log('Offering cancelled: '..tostring(err));Feeding.cancel(true) end
 return true
end
return Feeding
