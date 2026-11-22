import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
rig=bpy.data.objects['WhaleGirl_Rig'];sc=bpy.context.scene
meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=rig
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.frame_start=1;sc.frame_end=61;sc.frame_set(1)
out=R/'SourceAssets/Export';out.mkdir(exist_ok=True)
tex=out/'Textures';tex.mkdir(exist_ok=True)
textures=[]
for i,im in enumerate([im for im in bpy.data.images if im.type=='IMAGE' and im.size[0]>0 and im.name!='Render Result']):
 p=tex/f'T_WhaleGirl_{i:02}.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();textures.append({'image':im.name,'file':p.name,'width':im.size[0],'height':im.size[1]})

material_manifest=[]
# Convert VRM unlit graphs to basic textured Principled materials for FBX/UE import.
for mat in bpy.data.materials:
 if not mat.use_nodes: continue
 images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 if not images: continue
 material_manifest.append({'material':mat.name,'images':list(dict.fromkeys(im.name for im in images)),'double_sided':True})
 image=images[0];nodes=mat.node_tree.nodes;nodes.clear()
 output=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled');texture=nodes.new('ShaderNodeTexImage');texture.image=image
 shader.inputs['Roughness'].default_value=.8
 mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
 mat.node_tree.links.new(shader.outputs['BSDF'],output.inputs['Surface'])
# Keep only the authored face shapes used by the runtime; never alter the source blend.
face_map={"blink":"BFF_Blink","aa":"BFF_MouthOpen","ou":"BFF_MouthRound","happy":"BFF_Happy","sad":"BFF_Sad","angry":"BFF_Angry"}
face_shapes=[]
for obj in meshes:
 if not obj.data.shape_keys: continue
 if obj.name!='head.001':
  obj.shape_key_clear();continue
 for key in list(obj.data.shape_keys.key_blocks)[1:]:
  if key.name not in face_map: obj.shape_key_remove(key)
 for key in list(obj.data.shape_keys.key_blocks)[1:]:
  key.name=face_map[key.name];key.value=0;face_shapes.append(key.name)
assert set(face_shapes)==set(face_map.values()),face_shapes
# Export only the target rig, its meshes and one baked action. Keep the closing frame.
bpy.ops.export_scene.fbx(filepath=str(out/'WhaleGirl_Swim.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},use_mesh_modifiers=False,global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_step=1,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=False)
# GLB is an additional interchange/reference export; do not run the reference mannequin's actions.
bpy.ops.export_scene.gltf(filepath=str(out/'WhaleGirl_Swim.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True,export_force_sampling=True,export_cameras=False,export_lights=False)
manifest={'source_blend':'WhaleGirl_Swim_Preview.blend','animation':'WhaleGirl_Quaternius_Swim_Fwd','fps':30,'frame_start':1,'frame_end':61,'duration_seconds':2,'in_place':True,'skeleton_bones':len(rig.data.bones),'mesh_objects':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'model_author':'木子恶魔 / MZEM','animation_author':'Quaternius','animation_source':'Swim_Fwd_Loop / Universal Animation Library 1','animation_source_url':'https://quaternius.itch.io/universal-animation-library','preview_speed_relative_to_source':2/3,'textures':textures,'notes':['Tail heading corrected and a small secondary sway added.','VRM MToon and spring bones need UE-specific setup.','Model creator attribution required; follow the original creator terms. Publication with attribution clarified by the user on 2026-11-02.']}
manifest['interaction_animations']={'grab_eat_seconds':4.8,'hold_basin_loop_seconds':2,'basin':'Original creator TiePen morph extracted into an independent handheld prop'}
manifest['materials']=material_manifest
manifest['face_shapes']=face_shapes
manifest['files']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file()}
(R/'SourceAssets/asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('EXPORT_READY',json.dumps(manifest,ensure_ascii=False),flush=True)
