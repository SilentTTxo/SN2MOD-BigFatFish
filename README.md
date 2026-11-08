# Big Fat Fish · Subnautica 2

Swimming whale-girl companions for Subnautica 2, with formation following, head and eye tracking, blinking, subtle mouth motion, random sizes, and persistent saves.

为《深海迷航 2》添加鲸鱼娘外观的游泳伙伴，支持僚机跟随、头眼注视、随机眨眼、轻微嘴部动作、随机体型和存档保存。

**Version / 版本:** `0.4.1-dev`

**Tested target / 已验证目标环境:** Windows Steam public branch / 正式分支，UE 5.6.1，CL-131439. Other game builds are unverified / 其他游戏版本未验证。

[Download ZIP / 下载模组](Build/Releases/BigFatFish-0.4.1-dev.zip) · [User guide / 中英双语说明](Docs/BigFatFish_User_Guide_EN_ZH.md) · [Nexus description / Nexus 发布文案](Docs/BigFatFish_Nexus_Description_EN_ZH.md)

## English

### Features

- Spawn multiple companions; each has a saved random size between 0.5× and 1.5× the baseline.
- Wander, stay in place, or follow in a moving formation ahead and to either side of the player. The first row stays roughly 9–12 metres away.
- Smooth head, neck, and eye tracking, with an 8° eye-angle limit.
- Independent random blinking and occasional subtle mouth movement.
- Save and restore fish counts, transforms, behavior, and sizes alongside the game's own saves.

### Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

### Installation

1. Fully exit the game and download the mod ZIP linked above.
2. Extract it and merge its `Subnautica2` folder into the game root opened through **Steam → Manage → Browse local files**. Replace this mod's matching files when updating.
3. Start the game, load a save, and wait a few seconds. Open the in-game console with **F10 or tilde/backtick**, then enter:

```text
bigfatfish_spawn 3
bigfatfish_follow
```

The resulting file locations are:

```text
<game_root>/Subnautica2/Content/Paks/LogicMods/BigFatFish/
    BigFatFish.pak
    BigFatFish.utoc
    BigFatFish.ucas
<game_root>/Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFish/
    enabled.txt
    Scripts/...
```

### Commands

| Command | Effect |
| --- | --- |
| `bigfatfish_spawn [count]` | Add fish; default 1, maximum total 64. Repeated calls add more fish. |
| `bigfatfish_follow` | All fish follow in a front-side wing formation. |
| `bigfatfish_stay` | Hold current positions while animation and expressions continue. |
| `bigfatfish_wander` | Resume wandering from the current positions. |
| `bigfatfish_pause` | Toggle movement pause for this session. |
| `bigfatfish_gaze on` / `bigfatfish_gaze off` | Enable or disable head and eye tracking for this session. |
| `bigfatfish_remove` | Remove all current fish; save the game afterward to persist removal. |
| `bigfatfish_status` | Write mod version, fish count, and save status to `UE4SS.log`. |

### Saving and limitations

Use the game's own **Save** function or autosave and let it finish before quitting. The mod creates its data folder automatically:

```text
%LOCALAPPDATA%/Subnautica2/Saved/SaveGames/BigFatFish/
    <SaveId>_current.json
    <SaveId>_current.json.bak
```

Each game world keeps one current JSON and one backup; different worlds stay separate. Include these files when backing up or transferring saves. The latest mod state belongs to the world: loading an older game checkpoint does not roll the fish back to that checkpoint. Steam Cloud behavior is unverified.

Fish currently have no terrain avoidance or collision, and may pass through structures. Capture, combat, scanning, breeding, and native ecosystem integration are not implemented. Multiplayer, Game Pass, Linux, and experimental builds are unverified. Start with 1–5 fish; 64 is the code limit, not a performance guarantee.

## 中文

### 功能

- 可重复召唤多只大肥鱼，每只随机获得基准大小 0.5～1.5 倍的体型，并保存该倍率。
- 支持巡游、原地停留和主角前侧两翼的僚机跟随，第一排约保持 9～12 米距离。
- 平滑追踪主角的头、颈与双眼，眼球转角限制为 8°。
- 各自随机眨眼，偶尔轻微张嘴。
- 随游戏保存数量、位置、朝向、行为和体型，读档后自动恢复。

### 依赖

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

### 安装

1. 完全退出游戏，下载上方的模组 ZIP。
2. 解压，将其中的 `Subnautica2` 文件夹合并到 **Steam → 管理 → 浏览本地文件** 打开的游戏根目录；更新时覆盖本模组同名文件。
3. 启动游戏并载入存档，等待几秒，按 **F10 或波浪号/反引号键**打开游戏控制台，依次输入：

```text
bigfatfish_spawn 3
bigfatfish_follow
```

### 命令

| 命令 | 功能 |
| --- | --- |
| `bigfatfish_spawn [数量]` | 新增大肥鱼，默认 1 只，总数上限 64；多次输入会累加。 |
| `bigfatfish_follow` | 全部大肥鱼在主角前侧两翼跟随。 |
| `bigfatfish_stay` | 原地停留，继续播放动画和表情。 |
| `bigfatfish_wander` | 从当前位置开始巡游。 |
| `bigfatfish_pause` | 临时暂停或恢复位移。 |
| `bigfatfish_gaze on` / `bigfatfish_gaze off` | 临时开启或关闭头眼注视。 |
| `bigfatfish_remove` | 删除当前全部大肥鱼；之后保存游戏，才会记录删除。 |
| `bigfatfish_status` | 将版本、数量和存档状态写入 `UE4SS.log`。 |

### 保存与限制

使用游戏自身的**保存**或自动保存，等待保存完成后再退出。模组会自动创建上文所列的数据目录，无需手动建文件夹。

