"""V26 retention trials: fuller catch lips without globally deepening clips."""
from pathlib import Path
import json
import subprocess
import numpy as np
import trimesh
import manifold3d
from build_v24_geometry import smooth

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/v26"
OUT = ROOT / "print/v26_retention"


def simplify(mesh):
    solid = manifold3d.Manifold(manifold3d.Mesh64(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float64),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint64))).simplify(0.004).to_mesh()
    result = trimesh.Trimesh(vertices=solid.vert_properties[:, :3], faces=solid.tri_verts, process=True)
    assert result.is_watertight and result.is_winding_consistent and len(result.split()) == 1
    return result


def cover(letter, catch_height, catch_overlap, toe_reach):
    baseline = trimesh.load_mesh(ROOT / "source/v25/Revised_Controller_Cover.stl")
    vertices, faces = trimesh.remesh.subdivide_to_size(baseline.vertices, baseline.faces,
                                                      max_edge=0.60, max_iter=7)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    x, y, z = mesh.vertices.T.copy()
    ax = np.abs(x)
    revised = mesh.vertices.copy()
    # Raise the actual locking ridge and move its stop face slightly forward.
    # Do not move the underside of the tongue or deepen the entire clip.
    ridge = (smooth((y+12.65)/0.45)*smooth((-11.05-y)/0.45)*
             smooth((z-1.8)/0.6)*smooth((2.9-ax)/0.3))
    revised[:, 2] += catch_height*ridge
    revised[:, 1] += catch_overlap*ridge
    # Extend only the retaining toe of the pair of top hooks, along their
    # existing negative-Y direction. Keep their insertion depth unchanged.
    toe = (smooth((-1.9-z)/0.55)*smooth((ax-8.0)/0.30)*smooth((13.5-ax)/0.30)*
           smooth((y-7.4)/0.4)*smooth((10.1-y)/0.6))
    revised[:, 1] -= toe_reach*toe
    mesh.vertices = revised
    mesh = simplify(mesh)
    # Further exterior-only relief; retain the hook and root regions intact.
    lowered = mesh.copy()
    lowered.apply_translation([0, 0, -0.25])
    parts = [trimesh.boolean.intersection([mesh, lowered], engine="manifold")]
    for bounds in [
        [[-3.5, -14, -2], [3.5, -8.5, 3.7]],
        [[-16.5, -8.5, -2], [-13.5, -3, 4.3]],
        [[13.5, -8.5, -2], [16.5, -3, 4.3]],
        [[-13.6, 7, -5], [-8.0, 10, -0.8]],
        [[8.0, 7, -5], [13.6, 10, -0.8]],
    ]:
        bounds = np.array(bounds)
        region = trimesh.creation.box(extents=bounds[1]-bounds[0])
        region.apply_translation(bounds.mean(axis=0))
        parts.append(trimesh.boolean.intersection([mesh, region], engine="manifold"))
    result = simplify(trimesh.boolean.union(parts, engine="manifold"))
    result.export(SOURCE / f"Controller_Cover_{letter}.stl")
    saved = trimesh.load_mesh(SOURCE / f"Controller_Cover_{letter}.stl")
    assert saved.is_watertight and saved.is_winding_consistent
    return {"variant": letter, "catch_ridge_height_added_mm": catch_height,
            "catch_stop_face_forward_shift_mm": catch_overlap,
            "top_hook_toe_reach_added_mm": toe_reach,
            "extra_whole_clip_insertion_depth_mm": 0,
            "extra_shell_exterior_relief_mm": 0.25,
            "total_shell_relief_from_original_mm": 0.75,
            "bounds_mm": saved.bounds.tolist(), "physical_fit_verified": False}


def main():
    reports = {}
    for letter, height, overlap, toe in [("A", 0.20, 0.08, 0.15), ("B", 0.35, 0.15, 0.30)]:
        reports[letter] = cover(letter, height, overlap, toe)
        for selector, filename in [("cover", f"V26_{letter}_Cover_Fit_Test.stl"),
                                   ("mount", f"V26_{letter}_Vader_Mount.stl")]:
            path = OUT / filename
            subprocess.run(["openscad", "--export-format", "binstl", "-D", f'part="{selector}"',
                            "-D", f'variant="{letter}"', "-o", str(path),
                            str(SOURCE / "Vader5Pro_V26.scad")], check=True)
            mesh = simplify(trimesh.load_mesh(path))
            mesh.export(path)
    (ROOT / "validation/v26_retention/retention_trials.json").write_text(json.dumps({
        "evidence": "V25 seats better but can be pulled backward and falls off; shell still feels thick.",
        "diagnosis": "Insufficient catch engagement is plausible; not established from photos alone.",
        "verified_OEM_dimensions_available": False,
        "variants": reports}, indent=2)+"\n")


if __name__ == "__main__":
    main()
