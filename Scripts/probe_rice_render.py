import unreal,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report={}
for name in ['SM_BFF_RiceStalk','SM_BFF_RicePanicle','SM_BFF_CookedRice']:
 mesh=unreal.load_asset('/BigFatFishRice/Meshes/'+name)
 report[name]={'bounds':str(mesh.get_bounds()),'materials':[(str(s.get_editor_property('material_slot_name')),str(s.get_editor_property('imported_material_slot_name')),str(s.get_editor_property('material_interface'))) for s in mesh.get_editor_property('static_materials')]}
 task=unreal.AssetExportTask();task.object=mesh;task.filename=str(ROOT/'Logs/rice'/ (name+'.obj'));task.automated=True;task.prompt=False;task.replace_identical=True
 try:unreal.Exporter.run_asset_export_task(task)
 except Exception as e:report[name]['export_error']=str(e)
for name in ['M_RiceLeaf','M_RiceGrain']:
 mat=unreal.load_asset('/BigFatFishRice/Materials/'+name)
 report[name]={'api':[n for n in dir(unreal.MaterialEditingLibrary) if 'input' in n or 'property' in n]}
for name in ['BP_BFF_RiceGrain','BP_BFF_RiceHarvest','BP_BFF_CookedRice','BP_BFF_RicePlant']:
 bp=unreal.load_asset('/BigFatFishRice/Blueprints/'+name)
 sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
 comps=[]
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if isinstance(o,unreal.StaticMeshComponent):comps.append({'name':o.get_name(),'mesh':str(o.get_editor_property('static_mesh')),'overrides':str(o.get_editor_property('override_materials'))})
 report[name]=comps
(ROOT/'Logs/rice/render_probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
