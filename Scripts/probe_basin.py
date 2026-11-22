import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
o=bpy.data.objects['hair'];a=o.data.shape_keys.key_blocks['Basis'];b=o.data.shape_keys.key_blocks['TiePen'];r={}
for slot,m in enumerate(o.data.materials):
 ids={i for p in o.data.polygons if p.material_index==slot for i in p.vertices}
 r[m.name]={'vertices':len(ids),'changed':sum((a.data[i].co-b.data[i].co).length>1e-6 for i in ids)}
 for key,shape in [('basis',a),('basin',b)]:
  r[m.name][key]=[[min(shape.data[i].co[j] for i in ids),max(shape.data[i].co[j] for i in ids)] for j in range(3)]
(R/'Logs/basin_geometry_probe.json').write_text(json.dumps(r,indent=2),encoding='utf8')
