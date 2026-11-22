local M={}
local D,lastEvent,lastTime
local function valid(o) return o~=nil and o:IsValid() end
function M.configure(deps) D=deps end
function M.identify(value)
 local s=tostring(value):lower():gsub('[^%w]','')
 if s:find('thumbdown',1,true) or s:find('thumbsdown',1,true) then return 'angry' end
 if s:find('thumbup',1,true) or s:find('thumbsup',1,true) then return 'happy' end
 if s:find('frustrated',1,true) or s:find('expressive',1,true) then return 'sad' end
 if s:find('clap',1,true) then return 'basin' end
 if s:find('wave',1,true) then return 'movement' end
end
function M.react(kind)
 local _,pawn=D.ready();if not pawn then return end
 local time=pawn:GetGameTimeSinceCreation()
 if lastEvent==kind and lastTime and time-lastTime<1 then return end
 lastEvent,lastTime=kind,time
 local p=pawn:K2_GetActorLocation();local count=0
 for _,f in ipairs(D.fish()) do
  local q=f.position
  if valid(f.actor) and (p.X-q.X)^2+(p.Y-q.Y)^2+(p.Z-q.Z)^2<=3000^2 then
   if kind=='basin' then f.basinMode=not f.basinMode
   elseif kind=='movement' then
    f.mode=f.mode=='follow' and 'wander' or 'follow';f.velocity={X=0,Y=0,Z=0}
    if f.mode=='wander' then
     f.phase=0;f.startAngle=math.rad(f.yaw-D.config.MeshYawOffsetDegrees)-math.pi/2
     f.center={X=q.X-D.config.PatrolRadiusCm*math.cos(f.startAngle),Y=q.Y-D.config.PatrolRadiusCm*math.sin(f.startAngle),Z=q.Z}
    end
   else f.emotion={kind=kind,time=0} end
   count=count+1
  end
 end
 D.log('Emote '..kind..': '..count..' nearby fish reacted.')
end
function M.cleanup(f)
 if valid(f.basinProp) then f.basinProp:K2_DestroyActor() end
 f.basinProp=nil
end
function M.update(f,dt,world,feeding)
 local actor=f.actor;local mesh=actor.SkeletalMeshComponent;local anim=mesh:GetAnimInstance()
 if not valid(anim) then return end
 if not f.basinMode or feeding then
  if valid(actor.BasinMontage) then anim:Montage_Stop(.25,actor.BasinMontage);actor.BasinMontage=nil end
  M.cleanup(f);return
 end
 if not valid(actor.BasinAnimation) or not valid(actor.BasinPropClass) then return end
 if not valid(actor.BasinMontage) or not anim:Montage_IsPlaying(actor.BasinMontage) then
  actor.BasinMontage=anim:PlaySlotAnimationAsDynamicMontage(actor.BasinAnimation,D.name('DefaultSlot'),.3,.3,1,100000,-1,0)
 end
 if not valid(f.basinProp) then
  f.basinProp=world:SpawnActor(actor.BasinPropClass,f.position,{Pitch=0,Yaw=f.yaw,Roll=0})
  if not valid(f.basinProp) then return end
  local scale=D.config.Scale*f.size*.48
  f.basinProp:SetActorScale3D({X=scale,Y=scale,Z=scale})
 end
 local a,b=mesh:GetSocketLocation(D.name('hand_L')),mesh:GetSocketLocation(D.name('hand_R'))
 f.basinProp:K2_SetActorLocation({X=(a.X+b.X)/2,Y=(a.Y+b.Y)/2,Z=(a.Z+b.Z)/2-4*f.size},false,{},false)
 f.basinProp:K2_SetActorRotation({Pitch=0,Yaw=f.yaw,Roll=0},false)
end
local installed={}
function M.installHooks()
 local function install(path,callback)
  if installed[path] or not valid(StaticFindObject(path)) then return end
  local ok=pcall(RegisterHook,path,function(...)
   local success,err=pcall(callback,...)
   if not success then D.log('Gesture hook: '..tostring(err)) end
  end)
  if ok then installed[path]=true;D.log('Gesture hook ready: '..path) end
 end
 for _,method in ipairs({'PlayEmote','ServerPlayEmote'}) do
  install('/Script/UWEEmotes.UWEEmoteComponent:'..method,function(context,data)
   local component=context:get();local _,pawn=D.ready();if not pawn or not valid(component) then return end
   local owner=component:GetOwner();local pc=select(1,D.ready())
   if not valid(owner) or (owner:GetAddress()~=pawn:GetAddress() and owner:GetAddress()~=pc:GetAddress()) then return end
   local emote=data:get();if not valid(emote) then return end
   local kind=M.identify(emote:GetFullName())
   if kind then D.defer(function() M.react(kind) end) end
  end)
 end
 install('/Script/Subnautica2.SN2PlayerCharacter:Multicast_PlayOneShotAnim',function(context,tag)
  local actor=context:get();local _,pawn=D.ready();if not pawn or not valid(actor) or actor:GetAddress()~=pawn:GetAddress() then return end
  local kind=M.identify(tag:get().TagName:ToString())
  if kind then D.defer(function() M.react(kind) end) end
 end)
end
return M
