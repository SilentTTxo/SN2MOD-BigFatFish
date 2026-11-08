"""Create a standard cooked AnimBP: swim -> neck/head/eye look-at -> output."""
import json
import math
import sys
import uuid
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from editor_graph_import import import_nodes, remove_node, connect_nodes
BASE = "/Game/Mods/BigFatFish"
report = {}
mesh = unreal.load_asset(BASE + "/Character/SK_BigFatFish")
skeleton = mesh.get_editor_property("skeleton")
reference=unreal.AnimPoseExtensions.get_reference_pose(skeleton)
bone_names=[str(n) for n in unreal.AnimPoseExtensions.get_bone_names(reference)]
report["gaze_bone_candidates"]=[n for n in bone_names if any(s in n.lower() for s in ["head","eye","neck"])]
bone_map={}
for source in ["neck","head","eye.L","eye.R"]:
    candidates=[n for n in bone_names if n.replace("_", ".").replace("-", ".")==source]
    assert len(candidates)==1,(source,candidates,report["gaze_bone_candidates"])
    bone_map[source]=candidates[0]
report["bone_map"]=bone_map
axes={}
for source,bone in bone_map.items():
    transform=unreal.AnimPoseExtensions.get_bone_pose(reference,bone,unreal.AnimPoseSpaces.WORLD)
    q=transform.rotation
    aim=(1-2*(q.y*q.y+q.z*q.z),2*(q.x*q.y-q.w*q.z),2*(q.x*q.z+q.w*q.y))
    up=(2*(q.x*q.z-q.w*q.y),2*(q.y*q.z+q.w*q.x),1-2*(q.x*q.x+q.y*q.y))
    axes[source]=(aim,up)
report["axes"]=axes
def look_node(source,clamp):
    aim,up=axes[source]
    def vector(v):return '(X=%.9f,Y=%.9f,Z=%.9f)'%v
    return 'Node=(BoneToModify=(BoneName="'+bone_map[source]+'"),LookAt_Axis=(Axis='+vector(aim)+',bInLocalSpace=True),LookUp_Axis=(Axis='+vector(up)+',bInLocalSpace=True),bUseLookUpAxis=True,LookAtClamp='+str(clamp)+',Alpha=0,InterpolationTime=0)'
factory = unreal.AnimBlueprintFactory()
factory.set_editor_property("target_skeleton", skeleton)
bp = unreal.load_asset(BASE + "/Character/ABP_BigFatFish_Gaze")
if not bp:
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_BigFatFish_Gaze", BASE + "/Character", unreal.AnimBlueprint, factory)
variable_types={"GazeTargetWorld":unreal.BlueprintEditorLibrary.get_struct_type(unreal.Vector.static_struct())}
float_type=unreal.BlueprintEditorLibrary.get_basic_type_by_name("real")

for name in ["NeckAlpha","HeadAlpha","EyeAlpha"]: variable_types[name]=float_type
for name,pin_type in variable_types.items():
    # The graph is rebuilt on each run; variables may already exist on a saved BP.
    unreal.BlueprintEditorLibrary.add_member_variable(bp,name,pin_type)
    unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,name,True)
graphs = bp.get_animation_graphs()
report["graphs"] = [repr(g) for g in graphs]
graph = next(g for g in graphs if g.get_name() == "AnimGraph")
report["reference_pose_api"] = unreal.AnimPoseExtensions.get_reference_pose.__doc__
report["bone_pose_api"] = unreal.AnimPoseExtensions.get_bone_pose.__doc__
report["evaluate_api"] = unreal.AnimPoseExtensions.evaluate_animation_blueprint_with_input_pose.__doc__
nodes = bp.get_nodes_of_class(unreal.AnimGraphNode_Base)
report["graph_nodes_before"] = [repr(n) for n in nodes]
(ROOT / "Logs/gaze_animation_build.json").write_text(json.dumps(report,indent=2),encoding="utf8")
# Keep the factory's root (root nodes cannot be pasted). Rebuild the input chain.
root_node=next(n for n in nodes if isinstance(n,unreal.AnimGraphNode_Root))
for node in nodes:
    if node != root_node:
        remove_node(bp, node)
for variable in variable_types:
    old=unreal.find_object(graph,"Get"+variable)
    if old: remove_node(bp,old)
