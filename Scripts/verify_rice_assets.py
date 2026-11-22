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
report.update(status='PASS: persisted native rice item, builder recipe, planter rules, growth, save/replication components and pickups',
              components={name:obj.get_class().get_path_name() for name,obj in components.items()},
              ripening_seconds=60,gameplay_validation='not yet performed in game')
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('RICE_VALIDATION_PASS',json.dumps(report),flush=True)
