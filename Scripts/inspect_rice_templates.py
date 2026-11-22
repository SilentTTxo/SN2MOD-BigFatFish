"""Inspect cooked native farming templates without modifying their packages."""
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"Logs/rice/templates";out.mkdir(parents=True,exist_ok=True)
report={}
paths=[
    "/Game/Data/ItemType/DA_CherimoyaRotsacFruit_ItemType",
    "/Game/Data/ItemType/FarmablePlants/DA_Farmable_CherimoyaRotsac_ItemType",
    "/Game/Data/BaseBuilding/BuilderActions/FarmablePlants/DA_Farmable_CherimoyaRotsac_ConstructData",
    "/Game/Data/CraftingRecipes/Builder/FarmablePlants/DA_Farmable_CherimoyaRotsac_Recipe",
    "/Game/Blueprints/BaseBuilding/FarmablePlants/BP_FarmableCherimoyaRotsac",
    "/Game/Prototyping/Resources/CherimoyaRotsac/BP_CherimoyaRotsac_Fruit",
    "/Game/Developers/sewlek/Farming/DA_TestSeedData",
]
def text_export(obj,name):
    task=unreal.AssetExportTask();task.object=obj;task.filename=str(out/(name+".copy"))
    task.automated=True;task.prompt=False;task.replace_identical=True
    task.exporter=unreal.ObjectExporterT3D()
    return unreal.Exporter.run_asset_export_task(task)
for path in paths:
    entry={};report[path]=entry
    try:
        obj=unreal.load_asset(path)
        entry['loaded']=bool(obj)
        if not obj:
            cls=unreal.load_class(None,path+'.'+path.split('/')[-1]+'_C')
            entry['generated_class']=cls.get_path_name() if cls else None
            if cls:
                cdo=unreal.get_default_object(cls)
                entry['cdo_exported']=text_export(cdo,'CDO_'+path.split('/')[-1])
                entry['class_exported']=text_export(cls,'CLASS_'+path.split('/')[-1])
                props={}
                for name in ('root_component','static_mesh_component','plant_grower','seed_grower','save_component','asset_data_component','ability_system_data'):
                    try: props[name]=str(cdo.get_editor_property(name))
                    except Exception: pass
                entry['cdo_properties']=props
                print('RICE_CLASS_LOADED',path,entry['generated_class'],flush=True)
            (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
            continue
        entry['class']=obj.get_class().get_path_name()
        print('RICE_TEMPLATE_LOADED',path,entry['class'],flush=True)
        try: entry['exported']=text_export(obj,obj.get_name())
        except Exception as e: entry['export_error']=str(e)
        if isinstance(obj,unreal.Blueprint):
            cls=obj.generated_class();cdo=unreal.get_default_object(cls)
            entry['generated_class']=cls.get_path_name()
            try: entry['cdo_exported']=text_export(cdo,'CDO_'+obj.get_name())
            except Exception as e: entry['cdo_export_error']=str(e)
            props={}
            for name in ('root_component','static_mesh_component','plant_grower','seed_grower','save_component','asset_data_component','ability_system_data'):
                try: props[name]=str(cdo.get_editor_property(name))
                except Exception: pass
            entry['cdo_properties']=props
    except Exception as e:
        entry['error']=str(e)
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('RICE_TEMPLATES_COMPLETE',json.dumps(report),flush=True)
unreal.SystemLibrary.quit_editor()