每个游戏世界只保留 **1 个当前 JSON + 1 个 `.bak`**，不同世界的数据相互独立。备份或迁移存档时，请同时保留这两个文件。本版保存世界对应的最新模组状态，载入原版旧检查点不会同时回退大肥鱼；Steam 云同步未验证。

当前没有地形避障与碰撞，可能穿过地形和建筑；未接入捕捉、战斗、扫描、繁殖或原版生态系统。多人、Game Pass、Linux 和实验分支未验证。建议先召唤 1～5 只，64 是代码上限。

## Development / 开发

This repository includes the Lua runtime, the Blender source and exported model, this mod's editable Unreal assets, build scripts, offline tests, and the packaged ZIP. The engine, community modkit checkout, caches, downloads, logs, and personal saves are excluded.

仓库包含 Lua 运行时、Blender 源文件与模型导出、可编辑的本模组 Unreal 资源、构建脚本、离线测试和发布 ZIP；不包含引擎、完整社区 Modkit、缓存、下载文件、日志或个人存档。

| Path / 路径 | Contents / 内容 |
| --- | --- |
| `Runtime/BigFatFish/` | UE4SS runtime scripts / 运行时脚本 |
| `ContentProject/` | Content-only Unreal project and this mod's assets / 内容项目及模组资源 |
| `SourceAssets/` | Blender source, FBX/GLB, textures and asset manifest / 源模型、导出和贴图 |
| `Scripts/` | Export, import, animation graph, build, packaging and test scripts / 资源流水线与测试 |
| `Build/Package/LogicMods/BigFatFish/` | Cooked containers / 烹饪后的资源三件套 |
| `Build/Releases/` | Installable ZIP and hash manifest / 安装包及校验清单 |
| `Docs/` | Bilingual user guide and Nexus description / 双语说明与发布文案 |
| `SAVE_INTEGRATION.md` | Save-system implementation notes / 保存逻辑开发记录 |

### Build / 构建

The content pipeline targets the matched **SN2 custom UE 5.6.1 editor**, Python 3, and Blender (the source was prepared in Blender 5.2.1 LTS). The editor graph bridge is tied to the UE 5.6.1 editor ABI. The engine is not distributed in this repository. Lua-only changes do not require an editor or a recook.

资源构建使用匹配游戏的 **SN2 定制 UE 5.6.1 编辑器**、Python 3 和 Blender；源文件在 Blender 5.2.1 LTS 下制作。编辑器动画图桥接依赖 UE 5.6.1 的 ABI，仓库不附带引擎。只修改 Lua 时无需编辑器或重新烹饪。

Run from the repository root. Set `engine_root` and `game_root` in `project.json` to your local paths. Preserve the existing content project configuration; it is already included, so `prepare_content_project.py` is not needed for a normal checkout.

在仓库根目录执行下列命令，先将 `project.json` 中的 `engine_root` 和 `game_root` 改为本机路径。仓库已经包含配置好的内容项目，正常克隆后无需运行 `prepare_content_project.py`。

```text
python Scripts/workflow.py check
python Scripts/workflow.py import
python Scripts/workflow.py verify
python Scripts/workflow.py cook
python Scripts/verify_package.py
```

To re-export after editing the model / 修改模型后重新导出：

```text
blender --background --python Scripts/export_blender.py
```

To install a full build or update only Lua, fully exit the game first / 完全退出游戏后安装完整构建或只更新 Lua：

```text
python Scripts/workflow.py install
python Scripts/workflow.py install-runtime
```

The two install commands are alternatives. The script-only command requires an existing installation. Fully restart the game after updating. To produce the installable ZIP after a matching local installation / 两个安装命令按需选择；仅脚本更新要求已有完整安装，更新后需重启游戏。完成对应版本的本机安装后，可生成发布 ZIP：

```text
python Scripts/package_release.py
```

Packaging checks container hashes, verifies runtime/assets match the installed files, and validates every ZIP entry. The original `WhaleGirl` names in source-model filenames are retained to preserve asset references; runtime IDs and commands use `BigFatFish`.

打包脚本会核对容器哈希、已安装文件与源文件的一致性，并校验压缩包的每个条目。模型源文件保留原有 `WhaleGirl` 名称以保持引用，运行时标识和命令统一为 `BigFatFish`。

### Offline tests / 离线测试

With Lua 5.4 available on your PATH / 安装 Lua 5.4 后：

```text
lua Scripts/test_runtime_v020.lua .
lua Scripts/test_gaze.lua .
lua Scripts/test_face.lua .
```

The runtime test filename is historical; it covers the current implementation with mocked game/disk APIs. Tests cover save success/failure, world isolation, restore behavior, one-current-file rotation, directory creation, movement, gaze and facial scheduling. These tests do not substitute for visual checks in the game.

运行时测试文件名沿用早期命名，内容测试当前实现，使用模拟的游戏与磁盘接口；覆盖保存成功/失败、世界隔离、恢复、单文件轮换、自动创建目录、移动、注视与表情调度。离线测试不代替游戏内画面验证。

## Credits / 借物表

- **Model / 模型：** 木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》。
- **Swimming animation / 游泳动作：** [Quaternius — Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html), `Swim_Fwd_Loop`, CC0; retargeted and adjusted / 已重定向并调整。
- **Runtime / 运行环境：** [UE4SS-RE / RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) contributors.
- **JSON：** [rxi/json.lua](https://github.com/rxi/json.lua), MIT; [included license / 随附许可证](Runtime/BigFatFish/Scripts/json.LICENSE).
- **Game / 游戏：** Unknown Worlds — Subnautica 2.

Model, textures, and original facial morphs belong to their creator. Attribution does not change the creator's original terms. / 模型、贴图和原有面部形态归原作者，借物署名不改变原作者的使用条件。
