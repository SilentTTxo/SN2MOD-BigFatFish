# Big Fat Fish 存档接入记录

v0.4.1：首次写入时自动创建存档目录；每个 SaveId 仅保留一个当前 JSON 和一个 .bak，停止生成时间戳历史快照。现有历史快照已归档到开发目录 Build/Backups/SaveSnapshots_20261102_v041。

v0.2.1 修复：原 v0.2.0 的游戏实测已确认 JSON 正常写入，但读档后未命中时间戳记录，出现恢复零只。改为 SaveId 主记录，历史检查点仅作快照备份，不用最新文件猜槽位。按用户要求不迁移/恢复旧鱼。

当前游戏：public / UE 5.6.1 / CL-131439。此记录区分代码核对与游戏实测。

## 调研结论

- 社区 Mariana.SaveData 使用 onSave/onLoad 回调，将每个 MOD 的 JSON 数据与游戏槽位关联。它并不把任意 Lua table 直接嵌入原生 .sav。
- 已阅读文档和实际源码。其默认 hook 猜测 SN2SaveManager.SaveGame / GameplayStatics.SaveGameToSlot，当前版本无法据此确认可靠性；本模组不引入该框架，也不使用无法识别槽位时的 default 回退。
- 当前 modkit 的 jmap 直接列出了 UWESaveSystem 反射类，已据此确定下列真实接口。接口存在不等于游戏路径已实测触发。

## 当前版本的真实接口

`UWESaveGameSubsystem.SaveContext.ActiveSave` 是当前存档对象。
`SaveContext.SaveGameCollection.ContainerInfo.SaveId` 用于集合身份；集合不可用时使用当前 MetaData.SaveId。
`ActiveSave.MetaData.LastModified` 只用作诊断/快照标签，不再作为读档查找的必要条件，`ActiveSave:GetSlotName()` 只作为槽位标签。
保存完成通知：

- `/Script/UWESaveSystem.UWESaveCommunicationComponent:AsyncSaveGameCompleted(Result)`
- `/Script/UWESaveSystem.UWESaveCommunicationComponent:AutoSaveCompleted(Result)`

只在 Result=true 时落盘。额外轮询 `UWESaveGameSubsystem:GetLastSaveToDiscTimeStamp()`，补偿未收到的成功通知。不会凭磁盘最新文件推测当前槽位。

加载时必须有真实 SN2PlayerCharacter、有效存档身份，并在同一世界连续稳定三次，随后重建一次。切换存档/世界会释放旧实例。未知槽位拒绝生成，避免写错存档。

## 数据与原生存档的关系

`SaveGames/BigFatFish/<SaveId>_current.json` 是当前世界的主记录；仅轮换 `<SaveId>_current.json.bak` 一份备份，不再写历史快照。包含 version=1、saveId、checkpoint（诊断标签）、槽位标签、鱼列表。每只保存 id、position、yaw、center、phase、startAngle、mode、size，不保存 UObject 指针。

只有原生保存成功才更新模组主记录。加载由真实 SaveId 隔离，不因 ActiveSave 内存时间戳变化而丢失。不自动读取旧版 timestamp-only 文件；用户将重新生成测试。原版旧检查点回退与 MOD 历史状态未实现联动，此版本恢复该世界最新成功保存的 MOD 状态。

临时文件、flush/close、Windows 备份再改名提交；损坏主文件尝试 .bak。版本、身份、检查点、数值和数组均验证。读到无法恢复的数据时保留文件并停止覆盖。

这属于与游戏存档生命周期关联的 MOD 数据，而非全局配置。迁移或备份游戏存档时需一起复制本文件夹；Steam 云同步覆盖范围未验证。

## 为什么暂不直接嵌入 .sav

原生 `UWESaveComponent`、`UWESaveHandle`、`RegisterCustomSaveGameInfo` 确实存在，但仅给临时 SkeletalMeshActor 增加保存组件，并不会自动序列化 Lua 表或注册其世界重建。原生记录还涉及类路径、SaveHandle、序列化回调和升级机制。未确认契约前向 .sav 注入记录不能算可靠接入。

当前方案实现独立数据记录并跟随原生保存/加载，不依赖修改原生存档格式。未来改为原生生物类时需进一步验证上述原生对象生命周期。

## 验证状态

离线测试已覆盖多实例、帧率无关移动、跟随、停留、保存成功/失败、只恢复一次、时间戳变化回归、不同存档隔离、删除持久化、损坏备份和提交失败。原生保存回调已在游戏中确认写入三只鱼；修复读取逻辑后的完整退出/重启读档仍待实测，不能将离线通过记作游戏验证成功。

## 参考

- https://github.com/GOD-GAMER/mariana-sn2/blob/main/docs/api/savedata.md
- https://github.com/GOD-GAMER/mariana-sn2/blob/main/Subnautica2/Binaries/Win64/Mods/Mariana/Scripts/api/savedata.lua
- https://docs.ue4ss.com/lua-api/global-functions/registerhook.html
- 本机 Modkit/Content/DynamicClasses/Subnautica2-131439.jmap.gz；提取的接口摘要 Logs/save_api.txt。

JSON 编解码器：https://github.com/rxi/json.lua （MIT）；Mariana 仅作研究参考，未复制其实现或作为依赖。


## 0.6.0 wild crop integration / 野生海稻

Wild plants use `UWEDynamicItemsManager:SpawnActorAndRegisterWithoutDropping` with a stable GUID derived from the native SaveId and one of eight population indices. The native `DynamicItemsSave.DynamicItems` and `ActiveActorsByID` maps are checked before spawning; an existing or streamed-out native record suppresses respawning. The plant Blueprint carries the same native save and grower components as the planted crop, with only `bStartsGrown=True` on the wild archetype. Native removal-out-of-range is disabled for these registered plants. Ground tracing is restricted to WorldStatic terrain and suitable slopes. No additional JSON file is created. Native runtime persistence still needs an in-game save/reload test.

野生海稻通过原生动态物体管理器登记，固定 GUID 来自原生 SaveId 和八个种群索引。生成前检查原生保存记录与活跃物体映射，已保存或流送卸载的植株不会重复补种。沿用种植版的原生保存、生长组件，野生资源默认成熟；不写新的 JSON。实机生长状态与原生保存恢复仍待验收。

Fish snapshots additionally save an optional boolean `basinMode`; legacy records default to no basin. Emotions, props, UObjects and unfinished feeding sequences are not serialized. A dropped serving is consumed only at the actual grab; inventory APIs are never called by the offering module. The existing one JSON + one backup policy is unchanged.


0.6.1 correction: GUIDs remain SaveId-scoped, but placement no longer depends on SaveId. Eight literal offsets define a fixed layout relative to the lifepod. An unloaded/unsuitable point is retried at exactly the same X/Y; no alternate candidate is selected. Existing native GUID records are never moved, deleted or replaced by this change.

0.6.1 修正：SaveId 仅用于 GUID 隔离，生成位置改为八个固定偏移。地形检测失败只在同一点重试，不换位置。原生存档中已有植株的位置不作迁移、删除或替换。
