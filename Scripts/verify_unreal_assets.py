"""Verify persisted assets in a fresh editor process before cooking them."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
BASE = "/Game/Mods/BigFatFish"
mesh = unreal.load_asset(BASE + "/Character/SK_BigFatFish")
animation = unreal.load_asset(BASE + "/Character/AN_BigFatFish_Swim")
assert isinstance(mesh, unreal.SkeletalMesh), "Saved mesh did not reload"
assert isinstance(animation, unreal.AnimSequence), "Saved animation did not reload"
assert mesh.get_editor_property("skeleton") == animation.get_editor_property("skeleton"), "Skeleton mismatch"
length = animation.get_editor_property("sequence_length")
assert abs(length - 2.0) < 0.05, f"Unexpected animation duration: {length}"
slots = mesh.get_editor_property("materials")
assert len(slots) == 6, "Incomplete mesh material sections"
assert all(slot.get_editor_property("material_interface") for slot in slots), "Missing material"
for slot in slots:
    material = slot.get_editor_property("material_interface")
    assert material.get_editor_property("used_with_skeletal_mesh"), f"Missing skeletal material usage: {material.get_path_name()}"
    node = unreal.MaterialEditingLibrary.get_material_property_input_node(material, unreal.MaterialProperty.MP_BASE_COLOR)
    assert isinstance(node, unreal.MaterialExpressionTextureSample), f"Missing base-color texture node: {material.get_path_name()}"
    assert isinstance(node.get_editor_property("texture"), unreal.Texture2D), "Unassigned base-color texture"
cls = unreal.EditorAssetLibrary.load_blueprint_class(BASE + "/BP_BigFatFish")
assert cls, "Saved blueprint did not compile/load"
component = unreal.get_default_object(cls).get_editor_property("skeletal_mesh_component")
assert component.get_editor_property("skeletal_mesh_asset") == mesh, "Blueprint lost its mesh"
gaze=unreal.load_asset(BASE+"/Character/ABP_BigFatFish_Gaze")
assert isinstance(gaze,unreal.AnimBlueprint)
assert gaze.get_editor_property("target_skeleton")==mesh.get_editor_property("skeleton")
assert component.get_editor_property("animation_mode")==unreal.AnimationMode.ANIMATION_BLUEPRINT
assert component.get_editor_property("anim_class")==gaze.generated_class()
anim_defaults=unreal.get_default_object(gaze.generated_class())
for name in ["NeckAlpha","HeadAlpha","EyeAlpha"]: assert anim_defaults.get_editor_property(name)==0
anim_defaults.get_editor_property("GazeTargetWorld")
look_nodes=gaze.get_nodes_of_class(unreal.AnimGraphNode_LookAt)
assert len(look_nodes)==4
bones={str(n.get_editor_property("node").get_editor_property("bone_to_modify").get_editor_property("bone_name")): n.get_editor_property("node").get_editor_property("look_at_clamp") for n in look_nodes}
assert bones=={"neck":15,"head":50,"eye_L":8,"eye_R":8},bones
players=gaze.get_nodes_of_class(unreal.AnimGraphNode_SequencePlayer)
assert len(players)==1
player=players[0].get_editor_property("node")
assert player.get_editor_property("sequence")==animation
assert player.get_editor_property("loop_animation")
assert component.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION
settings=json.loads((ROOT/'project.json').read_text(encoding='utf8'))
if settings.get('feeding_enabled'):
    feeding=unreal.load_asset(BASE+'/Character/AN_BigFatFish_GrabEat')
    assert isinstance(feeding,unreal.AnimSequence)
    assert abs(feeding.get_editor_property('sequence_length')-4.8)<.05
    assert feeding.get_editor_property('skeleton')==mesh.get_editor_property('skeleton')
    options=unreal.AnimPoseEvaluationOptions()
    swim_first=unreal.AnimPoseExtensions.get_anim_pose_at_time(animation,0.,options)
    feed_first=unreal.AnimPoseExtensions.get_anim_pose_at_time(feeding,0.,options)
    for bone in ('head','neck','hand_L','hand_R'):
        a=unreal.AnimPoseExtensions.get_bone_pose(swim_first,bone,unreal.AnimPoseSpaces.WORLD)
        b=unreal.AnimPoseExtensions.get_bone_pose(feed_first,bone,unreal.AnimPoseSpaces.WORLD)
        assert (a.translation-b.translation).length()<.3,(bone,a,b)
    swim_reach=unreal.AnimPoseExtensions.get_anim_pose_at_time(animation,1.6,options)
    feed_reach=unreal.AnimPoseExtensions.get_anim_pose_at_time(feeding,1.6,options)
    for bone in ('hand_L','hand_R'):
        a=unreal.AnimPoseExtensions.get_bone_pose(swim_reach,bone,unreal.AnimPoseSpaces.WORLD)
        b=unreal.AnimPoseExtensions.get_bone_pose(feed_reach,bone,unreal.AnimPoseSpaces.WORLD)
        assert (a.translation-b.translation).length()>10,(bone,'Reach gesture is missing')
    feeding_slots=gaze.get_nodes_of_class(unreal.AnimGraphNode_Slot)
    assert len(feeding_slots)==1 and str(feeding_slots[0].get_editor_property('node').get_editor_property('slot_name'))=='DefaultSlot'
bounds = mesh.get_bounds()
report = {
    "status": "persisted_assets_verified_not_game_tested",
    "engine": unreal.SystemLibrary.get_engine_version(),
    "animation_seconds": length,
    "material_slots": [str(s.get_editor_property("material_slot_name")) for s in slots],
    "bounds_extent_cm": [bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z],
    "blueprint_defaults": "mesh, native AnimBP, swim loop, four clamped gaze bones, public variables, no collision verified after reload",
    "skeletal_material_usage_and_texture_inputs": "all six verified",
}
(ROOT / "Logs/unreal_asset_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
unreal.log("BIGFATFISH_ASSETS_VERIFIED " + json.dumps(report))
