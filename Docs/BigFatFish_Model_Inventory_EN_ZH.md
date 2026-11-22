# Big Fat Fish — Model inventory / 模型动作与道具清单

检查来源 / Inspected sources：作者提供的原始 VRM、项目 Blender 源文件与当前游戏导出。 / Original creator-provided VRM, project Blender scene, and current game export.

模型 / Model：木子恶魔 / MZEM —《蓝色小肥鱼 Deepseek 鲸鱼娘 VRM》。

## 当前模组 / Current mod

| 功能 / Feature | 状态 / Status |
| --- | --- |
| 循环游泳 / Swimming loop | 已接入，约 2 秒循环，Quaternius 动作重定向。 / Integrated, roughly two seconds, retargeted from Quaternius. |
| 伸手、抢饭、捧饭 / Reach, grab and hold food | 新制 4.8 秒动作，叠在原游泳姿态上，游戏内效果待验收。 / Newly authored 4.8-second gesture over the swim pose; in-game validation pending. |
| 吃饭嘴部动作 / Eating mouth motion | 使用原有嘴型形态程序驱动，与抢饭流程同步；待游戏内验收。 / Procedurally driven original mouth morphs synchronized with feeding; in-game validation pending. |
| 随机眨眼、轻微嘴部动作 / Random blink and soft mouth motion | 已接入三个形态：BFF_Blink、BFF_MouthOpen、BFF_MouthRound。 / Three imported targets: BFF_Blink, BFF_MouthOpen and BFF_MouthRound. |
| 头颈、眼球追踪 / Head, neck and eye tracking | 骨骼程序控制，眼球夹角仍限制为 8°。 / Procedural bone tracking; eye angles remain clamped to 8 degrees. |
| 僚机跟随、巡游、停留 / Formation follow, wander, stay | 运行时移动逻辑，不是模型自带动画。 / Runtime locomotion behavior, not original model animation clips. |
| 盛饭碗、空饭碗 / Full and empty rice bowls | 本项目新制道具，供抢饭与吃完后的空碗切换。 / Newly authored props for the feeding sequence. |

## 原始 VRM 自带 / Included in the original VRM

| 类型 / Type | 原始名称 / Original names | 当前游戏接入 / Current game integration |
| --- | --- | --- |
| 眨眼 / Blinks | blink、blinkLeft、blinkRight | 仅双眼 blink 已导出。 / Combined blink only. |
| 嘴型 / Mouth shapes | aa、ih、ou、ee、oh | aa、ou 已导出，其他尚未导入。 / aa and ou imported; others not imported. |
| 情绪 / Emotions | happy、angry、sad、relaxed | 原包有形态，当前未导入。 / Present in the source, not imported. |
| 眼神形态 / Gaze morphs | lookup、lookDown、lookleft、lookRight | 当前用骨骼追踪代替这些形态。 / The mod uses bone tracking instead. |
| 饭盆形态 / Basin morph | TiePen，位于 hair 网格；有独立 TiePen 材质和 TiPen_Color_Studio 贴图 | 原包确实包含；当前导出未保留此形态开关。本次抢饭使用新制饭碗。 / Confirmed in the original; its morph toggle is not preserved in the current game export. Feeding uses the new bowl prop. |
| VRM 弹簧骨 / VRM spring bones | 头发、耳部等的弹簧骨和碰撞配置 / Hair, ear and other spring/collider settings | 尚未移植为 UE 实时物理；不等于现成动作片段。 / Not ported to UE runtime physics; these are not animation clips. |

原始 VRM 的 `animations` 列表为空，因此没有自带可直接播放的游泳、吃饭、跳舞动作。`neutral`、`surprised` 预设名称存在，但没有绑定对应形态；不能把它们计为已经可用的表情。

The original VRM has no animation clips. Its neutral and surprised preset names have no bound morphs, so they are not counted as usable expressions.

Blender 工程还保存了 Quaternius 参考人形的多个动作，当前只有游泳完成了鲸鱼娘重定向；它们不能直接算作鲸鱼娘已经支持的动作。本版抢饭动作为项目自行制作的手臂动作叠加。

The Blender scene also contains multiple Quaternius reference-mannequin clips. Only swimming was retargeted to this character; the other reference clips are not ready-to-use character actions. The feeding gesture is newly authored for this project.
