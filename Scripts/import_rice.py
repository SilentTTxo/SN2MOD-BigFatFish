"""Create a native farmable rice plant and grain item in the isolated modkit."""
import json
import traceback
import sys
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from editor_property_import import set_properties
BASE='/BigFatFishRice'
OUT=ROOT/'Logs/rice';OUT.mkdir(parents=True,exist_ok=True)
assets=unreal.EditorAssetLibrary
tools=unreal.AssetToolsHelpers.get_asset_tools()
created=[]

def cls(path):
    value=unreal.find_object(None,path)
    assert value,path
    return value

def data(name,class_path):
    path=BASE+'/Data/'+name
    obj=unreal.load_asset(path)
    if obj is None:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',cls(class_path))
        obj=tools.create_asset(name,BASE+'/Data',cls(class_path),factory)
    assert obj,path
    created.append(path)
    return obj

def blueprint(name,parent):
    path=BASE+'/Blueprints/'+name
    obj=unreal.load_asset(path)
    if obj is None:
        factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',parent)
        obj=tools.create_asset(name,BASE+'/Blueprints',unreal.Blueprint,factory)
    assert obj,path
    created.append(path)
    return obj

sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib=unreal.SubobjectDataBlueprintFunctionLibrary
def component(bp,name,class_type):
    handles=sub.k2_gather_subobject_data_for_blueprint(bp)
    for handle in handles:
        obj=lib.get_object_for_blueprint(lib.get_data(handle),bp)
        if obj and obj.get_name().removesuffix('_GEN_VARIABLE')==name:return obj,handle
    params=unreal.AddNewSubobjectParams(parent_handle=handles[0],new_class=class_type,blueprint_context=bp)
    handle,reason=sub.add_new_subobject(params)
    assert not str(reason),(name,str(reason))
    sub.rename_subobject(handle,unreal.Text(name))
    obj=lib.get_object_for_blueprint(lib.get_data(handle),bp)
    assert obj,name
    return obj,handle

def attach_data(component,data_assets):
    user_data=unreal.find_object(component,'RiceAssetData')
    if user_data is None:user_data=unreal.new_object(cls('/Script/UWEAssetRegistry.UWEAssetUserData'),outer=component,name='RiceAssetData')
    user_data.set_editor_property('DataAssets',data_assets)
    component.set_editor_property('asset_user_data',[user_data])

def save(obj):
    assert assets.save_loaded_asset(obj,False),obj.get_path_name()

