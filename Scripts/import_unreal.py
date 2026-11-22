"""Run inside the matched custom Unreal Editor; not in system Python.

Creates content assets only. Runtime behaviour is in Runtime/BigFatFish/Scripts.
This script has not been executed until Logs/unreal_import_report.json exists.
"""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[1]
BASE = "/Game/Mods/BigFatFish"
CHUNK_ID = 237
tools = unreal.AssetToolsHelpers.get_asset_tools()
assets = unreal.EditorAssetLibrary


def import_file(path, destination, name, options=None):
    task = unreal.AssetImportTask()
    for key, value in {
        "filename": str(path), "destination_path": destination,
        "destination_name": name, "automated": True,
        "replace_existing": True, "replace_existing_settings": True, "save": True,
    }.items():
        task.set_editor_property(key, value)
    if options is not None:
        task.set_editor_property("options", options)
        task.set_editor_property("factory", unreal.FbxFactory())
    tools.import_asset_tasks([task])
    return [unreal.load_asset(p) for p in task.get_editor_property("imported_object_paths")]


def blueprint(name, parent):
    path = f"{BASE}/{name}"
    existing = unreal.load_asset(path)
    if existing:
        return existing
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    result = tools.create_asset(name, BASE, unreal.Blueprint, factory)
    if not result:
        raise RuntimeError(f"Could not create {path}")
    unreal.BlueprintEditorLibrary.compile_blueprint(result)
    return result


