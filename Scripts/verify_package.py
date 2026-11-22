"""List the actual IoStore directory and check this mod's complete asset set."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
settings = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
package = ROOT / "Build/Package/LogicMods/BigFatFish"
listing = ROOT / "Logs/package_contents.csv"
with (ROOT / "Logs/package_inspect.log").open("w", encoding="utf-8") as output:
    subprocess.run([str(Path(settings["engine_root"]) / "Engine/Binaries/Win64/UnrealPak.exe"),
                    str(package / "BigFatFish.utoc"), "-List", f"-csv={listing}"],
                   stdout=output, stderr=subprocess.STDOUT, check=True)
with listing.open(encoding="utf-8-sig", newline="") as source:
    filenames = {row["Filename"].strip() for row in csv.DictReader(source, skipinitialspace=True)}
prefix = "../../../Subnautica2/Content/Mods/BigFatFish/"
expected = {"ModActor.uasset", "BP_BigFatFish.uasset",
            "Character/SK_BigFatFish.uasset", "Character/SK_BigFatFish_Skeleton.uasset",
            "Character/AN_BigFatFish_Swim.uasset", "Character/ABP_BigFatFish_Gaze.uasset"}
if settings.get('feeding_enabled'):expected.add('Character/AN_BigFatFish_GrabEat.uasset')
expected.update(f"Textures/T_BigFatFish_{i:02}.uasset" for i in range(6))
expected.update(f"Textures/T_BigFatFish_{i:02}.ubulk" for i in range(6))
expected.update(f"Materials/M_BigFatFish_{name}.uasset" for name in ["body", "clothing", "expression", "hair", "head", "TiePen"])
missing = {prefix + name for name in expected} - filenames
assert not missing, f"Missing cooked payload: {sorted(missing)}"
assert all(name.startswith(prefix) or name == "<ContainerHeader>" for name in filenames), "Unexpected payload outside this mod"
manifest = json.loads((ROOT / "Build/package_manifest.json").read_text(encoding="utf-8"))
for entry in manifest["files"]:
    assert hashlib.sha256((package / entry["name"]).read_bytes()).hexdigest() == entry["sha256"]
report = {"status": "complete_package_verified_not_game_tested",
          "expected_payload_files": len(expected), "listed_entries": len(filenames),
          "container_size_bytes": sum(p.stat().st_size for p in package.iterdir() if p.is_file()),
          "only_bigfatfish_assets": True, "sha256": "passed"}
(ROOT / "Logs/package_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
