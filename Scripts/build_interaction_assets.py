"""GC-owned animation resources and the original handheld basin."""
import unreal
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='/Game/Mods/BigFatFish'
tools=unreal.AssetToolsHelpers.get_asset_tools()
mesh=unreal.load_asset(B+'/Character/SK_BigFatFish')
task=unreal.AssetImportTask();task.filename=str(R/'SourceAssets/Export/BigFatFish_HoldBasin.fbx');task.destination_path=B+'/Character';task.destination_name='AN_BigFatFish_HoldBasin'
task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True;task.factory=unreal.FbxFactory()
opt=unreal.FbxImportUI();opt.import_mesh=False;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;opt.skeleton=mesh.get_editor_property('skeleton')
for setting in ('convert_scene','convert_scene_unit','force_front_x_axis','use_default_sample_rate'):opt.anim_sequence_import_data.set_editor_property(setting,True)
task.options=opt;tools.import_asset_tasks([task]);hold=unreal.load_asset(B+'/Character/AN_BigFatFish_HoldBasin');assert hold
task=unreal.AssetImportTask();task.filename=str(R/'SourceAssets/Export/SM_BFF_OriginalBasin.fbx');task.destination_path=B+'/Props';task.destination_name='SM_BFF_OriginalBasin';task.automated=True;task.replace_existing=True;task.save=True
opt=unreal.FbxImportUI();opt.import_as_skeletal=False;opt.import_animations=False;opt.import_materials=False;opt.import_textures=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.force_front_x_axis=True
task.options=opt;tools.import_asset_tasks([task]);basin=unreal.load_asset(B+'/Props/SM_BFF_OriginalBasin');assert basin
material=unreal.load_asset(B+'/Materials/M_BigFatFish_TiePen');assert material
for i in range(len(basin.get_editor_property('static_materials'))):basin.set_material(i,material)
unreal.EditorAssetLibrary.save_loaded_asset(basin,False)
prop=unreal.load_asset(B+'/Props/BP_BFF_BasinProp')
if not prop:
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.StaticMeshActor)
 prop=tools.create_asset('BP_BFF_BasinProp',B+'/Props',unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.compile_blueprint(prop)
comp=unreal.get_default_object(prop.generated_class()).static_mesh_component
comp.set_static_mesh(basin);comp.set_mobility(unreal.ComponentMobility.MOVABLE);comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
unreal.EditorAssetLibrary.save_loaded_asset(prop,False)
bp=unreal.load_asset(B+'/BP_BigFatFish')
# These reflected UPROPERTYs, unlike Lua UObject wrappers, are GC roots via live actors.
values={'FeedAnimation':unreal.load_asset(B+'/Character/AN_BigFatFish_GrabEat'),'BasinAnimation':hold,'BasinPropClass':prop.generated_class()}
for name in ('FeedFullMesh','FeedEmptyMesh','FeedServingClass','FeedMontage','BasinMontage'):values[name]=None
for name in values:
 unreal.BlueprintEditorLibrary.add_member_variable(bp,name,unreal.BlueprintEditorLibrary.get_object_reference_type(unreal.Object))
 unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
for name,value in values.items():cdo.set_editor_property(name,value)
unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
assert cdo.get_editor_property('FeedAnimation') and cdo.get_editor_property('BasinAnimation')
print('INTERACTION_ASSETS_READY',flush=True)
