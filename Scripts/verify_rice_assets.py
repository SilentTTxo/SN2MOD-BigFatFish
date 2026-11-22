"""Reload and validate the persisted native rice definitions and SCS templates."""
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Logs/rice/validation';OUT.mkdir(parents=True,exist_ok=True)
BASE='/BigFatFishRice'
report={'status':'pending','exports':{}}
def export(obj,name):
    path=OUT/(name+'.copy')
    task=unreal.AssetExportTask();task.object=obj;task.filename=str(path)
    task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.ObjectExporterT3D()
    assert unreal.Exporter.run_asset_export_task(task),name
    data=path.read_bytes();text=data.decode('utf16' if data.startswith(b'\xff\xfe') else 'utf8')
    report['exports'][name]=str(path)
    return text

grain=unreal.load_asset(BASE+'/Data/DA_BFF_RiceGrain_ItemType');assert grain
plant_item=unreal.load_asset(BASE+'/Data/DA_BFF_RicePlant_ItemType');assert plant_item
recipe=unreal.load_asset(BASE+'/Data/DA_BFF_RicePlant_Recipe');assert recipe
action=unreal.load_asset(BASE+'/Data/DA_BFF_RicePlant_ConstructData');assert action
grain_text=export(grain,'grain')
assert 'ItemType.Flora' in grain_text and 'BP_BFF_RiceGrain' in grain_text
recipe_text=export(recipe,'recipe')
assert 'DA_BFF_RiceGrain_ItemType' in recipe_text and 'DA_BFF_RicePlant_ItemType' in recipe_text
assert 'DefaultRecipeState=Locked' not in recipe_text  # native CL-131439 CDO default is Unlocked
assert 'DA_BuilderFarming_PlantsCategory' in recipe_text
action_text=export(action,'construction')
assert 'DA_BFF_RicePlant_Recipe' in action_text and 'BuildableSurface.Planter' in action_text
assert 'PlacementParamsSource=DataAsset' not in action_text  # native CDO default is LocalParams
assert 'CannotPickup' in export(plant_item,'plant_item')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib=unreal.SubobjectDataBlueprintFunctionLibrary
bp=unreal.load_asset(BASE+'/Blueprints/BP_BFF_RicePlant');assert bp
components={}
for handle in sub.k2_gather_subobject_data_for_blueprint(bp):
    obj=lib.get_object_for_blueprint(lib.get_data(handle),bp)
    if obj:components[obj.get_name().removesuffix('_GEN_VARIABLE')]=obj
grower=components['RiceSeedGrower']
assert abs(grower.get_editor_property('relative_location').z-72)<.01
assert abs(grower.get_editor_property('OffsetLocation').z)<.01
assert grower.get_editor_property('SeedProgressPrimaryHintKey')=='FarmableProgressPercent'
assert unreal.load_asset('/Game/StringTables/ST_WorldObjectHint')
assert unreal.StringTableLibrary.is_registered_table_entry(unreal.Name('/Game/StringTables/ST_WorldObjectHint.ST_WorldObjectHint'),'FarmableProgressPercent')
assert abs(grower.get_editor_property('RipenTime')-60)<.01
assert 'BP_BFF_RiceHarvest' in str(grower.get_editor_property('SeedClass'))
assert components['RiceSave'].get_class().get_path_name()=='/Script/UWESaveSystem.UWESaveComponent'
assert components['RiceSeedReplication'].get_class().get_path_name()=='/Script/UWEFarming.UWESeedGrowerReplicatorComponent'
assert components['RiceStalk'].get_editor_property('static_mesh').get_name()=='SM_BFF_RiceStalk'
assert 'DA_BFF_RicePlant_ConstructData' in export(components['RiceAssetData'],'plant_asset_data')
export(grower,'seed_grower')
for name in ('BP_BFF_RiceGrain','BP_BFF_RiceHarvest'):
    pickup=unreal.load_asset(BASE+'/Blueprints/'+name);assert pickup
    cdo=unreal.get_default_object(pickup.generated_class())
    assert cdo.get_editor_property('ItemType')==grain,name
    assert cdo.get_editor_property('Mesh').get_editor_property('static_mesh'),name
    export(cdo,name)
