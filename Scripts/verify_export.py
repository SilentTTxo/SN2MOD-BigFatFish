import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
(R/'Logs').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
materials=[]
for m in bpy.data.materials:
 if not m.use_nodes: continue
 imgs=[]
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image and n.image.name not in imgs: imgs.append(n.image.name)
 if imgs: materials.append({'material':m.name,'images':imgs,'double_sided':not m.use_backface_culling})
p=R/'SourceAssets/asset_manifest.json';d=json.loads(p.read_text(encoding='utf-8'));assert d['materials']==materials
print('MATERIALS',json.dumps(materials,ensure_ascii=False),flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'SourceAssets/Export/WhaleGirl_Swim.fbx'))
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];meshes=[o for o in bpy.data.objects if o.type=='MESH']
assert len(rigs)==1 and len(meshes)==6
assert len(rigs[0].data.bones)==146
assert len(bpy.data.actions)==1
assert len([im for im in bpy.data.images if im.source=='FILE'])>=6
assert all(im.has_data for im in bpy.data.images if im.source=='FILE')
report={'rigs':len(rigs),'bones':len(rigs[0].data.bones),'meshes':len(meshes),'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions],'loaded_images':[(im.name,list(im.size)) for im in bpy.data.images if im.source=='FILE']}
(R/'Logs/fbx_roundtrip.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('FBX_ROUNDTRIP_OK',json.dumps(report,ensure_ascii=False),flush=True)
