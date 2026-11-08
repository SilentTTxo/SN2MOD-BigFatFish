"""Read-only inspection of the matched editor's animation authoring APIs."""
import json
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[1]
report = {}
for name in ["BlueprintEditorLibrary", "AnimBlueprintFactory", "AnimGraphNode_LookAt", "AnimGraphNode_Root", "AnimPoseExtensions", "AnimationBlueprintLibrary", "EdGraph", "AnimBlueprint", "BoneReference", "AnimNode_LookAt"]:
    cls = getattr(unreal, name, None)
    report[name] = {"exists": cls is not None, "members": [m for m in dir(cls) if not m.startswith("_")]} if cls else {}
for module in ["UnrealEd", "CoreUObject", "BlueprintGraph", "AnimGraph"]:
    report[module + "_dll"] = str(ROOT / "Engine/SN2-Engine-V4/Engine/Binaries/Win64" / f"UnrealEditor-{module}.dll")
mesh = unreal.load_asset("/Game/Mods/BigFatFish/Character/SK_BigFatFish")
report["mesh_repr"] = repr(mesh)
report["skeleton_repr"] = repr(mesh.get_editor_property("skeleton"))
factory = unreal.AnimBlueprintFactory()
factory.set_editor_property("target_skeleton", mesh.get_editor_property("skeleton"))
bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_BigFatFish_Gaze", "/Game/Mods/BigFatFish/Character", unreal.AnimBlueprint, factory)
if not bp:
    bp = unreal.load_asset("/Game/Mods/BigFatFish/Character/ABP_BigFatFish_Gaze")
report["blueprint"] = repr(bp)
for name in ["function_graphs", "ubergraph_pages"]:
    try:
        graphs = bp.get_editor_property(name)
        report[name] = [{"repr":repr(g), "name":g.get_name(), "nodes":[repr(n) for n in g.get_editor_property("nodes")]} for g in graphs]
    except Exception as e:
        report[name] = str(e)
(ROOT / "Logs/gaze_editor_probe.json").write_text(json.dumps(report, indent=2), encoding="utf8")
unreal.log("GAZE_API_PROBE_COMPLETE")
