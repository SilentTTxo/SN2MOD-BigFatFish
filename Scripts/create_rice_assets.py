"""Author smooth sea-rice meshes with a top growth pivot and a cooked rice bowl."""
import bpy
import bmesh
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
palette={}
for name, color in (("RiceStem", (.018,.20,.055,1)), ("RiceLeaf", (.025,.38,.095,1)),
                    ("RiceGrain", (.82,.52,.075,1)), ("RiceGrainLight", (.95,.72,.19,1)),
                    ("RiceBowl",(.025,.14,.18,1)),("CookedRice",(.91,.88,.76,1)),("CookedRiceShade",(.76,.73,.61,1))):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = .55 if name!='RiceBowl' else .25
    materials.append(material)
    palette[name]=color

class Geometry:
    def __init__(self):
        self.vertices=[]; self.faces=[]; self.slots=[]

    def polygon(self, points, slot):
        offset=len(self.vertices)
        self.vertices.extend(tuple(p) for p in points)
        self.faces.append(tuple(range(offset, offset+len(points))))
        self.slots.append(slot)

    def tube(self, points, radius, slot, sides=12):
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
        for row in range(8):
            angle=math.pi*row/7
            rings.append([center + axis*(math.cos(angle)*size*2.6)
                          +(x*math.cos(t)+y*math.sin(t))*math.sin(angle)*size
                          for t in [j*math.tau/12 for j in range(12)]])
        for a,b in zip(rings,rings[1:]):
            for j in range(12): self.polygon([a[j],a[(j+1)%12],b[(j+1)%12],b[j]],slot)

    def object(self,name):
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices,[],self.faces); mesh.update()
        for poly,slot in zip(mesh.polygons,self.slots): poly.material_index=slot
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(mesh);bm.free();mesh.update()
        for poly in mesh.polygons:poly.use_smooth=True
        uv=mesh.uv_layers.new(name='UVMap')
        zs=[v.co.z for v in mesh.vertices];xs=[v.co.x for v in mesh.vertices]
        z0,z1=min(zs),max(zs);x0,x1=min(xs),max(xs)
        for loop in mesh.loops:
            co=mesh.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=((co.x-x0)/max(x1-x0,.0001),(co.z-z0)/max(z1-z0,.0001))
        obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
        for material in materials: mesh.materials.append(material)
        return obj

g=Geometry();panicle_anchor=.72
for stem in range(6):
    theta=stem*math.tau/6+.3
    direction=Vector((math.cos(theta),math.sin(theta),0))
    base=direction*.012
    height=panicle_anchor+random.uniform(-.018,.018)
    points=[base+Vector((0,0,height*t))+direction*(.035*t*t) for t in [i/18 for i in range(19)]]
    g.tube(points,.0032,0)
    for layer in range(3):
        z=height*(.18+layer*.19)
        bearing=theta+(math.pi if layer%2 else 0)+.5
        forward=Vector((math.cos(bearing),math.sin(bearing),0))
        sideways=Vector((-forward.y,forward.x,0))
        start=base+Vector((0,0,z))
        rows=[]
        for t in [i/24 for i in range(25)]:
            center=start+forward*(.27*t)+Vector((0,0,.16*math.sin(math.pi*.95*t)-.05*t))
            width=.020*(max(0,math.sin(math.pi*t))**.8)
            rows.append([center+sideways*(width*u)+Vector((0,0,.006*(1-u*u)*math.sin(math.pi*t))) for u in (-1,-.5,0,.5,1)])
        for a,b in zip(rows,rows[1:]):
            for j in range(4):g.polygon([a[j],b[j],b[j+1],a[j+1]],1)
    top=points[-1]
    panicle=[top+direction*(.12*t)+Vector((0,0,.055*math.sin(math.pi*t)-.080*t)) for t in [i/20 for i in range(21)]]
    g.tube(panicle,.0018,2)
    for j in range(7):
        t=(j+1)/8
        center=top+direction*(.12*t)+Vector((0,0,.055*math.sin(math.pi*t)-.080*t))
        for sign in (-1,1):
            side=Vector((-direction.y,direction.x,0))*sign
            tip=center+side*(.022*(1-t)+.008)+Vector((0,0,-.015))
            g.tube([center,tip],.0008,2,8)
            g.grain(tip,side*.3+Vector((0,0,-1)),.0040,2+(j%2))
