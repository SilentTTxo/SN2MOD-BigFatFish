# Big Fat Fish — Sea Rice / 海稻

Version / 版本：0.2.0-prototype · Windows Steam，UE 5.6.1，CL-131439。

增加海稻、可采收海稻谷和装配台的大白饭配方。海稻使用更圆润的几何、平滑法线和颜色贴图，稻穗以植株顶端为生长原点。另附的大肥鱼 0.4.2 更新修复眨眼、嘴型启用时脸部材质回退的问题。

Adds Sea Rice, harvestable grains, and a Steamed Rice recipe at the fabricator. The crop has smoother geometry, smooth normals, color textures, and panicles that grow around the crown. The separate Big Fat Fish 0.4.2 update fixes face materials falling back when blink or mouth morphs activate.

种植和采收已由玩家验收。新版外观、米饭制作/食用、再次结穗和存档恢复仍需游戏内验证。大白饭召唤大肥鱼尚未接入。

Planting and harvesting have been accepted by the player. Updated visuals, crafting/consumption, regrowth, and save restoration still need in-game validation. Summoning a fish with Steamed Rice is not implemented yet.

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
4. 在装配台的餐食分类寻找 `Steamed Rice / 大白饭`。1 份海稻谷 + 1 瓶水 → 1 碗大白饭，制作时间 5 秒。物品配置为可从背包食用，食物 +25、水分 +5，实际效果待验收。 / Find Steamed Rice in the fabricator's Meals category. One Sea Rice Grain + one bottle of Water yields one bowl in five seconds. It is configured as inventory-consumable with +25 food and +5 water; actual behavior needs validation.
5. 使用游戏自身的保存，分别检查生长中、成熟、采收后和制作米饭后的保存/重载。 / Use the game's save function and check save/reload while growing, when ripe, after harvesting, and after crafting rice.

旧版已存在的稻穗如位置异常，先采收一次并等待重新结穗，或对比新栽的海稻；更新保留原有资源 ID，不会主动删除植株或背包物品。

If panicles created by the previous version are misplaced, harvest once and wait for regrowth, or compare with a newly planted crop. Asset IDs are retained; the update does not delete plants or inventory items.

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
