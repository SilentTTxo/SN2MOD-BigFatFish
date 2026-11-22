"""Extract the creator's TiePen basin and bake a seamless two-hand hold loop."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
hair=bpy.data.objects['hair'];shape=hair.data.shape_keys.key_blocks['TiePen']
polys=[p for p in hair.data.polygons if hair.data.materials[p.material_index].name=='TiePen']
indices=sorted({i for p in polys for i in p.vertices});remap={v:i for i,v in enumerate(indices)}
positions=[hair.matrix_world@shape.data[i].co for i in indices]
center=Vector(((min(v.x for v in positions)+max(v.x for v in positions))/2,
               (min(v.y for v in positions)+max(v.y for v in positions))/2,min(v.z for v in positions)))
mesh=bpy.data.meshes.new('BFF_OriginalBasin');mesh.from_pydata([v-center for v in positions],[],[[remap[i] for i in p.vertices] for p in polys]);mesh.update()
uv=mesh.uv_layers.new(name='UVMap')
for target,source in zip(mesh.polygons,polys):
 target.use_smooth=True
 for ti,si in zip(target.loop_indices,source.loop_indices):uv.data[ti].uv=hair.data.uv_layers.active.data[si].uv
obj=bpy.data.objects.new('SM_BFF_OriginalBasin',mesh);bpy.context.collection.objects.link(obj)
mesh.materials.append(bpy.data.materials['TiePen'])
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
out=R/'SourceAssets/Export/SM_BFF_OriginalBasin.fbx'
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='AUTO')
# The feeding author's IK setup already solves the same skeleton and scale.
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
rig=bpy.data.objects['WhaleGirl_Rig'];scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
constraints=[]
for side in ('L','R'):
 target=bpy.data.objects.new('BasinHand_'+side,None);bpy.context.collection.objects.link(target)
 bone=rig.pose.bones['lower_arm.'+side];ik=bone.constraints.new('IK');ik.target=target;ik.chain_count=2;ik.use_tail=True
 constraints.append((bone,ik,target))
samples=[]
for frame in range(61):
 scene.frame_set(frame%60+1)
 for _,ik,_ in constraints:ik.influence=0
 bpy.context.view_layer.update()
 head=rig.pose.bones['head'].matrix.translation.copy();neck=rig.pose.bones['neck'].matrix.translation.copy()
 forward=(head-neck).normalized();right=forward.cross(Vector((0,0,1)))
 if right.length<.1:right=Vector((1,0,0))
 right.normalize();up=right.cross(forward).normalized()
 for i,(_,ik,target) in enumerate(constraints):
  target.location=rig.matrix_world@(head+forward*.09-up*.12+right*((-1 if i==0 else 1)*.095));ik.influence=1
 bpy.context.view_layer.update();evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());poses={}
 for bone in evaluated.pose.bones:
  kwargs={}
  if bone.parent:kwargs={'parent_matrix':bone.parent.matrix,'parent_matrix_local':bone.parent.bone.matrix_local}
  basis=bone.bone.convert_local_to_pose(bone.matrix,bone.bone.matrix_local,invert=True,**kwargs)
  loc,rot,scale=basis.decompose();poses[bone.name]=(loc.copy(),rot.copy(),scale.copy())
 samples.append(poses)
for bone,ik,target in constraints:bone.constraints.remove(ik)
rig.animation_data.action=bpy.data.actions.new('BFF_HoldBasin_Loop')
for frame,poses in enumerate(samples,1):
 for name,(loc,rot,scale) in poses.items():
  b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.location=loc;b.rotation_quaternion=rot;b.scale=scale
  for channel in ('location','rotation_quaternion','scale'):b.keyframe_insert(channel,frame=frame,group=name)
scene.frame_start=1;scene.frame_end=61;scene.render.fps=30
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(R/'SourceAssets/Export/BigFatFish_HoldBasin.fbx'),use_selection=True,object_types={'ARMATURE'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_step=1,bake_anim_simplify_factor=0)
(R/'Logs/basin_export.json').write_text(json.dumps({'vertices':len(indices),'polygons':len(polys),'source_shape':'hair/TiePen','held_by':'Big Fat Fish','hold_seconds':2},indent=2),encoding='utf8')
print('BASIN_EXPORTED',flush=True)
