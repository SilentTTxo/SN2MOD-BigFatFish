"""Package only Big Fat Fish runtime/assets and player documentation."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
project = json.loads((ROOT / "project.json").read_text(encoding="utf-8-sig"))
version = project["version"]
game = Path(project["game_root"])
entries = {}

def add(source, destination, installed=None):
    data = source.read_bytes()
    if installed is not None:
        assert installed.read_bytes() == data, f"Installed file differs: {installed}"
    assert destination not in entries, destination
    entries[destination] = data

containers = ROOT / "Build/Package/LogicMods/BigFatFish"
asset_manifest = json.loads((ROOT / "Build/package_manifest.json").read_text(encoding="utf-8-sig"))
hashes = {item["name"]: item["sha256"] for item in asset_manifest["files"]}
for extension in ("pak", "utoc", "ucas"):
    name = f"BigFatFish.{extension}"
    source = containers / name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == hashes[name], name
    destination = f"Subnautica2/Content/Paks/LogicMods/BigFatFish/{name}"
    add(source, destination, game / destination)

runtime = ROOT / "Runtime/BigFatFish"
runtime_files = ["enabled.txt"] + [f"Scripts/{name}" for name in (
    "main.lua", "config.lua", "gaze.lua", "face.lua", "face_morphs.lua",
    "storage.lua", "save_adapter.lua", "json.lua", "json.LICENSE",
)]
assert {p.relative_to(runtime).as_posix() for p in runtime.rglob("*") if p.is_file()} == set(runtime_files)
for relative in runtime_files:
    destination = f"Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFish/{relative}"
    add(runtime / relative, destination, game / destination)

add(ROOT / "Docs/BigFatFish_User_Guide_EN_ZH.md", "BigFatFish_User_Guide_EN_ZH.md")
readme = f"""Big Fat Fish {version}

依赖 / Requirement: UE4SS
https://www.nexusmods.com/subnautica2/mods/36

安装：
1. 完全退出游戏。
2. 将本压缩包中的 Subnautica2 文件夹合并到 Steam“浏览本地文件”打开的游戏根目录；更新时覆盖本模组同名文件。
3. 启动游戏并载入存档，等待几秒。打开游戏控制台后输入：
   bigfatfish_spawn 3
   bigfatfish_follow

Installation:
1. Fully exit the game.
2. Merge this archive's Subnautica2 folder into the game root opened through Steam > Browse local files. Replace this mod's matching files when updating.
3. Start the game, load a save, and wait a few seconds. Open the in-game console and enter:
   bigfatfish_spawn 3
   bigfatfish_follow

通过游戏自身的保存功能保存；模组自动创建数据目录，每个世界保留一个 JSON 和一个 .bak。
Save using the game's own save function. The mod creates its data folder automatically and keeps one JSON and one .bak per world.

完整命令、借物表和说明见 / Full commands, credits and documentation:
BigFatFish_User_Guide_EN_ZH.md

模型 / Model: 木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》
游泳动作 / Swim: Quaternius Universal Animation Library, Swim_Fwd_Loop (CC0)
JSON: rxi/json.lua (MIT); license included in Scripts/json.LICENSE.
"""
entries["README.txt"] = readme.replace("\n", "\r\n").encode("utf-8-sig")

output = ROOT / "Build/Releases"
output.mkdir(parents=True, exist_ok=True)
archive = output / f"BigFatFish-{version}.zip"
temporary = archive.with_suffix(".zip.tmp")
with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as package:
    for name, data in sorted(entries.items()):
        package.writestr(name, data)
with ZipFile(temporary) as package:
    assert package.testzip() is None
    assert set(package.namelist()) == set(entries)
    for name, data in entries.items():
        assert package.read(name) == data, name
temporary.replace(archive)
manifest = {
    "version": version,
    "archive": archive.name,
    "size_bytes": archive.stat().st_size,
    "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}
              for name, data in sorted(entries.items())],
}
archive.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: manifest[key] for key in ("version", "archive", "size_bytes", "sha256")}, ensure_ascii=False))
print(f"PASS: {len(entries)} files verified; runtime and containers match installed files.")
print(archive)
