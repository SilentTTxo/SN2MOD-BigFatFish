"""Inspect native meal recipes and current rice material connections."""
import json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Logs/rice/cooking_probe';OUT.mkdir(parents=True,exist_ok=True)
paths=[
 '/Game/Data/CraftingRecipes/Fabricator/DA_CherimoyaChutney_Recipe',
 '/Game/Data/ItemType/DA_CherimoyaChutney_ItemType',
 '/Game/Data/ItemType/DA_Water_ItemType',
 '/Game/Data/CraftingRecipes/Categories/Fabricator/DA_SustenanceMeals',
 '/BigFatFishRice/Materials/M_RiceStem','/BigFatFishRice/Materials/M_RiceLeaf',
 '/BigFatFishRice/Materials/M_RiceGrain',
]
report={}
for path in paths:
 obj=unreal.load_asset(path)
 if not obj:report[path]='missing';continue
 name=obj.get_name();task=unreal.AssetExportTask();task.object=obj
 task.filename=str(OUT/(name+'.copy'));task.automated=True;task.prompt=False
 task.replace_identical=True;task.exporter=unreal.ObjectExporterT3D()
 report[path]={'class':obj.get_class().get_path_name(),'exported':unreal.Exporter.run_asset_export_task(task)}
 if isinstance(obj,unreal.Material):
  connected=unreal.MaterialEditingLibrary.get_material_property_input_node(obj,unreal.MaterialProperty.MP_BASE_COLOR)
  report[path]['base_color_node']=str(connected)
  if connected:
   try:report[path]['constant']=str(connected.get_editor_property('constant'))
   except Exception as e:report[path]['error']=str(e)
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('RICE_COOKING_PROBE',json.dumps(report),flush=True)
