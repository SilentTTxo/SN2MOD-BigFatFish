-- Deterministic native dynamic-item GUIDs prevent duplicate wild populations.
local M={}
local D,session,stable,done,attempts,lastScan
local function valid(o) return o~=nil and o:IsValid() end
local function text(value) return type(value)=='string' and value or value:ToString() end
function M.configure(deps) D=deps end
local function hash(s,seed)
 local n=seed
 for i=1,#s do n=(n*131+s:byte(i))%2147483647 end
 return n
end
function M.guid(id,index)
 local key='BigFatFishSeaRiceV1:'..id..':'..index
 return {A=hash(key,237),B=hash(key,581),C=hash(key,936),D=hash(key,401)}
end
function M.poll()
 local pc=D.player();if not valid(pc) or not valid(pc.Pawn) then session=nil;return end
 local pawn=pc.Pawn;local world=pawn:GetWorld();if not valid(world) or not pawn:HasAuthority() then return end
 local saves=FindFirstOf('UWESaveGameSubsystem');if not valid(saves) then return end
 local active=saves.SaveContext.ActiveSave;if not valid(active) then return end
 local guidlib=StaticFindObject('/Script/Engine.Default__KismetGuidLibrary');if not valid(guidlib) then return end
 local collection=saves.SaveContext.SaveGameCollection
 local id=text(guidlib:Conv_GuidToString(valid(collection) and collection.ContainerInfo.SaveId or active.MetaData.SaveId))
 if id:gsub('[0%-]','')=='' then return end
 local key=tostring(world:GetAddress())..id
 if session~=key then session=key;stable=0;done={};attempts={};lastScan=nil end
 stable=stable+1;if stable<20 then return end -- wait for native save proxies and terrain
 local complete=0;for i=1,8 do if done[i] then complete=complete+1 end end
 if complete==8 then return end
 local now=pawn:GetGameTimeSinceCreation()
 if lastScan and now-lastScan<5 then return end
 lastScan=now
 local manager
 for _,m in ipairs(FindAllOf('UWEDynamicItemsManager') or {}) do
  if valid(m) and m:GetWorld():GetAddress()==world:GetAddress() then manager=m;break end
 end
 if not manager then return end
 local pod
 for _,class in ipairs({'BP_StaticLifepod_Underwater_C','BP_StaticLifepod_C','BP_Lifepod_C','BP_LifepodPlayerStart_C'}) do
  for _,a in ipairs(FindAllOf(class) or {}) do
   if valid(a) and a:GetWorld():GetAddress()==world:GetAddress() then pod=a;break end
  end
  if pod then break end
 end
 if not pod then return end
 local center=pod:K2_GetActorLocation();local player=pawn:K2_GetActorLocation()
 if (player.X-center.X)^2+(player.Y-center.Y)^2>10000^2 then return end
 local ids={}
 local function collect(k) ids[text(guidlib:Conv_GuidToString(k:get()))]=true end
 manager.DynamicItemsSave.DynamicItems:ForEach(collect)
 manager.ActiveActorsByID:ForEach(collect)
 local helper=StaticFindObject('/Script/AssetRegistry.Default__AssetRegistryHelpers')
 local path='/BigFatFishRice/Blueprints/BP_BFF_WildRice'
 local cls=StaticFindObject(path..'.BP_BFF_WildRice_C')
 if not valid(cls) and valid(helper) then cls=helper:GetAsset({PackageName=D.name(path),AssetName=D.name('BP_BFF_WildRice_C')}) end
 if not valid(cls) then return end
 local system=StaticFindObject('/Script/Engine.Default__KismetSystemLibrary');if not valid(system) then return end
 local created=0
 for index=1,8 do
  local guid=M.guid(id,index);local guidText=text(guidlib:Conv_GuidToString(guid))
  if ids[guidText] then done[index]=true end
  if not done[index] then
   local patch=math.floor((index-1)/2);local seed=hash(id,patch+1)
   local angle=patch*math.pi/2+(seed%1000)/1000*.8
   local trial=attempts[index] or 0
   local radius=2500+(seed+trial*237)%2500;local offset=index%2*100
   angle=angle+trial*.12;attempts[index]=trial+1
   local x,y=center.X+math.cos(angle)*radius+offset,center.Y+math.sin(angle)*radius
   local hit={}
   local ok=system:LineTraceSingleForObjects(pawn,{X=x,Y=y,Z=center.Z+1500},{X=x,Y=y,Z=center.Z-12000},{0},false,{pod,pawn},0,hit,true,{R=0,G=0,B=0,A=0},{R=0,G=0,B=0,A=0},0)
   if ok and hit.ImpactNormal.Z>.7 and hit.ImpactPoint.Z<center.Z-100 then
    local p=hit.ImpactPoint
    local actor=manager:SpawnActorAndRegisterWithoutDropping(cls,{Translation={X=p.X,Y=p.Y,Z=p.Z+2},Rotation={X=0,Y=0,Z=0,W=1},Scale3D={X=1,Y=1,Z=1}},guid)
    if valid(actor) then manager:SetRemoveIfOutOfRange(actor,false);done[index]=true;created=created+1 end
   end
  end
 end
 if created>0 then D.log('Registered '..created..' wild Sea Rice plants in native dynamic-item saves near the lifepod.') end
end
return M
