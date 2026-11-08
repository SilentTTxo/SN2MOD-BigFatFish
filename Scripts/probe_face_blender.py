import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
report={"meshes":{},"bones":[]}
for obj in bpy.data.objects:
    if obj.type=='MESH':
        shapes=[]
        if obj.data.shape_keys:
            basis=obj.data.shape_keys.key_blocks[0]
            for k in obj.data.shape_keys.key_blocks:
                changed=sum((a.co-b.co).length>0.000001 for a,b in zip(k.data,basis.data))
                shapes.append({"name":k.name,"vertices_changed":changed})
        report['meshes'][obj.name]={"vertices":len(obj.data.vertices),"shapes":shapes}
    if obj.type=='ARMATURE': report['bones']=[b.name for b in obj.data.bones if any(x in b.name.lower() for x in ['jaw','mouth','lip','eye','head'])]
(ROOT/'Logs/face_source_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FACE_SOURCE_PROBE_COMPLETE')
