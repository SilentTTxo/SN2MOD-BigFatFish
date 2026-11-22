import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Logs/BigFatFish_Feeding_Preview.blend'))
s=bpy.context.scene
s.frame_set(75);s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
if s.render.engine=='CYCLES':s.cycles.samples=12
s.render.filepath=str(R/'Logs/feeding_gesture_preview.png');bpy.ops.render.render(write_still=True)
