"""Local build entry point. No change to PowerShell execution policy is needed."""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    command = [str(x) for x in command]
    print("Running:", subprocess.list2cmdline(command), flush=True)
    # Batch launchers are Microsoft's/Unreal's own build entry points. There
    # are no filesystem deletion commands, and this does not change policies.
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    (ROOT / "Logs").mkdir(exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["check", "build-editor", "import", "verify", "cook", "install", "install-runtime"], default="check", nargs="?")
    parser.add_argument("--engine-root", type=Path, default=Path(SETTINGS["engine_root"]))
    options = parser.parse_args()
    engine = options.engine_root
    editor = engine / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
    report_path = ROOT / "Logs/unreal_import_report.json"
    project = ROOT / SETTINGS.get("unreal_project", "Modkit/Subnautica2.uproject")
    build = ROOT / "Build"
    package = build / "Package/LogicMods/BigFatFish"
    if options.action == "check":
        print(json.dumps({
            "project_root": str(ROOT), "engine_installed": editor.is_file(),
            "required_engine": f"{SETTINGS['required_engine_major']}.{SETTINGS['required_engine_minor']} custom SN2 build",
            "observed_game_engine": SETTINGS["observed_game_engine"],
            "modkit_commit": SETTINGS["modkit_commit"],
            "model_export_ready": (ROOT / "SourceAssets/Export/WhaleGirl_Swim.fbx").is_file(),
            "unreal_import_completed": report_path.is_file(),
            "custom_release_verified": SETTINGS["custom_engine_release_verified"],
            "unreal_project": str(project),
            "cooked_package_ready": (build / "package_manifest.json").is_file(),
        }, ensure_ascii=False, indent=2))
        return
    if options.action == "install-runtime":
        game = Path(SETTINGS["game_root"])
        destination = game / "Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFish"
        assert destination.resolve().is_relative_to(game.resolve())
        if not destination.is_dir():
            raise RuntimeError("Install the resource pack and runtime once before a script-only update")
        backup = build / "Backups" / (datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_runtime")
        shutil.copytree(destination, backup / "Runtime")
        shutil.copytree(ROOT / "Runtime/BigFatFish", destination, dirs_exist_ok=True)
        report = {"version": SETTINGS["version"], "display_name": SETTINGS["display_name"],
                  "runtime": str(destination), "backup": str(backup),
                  "resource_pack": "unchanged", "status": "runtime_installed_restart_required",
                  "files": {str(p.relative_to(destination)): digest(p) for p in destination.rglob("*") if p.is_file()}}
        (ROOT / "Logs/runtime_install.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Runtime updated; resource containers untouched. Fully restart the game to load new scripts.")
        return
    version_file = engine / "Engine/Build/Build.version"
    if not editor.is_file() or not version_file.is_file():
        raise RuntimeError(f"Custom engine not installed at {engine}; see SETUP_STATUS.txt")
    version = json.loads(version_file.read_text(encoding="utf-8-sig"))
    if (version["MajorVersion"], version["MinorVersion"]) != (SETTINGS["required_engine_major"], SETTINGS["required_engine_minor"]):
        raise RuntimeError("Engine does not match the currently installed game branch")
    if not SETTINGS["custom_engine_release_verified"]:
        raise RuntimeError("Verify the SN2 custom-engine release against this game build before cooking")
    if options.action == "build-editor":
        if SETTINGS.get("content_only", False):
            print("Content-only prototype uses the prebuilt editor; no C++ project build is required.")
            return
        run([engine / "Engine/Build/BatchFiles/Build.bat", "Subnautica2Editor", "Win64", "Development", f"-Project={project}", "-WaitMutex", "-NoHotReloadFromIDE"])
        return
    if options.action == "import":
        run([editor, project, "-run=pythonscript", f"-script={ROOT / 'Scripts/import_unreal.py'}", "-ddc=InstalledNoZenLocalFallback", "-unattended", "-nop4", "-nosplash", "-stdout", "-FullStdOutLogOutput", "-UTF8Output"])
        if not report_path.is_file():
            raise RuntimeError("Unreal import did not create its success report")
        if SETTINGS.get("gaze_enabled"):
            run([editor, project, "-run=pythonscript", f"-script={ROOT / 'Scripts/build_gaze_animation.py'}", "-ddc=InstalledNoZenLocalFallback", "-unattended", "-nop4", "-nosplash", "-stdout", "-FullStdOutLogOutput"])
        if SETTINGS.get('feeding_enabled'):
            run([editor,project,'-run=pythonscript',f"-script={ROOT / 'Scripts/build_feeding_assets.py'}",'-ddc=InstalledNoZenLocalFallback','-unattended','-nop4','-nosplash','-stdout','-FullStdOutLogOutput'])
        run([editor,project,'-run=pythonscript',f"-script={ROOT / 'Scripts/build_interaction_assets.py'}",'-ddc=InstalledNoZenLocalFallback','-unattended','-nop4','-nosplash','-stdout','-FullStdOutLogOutput'])
        return
    if options.action == "verify":
        run([editor, project, "-run=pythonscript", f"-script={ROOT / 'Scripts/verify_unreal_assets.py'}", "-ddc=InstalledNoZenLocalFallback", "-unattended", "-nop4", "-nosplash", "-stdout", "-FullStdOutLogOutput"])
        if SETTINGS.get("face_enabled"):
            run([editor, project, "-run=pythonscript", f"-script={ROOT / 'Scripts/verify_face_assets.py'}", "-ddc=InstalledNoZenLocalFallback", "-unattended", "-nop4", "-nosplash", "-stdout", "-FullStdOutLogOutput"])
        if not (ROOT / "Logs/unreal_asset_validation.json").is_file():
            raise RuntimeError("Persisted Unreal asset validation failed")
        return
    if not report_path.is_file():
        raise RuntimeError("Import and validate the Unreal assets before cooking or installing")
    if options.action == "cook":
        run([engine / "Engine/Build/BatchFiles/RunUAT.bat", "BuildCookRun", f"-project={project}", "-platform=Win64", "-clientconfig=Shipping", "-skipbuild" if SETTINGS.get("content_only", False) else "-build", "-AdditionalCookerOptions=-ddc=InstalledNoZenLocalFallback", "-cook", "-stage", "-pak", "-iostore", "-archive", f"-archivedirectory={build}", "-nocompileeditor", "-installed", "-nop4", "-utf8output", "-unattended"])
        pak_root = build / "Windows/Subnautica2/Content/Paks"
        sources = [pak_root / f"pakchunk{SETTINGS['chunk_id']}-Windows.{extension}" for extension in ["pak", "utoc", "ucas"]]
        if not all(p.is_file() for p in sources):
            raise RuntimeError("Cook did not produce all three expected chunk files")
        package.mkdir(parents=True, exist_ok=True)
        entries = []
        for source in sources:
            destination = package / ("BigFatFish" + source.suffix)
            shutil.copy2(source, destination)
            entries.append({"name": destination.name, "sha256": digest(destination)})
        (build / "package_manifest.json").write_text(json.dumps({"status": "cooked_not_game_tested", "mod_version": SETTINGS["version"], "display_name": SETTINGS["display_name"], "game_engine": SETTINGS["observed_game_engine"], "files": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    process_list = subprocess.check_output(["tasklist", "/fi", "IMAGENAME eq Subnautica2-Win64-Shipping.exe", "/fo", "csv", "/nh"])
    if b"Subnautica2-Win64-Shipping.exe" in process_list:
        raise RuntimeError("Exit the game before installing the new cooked resource container")
    manifest = json.loads((build / "package_manifest.json").read_text(encoding="utf-8-sig"))
    for entry in manifest["files"]:
        if digest(package / entry["name"]) != entry["sha256"]:
            raise RuntimeError("Cooked package hash mismatch")
    game = Path(SETTINGS["game_root"])
    asset_destination = game / "Subnautica2/Content/Paks/LogicMods/BigFatFish"
    lua_destination = game / "Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFish"
    backup = build / "Backups" / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for directory, name in [(asset_destination, "Assets"), (lua_destination, "Runtime")]:
        if directory.exists():
            shutil.copytree(directory, backup / name)
    # Retire only this mod's legacy installation, after backing it up. Keeping
    # WhaleGirl active would register its old replacing-spawn command as well.
    for directory, name in [
        (game / "Subnautica2/Content/Paks/LogicMods/WhaleGirl", "LegacyAssets"),
        (game / "Subnautica2/Binaries/Win64/ue4ss/Mods/WhaleGirl", "LegacyRuntime"),
    ]:
        directory = directory.resolve()
        assert directory.is_relative_to(game.resolve()) and directory.name == "WhaleGirl"
        if directory.exists():
            target = (backup / name).resolve()
            assert target.is_relative_to((build / "Backups").resolve())
            shutil.copytree(directory, target)
            shutil.rmtree(directory)
    save_directory = Path(os.environ["LOCALAPPDATA"]) / "Subnautica2/Saved/SaveGames/BigFatFish"
    save_directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package, asset_destination, dirs_exist_ok=True)
    shutil.copytree(ROOT / "Runtime/BigFatFish", lua_destination, dirs_exist_ok=True)
    installed = {"version": SETTINGS["version"], "display_name": SETTINGS["display_name"],
                 "assets": str(asset_destination), "runtime": str(lua_destination),
                 "save_sidecars": str(save_directory), "backup": str(backup),
                 "status": "installed_awaiting_game_test"}
    (ROOT / "Logs/runtime_install.json").write_text(json.dumps(installed, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Installed Big Fat Fish. Load a save, wait two seconds, then bigfatfish_spawn [count].")


if __name__ == "__main__":
    main()
