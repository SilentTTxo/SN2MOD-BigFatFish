"""Author original low-poly rice plant/grain geometry in Blender; metres, Z-up."""
import bpy
import json
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SourceAssets/Rice"
EXPORT = OUT / "Export"
EXPORT.mkdir(parents=True, exist_ok=True)
(ROOT / "Logs/rice").mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(22026)
materials = []
for name, color in (("RiceStem", (.15,.35,.035,1)), ("RiceLeaf", (.23,.52,.055,1)),
                    ("RiceGrain", (.77,.48,.12,1)), ("RiceGrainLight", (.95,.70,.24,1))):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = .8
    materials.append(material)

class Geometry:
    def __init__(self):
        self.vertices=[]; self.faces=[]; self.slots=[]

    def polygon(self, points, slot):
        offset=len(self.vertices)
        self.vertices.extend(tuple(p) for p in points)
        self.faces.append(tuple(range(offset, offset+len(points))))
        self.slots.append(slot)

    def tube(self, points, radius, slot, sides=5):
        rings=[]
        for i,p in enumerate(points):
            tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
            tangent.normalize()
            side=tangent.cross(Vector((1,0,0)))
            if side.length < .01: side=tangent.cross(Vector((0,1,0)))
            side.normalize(); up=tangent.cross(side).normalized()
            rings.append([Vector(p)+(side*math.cos(a)+up*math.sin(a))*radius
                          for a in [j*math.tau/sides for j in range(sides)]])
        for a,b in zip(rings,rings[1:]):
            for j in range(sides): self.polygon([a[j],a[(j+1)%sides],b[(j+1)%sides],b[j]],slot)
        self.polygon(list(reversed(rings[0])),slot)
        self.polygon(rings[-1],slot)

    def grain(self, center, direction, size, slot):
        center=Vector(center); axis=Vector(direction).normalized()
        x=axis.cross(Vector((0,0,1)))
        if x.length<.01: x=Vector((1,0,0))
        x.normalize(); y=axis.cross(x).normalized()
        rings=[]
        for row in range(5):
            angle=math.pi*row/4
            rings.append([center + axis*(math.cos(angle)*size*2.6)
                          +(x*math.cos(t)+y*math.sin(t))*math.sin(angle)*size
                          for t in [j*math.tau/6 for j in range(6)]])
        for a,b in zip(rings,rings[1:]):
            for j in range(6): self.polygon([a[j],a[(j+1)%6],b[(j+1)%6],b[j]],slot)

    def object(self,name):
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices,[],self.faces); mesh.update()
        obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
        for material in materials: mesh.materials.append(material)
        for poly,slot in zip(mesh.polygons,self.slots): poly.material_index=slot
        return obj

g=Geometry()
for stem in range(6):
    theta=stem*math.tau/6+.3
    direction=Vector((math.cos(theta),math.sin(theta),0))
    base=direction*.012
    height=.60+random.random()*.18
    points=[base+Vector((0,0,height*t))+direction*(.035*t*t) for t in [0,.25,.5,.75,1]]
    g.tube(points,.0028,0)
    for layer in range(3):
        z=height*(.18+layer*.19)
        bearing=theta+(math.pi if layer%2 else 0)+.5
        forward=Vector((math.cos(bearing),math.sin(bearing),0))
        sideways=Vector((-forward.y,forward.x,0))
        start=base+Vector((0,0,z))
        rows=[]
        for t in [0,.2,.4,.6,.8,1]:
            center=start+forward*(.24*t)+Vector((0,0,.17*math.sin(t*2.1)))
            width=.014*(math.sin(math.pi*t)**.8)
            rows.append([center-sideways*width,center+Vector((0,0,.0025*math.sin(math.pi*t))),center+sideways*width])
        for a,b in zip(rows,rows[1:]):
            g.polygon([a[0],b[0],b[1],a[1]],1)
            g.polygon([a[1],b[1],b[2],a[2]],1)
    top=points[-1]
    panicle=[top+direction*(.10*t)+Vector((0,0,.07*math.sin(math.pi*t)-.055*t)) for t in [0,.2,.4,.6,.8,1]]
    g.tube(panicle,.0018,2)
    for j in range(7):
        t=(j+1)/8
        center=top+direction*(.10*t)+Vector((0,0,.07*math.sin(math.pi*t)-.055*t))
        for sign in (-1,1):
            side=Vector((-direction.y,direction.x,0))*sign
            tip=center+side*(.022*(1-t)+.008)+Vector((0,0,-.015))
            g.tube([center,tip],.0008,2,3)
            g.grain(tip,side*.3+Vector((0,0,-1)),.0034,2+(j%2))
plant=g.object("SM_BFF_RicePlant")
stalk_geometry=Geometry();panicle_geometry=Geometry()
for face,slot in zip(g.faces,g.slots):
    (stalk_geometry if slot<2 else panicle_geometry).polygon([g.vertices[i] for i in face],slot)
stalk=stalk_geometry.object("SM_BFF_RiceStalk")
panicle=panicle_geometry.object("SM_BFF_RicePanicle")
stalk.hide_render=True;panicle.hide_render=True
grain_geometry=Geometry()
for i in range(7):
    angle=i*math.tau/7
    grain_geometry.grain((.009*math.cos(angle),.009*math.sin(angle),.006),(.3*math.cos(angle),.3*math.sin(angle),1),.0027,2+i%2)
grain=grain_geometry.object("SM_BFF_RiceGrain")

manifest={"status":"prototype geometry; native planting validation pending", "units":"metres; exported FBX converts to cm", "pivot":"soil/base origin", "provenance":"Original procedural geometry authored by Scripts/create_rice_assets.py; no external model or texture", "assets":[]}
for obj in (plant,grain,stalk,panicle):
    bpy.ops.object.select_all(action="DESELECT");obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(EXPORT/(obj.name+".fbx")), use_selection=True, object_types={"MESH"},
        axis_forward="-Y",axis_up="Z",apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
    obj.data.calc_loop_triangles()
    manifest["assets"].append({"name":obj.name,"triangles":len(obj.data.loop_triangles),"dimensions_metres":list(obj.dimensions),"material_slots":len(obj.data.materials),"collision":"configured on native plant template during import"})
grain.hide_render=True
bpy.ops.object.camera_add(location=(1.25,-1.75,.95))
camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.38))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type="ORTHO";camera.data.ortho_scale=1.05
scene=bpy.context.scene;scene.camera=camera
scene.render.engine="CYCLES";scene.cycles.samples=24
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("RicePreviewWorld")
scene.world.color=(.15,.15,.15)
for location,power,size in [((1,-2,3),280,3),((-2,-1,1),160,2)]:
    bpy.ops.object.light_add(type="AREA",location=location)
    bpy.context.object.data.energy=power;bpy.context.object.data.shape="DISK";bpy.context.object.data.size=size
    bpy.context.object.rotation_euler=(Vector((0,0,.3))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
scene.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Rice_Prototype.blend"))
scene.render.filepath=str(ROOT/"Logs/rice/rice_preview.png");bpy.ops.render.render(write_still=True)
plant.hide_render=True;grain.hide_render=False
camera.location=(.06,-.08,.065);camera.rotation_euler=(Vector((0,0,.006))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.045
scene.render.resolution_x=256;scene.render.resolution_y=256
scene.render.filepath=str(EXPORT/"T_BFF_RiceGrain.png");bpy.ops.render.render(write_still=True)
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print("RICE_GEOMETRY_READY",json.dumps(manifest),flush=True)
