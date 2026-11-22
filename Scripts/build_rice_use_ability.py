"""Ordinary native food and a GC-owned full/empty serving prop."""
import sys
from pathlib import Path
import unreal
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'Scripts'))
from editor_property_import import set_properties
from rice_localization import set_text
B='/BigFatFishRice';tools=unreal.AssetToolsHelpers.get_asset_tools()
serving=unreal.load_asset(B+'/Blueprints/BP_BFF_RiceServing')
if not serving:
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.StaticMeshActor)
 serving=tools.create_asset('BP_BFF_RiceServing',B+'/Blueprints',unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.add_member_variable(serving,'EmptyMesh',unreal.BlueprintEditorLibrary.get_object_reference_type(unreal.StaticMesh))
unreal.BlueprintEditorLibrary.compile_blueprint(serving)
cdo=unreal.get_default_object(serving.generated_class())
cdo.set_editor_property('EmptyMesh',unreal.load_asset(B+'/Meshes/SM_BFF_EmptyRiceBowl'))
sc=cdo.static_mesh_component;mesh=unreal.load_asset(B+'/Meshes/SM_BFF_CookedRice');assert mesh
sc.set_static_mesh(mesh);sc.set_mobility(unreal.ComponentMobility.MOVABLE);sc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for i in range(len(mesh.get_editor_property('static_materials'))):sc.set_material(i,mesh.get_material(i))
assert unreal.EditorAssetLibrary.save_loaded_asset(serving,False)
item=unreal.load_asset(B+'/Data/DA_BFF_CookedRice_ItemType');assert item
set_properties(item,'''Abilities=("/Game/Blueprints/AbilitySystem/Abilities/GA_Consume.GA_Consume_C","/Game/Blueprints/AbilitySystem/Abilities/Tools/GA_DropHeldItem.GA_DropHeldItem_C")
TunableData=(((TagName="ItemType.TunableData.Food"),25.000000))
bUseFromInventory=True''')
set_text(item,'ItemDescription','FoodDescription')
assert unreal.EditorAssetLibrary.save_loaded_asset(item,False)
print('NATIVE_RICE_FOOD_READY',flush=True)
