# Big Fat Fish — Sea Rice / 海稻

Version / 版本：0.3.0-prototype · Windows Steam，UE 5.6.1，CL-131439。

增加海稻、可采收海稻谷和装配台的大白饭配方。海稻使用更圆润的几何、平滑法线和颜色贴图，稻穗以植株顶端为生长原点。另附的大肥鱼 0.5.0 更新修复眨眼、嘴型启用时脸部材质回退的问题。

Adds Sea Rice, harvestable grains, and a Steamed Rice recipe at the fabricator. The crop has smoother geometry, smooth normals, color textures, and panicles that grow around the crown. The separate Big Fat Fish 0.5.0 update fixes face materials falling back when blink or mouth morphs activate.

种植、采收、大白饭制作已由玩家验收。本版修正网格仍绑定灰色默认材质的问题、原生生长提示键及顶部稻穗定位，并接入大白饭抢饭召唤；这些修改的游戏内效果仍待验收。

Planting, harvesting and Steamed Rice crafting have been accepted by the player. This version repairs default-gray material bindings, the growth hint key and the crown anchor, and adds rice-based fish summoning. The changes still require in-game validation.

## 依赖 / Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

## 安装 / Installation

1. 完全退出游戏。 / Fully exit the game.
2. 将 ZIP 中的 `Subnautica2` 文件夹合并到游戏根目录（Steam → 管理 → 浏览本地文件），更新时覆盖本模组同名文件。 / Merge the archive's `Subnautica2` folder into the game root opened via Steam → Manage → Browse local files; replace this mod's matching files when updating.
3. 启动游戏，载入已解锁原版种植设施的存档。 / Start the game and load a save with native farming unlocked.

## 使用 / Use

控制台测试命令 / Console test commands:

```text
bigfatfish_rice_give 3
bigfatfish_rice_status
```

1. 背包获得 `Sea Rice Grain / 海稻谷`。 / Receive Sea Rice Grain in your inventory.
2. 在建造器的原版种植/植物分类选择 `Sea Rice / 海稻`，消耗 1 份海稻谷栽种在原版种植槽上。 / Choose Sea Rice in the builder's farming/plants category and spend one grain to plant it on a native planter.
3. 等待约 60 秒采收成熟稻穗；60 秒为测试周期。 / Harvest ripe panicles after roughly 60 seconds; this duration is provisional for testing.
4. 在装配台的餐食分类寻找 `Steamed Rice / 大白饭`。1 份海稻谷 + 1 瓶水 → 1 碗大白饭，制作时间 5 秒。新版大白饭用于喂鱼，不再给玩家增加饱食度或水分。 / Find Steamed Rice in the fabricator's Meals category. One Sea Rice Grain + one bottle of Water yields one bowl in five seconds. It is now an offering for the fish, without restoring player food or water.
5. 使用游戏自身的保存，分别检查生长中、成熟、采收后和制作米饭后的保存/重载。 / Use the game's save function and check save/reload while growing, when ripe, after harvesting, and after crafting rice.

更新保留原有资源 ID。顶部定位修正也会处理当前世界中已存在且仍归属植株的稻穗，不移动已采收/掉落的物品。

Asset IDs are retained. Crown anchoring also corrects existing panicles still owned by a grower; harvested or dropped items are not repositioned.

## 大白饭召唤 / Summoning with rice

使用 Big Fat Fish 0.5.0 完整包。大白饭制作配方不变；在背包使用一碗大白饭，会显示饭碗，一只新鲸鱼娘从玩家身后绕到前方，伸手抢走、吃饭，随后加入跟随。

Use the complete Big Fat Fish 0.5.0 package. The crafting recipe is unchanged. Using Steamed Rice shows a bowl; a new companion swims from behind the player, reaches for the bowl, eats, and joins formation following.

约 1.6 秒抢到饭时才扣除 1 份，约 4.8 秒完成。过程中再次使用不会再扣物品；启动失败或抢到前缺少米饭则取消。单机/本地主角逻辑已做离线检查，联网行为未验收。动画对位、游戏内使用入口及演出需实机验收。

One serving is deducted at the grab around 1.6 seconds, and the sequence finishes around 4.8 seconds. Repeated uses during an active sequence spend no additional rice. Missing food or startup failure cancels the arrival. Local-player transaction logic has offline coverage; multiplayer, the in-game use entry point and visual alignment remain unverified.

吃完后使用游戏保存，保存新同伴。临时饭碗不写入大肥鱼 JSON，尚未抢到饭的新鱼也不会写入同伴存档。

Save the game after feeding to keep the companion. Temporary bowls are not written to the companion JSON, and an unpaid arrival is not persisted as a companion.

## 保存 / Saving

海稻和大白饭接入原生物品、建造和保存组件，不创建额外 JSON 数据目录。保存恢复效果仍需游戏内验收。

Sea Rice and Steamed Rice use native items, construction, and save components. They create no extra JSON data directory. Persistence still requires in-game validation.

## 排错与卸载 / Troubleshooting and removal

- 新版菜谱未出现：完全重启游戏，确认 `BigFatFishRice` 内容包目录正确，并保留日志。 / If the new recipe is missing, fully restart the game, verify the BigFatFishRice content location, and keep the logs.
- 日志 / Log：`<game_root>/Subnautica2/Binaries/Win64/ue4ss/UE4SS.log`，搜索 / search `BigFatFishRice`；游戏日志 / game log：`%LOCALAPPDATA%/Subnautica2/Saved/Logs/Subnautica2.log`。
- 卸载前在游戏中拆除海稻、清空海稻谷和大白饭并保存，再退出，移除本包的两个目录。 / Before uninstalling, remove the crop, grains and cooked rice in-game and save; then exit and remove the two directories below.

```text
<game_root>/Subnautica2/Mods/BigFatFishRice/
<game_root>/Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFishRice/
```

## 开发 / Development

海稻、谷粒、碗饭、贴图和图标为本项目使用 Blender 程序制作的原创原型，使用原版种植/餐食分类及原生放置规则。

The crop, grains, rice bowl, textures and icons are original procedural Blender assets authored for this project. Native farming/meal categories and planter rules are reused.

```text
python Scripts/rice_workflow.py prepare
python Scripts/rice_workflow.py import
python Scripts/rice_workflow.py verify
python Scripts/rice_workflow.py cook
python Scripts/rice_workflow.py package
python Scripts/rice_workflow.py install
```

开发沿用本项目匹配的定制引擎和 Modkit；prepare 在 Build/Tests 创建隔离工程。 / Development reuses the matched custom editor and local Modkit; prepare creates an isolated project in Build/Tests.
