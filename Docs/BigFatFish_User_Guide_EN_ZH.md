# Big Fat Fish — 使用说明 / User Guide

版本 / Version: **0.4.2-dev**
更新 / Updated: **2026-11-02**  
适用环境 / Target: Windows Steam，Subnautica 2 正式分支 / public branch，UE 5.6.1，CL-131439。

## 1. 这是什么 / What it does

Big Fat Fish 在世界中生成鲸鱼娘外观的游泳伙伴，可巡游、停留或在主角前侧以僚机队形跟随。它有平滑头眼追踪、随机眨眼、轻微嘴部动作和独立随机体型。当前为手动召唤的观赏伙伴，不替换原版鱼，也不参与原版生态系统。

Big Fat Fish spawns swimming companions using a whale-girl model. They can wander, stay in place, or follow in a wing formation ahead of the player. Features include smooth head/eye tracking, independent random blinking, subtle mouth motion, and individual random sizes. These are manually spawned visual companions; they do not replace existing fish or participate in the native ecosystem.

## 2. 依赖 / Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

## 3. 安装 / Installation

`<game_root>` 是 Steam“管理 → 浏览本地文件”打开的游戏根目录。

1. 完全退出游戏。
2. 将 BigFatFish.pak、BigFatFish.utoc、BigFatFish.ucas 放入 `<game_root>\Subnautica2\Content\Paks\LogicMods\BigFatFish\`；将本模组运行时 BigFatFish 文件夹放入 `<game_root>\Subnautica2\Binaries\Win64\ue4ss\Mods\BigFatFish\`，保留 enabled.txt 和完整 Scripts 文件夹。
3. 启动游戏，载入存档，等待几秒后使用命令。

存档目录由模组自动创建，无需手动操作。更新时同时替换本模组资源和脚本，并完整重启游戏。

`<game_root>` is the folder opened through Steam → Manage → Browse local files.

1. Fully exit the game.
2. Put BigFatFish.pak, BigFatFish.utoc, and BigFatFish.ucas in `<game_root>\Subnautica2\Content\Paks\LogicMods\BigFatFish\`. Put the BigFatFish runtime folder in `<game_root>\Subnautica2\Binaries\Win64\ue4ss\Mods\BigFatFish\`, keeping enabled.txt and the complete Scripts folder.
3. Start the game, load a save, and wait a few seconds before using commands.

The save-data folder is created automatically. Update this mod's assets and scripts together, then fully restart the game.

## 4. 第一次使用 / First use

载入存档、进入开阔水域，等待日志出现 `Game slot ready`（世界就绪后通常约两秒）。按 **F10 或 `~` / 反引号**打开游戏内控制台。

Load a save, enter open water, and wait for `Game slot ready` in the log, usually about two seconds after the world is ready. Open the in-game console with F10 or the tilde/backtick key.

依次输入 / Enter separately:

```text
bigfatfish_spawn 3
bigfatfish_follow
```

随后用游戏自身的“保存”保存。保存完成后再退出；下次进入同一世界，应自动重建已保存的鱼，无需再次召唤。 / Save through the game's own save function and let it finish before quitting. Loading the same world should reconstruct the saved fish without another spawn command.

## 5. 命令表 / Commands

| 命令 / Command | 功能 / Effect |
|---|---|
| `bigfatfish_spawn` | 新增一只，不替换已有的鱼。 / Add one fish without replacing existing fish. |
| `bigfatfish_spawn 5` | 新增五只，总数上限 64。 / Add five; maximum total is 64. |
| `bigfatfish_follow` | 所有鱼进入摄像机前侧两翼队形。第一排约距主角 9～12 米，后排更远。 / All fish follow in front-side wings; the first row is roughly 9–12 m away, with later rows farther out. |
| `bigfatfish_stay` | 所有鱼停留在当前位置，继续游泳动画、表情和注视。 / Stay at the current locations while swim animation, expressions, and gaze continue. |
| `bigfatfish_wander` | 所有鱼从当前位置开始环绕巡游。 / Begin a wandering circle from each current location. |
| `bigfatfish_pause` | 切换位移暂停；不会暂停游泳、眨眼和嘴部动作。 / Toggle movement pause; swim animation, blinking, and mouth motion continue. |
| `bigfatfish_gaze off` | 平滑关闭所有鱼的头眼注视。 / Smoothly disable head/eye tracking for all fish. |
| `bigfatfish_gaze on` | 开启头眼注视，默认开启。 / Enable tracking; enabled by default. |
| `bigfatfish_remove` | 删除本模组当前所有鱼；再进行游戏保存才会持久记录删除。 / Remove all current fish; save the game afterward to persist removal. |
| `bigfatfish_status` | 在 UE4SS.log 查看版本、数量、存档状态、ID、体型、行为和注视状态。 / Log version, count, save readiness, IDs, sizes, behavior, and gaze status. |

除 spawn 数量外，目前没有按 ID 单独控制某一只的命令，也没有嘴型/眨眼命令；嘴部动作和眨眼自动播放。旧 `whale_*` 命令已删除。 / There are no per-ID controls or mouth/blink commands in this version. Facial motion runs automatically. Legacy whale_* commands have been removed.

## 6. 动画、表情与大小 / Animation, expressions, and size

原始 VRM 没有附带全身动画片段。当前游泳来自 Quaternius，头眼注视由程序控制。模型本身提供以下 **16 个面部形态（Morph Targets，不是 16 段动作）**：

The original VRM contains no full-body animation clips. The current swim was retargeted from Quaternius, and gaze is procedural. The model provides **16 facial morphs, not 16 animation clips**:

| 类型 / Type | 原始名称 / Original names | v0.4.0 状态 / Status |
|---|---|---|
| 双眼与单眼眨眼 / Both-eye and single-eye blink | `blink`, `blinkLeft`, `blinkRight` | 已接入双眼随机眨眼；左右单眼形态未接入。 / Both-eye random blinking is active; separate winks are not integrated. |
| 视线形态 / Gaze shapes | `lookup`, `lookDown`, `lookleft`, `lookRight` | 未接入；当前眼神使用眼骨骼。 / Not integrated; current gaze uses eye bones. |
| 五种口型 / Five mouth shapes | `aa`, `ih`, `ou`, `ee`, `oh` | 已接入 aa/ou 的轻微组合；其他口型未接入。 / Subtle aa/ou blending is active; other shapes are not integrated. |
| 情绪 / Emotions | `happy`, `angry`, `sad`, `relaxed` | 原模型自带，当前资源包未接入。 / Available in the source model; not integrated in this package. |

原模型还有名为 `TiePen` 的头发形态，具体视觉用途未验证，不作为现有动作宣传。当前资源包仅保留已使用的 `BFF_Blink`、`BFF_MouthOpen`、`BFF_MouthRound` 三个形态。扩展表情需要重新导出和烹饪，不能只输入原始形态名称来启用。

The source also has a hair shape named TiePen; its visual purpose is unverified. The current package includes only BFF_Blink, BFF_MouthOpen, and BFF_MouthRound. Adding other expressions requires a new asset export and cook; entering their names does not enable them.

眨眼各自随机，间隔约 2.5～7 秒；嘴巴偶尔轻微张合，不含语音或语音同步。眼球追踪限角为 8°，头部 50°，颈部 15°且权重较低；身后死角和远距离会减弱注视。

Blinking is independent, roughly every 2.5–7 seconds. Mouth motion is subtle and intermittent, without voice or lip-sync. Eye tracking is limited to 8°, head tracking to 50°, and neck tracking to 15° with a reduced weight. Gaze fades near the rear dead angle and at long distances.

新生成的鱼按基准**线性尺寸**随机取 0.5～1.5 倍，三个轴同比例缩放；不是数学意义上体积随机取该倍率。基准 `config.lua` 的 Scale 为 2，因此实际 Actor Scale 为 1～3。随机倍率只在召唤时生成并保存，旧鱼没有该字段时保持基准大小。

New fish get a uniform random **linear size multiplier** of 0.5–1.5 relative to the baseline, applied equally to all axes; this is not a volume multiplier. The default config Scale is 2, producing an Actor Scale of 1–3. Each multiplier is generated once and saved. Older fish without a saved multiplier keep the baseline size.

## 7. 保存、备份与卸载 / Saves, backups, and removal

保存的内容 / Saved: 数量、ID、位置、巡游中心、朝向、运动阶段、巡游/停留/跟随行为、随机体型。 / Count, IDs, positions, patrol centers, heading, movement phase, wander/stay/follow mode, and size multiplier.

临时内容 / Session-only: 全局位移暂停、注视开关、眨眼与嘴部动作的随机时间表。 / Global movement pause, gaze toggle, and blink/mouth schedules.

数据目录 / Data folder:

```text
%LOCALAPPDATA%\Subnautica2\Saved\SaveGames\BigFatFish\
```

每个游戏存档只保留一个 `_current.json` 主记录和一个 `.json.bak` 备份，不再生成时间戳快照。目录在首次写入时自动创建。本模组不修改原版 `.sav`。原版回退旧检查点时，本模组仍加载该世界最新的鱼记录，不会自动回退到同一历史时刻。Steam 云同步未验证；备份和迁移时连同上述整个文件夹一起复制。

Each save-world keeps one _current.json file and one .json.bak backup. Timestamped snapshots are no longer generated. The directory is created automatically on first write. The mod does not edit native .sav files. Loading an older native checkpoint still uses that world's latest fish record rather than rolling fish back to the same historical moment. Cloud sync is unverified; copy this entire folder when backing up or moving saves.

卸载时退出游戏，移除本模组的三件套资源及 `ue4ss\Mods\BigFatFish`，不要删除其他 MOD 或整个 UE4SS。可保留附属数据供重新安装恢复；若想先保存一个没有鱼的状态，先运行 remove 再游戏保存。

To uninstall, exit the game and remove only the BigFatFish containers and ue4ss\Mods\BigFatFish. Keep other mods and UE4SS intact. Sidecars may be retained for reinstalling. To save an empty fish state first, use remove and then save the game.

## 8. 限制与排错 / Limits and troubleshooting

- 当前没有地形避障或碰撞，可能穿过地形/建筑；不是可捕捉、战斗、扫描或繁殖的原生生物。 / No obstacle avoidance or collision; fish may pass through terrain or structures. No native capture, combat, scanning, or breeding integration.
- 多人同步、Game Pass、Linux 和实验分支未验证，不标为支持。 / Multiplayer synchronization, Game Pass, Linux, and the experimental branch are unverified.
- 64 是代码上限，不是性能保证；建议先试 1～5 只。 / 64 is a code limit, not a performance guarantee; start with 1–5.
- 不能开控制台：检查控制台键位和键盘布局。 / No console: check your console key binding and keyboard layout.
- 输入无反应：确认日志含 v0.4.2 loaded 与 Game slot ready，使用 bigfatfish_* 命令；检查是否缺少 UE4SS API。 / No response: check for v0.4.2 loaded and Game slot ready, correct command spelling, and missing loader APIs.
- 模型/表情不对：核对三件套与 Lua 是否同版本，完全退出后重启。 / Wrong model or expressions: ensure matching containers and Lua, then fully restart.
- 读档无鱼：先确认原来进行过成功的游戏保存、该世界的附属文件仍在、目录可写；看日志 restored / Saved / Error 信息。 / Missing fish after loading: check that a game save succeeded, sidecars exist for that world, and the folder is writable; inspect restored, Saved, and Error messages.

日志 / Logs:

```text
<game_root>\Subnautica2\Binaries\Win64\ue4ss\UE4SS.log
%LOCALAPPDATA%\Subnautica2\Saved\Logs\Subnautica2.log
```

当前验证依据：编辑器实际头/颈/双眼姿态及限角、形态导入与权重接口、离线运行时/保存测试、资源包完整性校验；真实运行日志已记录 v0.4.0 加载、重建 3 只并保存 4 只。完整画面表现、体型的游戏内重进对比和多人同步未据此认定通过。

Validation includes actual editor head/neck/eye pose and angle-limit checks, imported morphs and weight APIs, offline runtime/save tests, and package integrity checks. Live logs show v0.4.0 loading, restoring three fish, and saving four. These logs do not by themselves verify every visual detail, an in-game size comparison across reloads, or multiplayer synchronization.

## 9. 借物表 / Credits

- **模型 / Model:** 木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》。模型、贴图及原有面部形态归原作者；本模组负责游戏接入和行为，不将模型署为自制。 / Model, textures, and authored facial morphs belong to the original creator. This mod supplies game integration and behavior, not original model authorship.
- **游泳动作 / Swimming animation:** [Quaternius — Universal Animation Library](https://quaternius.com/packs/universalanimationlibrary.html)，Swim_Fwd_Loop，CC0，已重定向并调整。 / Retargeted and adjusted; CC0.
- **运行环境 / Runtime:** [UE4SS-RE / RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) 及随附组件作者 / and bundled component contributors.
- **JSON:** [rxi/json.lua](https://github.com/rxi/json.lua)，MIT；保留随包 json.LICENSE。 / MIT; retain the included json.LICENSE.
- **游戏 / Game:** Unknown Worlds — Subnautica 2。

模型按原作者使用条件与借物署名要求使用；本模组不授予他人超出原授权范围的模型使用权。 / Use the model under its creator's terms and attribution requirements; this mod does not grant additional model rights.

