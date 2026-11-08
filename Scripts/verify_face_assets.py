"""Check imported face targets and their runtime skeletal-component API."""
import json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[1]
mesh=unreal.load_asset('/Game/Mods/BigFatFish/Character/SK_BigFatFish')
names=[str(n) for n in mesh.get_all_morph_target_names()]
bindings={}
for key,suffix in {'blink':'BFF_Blink','mouthOpen':'BFF_MouthOpen','mouthRound':'BFF_MouthRound'}.items():
    found=[n for n in names if n.endswith(suffix)]
    assert len(found)==1,(suffix,names)
    bindings[key]=found[0]
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector())
component=actor.get_editor_property('skeletal_mesh_component')
component.set_skeletal_mesh_asset(mesh)
for key,name in bindings.items():
    component.set_morph_target(name,0.7,True)
    assert abs(component.get_morph_target(name)-0.7)<0.001,name
    component.set_morph_target(name,0.0,True)
actors.destroy_actor(actor)
(ROOT/'Runtime/BigFatFish/Scripts/face_morphs.lua').write_text('return {\n'+''.join(f'    {key} = "{value}",\n' for key,value in bindings.items())+'}\n',encoding='utf8')
report={'status':'PASS: imported blink/mouth morphs and component set/get weights','all_morph_targets':names,'runtime_bindings':bindings}
(ROOT/'Logs/face_asset_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
unreal.log('FACE_ASSETS_VERIFIED '+json.dumps(report))
