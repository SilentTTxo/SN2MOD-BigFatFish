# Big Fat Fish — Rice planting prototype / 水稻种植原型

Version / 版本：0.1.0-prototype · Target / 目标：Windows Steam，UE 5.6.1，CL-131439。

此包为单独测试的水稻种植内容，包含原生稻谷物品、水稻建造配方、植株、可采收稻穗及测试命令。米饭制作和召唤大肥鱼在后续阶段接入。本版不修改大肥鱼现有文件。

This separate prototype contains a native rice-grain item, a builder planting recipe, a rice plant, harvestable panicles, and test commands. Cooked rice and fish summoning are later stages. Existing BigFatFish files are not modified.

验证状态 / Validation：已通过编辑器保存后重新加载检查、16 个资源的容器完整性检查、烹饪和游戏启动挂载检查，测试命令已加载。实际种植、采收和存档恢复待验证。 / Passed editor save/reload checks, integrity checks for 16 assets, cooking, native game startup mounting, and test-command loading. Planting, harvesting, and gameplay save restoration remain unverified.

## 依赖 / Requirement

[UE4SS for Subnautica 2](https://www.nexusmods.com/subnautica2/mods/36)

## 安装 / Installation

1. 完全退出游戏。 / Fully exit the game.
2. 将 ZIP 中的 `Subnautica2` 文件夹合并到游戏根目录（Steam → 管理 → 浏览本地文件）。 / Merge the archive's `Subnautica2` folder into the game root opened via Steam → Manage → Browse local files.
3. 启动游戏并载入有原版种植槽/水培设施的存档。 / Start the game and load a save with an unlocked native planter/aquafarm.

本包自己的内容位于 / This package's files are placed in:

```text
<game_root>/Subnautica2/Mods/BigFatFishRice/
<game_root>/Subnautica2/Binaries/Win64/ue4ss/Mods/BigFatFishRice/
```

## 第一轮测试 / First test

打开控制台输入 / Open the console and enter:

```text
bigfatfish_rice_status
bigfatfish_rice_give 3
```

1. 背包中应出现 `Rice Grain / 稻谷`，带稻谷图标。 / Check for Rice Grain in the inventory with its grain icon.
2. 打开建造器，在原版种植/植物分类中寻找 `Rice / 水稻`。当前版本原生作物通过建造器在种植槽表面栽种。 / Open the builder's farming/plants category and find Rice. The target game's farming system places plants on planters using the builder.
3. 消耗 1 份稻谷栽种一株，等待约 60 秒，尝试采收成熟稻穗。 / Spend one rice grain to plant a stalk, wait roughly 60 seconds, and try harvesting its ripe panicles.
4. 分别在生长中、成熟后、采收后使用游戏自身的保存，退出并重新载入，检查植株和背包物品。 / Save with the game's own save function while growing, when ripe, and after harvesting; quit/reload and check plants and inventory.

60 秒是方便测试的暂定周期。水稻模型为本项目程序制作的原型。存活茎叶与可采收稻穗分开；稻穗通过原生种子生长组件成熟。是否按预期再次结穗，以及保存后的生长进度，需要游戏内验证。

The 60-second cycle is provisional for testing. Geometry is authored procedurally for this project. Stalks and harvestable panicles are separate meshes; the panicles ripen through the native seed grower. Regrowth and saved growth progress require in-game verification.

## 保存 / Saving

本原型使用游戏的原生背包、建造物及 `UWESaveComponent` 保存。不会生成额外的水稻 JSON 或按时间增长的备份文件。最终效果以游戏内保存/重载测试为准。

This prototype uses native inventory/buildable saving and UWESaveComponent. It creates no rice JSON sidecars or accumulating timestamped backups. Actual persistence remains subject to in-game save/reload tests.

## 排错与卸载 / Troubleshooting and removal

- `native rice item mounted=false`：检查内容包目录，完全重启游戏。 / Check the native content directory and fully restart the game.
- 有稻谷但建造菜单没有水稻：保留日志，检查原版种植设施是否已经解锁。 / Keep logs and check whether native farming is unlocked.
- 无法栽种、采收或读档恢复：记录操作时机与日志，不代表这些环节已经验证成功。 / Record the operation and logs if planting, harvesting, or persistence fails; these remain test points.
- 日志 / Log：`<game_root>/Subnautica2/Binaries/Win64/ue4ss/UE4SS.log`，搜索 / search `BigFatFishRice`。
- 卸载前建议先在游戏内拆除水稻、清空稻谷并保存，再退出游戏移除上述两个 `BigFatFishRice` 文件夹。 / Before uninstalling, remove rice plants and grains in-game and save, then exit and remove the two BigFatFishRice folders listed above.

## 资源 / Assets

水稻、稻穗、稻谷模型和图标由 `Scripts/create_rice_assets.py` 使用 Blender 制作；原型使用原版种植分类和放置规则。 / Rice geometry and the grain icon are authored with Blender by Scripts/create_rice_assets.py; the prototype uses the game's native farming category and planter rules.

开发命令 / Development commands:

```text
python Scripts/rice_workflow.py prepare
python Scripts/rice_workflow.py import
python Scripts/rice_workflow.py verify
python Scripts/rice_workflow.py cook
python Scripts/rice_workflow.py package
python Scripts/rice_workflow.py install
```

开发环境沿用本项目定制引擎和 Modkit；prepare 会在 Build/Tests 中创建隔离工程。 / Development reuses the matched custom editor and local Modkit; prepare creates an isolated workspace under Build/Tests.
