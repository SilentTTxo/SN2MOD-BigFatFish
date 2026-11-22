"""Prepare an isolated editor workspace with Suzie, without FMOD editor startup."""
import json
import shutil
from pathlib import Path
from rice_schema import build_schema

ROOT=Path(__file__).resolve().parents[1]
project=ROOT/"Build/Tests/RiceProject"
project.mkdir(parents=True,exist_ok=True)
plugins=[]
for descriptor in sorted((ROOT/"Modkit/Plugins").glob("*/*.uplugin")):
    plugins.append({"Name":descriptor.stem,"Enabled":descriptor.stem=="Suzie"})
plugins.extend({"Name":name,"Enabled":True} for name in ("PythonScriptPlugin","EditorScriptingUtilities","GameplayAbilities","ModelViewViewModel","PCG"))
plugins.append({"Name":"BigFatFishRice","Enabled":True})
(project/"Subnautica2.uproject").write_text(json.dumps({
    "FileVersion":3,"EngineAssociation":"","Description":"Big Fat Fish rice planting workspace",
    "AdditionalPluginDirectories":[str(ROOT/"Modkit/Plugins")],
    "Plugins":plugins,
},indent=2),encoding="utf-8")
(project/"Config").mkdir(exist_ok=True)
shutil.copy2(ROOT/"ContentProject/Config/DefaultEngine.ini",project/"Config/DefaultEngine.ini")
shutil.copy2(ROOT/"Modkit/Config/DefaultGameplayTags.ini",project/"Config/DefaultGameplayTags.ini")
with (project/"Config/DefaultGameplayTags.ini").open('a',encoding='utf8') as tags:
    tags.write('\n[/Script/GameplayTags.GameplayTagsSettings]\n')
    for tag in ('BuildableSurface.Planter','SculpturalBase.BrushType.Planter'):
        tags.write('+GameplayTagList=(Tag="'+tag+'",DevComment="Existing game planter tag needed for rice authoring")\n')
with (project/"Config/DefaultEngine.ini").open("a",encoding="utf-8") as config:
    config.write("\n[Core.Log]\nLogProperty=Error\nLogStreaming=Warning\n\n[/Script/UnrealEd.CookerSettings]\ncook.AllowCookedDataInEditorBuilds=True\ns.AllowUnversionedContentInEditor=1\n")
    full=(ROOT/"Modkit/Config/DefaultEngine.ini").read_text(encoding='utf-8-sig')
    section=full.split('[/Script/Engine.CollisionProfile]',1)[1].split('\n[',1)[0]
    config.write('\n[/Script/Engine.CollisionProfile]'+section+'\n')
(project/"Config/DefaultGame.ini").write_text('''[/Script/EngineSettings.GeneralProjectSettings]
ProjectName=Subnautica2

[/Script/UnrealEd.ProjectPackagingSettings]
Build=Never
BuildConfiguration=PPBC_Shipping
UsePakFile=True
bUseIoStore=True
bUseZenStore=False
bGenerateChunks=False
bCookAll=False
bShareMaterialShaderCode=False
bSharedMaterialNativeLibraries=False
bCompressed=True
IncludePrerequisites=False

[Staging]
+RemapDirectories=(From="Subnautica2/Plugins/BigFatFishRice",To="Subnautica2/Mods/BigFatFishRice")
''',encoding="utf-8")
dynamic=project/"Content/DynamicClasses"
dynamic.mkdir(parents=True,exist_ok=True)
count=build_schema(ROOT/"Modkit/Content/DynamicClasses/Subnautica2-131439.jmap.gz",dynamic/"Subnautica2-131439.jmap.gz")
shutil.copy2(ROOT/"Modkit/GameInstallDirectory.txt",project/"GameInstallDirectory.txt")
release=project/'Releases/SN2Base/Windows'
release.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'Modkit/Releases/SN2Base/Windows/AssetRegistry.bin',release/'AssetRegistry.bin')
(ROOT/"RiceContent").mkdir(exist_ok=True)
source_plugin=ROOT/"RiceContent/BigFatFishRice"
source_plugin.mkdir(exist_ok=True)
descriptor={"FileVersion":3,"Version":2,"VersionName":"0.2.0-prototype","FriendlyName":"Big Fat Fish - Rice",
    "Description":"Native rice planting prototype","Category":"Mods","CreatedBy":"SilentTTxo",
    "CanContainContent":True,"EnabledByDefault":True,"Installed":True,"IsBetaVersion":True,"SemVersion":"0.2.0","RequiredOnRemote":False}
(source_plugin/"BigFatFishRice.uplugin").write_text(json.dumps(descriptor,indent=2),encoding='utf8')
shutil.copytree(source_plugin,project/"Plugins/BigFatFishRice",dirs_exist_ok=True)
print(project/"Subnautica2.uproject", "farming schema objects:", count)
