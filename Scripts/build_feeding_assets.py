"""Import the authored grab/eat clip and place a montage slot before gaze."""
import sys,uuid,json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Scripts'))
from editor_graph_import import import_nodes,remove_node,connect_nodes
BASE='/Game/Mods/BigFatFish'
mesh=unreal.load_asset(BASE+'/Character/SK_BigFatFish');assert mesh
tools=unreal.AssetToolsHelpers.get_asset_tools()
task=unreal.AssetImportTask();task.filename=str(ROOT/'SourceAssets/Export/BigFatFish_GrabEat.fbx')
task.destination_path=BASE+'/Character';task.destination_name='AN_BigFatFish_GrabEat'
task.automated=True;task.replace_existing=True;task.save=True
opt=unreal.FbxImportUI();opt.import_mesh=False;opt.import_animations=True;opt.import_materials=False;opt.import_textures=False
opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION
opt.skeleton=mesh.get_editor_property('skeleton');task.options=opt;task.factory=unreal.FbxFactory()
tools.import_asset_tasks([task])
animation=unreal.load_asset(BASE+'/Character/AN_BigFatFish_GrabEat')
assert isinstance(animation,unreal.AnimSequence),str(task.imported_object_paths)
assert abs(animation.get_editor_property('sequence_length')-4.8)<.05
bp=unreal.load_asset(BASE+'/Character/ABP_BigFatFish_Gaze');assert bp
graph=next(g for g in bp.get_animation_graphs() if g.get_name()=='AnimGraph')
for name in ('FeedSlot','LocalToComponent'):
    obj=unreal.find_object(graph,name)
    if obj:remove_node(bp,obj)
def pin(name,output=False,component=False):
    typ='ComponentSpacePoseLink' if component else 'PoseLink'
    return 'CustomProperties Pin (PinId='+uuid.uuid4().hex.upper()+',PinName="'+name+'",'+('Direction="EGPD_Output",' if output else '')+'PinType.PinCategory="struct",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct\'/Script/Engine.'+typ+'\'",)'
blocks=[]
for cls,name,props,pins in [
    ('AnimGraphNode_Slot','FeedSlot','Node=(SlotName="DefaultSlot",bAlwaysUpdateSourcePose=True)',[pin('Source'),pin('Pose',True)]),
    ('AnimGraphNode_LocalToComponentSpace','LocalToComponent','',[pin('LocalPose'),pin('ComponentPose',True,True)]),
]:
    blocks.append('\n'.join(['Begin Object Class=/Script/AnimGraph.'+cls+' Name="'+name+'"',props,'NodeGuid='+uuid.uuid4().hex.upper(),*pins,'End Object']))
import_nodes(graph,'\n'.join(blocks))
nodes={n:unreal.find_object(graph,n) for n in ('SwimSequence','FeedSlot','LocalToComponent','NeckLookAt')}
connect_nodes(nodes['SwimSequence'],'Pose',nodes['FeedSlot'],'Source')
connect_nodes(nodes['FeedSlot'],'Pose',nodes['LocalToComponent'],'LocalPose')
connect_nodes(nodes['LocalToComponent'],'ComponentPose',nodes['NeckLookAt'],'ComponentPose')
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert bp.generated_class()
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
(ROOT/'Logs/feeding_asset_validation.json').write_text(json.dumps({'status':'built; runtime visual test pending','animation':animation.get_path_name(),'duration_seconds':animation.get_editor_property('sequence_length'),'slot':'DefaultSlot'},indent=2),encoding='utf8')
print('FEEDING_ASSETS_READY',flush=True)
