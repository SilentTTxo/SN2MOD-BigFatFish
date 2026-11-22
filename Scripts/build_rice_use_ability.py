"""An inventory ability dispatches a UE4SS event, without native food consumption."""
import json,sys,uuid
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from editor_graph_import import import_nodes,connect_nodes,remove_node
from editor_property_import import set_properties
BASE='/BigFatFishRice'
tools=unreal.AssetToolsHelpers.get_asset_tools()
parent=unreal.find_object(None,'/Script/UWEAbilitySystem.UWEGameplayAbility');assert parent
bp=unreal.load_asset(BASE+'/Blueprints/GA_BFF_OfferRice')
if not bp:
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',parent)
    bp=tools.create_asset('GA_BFF_OfferRice',BASE+'/Blueprints',unreal.Blueprint,factory)
graph=unreal.find_object(bp,'EventGraph');assert graph
# The whole event graph is authored here. Imported nodes are recreated by name.
for name in ('OfferActivate','OfferDispatch','OfferEnd','OfferEvent'):
    old=unreal.find_object(graph,name)
    if old:remove_node(bp,old)
def pin(name,output=False,category='exec'):
    return 'CustomProperties Pin (PinId='+uuid.uuid4().hex.upper()+',PinName="'+name+'",'+('Direction="EGPD_Output",' if output else '')+'PinType.PinCategory="'+category+'",)'
def block(cls,name,props,pins):
    return '\n'.join(['Begin Object Class=/Script/BlueprintGraph.'+cls+' Name="'+name+'"',props,'NodeGuid='+uuid.uuid4().hex.upper(),*pins,'End Object'])
text='\n'.join([
    block('K2Node_Event','OfferActivate','EventReference=(MemberParent="/Script/CoreUObject.Class\'/Script/GameplayAbilities.GameplayAbility\'",MemberName="K2_ActivateAbility")\nbOverrideFunction=True',[pin('then',True)]),
    block('K2Node_CallFunction','OfferEnd','FunctionReference=(MemberParent="/Script/CoreUObject.Class\'/Script/GameplayAbilities.GameplayAbility\'",MemberName="K2_EndAbility",bSelfContext=True)',[pin('execute'),pin('then',True)]),
])
import_nodes(graph,text)
nodes={n:unreal.find_object(graph,n) for n in ('OfferActivate','OfferDispatch','OfferEnd')}
connect_nodes(nodes['OfferActivate'],'then',nodes['OfferEnd'],'execute')
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert bp.generated_class()
assert unreal.find_object(bp.generated_class(),'K2_ActivateAbility')
cdo=unreal.get_default_object(bp.generated_class())
# Input classification observed on the game's consume ability CDO. Reuse only
# the native input asset; do not load/copy the consume Blueprint implementation.
set_properties(cdo,'InputAction="/Game/Gameplay/Input/IA_ActivateToolPrimary.IA_ActivateToolPrimary"\nActivationPolicy=OnInputTriggered\nPriority=0')
copied={'InputAction':'/Game/Gameplay/Input/IA_ActivateToolPrimary','ActivationPolicy':'OnInputTriggered'}
set_properties(cdo,'AbilityInfoData=(TextInputOverride=INVTEXT("Offer Rice / 喂大肥鱼"),TextOverrideType=None)')
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
serving=unreal.load_asset(BASE+'/Blueprints/BP_BFF_RiceServing')
if not serving:
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.StaticMeshActor)
    serving=tools.create_asset('BP_BFF_RiceServing',BASE+'/Blueprints',unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.compile_blueprint(serving)
sc=unreal.get_default_object(serving.generated_class()).get_editor_property('static_mesh_component')
mesh=unreal.load_asset(BASE+'/Meshes/SM_BFF_CookedRice');assert mesh
sc.set_static_mesh(mesh);sc.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
sc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
for index,slot in enumerate(mesh.get_editor_property('static_materials')):sc.set_material(index,mesh.get_material(index))
assert unreal.EditorAssetLibrary.save_loaded_asset(serving,False)
item=unreal.load_asset(BASE+'/Data/DA_BFF_CookedRice_ItemType');assert item
set_properties(item,'Abilities(0)="'+bp.generated_class().get_path_name()+'"\nTunableData=()\nbUseFromInventory=True')
item.set_editor_property('ItemDescription',unreal.Text('Offer this rice to attract a hungry Big Fat Fish. / 拿出大白饭，吸引一只饥饿的大肥鱼来抢饭。'))
assert unreal.EditorAssetLibrary.save_loaded_asset(item,False)
(ROOT/'Logs/rice/use_ability_report.json').write_text(json.dumps({'status':'built_pending_game_test','class':bp.generated_class().get_path_name(),'copied_native_input':copied,'event':'K2_ActivateAbility (filtered to GA_BFF_OfferRice_C)'},indent=2),encoding='utf8')
print('RICE_OFFER_ABILITY_READY',flush=True)