cooked=unreal.load_asset(BASE+'/Data/DA_BFF_CookedRice_ItemType');assert cooked
cooked_text=export(cooked,'cooked_item')
assert 'GA_Consume_C' in cooked_text and 'bUseFromInventory=True' in cooked_text
assert 'ItemType.TunableData.Food' in cooked_text
assert 'GA_BFF_OfferRice_C' not in cooked_text
meal=unreal.load_asset(BASE+'/Data/DA_BFF_CookedRice_Recipe');assert meal
meal_text=export(meal,'cooked_recipe')
for value in ('DA_SustenanceMeals','DA_BFF_RiceGrain_ItemType','DA_Water_ItemType','DA_BFF_CookedRice_ItemType'):
    assert value in meal_text,value
assert 'DefaultRecipeState=Locked' not in meal_text
bowl=unreal.load_asset(BASE+'/Blueprints/BP_BFF_CookedRice');assert bowl
bowl_cdo=unreal.get_default_object(bowl.generated_class())
assert bowl_cdo.get_editor_property('ItemType')==cooked
assert bowl_cdo.get_editor_property('Mesh').get_editor_property('static_mesh').get_name()=='SM_BFF_CookedRice'
for name in ('RiceStem','RiceLeaf','RiceGrain','RiceGrainLight','RiceBowl','CookedRice','CookedRiceShade'):
    material=unreal.load_asset(BASE+'/Materials/M_'+name);assert material
    assert material.get_editor_property('used_with_nanite'),name
    glow=unreal.MaterialEditingLibrary.get_material_property_input_node(material,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    assert isinstance(glow,unreal.MaterialExpressionConstant) and glow.get_editor_property('r')==0,name
    assert material.get_editor_property('shading_model')==unreal.MaterialShadingModel.MSM_DEFAULT_LIT
    material_text=export(material,'material_'+name)
    assert 'T_BFF_'+name+'_Color' in material_text,name
for name in ('SM_BFF_RicePlant','SM_BFF_RiceStalk','SM_BFF_RicePanicle','SM_BFF_RiceGrain','SM_BFF_CookedRice','SM_BFF_EmptyRiceBowl'):
    mesh=unreal.load_asset(BASE+'/Meshes/'+name);assert mesh
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        expected=unreal.load_asset(BASE+'/Materials/M_'+str(slot.get_editor_property('imported_material_slot_name')))
        assert expected and mesh.get_material(index)==expected,(name,index)
for name in ('BP_BFF_RiceGrain','BP_BFF_RiceHarvest','BP_BFF_CookedRice'):
    cdo=unreal.get_default_object(unreal.load_asset(BASE+'/Blueprints/'+name).generated_class())
    comp=cdo.get_editor_property('Mesh');mesh=comp.get_editor_property('static_mesh')
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        assert comp.get_material(index)==mesh.get_material(index),(name,index)
assert 'NSLOCTEXT("BigFatFishRice"' in grain_text
assert unreal.load_asset(BASE+'/Blueprints/BP_BFF_RiceServing')
cultures={}
for culture,expected in [('en','Sea Rice Grain'),('zh-Hans','海稻'),('zh-Hant','海稻'),('fr','Sea Rice Grain'),('ja','Sea Rice Grain')]:
    assert unreal.InternationalizationLibrary.set_current_culture(culture)
    value=str(grain.get_editor_property('Name'));cultures[culture]=value
    assert value==expected,(culture,value,expected)
report['native_cultures']=cultures
wild=unreal.load_asset(BASE+'/Blueprints/BP_BFF_WildRice');assert wild
wild_components=[lib.get_object_for_blueprint(lib.get_data(h),wild) for h in sub.k2_gather_subobject_data_for_blueprint(wild)]
assert any(c and c.get_name()=='RiceSeedGrower_GEN_VARIABLE' and c.get_editor_property('bStartsGrown') for c in wild_components)
serving=unreal.get_default_object(unreal.load_asset(BASE+'/Blueprints/BP_BFF_RiceServing').generated_class())
assert serving.get_editor_property('EmptyMesh').get_name()=='SM_BFF_EmptyRiceBowl'
report.update(status='PASS: persisted native rice item, builder recipe, planter rules, growth, save/replication components and pickups',
              components={name:obj.get_class().get_path_name() for name,obj in components.items()},
              ripening_seconds=60,panicle_anchor_cm=72,version='0.4.1-prototype',
              gameplay_validation='Planting and harvest accepted in v0.1.0; v0.4.0 visuals, cooking and save/reload await game test')
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('RICE_VALIDATION_PASS',json.dumps(report),flush=True)
