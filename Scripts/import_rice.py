"""Create a native farmable rice plant and grain item in the isolated modkit."""
import json
import traceback
import sys
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from editor_property_import import set_properties
from rice_localization import set_text
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
    for name in ('SM_BFF_RicePlant','SM_BFF_RiceStalk','SM_BFF_RicePanicle','SM_BFF_RiceGrain','SM_BFF_CookedRice','SM_BFF_EmptyRiceBowl'):
        task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Rice/Export'/(name+'.fbx'))
        task.destination_path=BASE+'/Meshes';task.destination_name=name
        task.automated=True;task.replace_existing=True;task.save=True
        options=unreal.FbxImportUI();options.import_mesh=True;options.import_as_skeletal=False
        options.import_materials=False;options.import_textures=False;options.automated_import_should_detect_type=False
        options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True
        options.static_mesh_import_data.auto_generate_collision=True
        options.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task.options=options;task.factory=unreal.FbxFactory()
        tools.import_asset_tasks([task])
        mesh=unreal.load_asset(BASE+'/Meshes/'+name);assert isinstance(mesh,unreal.StaticMesh),name
        meshes[name]=mesh
    print('RICE_MESHES_IMPORTED',flush=True)
    colors=[('RiceStem',(.018,.20,.055)),('RiceLeaf',(.025,.38,.095)),('RiceGrain',(.82,.52,.075)),('RiceGrainLight',(.95,.72,.19)),
            ('RiceBowl',(.025,.14,.18)),('CookedRice',(.91,.88,.76)),('CookedRiceShade',(.76,.73,.61))]
    materials={}
    for name,color in colors:
        material=unreal.load_asset(BASE+'/Materials/M_'+name)
        if material is None:material=tools.create_asset('M_'+name,BASE+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        graph=unreal.MaterialEditingLibrary;graph.delete_all_material_expressions(material)
        texture_task=unreal.AssetImportTask();texture_task.filename=str(ROOT/'SourceAssets/Rice/Export'/('T_BFF_'+name+'_Color.png'))
        texture_task.destination_path=BASE+'/Textures';texture_task.automated=True;texture_task.replace_existing=True;texture_task.save=True
        tools.import_asset_tasks([texture_task])
        texture=unreal.load_asset(BASE+'/Textures/T_BFF_'+name+'_Color');assert texture
        texture.set_editor_property('srgb',True);save(texture)
        node=graph.create_material_expression(material,unreal.MaterialExpressionTextureSample)
        node.set_editor_property('texture',texture)
        assert graph.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
        roughness=graph.create_material_expression(material,unreal.MaterialExpressionConstant)
        roughness.set_editor_property('r',.25 if name=='RiceBowl' else .55)
        assert graph.connect_material_property(roughness,'',unreal.MaterialProperty.MP_ROUGHNESS)
        specular=graph.create_material_expression(material,unreal.MaterialExpressionConstant)
        specular.set_editor_property('r',.3)
        assert graph.connect_material_property(specular,'',unreal.MaterialProperty.MP_SPECULAR)
        glow=graph.create_material_expression(material,unreal.MaterialExpressionConstant)
        glow.set_editor_property('r',0.)
        material.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
        assert graph.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        material.set_editor_property('two_sided',True)
        material.set_editor_property('used_with_instanced_static_meshes',True)
        material.set_editor_property('used_with_nanite',True)
        graph.recompile_material(material);save(material);materials[name]=material
    for mesh in meshes.values():
        slots=mesh.get_editor_property('static_materials')
        # Iterating a reflected struct array yields copies; changing a slot does
        # not mutate the mesh. Use the mesh API and verify the actual binding.
        for index,slot in enumerate(slots):
            material=materials[str(slot.get_editor_property('imported_material_slot_name'))]
            mesh.set_material(index,material)
            assert mesh.get_material(index)==material,(mesh.get_name(),index)
        save(mesh)
    task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Rice/Export/T_BFF_RiceGrain.png')
    task.destination_path=BASE+'/Textures';task.automated=True;task.replace_existing=True;task.save=True
    tools.import_asset_tasks([task]);icon=unreal.load_asset(BASE+'/Textures/T_BFF_RiceGrain');assert icon
    task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Rice/Export/T_BFF_CookedRice.png')
    task.destination_path=BASE+'/Textures';task.automated=True;task.replace_existing=True;task.save=True
    tools.import_asset_tasks([task]);cooked_icon=unreal.load_asset(BASE+'/Textures/T_BFF_CookedRice');assert cooked_icon
    grain=data('DA_BFF_RiceGrain_ItemType','/Script/UWEInventory.UWEItemType')
    planted=data('DA_BFF_RicePlant_ItemType','/Script/UWEInventory.UWEItemType')
    recipe=data('DA_BFF_RicePlant_Recipe','/Script/UWECrafting.UWECraftingRecipe')
    action=data('DA_BFF_RicePlant_ConstructData','/Script/Subnautica2.SN2BuilderConstructActionData')
    cooked=data('DA_BFF_CookedRice_ItemType','/Script/UWEInventory.UWEItemType')
    cooked_recipe=data('DA_BFF_CookedRice_Recipe','/Script/UWECrafting.UWECraftingRecipe')
    print('RICE_DATA_CREATED',flush=True)
    pickup=blueprint('BP_BFF_RiceGrain',cls('/Script/UWEInventory.UWEBaseItem'))
    harvest=blueprint('BP_BFF_RiceHarvest',cls('/Script/UWEInventory.UWEBaseItem'))
    for bp,mesh in ((pickup,meshes['SM_BFF_RiceGrain']),(harvest,meshes['SM_BFF_RicePanicle'])):
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        cdo=unreal.get_default_object(bp.generated_class())
        cdo.set_editor_property('ItemType',grain)
        mesh_comp=cdo.get_editor_property('Mesh');assert mesh_comp
        mesh_comp.set_static_mesh(mesh)
        for index,slot in enumerate(mesh.get_editor_property('static_materials')):mesh_comp.set_material(index,slot.get_editor_property('material_interface'))
        attach_data(mesh_comp,[grain])
        save(bp)
    plant=blueprint('BP_BFF_RicePlant',unreal.Actor)
    mesh_comp,mesh_handle=component(plant,'RiceStalk',unreal.StaticMeshComponent)
    mesh_comp.set_static_mesh(meshes['SM_BFF_RiceStalk'])
    for index,slot in enumerate(meshes['SM_BFF_RiceStalk'].get_editor_property('static_materials')):mesh_comp.set_material(index,slot.get_editor_property('material_interface'))
    mesh_comp.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
    data_comp,_=component(plant,'RiceAssetData',cls('/Script/UWEAssetRegistry.UWEAssetDataComponent'))
    attach_data(data_comp,[action])
    component(plant,'RiceSave',cls('/Script/UWESaveSystem.UWESaveComponent'))
    grower,_=component(plant,'RiceSeedGrower',cls('/Script/UWEFarming.UWESeedGrowerComponent'))
    for key,value in {'SeedClass':harvest.generated_class(),'bStartsGrown':False,'HighPrioritySpawn':True,
                      'SpawnRate':0.,'SpawnTimeVariance':0.,'RipenTime':60.,'ShowRipeningProgress':True,
                      'SeedProgressPrimaryHintKey':'FarmableProgressPercent'}.items():
        grower.set_editor_property(key,value)
    set_text(grower,'SeedProgressFormatText','Growth')
    grower.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
    grower.set_editor_property('relative_location',unreal.Vector(0,0,72))
    grower.set_editor_property('OffsetLocation',unreal.Vector(0,0,0))
    component(plant,'RiceSeedReplication',cls('/Script/UWEFarming.UWESeedGrowerReplicatorComponent'))
    anchor,_=component(plant,'RicePlacementAnchor',cls('/Script/Subnautica2.UWEPlacementAnchor'))
    anchor.set_editor_property('UseForSamplePoints',True);anchor.set_editor_property('SampleRadius',10.)
    volume,_=component(plant,'RicePlacementVolume',cls('/Script/Subnautica2.UWEPlacementVolumeComponent'))
    volume.set_editor_property('relative_location',unreal.Vector(0,0,40))
    volume.set_editor_property('relative_scale3d',unreal.Vector(.20,.20,.32))
    unreal.BlueprintEditorLibrary.compile_blueprint(plant)
    unreal.get_default_object(plant.generated_class()).set_editor_property('replicates',True)
    # Separate archetype: wild plants start ripe; planted crops retain growth.
    save(plant)
    wild_path=BASE+'/Blueprints/BP_BFF_WildRice'
    wild=unreal.load_asset(wild_path)
    if not wild:wild=assets.duplicate_asset(plant.get_path_name(),wild_path)
    assert wild
    wild_grower,_=component(wild,'RiceSeedGrower',cls('/Script/UWEFarming.UWESeedGrowerComponent'))
    wild_grower.set_editor_property('bStartsGrown',True)
    set_text(wild_grower,'SeedProgressFormatText','Growth')
    unreal.BlueprintEditorLibrary.compile_blueprint(wild);save(wild)
    grain.set_editor_property('ActorClass',pickup.generated_class())
    set_text(grain,'Name','GrainName')
    set_text(grain,'ItemDescription','GrainDescription')
    grain.set_editor_property('Thumbnail',icon)
    tag=unreal.GameplayTag();assert tag.import_text('(TagName="ItemType.Flora")')
    grain.set_editor_property('TypeTag',tag)
    planted.set_editor_property('ActorClass',plant.generated_class())
    set_text(planted,'Name','PlantName')
    set_properties(planted,'PickupDestination=CannotPickup')
    set_text(recipe,'Name','PlantName')
    set_text(recipe,'Description','PlantDescription')
    recipe.set_editor_property('Thumbnail',icon)
    set_properties(recipe,f'''Output(0)=(ItemType="{planted.get_path_name()}",NumItems=1)
Requirements(0)=(ItemType="{grain.get_path_name()}",NumItems=1)
DefaultRecipeState=Unlocked''')
    recipe.set_editor_property('CraftingTime',0.)
    category=unreal.load_asset('/Game/Data/CraftingRecipes/Categories/Builder/DA_BuilderFarming_PlantsCategory')
    assert category,'Native farming category must load'
    recipe.set_editor_property('Category',category)
    recipe.set_editor_property('DuplicatesBuilderActionData',True)
    set_text(action,'Name','PlantName')
    set_text(action,'Description','BuildDescription')
    action.set_editor_property('Recipe',recipe);action.set_editor_property('Thumbnail',icon)
    action.set_editor_property('GhostMeshOverride',meshes['SM_BFF_RicePlant'])
    set_properties(action,'''Category=BaseObject
PlacementParamsSource=LocalParams
LocalPlacementParams=(SurfaceRules=(AllowedSurfaces=36,AllowedZones=1,AllowedBrushTypes=(GameplayTags=((TagName="SculpturalBase.BrushType.Planter"))),AllowedSurfaceTags=(GameplayTags=((TagName="BuildableSurface.Planter")))),SnappingRules=(OverrideCurrentSnapping=True),RotationRules=(bSnapsToSurfaceGridRotation=4),InteractionRules=(bOverrideInteractDistance=True,InteractDistance=750.000000))''')
    bowl=blueprint('BP_BFF_CookedRice',cls('/Script/UWEInventory.UWEBaseItem'))
    unreal.BlueprintEditorLibrary.compile_blueprint(bowl)
    bowl_cdo=unreal.get_default_object(bowl.generated_class());bowl_cdo.set_editor_property('ItemType',cooked)
    bowl_mesh=bowl_cdo.get_editor_property('Mesh');bowl_mesh.set_static_mesh(meshes['SM_BFF_CookedRice'])
    for index,slot in enumerate(meshes['SM_BFF_CookedRice'].get_editor_property('static_materials')):bowl_mesh.set_material(index,slot.get_editor_property('material_interface'))
    attach_data(bowl_mesh,[cooked])
    cooked.set_editor_property('ActorClass',bowl.generated_class())
    set_text(cooked,'Name','FoodName')
    set_text(cooked,'ItemDescription','FoodDescription')
    cooked.set_editor_property('Thumbnail',cooked_icon)
    set_properties(cooked,'''TypeTag=(TagName="ItemType.Fuel")
Abilities(0)="/Game/Blueprints/AbilitySystem/Abilities/GA_Consume.GA_Consume_C"
Abilities(1)="/Game/Blueprints/AbilitySystem/Abilities/Tools/GA_DropHeldItem.GA_DropHeldItem_C"
TunableData=(((TagName="ItemType.TunableData.Food"),25.000000))
bUseFromInventory=True''')
    set_text(cooked_recipe,'Name','FoodName')
    set_text(cooked_recipe,'Description','MealDescription')
    cooked_recipe.set_editor_property('Thumbnail',cooked_icon)
    cooked_recipe.set_editor_property('CraftingTime',5.)
    set_properties(cooked_recipe,f'''Output(0)=(ItemType="{cooked.get_path_name()}",NumItems=1)
Requirements(0)=(ItemType="{grain.get_path_name()}",NumItems=1)
Requirements(1)=(ItemType="/Game/Data/ItemType/DA_Water_ItemType.DA_Water_ItemType",NumItems=1)
DefaultRecipeState=Unlocked
Category="/Game/Data/CraftingRecipes/Categories/Fabricator/DA_SustenanceMeals.DA_SustenanceMeals"
OrderingIndex=510''')
    for obj in (pickup,harvest,plant,grain,planted,recipe,action,bowl,cooked,cooked_recipe):save(obj)
    report={'status':'editor_assets_created_game_test_pending','created':created,
            'native_growth_seconds':60,'grain_item':grain.get_path_name(),'plant_class':plant.generated_class().get_path_name(),
            'native_seed_grower':grower.get_class().get_path_name(),'save_component':'UWESaveComponent',
            'native_farming_category':category.get_path_name(),'version':'0.4.1-prototype',
            'harvesting':'accepted in game by user','panicle_anchor_cm':72,
            'cooked_rice':cooked.get_path_name(),'cooking_recipe':cooked_recipe.get_path_name()}
    (OUT/'import_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('RICE_IMPORT_COMPLETE',json.dumps(report),flush=True)

try:main()
except Exception:
    (OUT/'import_error.txt').write_text(traceback.format_exc(),encoding='utf8')
    raise
finally:
    if '-run=pythonscript' not in unreal.SystemLibrary.get_command_line().lower():unreal.SystemLibrary.quit_editor()
