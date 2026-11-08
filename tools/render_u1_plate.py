"""Blender 4.x: render the real oriented meshes and custom supports."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "validation/u1_black_pla/support_geometry.json").read_text())
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.75
    return m


part_mat = material("Black PLA parts", (0.07, 0.075, 0.085))
support_mat = material("Support illustration gray - prints in black PLA", (0.50, 0.60, 0.64))
bed_mat = material("PEI illustration", (0.18, 0.20, 0.22))
for name, data in report.items():
    for suffix, mat in [("_Oriented.stl", part_mat), ("_Custom_Supports.stl", support_mat)]:
        path = ROOT / "print/u1_black_pla" / (name+suffix)
        if not path.exists():
            continue
        bpy.ops.wm.stl_import(filepath=str(path))
        obj = bpy.context.object
        obj.location = (*data["plate_center_xy_mm"], 0)
        obj.data.materials.append(mat)
bpy.ops.mesh.primitive_cube_add(size=1, location=(135, 135, -1))
bed = bpy.context.object
bed.dimensions = (270, 270, 2)
bed.data.materials.append(bed_mat)
bpy.ops.object.camera_add(location=(270, -75, 235))
camera = bpy.context.object
camera.rotation_euler = (Vector((127, 112, 4))-camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 170
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.samples = 20
scene.cycles.use_denoising = False
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
for position, energy, size in [((80, 30, 180), 180000, 130), ((210, 170, 120), 100000, 100)]:
    bpy.ops.object.light_add(type="AREA", location=position)
    light = bpy.context.object
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (Vector((130, 110, 0))-light.location).to_track_quat("-Z", "Y").to_euler()
scene.view_settings.view_transform = "Standard"
scene.render.filepath = str(ROOT / "preview/U1_Black_PLA_Plate.png")
bpy.ops.render.render(write_still=True)
