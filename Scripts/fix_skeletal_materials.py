"""Repair explicit skeletal usage without reimporting existing geometry/animation."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
paths = unreal.EditorAssetLibrary.list_assets("/Game/Mods/BigFatFish/Materials", recursive=True)
fixed = []
for path in paths:
    material = unreal.load_asset(path)
    if not isinstance(material, unreal.Material):
        continue
    before = material.get_editor_property("used_with_skeletal_mesh")
    material.set_editor_property("used_with_skeletal_mesh", True)
    unreal.MaterialEditingLibrary.recompile_material(material)
    assert material.get_editor_property("used_with_skeletal_mesh"), path
    assert unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False)
    fixed.append({"material": material.get_path_name(), "before": before, "after": True})
assert len(fixed) == 6, fixed
(ROOT / "Logs/material_usage_fix.json").write_text(json.dumps(fixed, indent=2), encoding="utf-8")
unreal.log("BIGFATFISH_MATERIAL_FLAGS_FIXED " + json.dumps(fixed))
