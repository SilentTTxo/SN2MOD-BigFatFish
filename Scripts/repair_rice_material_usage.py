import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
fixed=[]
for name in ('RiceStem','RiceLeaf','RiceGrain','RiceGrainLight','RiceBowl','CookedRice','CookedRiceShade'):
 path='/BigFatFishRice/Materials/M_'+name
 m=unreal.load_asset(path)
 assert isinstance(m,unreal.Material),path
 m.set_editor_property('used_with_nanite',True)
 unreal.MaterialEditingLibrary.recompile_material(m)
 assert unreal.EditorAssetLibrary.save_loaded_asset(m,False)
 fixed.append(m.get_path_name())
(R/'Logs/rice/nanite_usage_fix.json').write_text(json.dumps(fixed,indent=2),encoding='utf8')