plant=g.object("SM_BFF_RicePlant")
stalk_geometry=Geometry();panicle_geometry=Geometry()
for face,slot in zip(g.faces,g.slots):
    if slot<2:stalk_geometry.polygon([g.vertices[i] for i in face],slot)
    else:panicle_geometry.polygon([Vector(g.vertices[i])-Vector((0,0,panicle_anchor)) for i in face],slot)
stalk=stalk_geometry.object("SM_BFF_RiceStalk")
panicle=panicle_geometry.object("SM_BFF_RicePanicle")
stalk.hide_render=True;panicle.hide_render=True
grain_geometry=Geometry()
for i in range(7):
    angle=i*math.tau/7
    grain_geometry.grain((.009*math.cos(angle),.009*math.sin(angle),.006),(.3*math.cos(angle),.3*math.sin(angle),1),.0027,2+i%2)
grain=grain_geometry.object("SM_BFF_RiceGrain")
for name,color in palette.items():
    image=bpy.data.images.new('T_BFF_'+name+'_Color',width=64,height=64,alpha=False)
    pixels=[]
    for y in range(64):
        for x in range(64):
            variation=.86+.13*y/63+.035*math.sin(x*.8+y*.23)
            pixels.extend([min(1,c*variation) for c in color[:3]]+[1])
    image.pixels.foreach_set(pixels);image.filepath_raw=str(EXPORT/(image.name+'.png'));image.file_format='PNG';image.save()

bowl_geometry=Geometry()
profile=[(.014,.000),(.020,.003),(.027,.007),(.038,.014),(.052,.029),(.066,.045),(.070,.052),
         (.069,.055),(.066,.055),(.063,.050),(.057,.040),(.045,.026),(.028,.019),(.005,.018)]
rings=[[Vector((radius*math.cos(t),radius*math.sin(t),z)) for t in [i*math.tau/48 for i in range(48)]] for radius,z in profile]
for a,b in zip(rings,rings[1:]):
    for i in range(48):bowl_geometry.polygon([a[i],a[(i+1)%48],b[(i+1)%48],b[i]],4)
# Closed white mound supports a readable bowl at gameplay and icon scale.
mound=[]
for row in range(10):
    theta=math.pi*.5*row/9
    radius=.063*math.sin(theta);z=.052+.023*math.cos(theta)
    mound.append([Vector((radius*math.cos(t),radius*math.sin(t),z)) for t in [i*math.tau/40 for i in range(40)]])
for a,b in zip(mound,mound[1:]):
    for i in range(40):bowl_geometry.polygon([a[i],a[(i+1)%40],b[(i+1)%40],b[i]],5)
for i in range(95):
    radius=.059*math.sqrt(random.random());angle=random.random()*math.tau
    z=.052+.023*math.sqrt(max(0,1-(radius/.063)**2))
    bowl_geometry.grain((radius*math.cos(angle),radius*math.sin(angle),z),
                        (math.cos(angle+.8),math.sin(angle+.8),.1),.0015,5+(i%4==0))
bowl=bowl_geometry.object('SM_BFF_CookedRice');bowl.hide_render=True

manifest={"status":"sea rice refinement; original harvest flow accepted by user", "units":"metres; exported FBX converts to cm", "pivot":"stalk at soil; panicle at 72 cm crown", "panicle_anchor_cm":panicle_anchor*100,"smooth_normals":True, "provenance":"Original procedural geometry authored by Scripts/create_rice_assets.py; no external model or texture", "assets":[]}
for obj in (plant,grain,stalk,panicle,bowl):
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
grain.hide_render=True;bowl.hide_render=False
camera.location=(.20,-.27,.20);camera.rotation_euler=(Vector((0,0,.040))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.19
scene.render.filepath=str(EXPORT/'T_BFF_CookedRice.png');bpy.ops.render.render(write_still=True)
(OUT/"asset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print("RICE_GEOMETRY_READY",json.dumps(manifest),flush=True)
