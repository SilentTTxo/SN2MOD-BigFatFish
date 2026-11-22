"""Bake a reach/grab/eat arm gesture over the existing retargeted swim pose."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
rig=bpy.data.objects['WhaleGirl_Rig'];scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
source=rig.animation_data.action;assert source
constraints=[];targets=[]
for side in ('L','R'):
    bone=rig.pose.bones['lower_arm.'+side]
    target=bpy.data.objects.new('BFF_FoodHand_'+side,None);bpy.context.collection.objects.link(target)
    constraint=bone.constraints.new('IK');constraint.target=target;constraint.chain_count=2;constraint.use_tail=True
    constraints.append((bone,constraint));targets.append(target)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
samples=[]
for frame in range(1,146):
    t=(frame-1)/30
    scene.frame_set((frame-1)%60+1)
    for bone,constraint in constraints:constraint.influence=0
    bpy.context.view_layer.update()
    head=rig.pose.bones['head'].matrix.translation.copy()
    neck=rig.pose.bones['neck'].matrix.translation.copy()
    forward=(head-neck).normalized();right=forward.cross(Vector((0,0,1)))
    if right.length<.1:right=Vector((1,0,0))
    right.normalize();up=right.cross(forward).normalized()
    amount=smooth((t-.25)/.8)*(1-smooth((t-4.05)/.75))
    reach=.21-.12*smooth((t-1.6)/.5)
    for i,((bone,constraint),target) in enumerate(zip(constraints,targets)):
        target.location=rig.matrix_world@(head+forward*reach-up*.12+right*((-1 if i==0 else 1)*.095))
        constraint.influence=amount
    bpy.context.view_layer.update()
    evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    poses={}
    for bone in evaluated.pose.bones:
        kwargs={}
        if bone.parent:kwargs={'parent_matrix':bone.parent.matrix,'parent_matrix_local':bone.parent.bone.matrix_local}
        basis=bone.bone.convert_local_to_pose(bone.matrix,bone.bone.matrix_local,invert=True,**kwargs)
        loc,rot,scale=basis.decompose();poses[bone.name]=(loc.copy(),rot.copy(),scale.copy())
    samples.append(poses)
for bone,constraint in constraints:bone.constraints.remove(constraint)
rig.animation_data.action=bpy.data.actions.new('BFF_GrabEat_4p8s')
for frame,poses in enumerate(samples,1):
    for name,(loc,rot,scale) in poses.items():
        bone=rig.pose.bones[name];bone.rotation_mode='QUATERNION';bone.location=loc;bone.rotation_quaternion=rot;bone.scale=scale
        for channel in ('location','rotation_quaternion','scale'):bone.keyframe_insert(channel,frame=frame,group=name)
scene.frame_start=1;scene.frame_end=145;scene.render.fps=30
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
out=ROOT/'SourceAssets/Export/BigFatFish_GrabEat.fbx'
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'ARMATURE'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_step=1,bake_anim_simplify_factor=0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Logs/BigFatFish_Feeding_Preview.blend'))
(ROOT/'Logs/feeding_animation_source.json').write_text(json.dumps({'duration_seconds':4.8,'frames':145,'fps':30,'source':'Existing Quaternius swim retarget plus newly authored arm IK reach/grab/eat gesture','hands':['hand.L','hand.R'],'fbx':str(out)},indent=2),encoding='utf8')
print('FEEDING_ANIMATION_EXPORTED',flush=True)
