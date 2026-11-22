"""Read-only farming asset discovery in the matched full SN2 modkit editor."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "Logs/rice"
out.mkdir(parents=True, exist_ok=True)
report = {"engine": unreal.SystemLibrary.get_engine_version(), "classes": {}, "assets": []}
for path in (
    "/Script/UWEInventory.UWEItemType", "/Script/UWEFarming.UWESeedData",
    "/Script/UWEFarming.UWEFarmTrayBase", "/Script/UWEFarming.UWEPlantGrowerComponent",
    "/Script/UWEFarming.UWESeedGrowerComponent", "/Script/UWEGameplay.UWEGameplayActor",
    "/Script/UWECrafting.UWECraftingRecipe", "/Script/UWEAssetRegistry.UWEAssetDataComponent",
):
    cls = unreal.find_object(None, path)
    report["classes"][path] = str(cls) if cls else None
print("RICE_CLASSES", json.dumps(report["classes"]), flush=True)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.wait_for_completion()
all_assets = registry.get_all_assets()
for data in all_assets:
    path = str(data.package_name)
    if any(term in path.lower() for term in ("farmtray", "growbed", "seeddata", "seed", "regrow", "plantgrow", "firstaidkititemtype")):
        report["assets"].append({"path": path, "class": str(data.asset_class_path)})
report["total_asset_count"] = len(all_assets)
(out / "editor_discovery.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("RICE_DISCOVERY", len(all_assets), "assets; candidates", len(report["assets"]), flush=True)
if "-run=pythonscript" not in unreal.SystemLibrary.get_command_line().lower():
    unreal.SystemLibrary.quit_editor()
