"""Blender 4.x geometric preview renderer, invoked by render_preview.py."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[sys.argv.index("--") + 1])
OUT.mkdir(parents=True, exist_ok=True)


def part(filename, name, color, translation=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=str(ROOT / "print" / filename))
    obj = bpy.context.object
    obj.name = name
    obj.location = translation
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.65
    obj.data.materials.append(material)
    return obj


for index in range(4):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 900
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.86, 0.92, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
    scene.view_settings.view_transform = "Standard"
    blue, orange, purple = (0.035, 0.26, 0.38), (0.9, 0.43, 0.065), (0.40, 0.12, 0.55)
    if index == 3:
        part("Vader5Pro_V23_Receiver_Fit_Test.stl", "Receiver fit test", blue)
        part("G7_V22_Lock_Key.stl", "Withdrawn key", purple, (7, 0, 0))
        target, eye, scale = (4, 0, 3), (60, 75, 80), 52
    else:
        part("Vader5Pro_V23_Mount.stl", "Vader mount", blue)
        if index in (0, 1):
            part("Box 2.stl", "Shared Box 2", orange, (1, 3.75, 27.10 if index == 1 else 13.10))
        part("G7_V22_Lock_Key.stl", "Shared key", purple, (12 if index == 1 else 0, 0, 7))
        target = (3, 0, 21) if index == 1 else (0, 0, 17 if index == 0 else 5)
        eye = (75, -90, 85) if index in (0, 1) else (65, 80, 95)
        scale = 80 if index == 1 else 70
    bpy.ops.object.camera_add(location=eye)
    camera = bpy.context.object
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    camera.data.clip_end = 1000
    scene.camera = camera
    for location, energy, size in [((20, -40, 90), 70000, 65), ((-50, 25, 45), 35000, 50)]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy, light.data.shape, light.data.size = energy, "DISK", size
        light.rotation_euler = (Vector((0, 0, 10)) - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUT / f"panel{index}.png")
    bpy.ops.render.render(write_still=True)
