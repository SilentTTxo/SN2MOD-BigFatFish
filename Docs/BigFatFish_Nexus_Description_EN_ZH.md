# Big Fat Fish — Swimming Companions

Version / 版本：0.4.1-dev

## English

### A swimming companion for your underwater adventures

Big Fat Fish adds manually summoned companions using a whale-girl model. Bring one along for company, or summon a small group and watch them cruise in a wing formation ahead of you.

### Features

- Looping swimming animation with smooth movement and turning.
- Wander, stay, and follow modes. Following uses front-side wings, roughly 9–12 meters away for the first row; additional rows sit farther out.
- Smooth head, neck, and eye tracking toward the player. Eye rotation is restricted to 8° to reduce extreme eye poses.
- Independent random blinking and subtle, intermittent mouth motion.
- Each newly summoned fish receives a random 0.5–1.5× baseline **linear size**. Its multiplier is saved, rather than rerolled when loading.
- Multiple companions: repeated spawn commands add more fish. The current code limit is 64; start with a small group for performance.
- Save-aware persistence: fish count, position, heading, behavior, and size are stored in separate mod data after successful game saves.

### Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

### Installation

`<game_root>` is the folder opened through Steam → Manage → Browse local files.

1. Fully exit the game.
2. Put BigFatFish.pak, BigFatFish.utoc, and BigFatFish.ucas in `<game_root>\Subnautica2\Content\Paks\LogicMods\BigFatFish\`. Put the BigFatFish runtime folder in `<game_root>\Subnautica2\Binaries\Win64\ue4ss\Mods\BigFatFish\`, keeping enabled.txt and the complete Scripts folder.
3. Start the game, load a save, and wait a few seconds before using commands.

The save-data folder is created automatically. Update this mod's assets and scripts together, then fully restart the game.

### Console commands

Open the in-game console with F10 or the tilde/backtick key. Enter commands individually:

```text
bigfatfish_spawn
bigfatfish_spawn 3
bigfatfish_follow
bigfatfish_stay
bigfatfish_wander
bigfatfish_pause
bigfatfish_gaze off
bigfatfish_gaze on
bigfatfish_status
bigfatfish_remove
```

- **spawn [count]:** add fish, default one; existing fish are retained.
- **follow / stay / wander:** change the behavior of all current companions.
- **pause:** toggle movement pause; swim animation and facial motion continue.
- **gaze off/on:** disable or enable head/eye tracking; enabled by default.
- **status:** write version, count, per-fish IDs, size multipliers, behavior, and gaze state to UE4SS.log.
- **remove:** remove all companions. Save the game afterward to persist removal.

There are no per-ID controls or manual expression commands in this version. Blinking and mouth motion run automatically.

### Saving and removal

Use the game's normal Save function or let an automatic save complete. The mod automatically creates its save-data folder. Each save-world keeps only one current JSON and one .bak backup in:

```text
%LOCALAPPDATA%\Subnautica2\Saved\SaveGames\BigFatFish\
```

Loading the same world reconstructs its saved fish. Existing fish without a saved size field retain the baseline size. Gaze toggles, movement pause, and facial schedules are session-only.

The mod does not edit native .sav files. Its current record is scoped to the save-world SaveId: loading an older native checkpoint still uses the latest mod record for that world, rather than rolling companions back to the same checkpoint. Back up this folder with your game saves; Steam Cloud synchronization is unverified.

To uninstall, exit the game and remove only this mod's asset containers and BigFatFish Lua folder. Keep sidecar data if you may reinstall. Do not remove shared UE4SS files needed by other mods.

### Good to know

These are visual companions, with no native capture, scanning, combat, breeding, collision, or terrain avoidance. They may pass through scenery. They do not naturally spawn in biomes or replace existing fish. Multiplayer synchronization is not implemented as a supported feature.

The original VRM has facial morphs but no full-body animation clips. This version integrates blinking and two mouth shapes; other source expressions, such as winks and happy/angry/sad/relaxed faces, are not selectable features in this release. Mouth motion has no voice or lip-sync.

This is a development build. Automated/editor checks have passed, and live logs confirm loading, restoration, and saving; broader visual testing is ongoing. Other game builds, Game Pass, Linux, and the experimental branch are unverified.


---

## 中文

### 陪你探索海底的游泳伙伴

Big Fat Fish 可以手动召唤鲸鱼娘外观的游泳伙伴。带上一只陪你探索，或者召唤一小群，在主角前侧组成僚机队形一起游动。

### 主要功能

- 循环游泳动画，平滑位移和转向。
- 巡游、停留、跟随三种模式。跟随时位于主角视野前侧两翼，第一排约保持 9～12 米，后排更远。
- 平滑的头、颈与双眼注视，眼球限角收紧为 8°，减少眼仁过度转到边缘。
- 每只鱼独立随机眨眼，偶尔轻微张合嘴巴。
- 新召唤的鱼按基准**线性尺寸**随机取 0.5～1.5 倍；倍率会保存，读档不重新抽取。
- 支持多只同时存在，多次召唤会新增。代码上限 64 只，建议从少量开始。
- 游戏保存成功后，数量、位置、朝向、行为和体型写入独立附属数据。

### 依赖

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

### 安装

`<game_root>` 是 Steam“管理 → 浏览本地文件”打开的游戏根目录。

1. 完全退出游戏。
2. 将 BigFatFish.pak、BigFatFish.utoc、BigFatFish.ucas 放入 `<game_root>\Subnautica2\Content\Paks\LogicMods\BigFatFish\`；将本模组运行时 BigFatFish 文件夹放入 `<game_root>\Subnautica2\Binaries\Win64\ue4ss\Mods\BigFatFish\`，保留 enabled.txt 和完整 Scripts 文件夹。
3. 启动游戏，载入存档，等待几秒后使用命令。

存档目录由模组自动创建，无需手动操作。更新时同时替换本模组资源和脚本，并完整重启游戏。

### 操作命令

按 **F10 或 `~` / 反引号**打开游戏内控制台。每条命令单独输入：

```text
bigfatfish_spawn
bigfatfish_spawn 3
bigfatfish_follow
bigfatfish_stay
bigfatfish_wander
bigfatfish_pause
bigfatfish_gaze off
bigfatfish_gaze on
bigfatfish_status
bigfatfish_remove
```

- **spawn [数量]：** 新增指定数量，默认一只，不替换已有的鱼。
- **follow / stay / wander：** 所有鱼切换为跟随、停留或巡游。
- **pause：** 暂停/恢复位移，游泳动画与表情继续。
- **gaze off/on：** 关闭/开启头眼注视，默认开启。
- **status：** 在 UE4SS.log 输出版本、数量、各只 ID、体型倍率、行为与注视状态。
- **remove：** 删除所有伙伴，再进行游戏保存才会持久记录删除。

当前没有按 ID 单独控制或手动切换表情的命令，眨眼与嘴部动作自动播放。

### 保存与卸载

使用游戏本身的“保存”或等待自动保存完成。模组自动创建存档目录，每个游戏存档只保留一个当前 JSON 和一个 .bak 备份，位置为：

```text
%LOCALAPPDATA%\Subnautica2\Saved\SaveGames\BigFatFish\
```

再次进入同一世界会重建已保存的鱼。旧鱼未记录体型时保持基准大小；注视开关、位移暂停和表情时间表不保存。

本模组不修改原版 .sav。记录按存档世界 SaveId 关联；回退原版旧检查点时，仍使用该世界最新的鱼记录，不会同步回退鱼的历史状态。备份时请连同上述文件夹一起保存，Steam 云同步未验证。

卸载时退出游戏，只移除本模组的三件套与 BigFatFish Lua 文件夹。附属数据可保留供重装恢复；不要删除其他 MOD 所需的共享 UE4SS 文件。

### 注意事项

伙伴用于观赏，没有原生捕捉、扫描、战斗、繁殖、碰撞或地形避障，可能穿过场景。不参与生态刷新，也不替换原版鱼。多人同步尚未作为受支持功能实现。

原 VRM 自带面部形态，没有全身动作片段；本版接入了眨眼与两个嘴型。左右单眼眨眼、开心/生气/难过/放松等其他源表情尚不能在游戏中切换。嘴部动作不包含语音或语音同步。

当前为开发版。自动化与编辑器检查通过，真实日志确认了加载、恢复和保存；更多视觉测试仍在进行。其他游戏版本、Game Pass、Linux 和实验分支未验证。


---

## 借物表 / Credits

**模型、贴图、原有面部形态 / Model, textures, and authored facial morphs**  
木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》

模型归原作者所有。本模组负责游戏接入与行为制作，不将模型、贴图或原有表情署为自制。 / All model assets belong to their original creator. This mod provides game integration and behavior, not original authorship of the model, textures, or facial shapes.

**游泳动作 / Swimming animation**  
[Quaternius — Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html)，Swim_Fwd_Loop，CC0。已重定向并调整。 / Retargeted and adjusted; CC0.

**运行环境 / Runtime and bundled helpers**  
[UE4SS-RE / RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) 及组件贡献者 / and component contributors.

**JSON 库 / JSON library**  
[rxi/json.lua](https://github.com/rxi/json.lua)，MIT，保留随包许可证。 / MIT; its license is retained in the distribution.

**游戏 / Game**  
Unknown Worlds — Subnautica 2。

模型按原作者使用条件与借物署名要求使用；本模组不另行授予模型的转载、再分发或其他使用权限。 / The model is used under its creator's terms and attribution requirements; this mod does not independently grant model reupload, redistribution, or other rights.

本模组为玩家制作，与 Unknown Worlds 或 KRAFTON 无隶属关系，也未获其背书。 / A fan-made mod, not affiliated with or endorsed by Unknown Worlds or KRAFTON.