specs = [
    ("AnimGraphNode_SequencePlayer", "SwimSequence", "Node=(Sequence=\"/Script/Engine.AnimSequence'" + BASE + "/Character/AN_BigFatFish_Swim.AN_BigFatFish_Swim'\",bLoopAnimation=True)", None, "Pose", False),
    ("AnimGraphNode_LocalToComponentSpace", "LocalToComponent", "", "LocalPose", "ComponentPose", True),
    ("AnimGraphNode_LookAt", "NeckLookAt", look_node("neck",15), "ComponentPose", "Pose", True),
    ("AnimGraphNode_LookAt", "HeadLookAt", look_node("head",50), "ComponentPose", "Pose", True),
    ("AnimGraphNode_LookAt", "LeftEyeLookAt", look_node("eye.L",8), "ComponentPose", "Pose", True),
    ("AnimGraphNode_LookAt", "RightEyeLookAt", look_node("eye.R",8), "ComponentPose", "Pose", True),
    ("AnimGraphNode_ComponentToLocalSpace", "ComponentToLocal", "", "ComponentPose", "Pose", False),
    ("AnimGraphNode_Root", "AnimGraphNode_Root_Gaze", "", "Result", None, False),
]
ids = [{"in": uuid.uuid4().hex.upper(), "out":uuid.uuid4().hex.upper()} for _ in specs]
blocks=[]
for i,(cls,name,props,input_name,output_name,component_output) in enumerate(specs[:-1]):
    lines=[f'Begin Object Class=/Script/AnimGraph.{cls} Name="{name}"',props,
           f'NodePosX={i*220}', 'NodePosY=0', f'NodeGuid={uuid.uuid4().hex.upper()}']
    for output,pin_name in [(False,input_name),(True,output_name)]:
        if pin_name is None: continue
        key="out" if output else "in"
        component = component_output if output else cls not in ["AnimGraphNode_Root", "AnimGraphNode_LocalToComponentSpace"]
        pose_type="ComponentSpacePoseLink" if component else "PoseLink"
        neighbor=i+1 if output else i-1
        link_key="in" if output else "out"
        pin=[f'PinId={ids[i][key]}',f'PinName="{pin_name}"',f'Direction="EGPD_{"Output" if output else "Input"}"',
             'PinType.PinCategory="struct"',f'PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct\'/Script/Engine.{pose_type}\'"',
             'PersistentGuid=00000000000000000000000000000000', 'bHidden=False', 'bNotConnectable=False', 'bDefaultValueIsReadOnly=False', 'bDefaultValueIsIgnored=False', 'bOrphanedPin=False']
        lines.append('CustomProperties Pin ('+','.join(pin)+',)')
    lines.append('End Object');blocks.append('\n'.join(s for s in lines if s))
# Expose the standard LookAt location/alpha inputs and feed public AnimBP members.
for i in range(2,6):
    extra=[]
    for prop in ["LookAtLocation","Alpha"]:
        typ='PinType.PinCategory="struct",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct\'/Script/CoreUObject.Vector\'"' if prop=="LookAtLocation" else 'PinType.PinCategory="real",PinType.PinSubCategory="float"'
        extra.append('CustomProperties Pin (PinId='+uuid.uuid4().hex.upper()+',PinName="'+prop+'",'+typ+',)')
    optional='\n'.join('ShowPinForProperties('+str(j)+')=(PropertyName="'+prop+'",bShowPin=True,bCanToggleVisibility=True)' for j,prop in enumerate(["LookAtLocation","Alpha"]))
    blocks[i]=blocks[i].replace('End Object',optional+'\n'+'\n'.join(extra)+'\nEnd Object')
for name in variable_types:
    typ='PinType.PinCategory="struct",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct\'/Script/CoreUObject.Vector\'"' if name=="GazeTargetWorld" else 'PinType.PinCategory="real",PinType.PinSubCategory="float"'
    blocks.append('\n'.join(['Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="Get'+name+'"',
        'VariableReference=(MemberName="'+name+'",bSelfContext=True)', 'NodeGuid='+uuid.uuid4().hex.upper(),
        'CustomProperties Pin (PinId='+uuid.uuid4().hex.upper()+',PinName="'+name+'",Direction="EGPD_Output",'+typ+',)', 'End Object']))
text='\n'.join(blocks)
(ROOT / "Logs/gaze_graph.t3d").write_text(text,encoding="utf8")
import_nodes(graph,text)
report["nodes_after"]=[repr(n) for n in bp.get_nodes_of_class(unreal.AnimGraphNode_Base)]
node_map={n.get_name():n for n in bp.get_nodes_of_class(unreal.AnimGraphNode_Base)}
assert len(node_map)==8, report["nodes_after"]
for i in range(len(specs)-1):
    source=node_map[specs[i][1]]
    destination=root_node if i==len(specs)-2 else node_map[specs[i+1][1]]
    connect_nodes(source,specs[i][4],destination,specs[i+1][3])
(ROOT / "Logs/gaze_animation_build.json").write_text(json.dumps(report,indent=2),encoding="utf8")
for node_name,alpha in [("NeckLookAt","NeckAlpha"),("HeadLookAt","HeadAlpha"),("LeftEyeLookAt","EyeAlpha"),("RightEyeLookAt","EyeAlpha")]:
    for variable,pin in [("GazeTargetWorld","LookAtLocation"),(alpha,"Alpha")]:
        source=unreal.find_object(graph,"Get"+variable)
        assert source,variable
        connect_nodes(source,variable,node_map[node_name],pin)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
report["compiled_class"]=repr(bp.generated_class())
cdo=unreal.get_default_object(bp.generated_class())
report["runtime_variables"]={name:repr(cdo.get_editor_property(name)) for name in variable_types}
for name in ["NeckAlpha","HeadAlpha","EyeAlpha"]: cdo.set_editor_property(name,0.0)
# Persist only after the complete graph and all runtime bindings are validated.
unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
actor_cls=unreal.EditorAssetLibrary.load_blueprint_class(BASE+"/BP_BigFatFish")
component=unreal.get_default_object(actor_cls).get_editor_property("skeletal_mesh_component")
component.set_editor_property("animation_mode",unreal.AnimationMode.ANIMATION_BLUEPRINT)
component.set_editor_property("anim_class",bp.generated_class())
actor_bp=unreal.load_asset(BASE+"/BP_BigFatFish")
unreal.BlueprintEditorLibrary.compile_blueprint(actor_bp)
unreal.EditorAssetLibrary.save_loaded_asset(actor_bp,only_if_is_dirty=False)
(ROOT / "Logs/gaze_animation_build.json").write_text(json.dumps(report,indent=2),encoding="utf8")
unreal.log("GAZE_GRAPH_PROBE_COMPLETE")
