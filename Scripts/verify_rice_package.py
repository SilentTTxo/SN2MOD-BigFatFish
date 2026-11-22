"""Verify native item assets and localization in the cooked DLC containers."""
import csv,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];settings=json.loads((R/'project.json').read_text(encoding='utf8'))
pak=Path(settings['engine_root'])/'Engine/Binaries/Win64/UnrealPak.exe'
folder=R/'Build/RiceStage/Windows/Subnautica2/Mods/BigFatFishRice/Content/Paks/Windows'
toc=next(folder.glob('*.utoc'));listing=R/'Logs/rice/package_contents.csv'
with (R/'Logs/rice/package_inspect.log').open('wb') as out:subprocess.run([str(pak),str(toc),'-List','-csv='+str(listing)],stdout=out,stderr=subprocess.STDOUT,check=True)
with listing.open(encoding='utf-8-sig',newline='') as f:names={row['Filename'].strip() for row in csv.DictReader(f,skipinitialspace=True)}
for relative in ('Blueprints/BP_BFF_WildRice.uasset','Blueprints/BP_BFF_RicePlant.uasset','Blueprints/BP_BFF_CookedRice.uasset','Blueprints/BP_BFF_RiceServing.uasset','Data/DA_BFF_CookedRice_ItemType.uasset','Meshes/SM_BFF_EmptyRiceBowl.uasset'):
 assert any(n.endswith('/'+relative) for n in names),relative
with (R/'Logs/rice/pak_list.log').open('wb') as out:subprocess.run([str(pak),str(next(folder.glob('*.pak'))),'-List'],stdout=out,stderr=subprocess.STDOUT,check=True)
text=(R/'Logs/rice/pak_list.log').read_text(encoding='utf8',errors='replace')
for culture in ('en','zh','zh-Hans','zh-Hant'):assert '/'+culture+'/BigFatFishRice.locres' in text,culture
assert 'BigFatFishRice.locmeta' in text
report={'status':'PASS: native item, crop, wild crop, food and serving assets; four native culture resources','entries':len(names)}
(R/'Logs/rice/package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(report)
