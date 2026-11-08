"""V24: uniform Box 2 cavity, sliding cap, keyless dock and revised cover clips."""
from pathlib import Path
import json
import subprocess
import numpy as np
import trimesh
import manifold3d

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/v24"
OUT = ROOT / "print/v24_iemai_petg"


def smooth(value):
    value = np.clip(value, 0, 1)
    return value*value*(3-2*value)


def revise_cover():
    original = trimesh.load_mesh(ROOT / "originals/Vader5Pro_Original_V2_Cover.stl")
    # Subdivide long edges before the localized deformation, keeping feature
    # transitions continuous instead of stretching a few large triangles.
    vertices, faces = trimesh.remesh.subdivide_to_size(original.vertices, original.faces,
                                                      max_edge=1.0, max_iter=7)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    x, y, z = mesh.vertices.T.copy()
    changed = mesh.vertices.copy()
    ax = np.abs(x)
    feet = (smooth((-1.75-z)/0.65)*smooth((ax-8.1)/0.2)*smooth((13.5-ax)/0.2)*
            smooth((y-7.5)/0.4)*smooth((9.6-y)/0.5))
    changed[:, 1] += -(y-8.45)*0.20*feet
    changed[:, 2] -= 0.35*feet
    sides = (smooth((3.4-z)/1.2)*smooth((ax-13.7)/0.4)*smooth((16.5-ax)/0.4)*
             smooth((y+8.3)/0.4)*smooth((-3.2-y)/0.4))
    changed[:, 0] += -np.sign(x)*(ax-15.2)*0.18*sides
    changed[:, 2] -= 0.40*sides
    center = smooth((-9.8-y)/1.7)*smooth((3.2-ax)/0.3)*smooth((3.3-z)/0.3)
    changed[:, 0] -= x*(0.30/5.5)*center
    changed[:, 1] -= 0.40*center
    changed[:, 2] += -(z-1.65)*0.15*center-0.40*center
    mesh.vertices = changed
    solid = manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint32))).simplify(0.005).to_mesh()
    mesh = trimesh.Trimesh(vertices=solid.vert_properties[:, :3], faces=solid.tri_verts, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
    mesh.export(SOURCE / "Revised_Controller_Cover.stl")
    report = {"front_feet_y_thickness_scale_at_tip": 0.80,
              "front_feet_extra_depth_mm": 0.35,
              "side_hooks_x_thickness_scale_at_tip": 0.82,
              "side_hooks_extra_depth_mm": 0.40,
              "center_tab_z_thickness_scale": 0.85,
              "center_tab_extra_y_reach_mm": 0.40,
              "center_tab_z_offset_mm": -0.40,
              "center_tab_width_reduction_mm": 0.30,
              "original_bounds_mm": original.bounds.tolist(),
              "revised_bounds_mm": mesh.bounds.tolist(),
              "physical_controller_fit_tested": False}
    (ROOT / "validation/v24_iemai_petg/clip_changes.json").write_text(json.dumps(report, indent=2)+"\n")


def main():
    revise_cover()
    for selector, filename in [("mount", "Vader5Pro_V24_Mount.stl"),
                               ("box", "Box_2_V24.stl"),
                               ("cap", "Box_2_V24_Sliding_Cap.stl"),
                               ("cover", "Vader5Pro_V24_Clip_Fit_Cover.stl"),
                               ("receiver", "V24_Keyless_Receiver_Fit_Test.stl")]:
        path = OUT / filename
        subprocess.run(["openscad", "-D", f'part="{selector}"', "-o", str(path),
                        str(SOURCE / "Vader5Pro_V24.scad")], check=True)
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
        assert mesh.volume > 0
        mesh.export(path)


if __name__ == "__main__":
    main()
