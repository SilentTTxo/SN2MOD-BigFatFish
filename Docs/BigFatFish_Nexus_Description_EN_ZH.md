# Big Fat Fish

Version / 版本：0.6.0-dev (development / 开发测试版)

Swimming whale-girl companions with formation following, gaze, blinking, facial reactions and a handheld basin. Grow Sea Rice, cook Steamed Rice, then leave a dropped bowl for more than three seconds to attract a new companion. Eating it yourself restores 25 food instead.

鲸鱼娘外观的游泳伙伴，支持僚机跟随、注视、眨眼、情绪和手持饭盆。种海稻、做大白饭，丢下一碗超过三秒，引来一只新伙伴抢饭后跟随。自己吃饭只恢复 25 饱食度。

## 依赖 / Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

## 安装 / Installation

1. 完全退出游戏。 / Fully exit the game.
2. 将 ZIP 中的 `Subnautica2` 文件夹合并到 Steam“管理 → 浏览本地文件”打开的游戏根目录，更新时覆盖本模组同名文件。 / Merge the ZIP's `Subnautica2` folder into the game root opened through Steam → Manage → Browse local files; replace this mod's matching files when updating.
3. 启动游戏并载入存档。 / Start the game and load a save.

模组自动创建数据目录，不需要手动创建存档文件夹。 / The mod creates its save-data directory automatically.

## 海稻与大白饭 / Sea Rice and Steamed Rice

救生舱附近约 25–50 米的合适海底，会随机分布最多八株野生海稻。采收后保留一些海稻，在建造器的种植/植物分类消耗一份，栽种到原版种植槽。测试生长周期为 60 秒。装配台餐食分类：一份海稻 + 一瓶净水，五秒制作一碗大白饭。

Up to eight wild Sea Rice plants are distributed on suitable seabed roughly 25–50 m from the lifepod. Harvest and keep some grains for planting through the builder's farming/plants category on a native planter. The provisional growth cycle is 60 seconds. Fabricator → Meals: one Sea Rice Grain + one Water makes one Steamed Rice in five seconds.

**吃大白饭只恢复 25 饱食度，不召唤。** 将大白饭丢到世界里，连续超过三秒后吸引一只新大肥鱼。鱼从身后接近掉落的饭碗，伸手抓取、吃完后加入原有僚机跟随。每碗只触发一次；提前捡回或抢饭前捡回会取消，不额外扣除背包物品。演出中可关闭 PDA 观看。

**Eating rice restores 25 food and does not summon.** Drop a bowl into the world and leave it there for more than three seconds. A new fish approaches from behind, grabs the dropped bowl, eats, then joins the existing companion formation. One bowl triggers once. Picking it up before the grab cancels the offering without an extra inventory charge. Close the PDA to watch the sequence.

新增文本使用原生 FText 本地化：中文游戏只显示中文，其他语言显示英文。 / Native FText localization displays Chinese for Chinese game languages and English for all others.

## 手势 / Gestures

影响主角周围 30 米内的大肥鱼。 / Affects Big Fat Fish within 30 m of the player.

| 手势 / Gesture | 反应 / Reaction |
| --- | --- |
| 鼓掌 / Clap | 切换手持饭盆形态，再次鼓掌收起。饭盆由大肥鱼双手捧着。 / Toggle the original basin held in the fish's hands. |
| 挥手 / Wave | 切换巡游与僚机跟随。 / Toggle wander and wing formation follow. |
| 点赞 / Thumbs up | happy 表情，约七秒后恢复。 / Happy expression, fading after about seven seconds. |
| 沮丧 / Frustrated | sad 表情。 / Sad expression. |
| 差评 / Thumbs down | angry 表情。 / Angry expression. |

原有游泳、头颈注视、8° 眼球限角、随机眨眼、轻微嘴型保留。新鱼随机线性大小为基准的 0.5–1.5 倍。 / Existing swim, head/neck gaze, 8° eye clamps, random blinks and subtle mouth motion remain. New fish have a saved random linear size of 0.5–1.5× the baseline.

## 保存与限制 / Saving and limitations

使用游戏自身的保存。鱼的数量、位置、行为、大小、饭盆开关保存在 `%LOCALAPPDATA%\Subnautica2\Saved\SaveGames\BigFatFish\`，每个世界只有一个 `_current.json` 和一个 `.json.bak`。临时情绪和进食演出不保存；抢到饭之后的新鱼作为普通同伴保存。海稻、野生海稻和大白饭使用游戏原生保存机制；野生植株通过固定 GUID 登记为原生动态物体，读档不重新灌入一批成熟作物。

Use the game's save function. Fish count, transforms, behavior, size and basin toggle use one `_current.json` and one `.json.bak` per world in the path above. Temporary emotions and feeding progress are not saved. After grabbing its serving, the new fish is saved as a normal companion. Crops, wild crops and rice use native saves; stable GUIDs register wild plants with the native dynamic-item manager to prevent reseeding a fresh ripe population on every load.

回退游戏旧检查点时，鱼仍使用该世界最新的附属记录；云同步未验证。当前鱼没有碰撞和地形避障。多人、实验分支、Game Pass、Linux 未验证。0.6.0 的资源、语言切换、离线行为与打包检查通过；新演出、手势、野生海稻保存及崩溃修复仍需本机游戏复测。

Reverting a native checkpoint still uses the latest fish sidecar for that world; cloud sync is unverified. Fish have no collision or obstacle avoidance. Multiplayer, experimental builds, Game Pass and Linux are unverified. Version 0.6.0 passes asset, culture-switch, offline behavior and packaging checks; its new sequence, gestures, wild-crop persistence and crash fix still require in-game retesting.

日志 / Logs: `<game_root>/Subnautica2/Binaries/Win64/ue4ss/UE4SS.log`, `%LOCALAPPDATA%/Subnautica2/Saved/Logs/Subnautica2.log`.

卸载前移除种植物和新物品并保存，再退出游戏，仅移除本包安装的 BigFatFish、BigFatFishRice 目录与资源。附属鱼记录可以保留。 / Before uninstalling, remove crops and custom items in-game and save; then exit and remove only this package's BigFatFish and BigFatFishRice files. Fish sidecars may be kept.

## 借物表 / Credits

- 模型、贴图、饭盆及原有形态 / Model, textures, original basin and morphs：**木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》**。
- 游泳 / Swim：Quaternius Universal Animation Library, Swim_Fwd_Loop (CC0).
- JSON：rxi/json.lua (MIT), license included in `Scripts/json.LICENSE`.
- 海稻、米饭道具和抢饭/手持动作由本项目制作。 / Crop, rice props and feeding/hold gestures authored for this project.
