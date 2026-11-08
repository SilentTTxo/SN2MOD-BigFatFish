"""Create the small first prototype project without the full modkit's C++/FMOD dependencies."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
project = ROOT / "ContentProject"
(project / "Config").mkdir(parents=True, exist_ok=True)
(project / "Content").mkdir(exist_ok=True)
(project / "Subnautica2.uproject").write_text(json.dumps({
    "FileVersion": 3, "EngineAssociation": "", "Category": "Mods",
    "Description": "BigFatFish local content-only prototype for Subnautica 2 UE 5.6.1",
    "Plugins": [
        {"Name": "PythonScriptPlugin", "Enabled": True, "TargetAllowList": ["Editor"]},
        {"Name": "EditorScriptingUtilities", "Enabled": True, "TargetAllowList": ["Editor"]},
    ],
}, indent=2), encoding="utf-8")

# Preserve the community modkit's game-specific shader configuration, without
# loading its native game stubs or referencing the game's levels/audio assets.
allowed = {"/Script/WindowsTargetPlatform.WindowsTargetSettings",
           "/Script/Engine.RendererSettings", "DevOptions.Shaders",
           "/Script/HardwareTargeting.HardwareTargetingSettings"}
lines = []
include = False
for line in (ROOT / "Modkit/Config/DefaultEngine.ini").read_text(encoding="utf-8-sig").splitlines():
    if line.startswith("[") and line.endswith("]"):
        include = line[1:-1] in allowed
    if include:
        lines.append(line)
lines.extend(["", "[ConsoleVariables]", "Interchange.FeatureFlags.Import.FBX=False", "",
              "[/Script/EngineSettings.GameMapsSettings]",
              "GameDefaultMap=/Engine/Maps/Entry", "EditorStartupMap=/Engine/Maps/Entry", ""])
(project / "Config/DefaultEngine.ini").write_text("\n".join(lines), encoding="utf-8")
(project / "Config/DefaultGame.ini").write_text('''[/Script/EngineSettings.GeneralProjectSettings]
ProjectID=B58E67804BFC435E959A682A10506237
ProjectName=Subnautica2
ProjectVersion=0.1.0

[/Script/UnrealEd.ProjectPackagingSettings]
Build=Never
BuildConfiguration=PPBC_Shipping
UsePakFile=True
bUseIoStore=True
bGenerateChunks=True
bCookAll=False
bShareMaterialShaderCode=False
bSharedMaterialNativeLibraries=False
bCompressed=True
IncludePrerequisites=False
+DirectoriesToAlwaysCook=(Path="/Game/Mods/BigFatFish")

[/Script/Engine.AssetManagerSettings]
+PrimaryAssetTypesToScan=(PrimaryAssetType="PrimaryAssetLabel",AssetBaseClass="/Script/Engine.PrimaryAssetLabel",bHasBlueprintClasses=False,bIsEditorOnly=True,Directories=((Path="/Game/Mods")),SpecificAssets=,Rules=(Priority=-1,ChunkId=-1,bApplyRecursively=True,CookRule=Unknown))
''', encoding="utf-8")

settings_path = ROOT / "project.json"
settings = json.loads(settings_path.read_text(encoding="utf-8"))
settings.update({
    "engine_root": str(ROOT / "Engine/SN2-Engine-V4"),
    "required_engine_minor": 6,
    "observed_game_engine": "5.6.1 (public branch, CL-131439)",
    "previous_log_engine": "5.7.4-136704 (experimental branch; stale log)",
    "custom_engine_release_verified": True,
    "unreal_project": "ContentProject/Subnautica2.uproject",
    "content_only": True,
    "state": "extracting_matched_engine",
})
settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
print("Prepared content-only project:", project)
