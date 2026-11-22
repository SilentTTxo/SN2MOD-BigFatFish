-- Native rice planting prototype. No sidecar saves: inventory/plants use game saves.
local UEHelpers = require("UEHelpers")
local ITEM_PACKAGE = "/BigFatFishRice/Data/DA_BFF_RiceGrain_ItemType"
local ITEM_NAME = "DA_BFF_RiceGrain_ItemType"
local function log(message) print("[BigFatFishRice] " .. tostring(message) .. "\n") end
local function valid(object) return object ~= nil and object:IsValid() end
local function itemType()
    local item = StaticFindObject(ITEM_PACKAGE .. "." .. ITEM_NAME)
    if valid(item) then return item end
    local helper = StaticFindObject("/Script/AssetRegistry.Default__AssetRegistryHelpers")
    if valid(helper) then
        item = helper:GetAsset({PackageName = UEHelpers.FindOrAddFName(ITEM_PACKAGE),
            AssetName = UEHelpers.FindOrAddFName(ITEM_NAME)})
    end
    return valid(item) and item or nil
end
local function playerInventory()
    local pc = UEHelpers.GetPlayerController()
    local character = StaticFindObject("/Script/Subnautica2.SN2PlayerCharacter")
    if not valid(pc) or not valid(pc.Pawn) or not valid(character) or not pc.Pawn:IsA(character) then
        error("Load a game save before giving rice grain")
    end
    local inventory = pc.Pawn.InventoryComponent
    assert(valid(inventory), "Player inventory is not ready")
    return inventory
end
local function run(callback)
    ExecuteInGameThread(function()
        local ok, err = pcall(callback)
        if not ok then log("Error: " .. tostring(err)) end
    end)
end
-- Native ripening scales the seed actor. Keep its crown pivot at the actual
-- planted actor's crown, including older plants loaded from a save.
local growers={}
local function repairLegacyOverrides(component)
    if not valid(component) or not valid(component.StaticMesh) then return end
    for slot=0,component:GetNumMaterials()-1 do
        local expected=component.StaticMesh:GetMaterial(slot)
        local current=component:GetMaterial(slot)
        if valid(expected) and expected:GetFullName():find('/BigFatFishRice/Materials/',1,true)
            and (not valid(current) or current:GetFullName():find('/Engine/EngineMaterials/WorldGridMaterial',1,true)) then
            component:SetMaterial(slot,expected)
        end
    end
end
local function discoverGrowers()
    local pc=UEHelpers.GetPlayerController()
    if not valid(pc) or not valid(pc.Pawn) then growers={};return end
    local world=pc.Pawn:GetWorld();if not valid(world) then growers={};return end
    growers={}
    for _,plant in ipairs(FindAllOf('BP_BFF_RicePlant_C') or {}) do
        if valid(plant) and plant:GetWorld():GetAddress()==world:GetAddress() then
            growers[#growers+1]=plant
            repairLegacyOverrides(plant.RiceStalk)
            local grower=plant.RiceSeedGrower
            if valid(grower) and grower:HasSeed() then
                local seed=grower:GetSeedActor()
                if valid(seed) then repairLegacyOverrides(seed.Mesh) end
            end
        end
    end
end
local function anchorGrowingPanicles()
    for _,plant in ipairs(growers) do
        if valid(plant) then
            local grower=plant.RiceSeedGrower
            if valid(grower) and grower:HasSeed() then
                local seed=grower:GetSeedActor()
                if valid(seed) then
                    local base=plant:K2_GetActorLocation();local up=plant:GetActorUpVector()
                    local height=72*plant:GetActorScale3D().Z
                    seed:K2_SetActorLocation({X=base.X+up.X*height,Y=base.Y+up.Y*height,Z=base.Z+up.Z*height},false,{},false)
                end
            end
        end
    end
end
local lastGrowthError
local function growthGuard(callback)
    return function()
        local ok,err=pcall(callback)
        if not ok and tostring(err)~=lastGrowthError then lastGrowthError=tostring(err);log('Growth: '..lastGrowthError) end
    end
end
LoopInGameThreadWithDelay(500,growthGuard(discoverGrowers))
LoopInGameThreadAfterFrames(1,growthGuard(anchorGrowingPanicles))
RegisterConsoleCommandHandler("bigfatfish_rice_give", function(_, parts)
    local args = parts or {}
    run(function()
        assert(#args <= 1, "Usage: bigfatfish_rice_give [count]")
        local count = 3
        if args[1] then count = tonumber(args[1]) end
        assert(count and count % 1 == 0 and count >= 1 and count <= 20, "Count must be an integer from 1 to 20")
        local inventory = playerInventory()
        local item = assert(itemType(), "Native rice content is not mounted; check BigFatFishRice content installation")
        local before = inventory:GetItemCountByType(item)
        assert(inventory:AddItemTypeToInventory(item, count), "Game rejected the rice grant (check inventory space)")
        local after = inventory:GetItemCountByType(item)
        log("Rice grain requested=" .. count .. "; inventory before=" .. before .. "; after=" .. after ..
            ". Use the BUILDER farming/plants menu to plant Rice on a planter; prototype ripening time is 60 seconds.")
    end)
    return true
end)
RegisterConsoleCommandHandler("bigfatfish_rice_status", function()
    run(function()
        local item = itemType()
        log("v0.3.0-prototype; native rice item mounted=" .. tostring(valid(item)))
        if valid(item) then log("Inventory rice grain=" .. playerInventory():GetItemCountByType(item)) end
        discoverGrowers();log('Sea Rice plants in this world='..#growers)
        for index,plant in ipairs(growers) do
            if index>3 then break end
            local mesh=plant.RiceStalk
            if valid(mesh) then
                for slot=0,mesh:GetNumMaterials()-1 do
                    local material=mesh:GetMaterial(slot)
                    log('Plant '..index..' material '..slot..'='..(valid(material) and material:GetFullName() or 'NONE'))
                end
            end
            local grower=plant.RiceSeedGrower
            if valid(grower) then
                local seed=grower:GetSeedActor()
                if valid(seed) then
                    local a,b=plant:K2_GetActorLocation(),seed:K2_GetActorLocation()
                    log('Panicle relative height='..string.format('%.2f cm',b.Z-a.Z))
                end
            end
        end
    end)
    return true
end)
log("v0.3.0-prototype loaded. Commands: bigfatfish_rice_give [count], bigfatfish_rice_status")
