function FindAllOf() return {} end
function LoopInGameThreadWithDelay() end
function LoopInGameThreadAfterFrames() end
-- Exercise grant boundaries and native-content failure handling without touching saves.
local root=assert(arg[1])
local commands,logs={},{}
local granted,total,loaded,ready,reject=0,0,true,true,false
local valid=function() return true end
local item={IsValid=valid}
local character={IsValid=valid}
local inventory={IsValid=valid}
function inventory:GetItemCountByType(value) assert(value==item);return total end
function inventory:AddItemTypeToInventory(value,count)
    assert(value==item)
    if reject then return false end
    granted=granted+1;total=total+count;return true
end
local pawn={GetWorld=function() return {IsValid=valid,GetAddress=function() return 1 end} end,IsValid=function() return ready end,IsA=function(_,value) return value==character end,InventoryComponent=inventory}
local controller={IsValid=valid,Pawn=pawn}
package.preload.UEHelpers=function()
    return {GetPlayerController=function() return controller end,FindOrAddFName=function(s) return s end}
end
function StaticFindObject(path)
    if path=="/Script/Subnautica2.SN2PlayerCharacter" then return character end
    if path:find("DA_BFF_RiceGrain_ItemType",1,true) and loaded then return item end
    return nil
end
function ExecuteInGameThread(callback) callback() end
function RegisterConsoleCommandHandler(name,callback) commands[name]=callback end
local output=print
print=function(s)logs[#logs+1]=s end
dofile(root.."/Runtime/BigFatFishRice/Scripts/main.lua")
assert(commands.bigfatfish_rice_give and commands.bigfatfish_rice_status)
commands.bigfatfish_rice_give("",{})
assert(total==3 and granted==1)
commands.bigfatfish_rice_give("",{"5"})
assert(total==8 and granted==2)
for _,args in ipairs({{"0"},{"21"},{"1.5"},{"bad"},{"1","2"}}) do commands.bigfatfish_rice_give("",args) end
assert(total==8 and granted==2,"Invalid counts must never grant")
ready=false;commands.bigfatfish_rice_give("",{"2"});ready=true
loaded=false;commands.bigfatfish_rice_give("",{"2"});commands.bigfatfish_rice_status();loaded=true
reject=true;commands.bigfatfish_rice_give("",{"2"});reject=false
assert(total==8 and granted==2,"Unavailable inventory/content and rejected grant must not change count")
commands.bigfatfish_rice_status()
local found=false;for _,line in ipairs(logs) do if line:find("Inventory rice grain=8",1,true) then found=true end end;assert(found)
output("PASS: rice grants once via native inventory; count limits; menu/content/capacity guards; status; no sidecar writes")
