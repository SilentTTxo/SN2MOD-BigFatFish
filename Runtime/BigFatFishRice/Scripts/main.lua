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
        log("v0.1.0-prototype; native rice item mounted=" .. tostring(valid(item)))
        if valid(item) then log("Inventory rice grain=" .. playerInventory():GetItemCountByType(item)) end
    end)
    return true
end)
log("v0.1.0-prototype loaded. Commands: bigfatfish_rice_give [count], bigfatfish_rice_status")
