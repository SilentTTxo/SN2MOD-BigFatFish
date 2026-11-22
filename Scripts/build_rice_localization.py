"""Compile locres with UE's own localization commandlet, never patch asset bytes."""
import json,subprocess
from pathlib import Path
from rice_localization import CATALOG
R=Path(__file__).resolve().parents[1];settings=json.loads((R/'project.json').read_text(encoding='utf8'))
root=R/'RiceContent/BigFatFishRice/Content/Localization/BigFatFishRice';root.mkdir(parents=True,exist_ok=True)
manifest={'FormatVersion':1,'Namespace':'','Subnamespaces':[{'Namespace':'BigFatFishRice','Children':[{'Source':{'Text':en},'Keys':[{'Key':key,'Path':'BigFatFishRice'}]} for key,(en,zh) in CATALOG.items()]}]}
(root/'BigFatFishRice.manifest').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf8')
for culture in ('en','zh','zh-Hans','zh-Hant'):
 folder=root/culture;folder.mkdir(exist_ok=True)
 archive={'FormatVersion':2,'Namespace':'','Subnamespaces':[{'Namespace':'BigFatFishRice','Children':[{'Key':key,'Source':{'Text':en},'Translation':{'Text':en if culture=='en' else zh}} for key,(en,zh) in CATALOG.items()]}]}
 (folder/'BigFatFishRice.archive').write_text(json.dumps(archive,ensure_ascii=False),encoding='utf8')
config=R/'Build/Tests/RiceLocalization.ini'
config.write_text('[CommonSettings]\nSourcePath='+root.as_posix()+'\nDestinationPath='+root.as_posix()+'\nManifestName=BigFatFishRice.manifest\nArchiveName=BigFatFishRice.archive\nResourceName=BigFatFishRice.locres\nNativeCulture=en\nbSkipSourceCheck=False\n'+''.join('CulturesToGenerate='+c+'\n' for c in ('en','zh','zh-Hans','zh-Hant')),encoding='utf8')
with config.open('a',encoding='utf8') as f:f.write('\n[GatherTextStep0]\nCommandletClass=GenerateTextLocalizationResource\n')
with (R/'Logs/rice/localization.log').open('wb') as log:
 subprocess.run([str(Path(settings['engine_root'])/'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'),str(R/'Build/Tests/RiceProject/Subnautica2.uproject'),'-run=GatherText','-config='+str(config),'-ddc=InstalledNoZenLocalFallback','-unattended','-stdout','-FullStdOutLogOutput'],stdout=log,stderr=subprocess.STDOUT,check=True)
for culture in ('en','zh','zh-Hans','zh-Hant'):assert (root/culture/'BigFatFishRice.locres').stat().st_size>100,culture
print('NATIVE_LOCALIZATION_COMPILED')
