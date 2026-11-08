"""Evaluate the saved graph with tracking off/on, checking actual local bones."""
import json
import math
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[1]
BASE = "/Game/Mods/BigFatFish/Character/"
mesh = unreal.load_asset(BASE + "SK_BigFatFish")
bp = unreal.load_asset(BASE + "ABP_BigFatFish_Gaze")
skeleton = mesh.get_editor_property("skeleton")
reference = unreal.AnimPoseExtensions.get_reference_pose(skeleton)
# Evaluate a real registered skeletal component; the pose-extension helper
# requires an InputPose AnimBP and cannot evaluate this SequencePlayer graph.
import ctypes as C
editor_actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=editor_actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector())
component=actor.get_editor_property("skeletal_mesh_component")
component.set_skeletal_mesh_asset(mesh)
component.set_anim_instance_class(bp.generated_class())
component.set_editor_property("update_animation_in_editor",True)
anim=component.get_anim_instance()
assert anim
binaries=ROOT/"Engine/SN2-Engine-V4/Engine/Binaries/Win64"
core=C.WinDLL(str(binaries/"UnrealEditor-CoreUObject.dll"))
find=getattr(core,"?StaticFindObject@@YAPEAVUObject@@PEAVUClass@@PEAV1@PEB_W_N@Z")
find.argtypes=[C.c_void_p,C.c_void_p,C.c_wchar_p,C.c_bool];find.restype=C.c_void_p
pointer=find(None,None,component.get_path_name(),False)
engine=C.WinDLL(str(binaries/"UnrealEditor-Engine.dll"))
tick=getattr(engine,"?TickAnimation@USkeletalMeshComponent@@QEAAXM_N@Z")
tick.argtypes=[C.c_void_p,C.c_float,C.c_bool];tick.restype=None
refresh=getattr(engine,"?RefreshBoneTransforms@USkeletalMeshComponent@@UEAAXPEAUFActorComponentTickFunction@@@Z")
refresh.argtypes=[C.c_void_p,C.c_void_p];refresh.restype=None
names=[str(n) for n in unreal.AnimPoseExtensions.get_bone_names(reference)]

def evaluate(neck,head,eye,target):
    for name,value in {"NeckAlpha":neck,"HeadAlpha":head,"EyeAlpha":eye,"GazeTargetWorld":unreal.Vector(*target)}.items():
        anim.set_editor_property(name,value)
    tick(pointer,0.0,False)
    refresh(pointer,None)
    result={}
    for bone in names:
        transform=component.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT)
        parent=component.get_parent_bone(bone)
        if str(parent)!="None":
            pt=component.get_socket_transform(parent,unreal.RelativeTransformSpace.RTS_COMPONENT)
            transform=unreal.MathLibrary.make_relative_transform(transform,pt)
        result[bone]=transform.rotation
    return result

def rotation(pose,bone):return pose[bone]

def difference(a, b):
    dot = abs(a.x*b.x + a.y*b.y + a.z*b.z + a.w*b.w)
    return math.degrees(2*math.acos(min(1, dot)))

off = evaluate(0, 0, 0, (600, 400, 130))
on = evaluate(0.6, 1, 1, (600, 400, 130))
names = [str(n) for n in unreal.AnimPoseExtensions.get_bone_names(reference)]
angles = {bone: difference(rotation(off, bone), rotation(on, bone)) for bone in names}
report = {"local_rotation_change_degrees": angles, "runtime_variables": ["GazeTargetWorld", "NeckAlpha", "HeadAlpha", "EyeAlpha"]}
(ROOT / "Logs/gaze_pose_validation.json").write_text(json.dumps(report, indent=2), encoding="utf8")
for bone in ["neck", "head", "eye_L", "eye_R"]:
    assert angles[bone] > 0.2, (bone, angles[bone])
assert max(value for bone, value in angles.items() if bone not in ["neck", "head", "eye_L", "eye_R"]) < 0.1, "Tracking altered unrelated local bones"
limits={}
for target in [(0,1000,100),(0,-1000,100),(500,0,1000),(500,0,-1000),(-1000,100,100)]:
    neutral=evaluate(0,0,0,target)
    eyes=evaluate(0,0,1,target)
    changes={bone:difference(neutral[bone],eyes[bone]) for bone in ['eye_L','eye_R']}
    limits[str(target)]=changes
    assert max(changes.values())<=8.1,('Eye rotation exceeded safe cone',target,changes)
report['eye_extreme_rotation_limits']=limits
editor_actors.destroy_actor(actor)
report["status"] = "PASS: real head, neck and eye rotations; unrelated local bone rotations unchanged"
(ROOT / "Logs/gaze_pose_validation.json").write_text(json.dumps(report, indent=2), encoding="utf8")
unreal.log(report["status"])
