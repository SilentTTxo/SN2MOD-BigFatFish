import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/WhaleGirl_Swim_Preview.blend'))
r={'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions],'objects':[]}
for o in bpy.data.objects:
 if o.type not in ['MESH','ARMATURE']:continue
 entry={'name':o.name,'type':o.type,'dimensions':list(o.dimensions)}
 if o.type=='MESH':
  entry['materials']=[s.material.name if s.material else None for s in o.material_slots]
  entry['shapes']=[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []
  if o.data.shape_keys and 'TiePen' in o.data.shape_keys.key_blocks:
   a=o.data.shape_keys.key_blocks[0];b=o.data.shape_keys.key_blocks['TiePen'];entry['TiePen_deltas']={'changed':sum((x.co-y.co).length>1e-6 for x,y in zip(a.data,b.data)),'maximum':max((x.co-y.co).length for x,y in zip(a.data,b.data))}
 else:entry['bones']=[b.name for b in o.data.bones]
 r['objects'].append(entry)
(R/'Logs/model_inventory.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
