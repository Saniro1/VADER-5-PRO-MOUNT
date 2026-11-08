"""V25 fit trial: exterior relief with original clip reach; no claimed OEM dimensions."""
from pathlib import Path
import json
import subprocess
import numpy as np
import trimesh
import manifold3d
from build_v24_geometry import smooth

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/v25"
OUT = ROOT / "print/v25_quality"


def cover():
    original = trimesh.load_mesh(ROOT / "originals/Vader5Pro_Original_V2_Cover.stl")
    vertices, faces = trimesh.remesh.subdivide_to_size(original.vertices, original.faces, max_edge=0.8, max_iter=7)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    x, y, z = mesh.vertices.T.copy()
    ax = np.abs(x)
    new = mesh.vertices.copy()
    # Retain V24's localized thinning, restore the original reach/centers.
    feet = (smooth((-1.75-z)/0.65)*smooth((ax-8.1)/0.2)*smooth((13.5-ax)/0.2)*
            smooth((y-7.5)/0.4)*smooth((9.6-y)/0.5))
    new[:, 1] -= (y-8.45)*0.20*feet
    sides = (smooth((3.4-z)/1.2)*smooth((ax-13.7)/0.4)*smooth((16.5-ax)/0.4)*
             smooth((y+8.3)/0.4)*smooth((-3.2-y)/0.4))
    new[:, 0] -= np.sign(x)*(ax-15.2)*0.18*sides
    center = smooth((-9.8-y)/1.7)*smooth((3.2-ax)/0.3)*smooth((3.3-z)/0.3)
    new[:, 0] -= x*(0.30/5.5)*center
    new[:, 2] -= (z-1.65)*0.15*center

    mesh.vertices = new
    # Intersection with a downward translation trims the upper shell surface
    # while leaving the original lower/controller-facing surface in place.
    lowered = mesh.copy()
    lowered.apply_translation([0, 0, -0.50])
    relieved = trimesh.boolean.intersection([mesh, lowered], engine="manifold")
    restored = [relieved]
    protected_bounds = [
        [[-3.5, -14, -2], [3.5, -8.5, 3.7]],
        [[-16.5, -8.5, -2], [-13.5, -3, 4.3]],
        [[13.5, -8.5, -2], [16.5, -3, 4.3]],
        [[-13.6, 7, -5], [-8.0, 10, -0.8]],
        [[8.0, 7, -5], [13.6, 10, -0.8]],
    ]
    for bounds in protected_bounds:
        bounds = np.array(bounds)
        region = trimesh.creation.box(extents=bounds[1]-bounds[0])
        region.apply_translation(bounds.mean(axis=0))
        restored.append(trimesh.boolean.intersection([mesh, region], engine="manifold"))
    mesh = trimesh.boolean.union(restored, engine="manifold")
    trim = trimesh.creation.box(extents=[35.0, 32.98, 40])
    trim.apply_translation([0, -3.51, 5])  # Y[-20,12.98], preserving the rear tab.
    mesh = trimesh.boolean.intersection([mesh, trim], engine="manifold")
    solid = manifold3d.Manifold(manifold3d.Mesh64(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float64),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint64))).simplify(0.005).to_mesh()
    mesh = trimesh.Trimesh(vertices=solid.vert_properties[:, :3], faces=solid.tri_verts, process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
    mesh.export(SOURCE / "Revised_Controller_Cover.stl")
    report = {"status": "approximate-measurement seating trial", "verified_OEM_dimensions_found": False,
              "measurements_supplied": True, "user_measured_print_chord_inches": 0.91,
              "user_measured_original_chord_inches": 0.90, "reported_difference_mm": 0.254,
              "measurement_quality": "Approximate corner-to-corner comparison, axis/datum not established", "physical_fit_tested": False,
              "original_source_envelope_mm": original.extents.tolist(),
              "candidate_envelope_mm": mesh.extents.tolist(),
              "shell_exterior_vertical_relief_mm": 0.50,
              "rim_relief_per_x_edge_mm": 0.10, "positive_y_border_relief_mm": 0.10,
              "clip_reach": "Original-source reach restored; V24's added 0.35/0.40 mm extensions removed.",
              "latch_centers": "No global scaling; original nominal lateral centers retained.",
              "limits": "Photos do not establish millimeter dimensions, seating cause or OEM wall thickness."}
    (ROOT / "validation/v25_quality/fit_trial.json").write_text(json.dumps(report, indent=2)+"\n")


def main():
    cover()
    for selector, name in [("mount", "Vader5Pro_V25_Mount.stl"),
                           ("cover", "Vader5Pro_V25_Clip_Fit_Cover.stl"),
                           ("box", "Box_2_V25.stl"), ("cap", "Box_2_V25_Sliding_Cap.stl"),
                           ("receiver", "V25_Keyless_Receiver_Fit_Test.stl")]:
        path = OUT / name
        subprocess.run(["openscad", "--export-format", "binstl", "-D", f'part="{selector}"', "-o", str(path), str(SOURCE / "Vader5Pro_V25.scad")], check=True)
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split()) == 1
        mesh.export(path)
    # Small optional two-post travel test, on its own plate.
    pieces = []
    for extents, translation in [([40, 12, 0.8], [0, 0, 0.4]),
                                 ([4, 4, 15], [-13, 0, 8.25]),
                                 ([4, 4, 15], [13, 0, 8.25])]:
        m = trimesh.creation.box(extents=extents)
        m.apply_translation(translation)
        pieces.append(m)
    test = trimesh.boolean.union(pieces, engine="manifold")
    test.export(OUT / "Optional_Stringing_Test.stl")


if __name__ == "__main__":
    main()
