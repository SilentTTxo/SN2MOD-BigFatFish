import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
report={'api':str(unreal.AnimPoseExtensions.get_anim_pose_at_time.__doc__),'options':str(unreal.AnimPoseEvaluationOptions.__doc__),'samples':{}}
options=unreal.AnimPoseEvaluationOptions()
for name in ['AN_BigFatFish_Swim','AN_BigFatFish_GrabEat']:
 a=unreal.load_asset('/Game/Mods/BigFatFish/Character/'+name)
 samples=[]
 for t in [0.,.6,1.2,1.6,2.5,3.9,4.5]:
  pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(a,t%a.get_editor_property('sequence_length'),options)
  sample={'time':t}
  for bone in ['head','neck','hand_L','hand_R','lower_arm_L','lower_arm_R']:
   transform=unreal.AnimPoseExtensions.get_bone_pose(pose,bone,unreal.AnimPoseSpaces.WORLD)
   sample[bone]=list(transform.translation.to_tuple())
  samples.append(sample)
 report['samples'][name]=samples
(R/'Logs/feeding_pose_probe.json').write_text(json.dumps(report,indent=2),encoding='utf8')