def main():
    assets.make_directory(BASE)
    options = unreal.FbxImportUI()
    for key, value in {
        "automated_import_should_detect_type": False,
        "mesh_type_to_import": unreal.FBXImportType.FBXIT_SKELETAL_MESH,
        "import_as_skeletal": True, "import_mesh": True,
        "import_animations": True, "import_materials": False,
        "import_textures": False, "create_physics_asset": False,
        "override_animation_name": "AN_BigFatFish_Swim",
    }.items():
        options.set_editor_property(key, value)
    mesh_options = options.get_editor_property("skeletal_mesh_import_data")
    mesh_options.set_editor_property("import_morph_targets", True)
    mesh_options.set_editor_property("convert_scene", True)
    mesh_options.set_editor_property("convert_scene_unit", True)
    mesh_options.set_editor_property("force_front_x_axis", True)
    mesh_options.set_editor_property("update_skeleton_reference_pose", False)
    animation_options = options.get_editor_property("anim_sequence_import_data")
    animation_options.set_editor_property("use_default_sample_rate", True)
    animation_options.set_editor_property("convert_scene", True)
    animation_options.set_editor_property("convert_scene_unit", True)
    animation_options.set_editor_property("force_front_x_axis", True)
    existing_mesh=unreal.load_asset(BASE+"/Character/SK_BigFatFish")
    if existing_mesh:
        existing_mesh.get_editor_property("asset_import_data").set_editor_property("import_morph_targets",True)
    imported = import_file(ROOT / "SourceAssets/Export/WhaleGirl_Swim.fbx",
                           BASE + "/Character", "SK_BigFatFish", options)
    meshes = [o for o in imported if isinstance(o, unreal.SkeletalMesh)]
    animations = [o for o in imported if isinstance(o, unreal.AnimSequence)]
    # Legacy FBX reports the mesh as its primary imported object, while the
    # animation and skeleton are registered as additional objects in memory.
    if not animations:
        animation_asset = unreal.load_asset(BASE + "/Character/AN_BigFatFish_Swim")
        if isinstance(animation_asset, unreal.AnimSequence):
            animations = [animation_asset]
    if not meshes or len(animations) != 1:
        raise RuntimeError(f"Unexpected import: {len(meshes)} meshes, {len(animations)} animations")
    # FBX may produce multiple meshes on some importer versions. Do not silently
    # build an incomplete character if only a head or clothing was imported.
    if len(meshes) != 1:
        raise RuntimeError("Expected one combined skeletal mesh; configure FBX skeletal-mesh merge before continuing")
    mesh, animation = meshes[0], animations[0]
    manifest = json.loads((ROOT / "SourceAssets/asset_manifest.json").read_text(encoding="utf-8"))
    textures = {}
    for entry in manifest["textures"]:
        file = ROOT / "SourceAssets/Export/Textures" / entry["file"]
        imported_textures = import_file(file, BASE + "/Textures", file.stem.replace("WhaleGirl", "BigFatFish"))
        texture = next((o for o in imported_textures if isinstance(o, unreal.Texture2D)), None)
        if not texture:
            raise RuntimeError(f"Texture import failed: {file}")
        textures[entry["image"]] = texture
    materials = {}
    for entry in manifest["materials"]:
        name = "M_BigFatFish_" + entry["material"]
        material = unreal.load_asset(f"{BASE}/Materials/{name}")
        if material is None:
            material = tools.create_asset(name, BASE + "/Materials", unreal.Material, unreal.MaterialFactoryNew())
        graph = unreal.MaterialEditingLibrary
        graph.delete_all_material_expressions(material)
        texture_node = graph.create_material_expression(material, unreal.MaterialExpressionTextureSample, -400, 0)
        texture_node.set_editor_property("texture", textures[entry["images"][0]])
        graph.connect_material_property(texture_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        roughness = graph.create_material_expression(material, unreal.MaterialExpressionConstant, -400, 200)
        roughness.set_editor_property("r", 0.8)
        graph.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
        material.set_editor_property("two_sided", True)
        # This project disables automatic material usage. SetMaterialUsage is
        # conditional on that editor option and can silently leave the flag off.
        material.set_editor_property("used_with_skeletal_mesh", True)
        material.set_editor_property('used_with_morph_targets',True)
        assert material.get_editor_property("used_with_skeletal_mesh")
        # Expression atlas uses transparency. Other slots remain opaque for v0.1.
        if entry["material"] == "expression":
            material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
            graph.connect_material_property(texture_node, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
        graph.recompile_material(material)
        materials[entry["material"].lower()] = material
    material_slots = mesh.get_editor_property("materials")
    assigned = []
    for index, slot in enumerate(material_slots):
        slot_name = str(slot.get_editor_property("imported_material_slot_name"))
        key = slot_name.lower()
        if key not in materials:
            raise RuntimeError(f"Unmapped material slot: {slot_name}; fix before cooking")
        slot.set_editor_property("material_interface", materials[key])
        material_slots[index] = slot
        assigned.append(slot_name)
    mesh.set_editor_property("materials", material_slots)
    # Empty loader entry: BPModLoader creates it, while Lua owns test spawning.
    loader = blueprint("ModActor", unreal.Actor)
    bp = blueprint("BP_BigFatFish", unreal.SkeletalMeshActor)
    generated_class = assets.load_blueprint_class(BASE + "/BP_BigFatFish")
    cdo = unreal.get_default_object(generated_class)
    component = cdo.get_editor_property("skeletal_mesh_component")
    component.set_skeletal_mesh_asset(mesh)
    component.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    component.set_editor_property("animation_data", unreal.SingleAnimationPlayData(
        anim_to_play=animation, saved_looping=True, saved_playing=True,
        saved_position=0.0, saved_play_rate=1.0))
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_simulate_physics(False)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    label_path = BASE + "/PAL_BigFatFish"
    label = unreal.load_asset(label_path)
    if not label:
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.PrimaryAssetLabel)
        label = tools.create_asset("PAL_BigFatFish", BASE, unreal.PrimaryAssetLabel, factory)
    rules = label.get_editor_property("rules")
    rules.set_editor_property("chunk_id", CHUNK_ID)
    rules.set_editor_property("cook_rule", unreal.PrimaryAssetCookRule.ALWAYS_COOK)
    label.set_editor_property("rules", rules)
    label.set_editor_property("label_assets_in_my_directory", True)
    # Save explicitly: CDO/default-component edits are not always marked dirty.
    for obj in [mesh.get_editor_property("skeleton"), mesh, animation, bp, loader, label, *materials.values(), *textures.values()]:
        if not assets.save_loaded_asset(obj, only_if_is_dirty=False):
            raise RuntimeError(f"Failed to save {obj.get_path_name()}")
    report = {"engine_version": unreal.SystemLibrary.get_engine_version(),
              "mesh": mesh.get_path_name(), "animation": animation.get_path_name(),
              "blueprint": bp.get_path_name(), "material_slots": assigned,
              "chunk_id": CHUNK_ID, "status": "imported_not_game_tested"}
    (ROOT / "Logs/unreal_import_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("BIGFATFISH_IMPORT_OK " + json.dumps(report))


if __name__ == "__main__":
    main()
