"""Build/install only the isolated native rice prototype; keep BigFatFish untouched."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import datetime
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
settings=json.loads((ROOT/'project.json').read_text(encoding='utf8'))
ENGINE=Path(settings['engine_root'])
PROJECT=ROOT/'Build/Tests/RiceProject/Subnautica2.uproject'
LOGS=ROOT/'Logs/rice';LOGS.mkdir(parents=True,exist_ok=True)
def run(args,log):
    print('Running; log:',log,flush=True)
    with Path(log).open('wb') as output:subprocess.run([str(a) for a in args],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True)
def editor(script):
    run([ENGINE/'Engine/Binaries/Win64/UnrealEditor-Cmd.exe',PROJECT,'-run=pythonscript',
         '-script='+str(ROOT/'Scripts'/script),'-ddc=InstalledNoZenLocalFallback','-unattended','-nop4','-nosplash','-stdout','-FullStdOutLogOutput'],LOGS/(Path(script).stem+'.log'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sync_source():
    source=PROJECT.parent/'Plugins/BigFatFishRice'
    destination=ROOT/'RiceContent/BigFatFishRice'
    shutil.copy2(source/'BigFatFishRice.uplugin',destination/'BigFatFishRice.uplugin')
    shutil.copytree(source/'Content',destination/'Content',dirs_exist_ok=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','import','verify','cook','package','install'])
    action=parser.parse_args().action
    if action=='prepare':
        subprocess.run([sys.executable,ROOT/'Scripts/prepare_rice_project.py'],check=True);return
    if action in ('import','verify'):
        editor('import_rice.py' if action=='import' else 'verify_rice_assets.py')
        if action=='import':editor('build_rice_use_ability.py')
        if action=='verify':sync_source()
        return
    validation=LOGS/'validation/report.json'
    assert validation.is_file() and json.loads(validation.read_text(encoding='utf8'))['status'].startswith('PASS'), 'Run verify first'
    if action=='cook':
        run([ENGINE/'Engine/Build/BatchFiles/RunUAT.bat','BuildCookRun','-project='+str(PROJECT),
             '-unrealexe='+str(ENGINE/'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'),
             '-platform=Win64','-clientconfig=Shipping','-skipbuild','-cook','-stage','-pak','-iostore',
             '-dlcname=BigFatFishRice','-basedonreleaseversion=SN2Base',
             '-AdditionalCookerOptions=-CookAgainstFixedBase -AllowUncookedAssetReferences -ddc=InstalledNoZenLocalFallback',
             '-stagingdirectory='+str(ROOT/'Build/RiceStage'),'-nocompileeditor','-installed','-nop4','-utf8output','-unattended'],
             LOGS/'cook.log')
        print('Cook/stage finished:',ROOT/'Build/RiceStage',flush=True);return
    stage=ROOT/'Build/RiceStage/Windows/Subnautica2'
    candidates=[stage/'Mods/BigFatFishRice',stage/'Plugins/BigFatFishRice']
    plugin=next((p for p in candidates if (p/'BigFatFishRice.uplugin').is_file()),None)
    assert plugin,'Staged rice plugin not found'
    # UAT remaps the descriptor/virtual mount, but leaves container output in
    # Plugins. Match Alpakit's final merge so native Mods discovery sees both.
    staged_content=stage/'Plugins/BigFatFishRice/Content'
    if staged_content.is_dir() and plugin!=staged_content.parent:
        shutil.copytree(staged_content,plugin/'Content',dirs_exist_ok=True)
    containers=list(plugin.rglob('*.pak'))+list(plugin.rglob('*.utoc'))+list(plugin.rglob('*.ucas'))
    assert any(p.suffix=='.utoc' for p in containers),'Missing IoStore container'
    if action=='package':
        release=ROOT/'Build/Releases/BigFatFishRice-0.4.1-prototype.zip';release.parent.mkdir(exist_ok=True)
        entries={}
        for path in plugin.rglob('*'):
            if path.is_file():entries['Subnautica2/Mods/BigFatFishRice/'+path.relative_to(plugin).as_posix()]=path
        runtime=ROOT/'Runtime/BigFatFishRice'
        for path in runtime.rglob('*'):
            if path.is_file():entries['Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFishRice/'+path.relative_to(runtime).as_posix()]=path
        entries['README_Rice_EN_ZH.md']=ROOT/'Docs/BigFatFish_Rice_Prototype_EN_ZH.md'
        with ZipFile(release,'w',ZIP_DEFLATED,compresslevel=9) as package:
            for name,path in sorted(entries.items()):package.write(path,name)
        with ZipFile(release) as package:assert package.testzip() is None
        manifest={'status':'packaged_gameplay_test_pending','version':'0.4.1-prototype','zip_sha256':digest(release),
                  'files':[{ 'path':name,'sha256':digest(path)} for name,path in sorted(entries.items())]}
        release.with_suffix('.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
        print('ZIP:',release,'bytes:',release.stat().st_size);return
    game=Path(settings['game_root']).resolve()
    processes=subprocess.check_output(['tasklist','/fi','IMAGENAME eq Subnautica2-Win64-Shipping.exe','/fo','csv','/nh'])
    assert b'Subnautica2-Win64-Shipping.exe' not in processes,'Exit game before installing'
    backup=ROOT/'Build/Backups'/('Rice_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    destinations=[(plugin,game/'Subnautica2/Mods/BigFatFishRice'),
                  (ROOT/'Runtime/BigFatFishRice',game/'Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFishRice')]
    for index,(source,destination) in enumerate(destinations):
        assert destination.resolve().is_relative_to(game) and destination.name=='BigFatFishRice'
        if destination.exists():shutil.copytree(destination,backup/str(index))
        shutil.copytree(source,destination,dirs_exist_ok=True)
        for path in source.rglob('*'):
            if path.is_file():assert digest(path)==digest(destination/path.relative_to(source))
    print('Installed native rice plugin and test commands. Restart game; in-game planting/save validation pending.')

if __name__=='__main__':main()