def main():
    print('RICE_BUILD_START',flush=True)
    meshes={}
    for name in ('SM_BFF_RicePlant','SM_BFF_RiceStalk','SM_BFF_RicePanicle','SM_BFF_RiceGrain'):
        task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Rice/Export'/(name+'.fbx'))
        task.destination_path=BASE+'/Meshes';task.destination_name=name
        task.automated=True;task.replace_existing=True;task.save=True
        options=unreal.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False
        options.import_materials=False;options.import_textures=False;options.automated_import_should_detect_type=False
        options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True
        options.static_mesh_import_data.auto_generate_collision=True
        task.options=options;task.factory=unreal.FbxFactory()
        tools.import_asset_tasks([task])
        mesh=unreal.load_asset(BASE+'/Meshes/'+name);assert isinstance(mesh,unreal.StaticMesh),name
        meshes[name]=mesh
    print('RICE_MESHES_IMPORTED',flush=True)
    colors=[('RiceStem',(.15,.35,.035)),('RiceLeaf',(.23,.52,.055)),('RiceGrain',(.77,.48,.12)),('RiceGrainLight',(.95,.70,.24))]
    materials={}
    for name,color in colors:
        material=unreal.load_asset(BASE+'/Materials/M_'+name)
        if material is None:material=tools.create_asset('M_'+name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        graph=unreal.MaterialEditingLibrary;graph.delete_all_material_expressions(material)
        node=graph.create_material_expression(material,unreal.MaterialExpressionConstant3Vector)
        node.constant=unreal.LinearColor(*color,1)
        graph.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
        material.set_editor_property('two_sided',True)
        graph.recompile_material(material);save(material);materials[name]=material
    for mesh in meshes.values():
        slots=mesh.get_editor_property('static_materials')
        for slot in slots:
            slot.set_editor_property('material_interface',materials[str(slot.get_editor_property('imported_material_slot_name'))])
        mesh.set_editor_property('static_materials',slots);save(mesh)
    task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Rice/Export/T_BFF_RiceGrain.png')
    task.destination_path=BASE+'/Textures';task.automated=True;task.replace_existing=True;task.save=True
    tools.import_asset_tasks([task]);icon=unreal.load_asset(BASE+'/Textures/T_BFF_RiceGrain');assert icon
    grain=data('DA_BFF_RiceGrain_ItemType','/Script/UWEInventory.UWEItemType')
    planted=data('DA_BFF_RicePlant_ItemType','/Script/UWEInventory.UWEItemType')
    recipe=data('DA_BFF_RicePlant_Recipe','/Script/UWECrafting.UWECraftingRecipe')
    action=data('DA_BFF_RicePlant_ConstructData','/Script/Subnautica2.SN2BuilderConstructActionData')
    print('RICE_DATA_CREATED',flush=True)
    pickup=blueprint('BP_BFF_RiceGrain',cls('/Script/UWEInventory.UWEBaseItem'))
    harvest=blueprint('BP_BFF_RiceHarvest',cls('/Script/UWEInventory.UWEBaseItem'))
    for bp,mesh in ((pickup,meshes['SM_BFF_RiceGrain']),(harvest,meshes['SM_BFF_RicePanicle'])):
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        cdo=unreal.get_default_object(bp.generated_class())
        cdo.set_editor_property('ItemType',grain)
        mesh_comp=cdo.get_editor_property('Mesh');assert mesh_comp
        mesh_comp.set_static_mesh(mesh)
        attach_data(mesh_comp,[grain])
        save(bp)
    plant=blueprint('BP_BFF_RicePlant',unreal.Actor)
    mesh_comp,mesh_handle=component(plant,'RiceStalk',unreal.StaticMeshComponent)
    mesh_comp.set_static_mesh(meshes['SM_BFF_RiceStalk'])
    mesh_comp.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
    data_comp,_=component(plant,'RiceAssetData',cls('/Script/UWEAssetRegistry.UWEAssetDataComponent'))
    attach_data(data_comp,[action])
    component(plant,'RiceSave',cls('/Script/UWESaveSystem.UWESaveComponent'))
    grower,_=component(plant,'RiceSeedGrower',cls('/Script/UWEFarming.UWESeedGrowerComponent'))
    for key,value in {'SeedClass':harvest.generated_class(),'bStartsGrown':False,'HighPrioritySpawn':True,
                      'SpawnRate':0.,'SpawnTimeVariance':0.,'RipenTime':60.,'ShowRipeningProgress':True,
                      'SeedProgressFormatText':unreal.Text('{0}%'),'SeedProgressPrimaryHintKey':'BFFRiceGrowth'}.items():
        grower.set_editor_property(key,value)
    grower.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
    component(plant,'RiceSeedReplication',cls('/Script/UWEFarming.UWESeedGrowerReplicatorComponent'))
    anchor,_=component(plant,'RicePlacementAnchor',cls('/Script/Subnautica2.UWEPlacementAnchor'))
    anchor.set_editor_property('UseForSamplePoints',True);anchor.set_editor_property('SampleRadius',10.)
    volume,_=component(plant,'RicePlacementVolume',cls('/Script/Subnautica2.UWEPlacementVolumeComponent'))
    volume.set_editor_property('relative_location',unreal.Vector(0,0,40))
    volume.set_editor_property('relative_scale3d',unreal.Vector(.20,.20,.32))
    unreal.BlueprintEditorLibrary.compile_blueprint(plant)
    unreal.get_default_object(plant.generated_class()).set_editor_property('replicates',True)
    grain.set_editor_property('ActorClass',pickup.generated_class())
    grain.set_editor_property('Name',unreal.Text('Rice Grain / 稻谷'))
    grain.set_editor_property('ItemDescription',unreal.Text('Plant in an aquafarm with the builder. Keep some grains for replanting. / 使用建造器在种植槽栽种，留一部分稻谷再种。'))
    grain.set_editor_property('Thumbnail',icon)
    tag=unreal.GameplayTag();assert tag.import_text('(TagName="ItemType.Flora")')
    grain.set_editor_property('TypeTag',tag)
    planted.set_editor_property('ActorClass',plant.generated_class())
    planted.set_editor_property('Name',unreal.Text('Rice / 水稻'))
    set_properties(planted,'PickupDestination=CannotPickup')
    recipe.set_editor_property('Name',unreal.Text('Rice / 水稻'))
    recipe.set_editor_property('Description',unreal.Text('Grow rice in a planter. Harvest when ripe. / 在种植槽里栽种水稻，成熟后收获稻谷。'))
    recipe.set_editor_property('Thumbnail',icon)
    set_properties(recipe,f'''Output(0)=(ItemType="{planted.get_path_name()}",NumItems=1)
Requirements(0)=(ItemType="{grain.get_path_name()}",NumItems=1)
DefaultRecipeState=Unlocked''')
    recipe.set_editor_property('CraftingTime',0.)
    category=unreal.load_asset('/Game/Data/CraftingRecipes/Categories/Builder/DA_BuilderFarming_PlantsCategory')
    assert category,'Native farming category must load'
    recipe.set_editor_property('Category',category)
    recipe.set_editor_property('DuplicatesBuilderActionData',True)
    action.set_editor_property('Name',unreal.Text('Rice / 水稻'))
    action.set_editor_property('Description',unreal.Text('Plant rice in a planter. / 在种植槽里栽种水稻。'))
    action.set_editor_property('Recipe',recipe);action.set_editor_property('Thumbnail',icon)
    action.set_editor_property('GhostMeshOverride',meshes['SM_BFF_RicePlant'])
    set_properties(action,'''Category=BaseObject
PlacementParamsSource=LocalParams
LocalPlacementParams=(SurfaceRules=(AllowedSurfaces=36,AllowedZones=1,AllowedBrushTypes=(GameplayTags=((TagName="SculpturalBase.BrushType.Planter"))),AllowedSurfaceTags=(GameplayTags=((TagName="BuildableSurface.Planter")))),SnappingRules=(OverrideCurrentSnapping=True),RotationRules=(bSnapsToSurfaceGridRotation=4),InteractionRules=(bOverrideInteractDistance=True,InteractDistance=750.000000))''')
    for obj in (pickup,harvest,plant,grain,planted,recipe,action):save(obj)
    report={'status':'editor_assets_created_game_test_pending','created':created,
            'native_growth_seconds':60,'grain_item':grain.get_path_name(),'plant_class':plant.generated_class().get_path_name(),
            'native_seed_grower':grower.get_class().get_path_name(),'save_component':'UWESaveComponent',
            'native_farming_category':category.get_path_name()}
    (OUT/'import_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('RICE_IMPORT_COMPLETE',json.dumps(report),flush=True)

try:main()
except Exception:
    (OUT/'import_error.txt').write_text(traceback.format_exc(),encoding='utf8')
    raise
finally:
    if '-run=pythonscript' not in unreal.SystemLibrary.get_command_line().lower():unreal.SystemLibrary.quit_editor()
