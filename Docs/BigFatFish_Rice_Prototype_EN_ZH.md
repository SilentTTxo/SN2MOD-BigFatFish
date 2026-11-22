# Sea Rice / 海稻 — 0.4.0-prototype

Included in Big Fat Fish 0.6.0-dev / 包含于大肥鱼 0.6.0-dev 完整包。

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


## 保存 / Saving

作物、野生作物和食品走游戏原生保存，无额外 JSON。野生作物使用原生动态物体登记与固定 GUID，避免每次读档重复生成。作物材料自发光为零。新功能的实机表现与保存恢复需复测。

Crops, wild crops and food use native saves without new JSON files. Wild plants use native dynamic-item registration and stable GUIDs to avoid duplication across reloads. Crop materials have zero emissive output. The new features and native persistence still require in-game retesting.

完整命令、手势、保存说明和借物表见 BigFatFish_User_Guide_EN_ZH.md。 / See BigFatFish_User_Guide_EN_ZH.md for commands, gestures, saving and credits.
