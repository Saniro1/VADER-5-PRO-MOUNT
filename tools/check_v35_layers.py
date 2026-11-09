"""Check new layer islands against the previous five layers. Requires rtree."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "print/v35_pla"
results = {}
for name in ["Cover_A", "Mount_A", "Shared_Box_2", "Sliding_Cap", "Optional_Stringing_Test"]:
    part = trimesh.load_mesh(PRINT / (name+"_Oriented.stl"))
    support_path = PRINT / (name+"_Custom_Supports.stl")
    mesh = trimesh.util.concatenate([part, trimesh.load_mesh(support_path)]) if support_path.exists() else part
    # Midplanes for a 0.20 mm first layer, followed by 0.12 mm layers.
    heights = np.r_[0.10, 0.26+np.arange(int(mesh.bounds[1, 2]/0.12))*0.12]
    paths = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
    polygons, islands = [], []
    for i, (path, height) in enumerate(zip(paths, heights)):
        pieces = [] if path is None else list(path.polygons_full)
        polygons.append(unary_union(pieces))
        if i == 0:
            continue
        previous = polygons[i-1].buffer(0.15)
        previous_five = unary_union(polygons[max(0, i-5):i]).buffer(0.15)
        for polygon in pieces:
            if polygon.area > 0.03 and not polygon.intersects(previous):
                islands.append({"z": float(height), "area": polygon.area,
                                "distance_to_underlying_5_layers": polygon.distance(previous_five),
                                "bounds": list(polygon.bounds)})
    print(name, "new islands checked:", len(islands), flush=True)
    results[name] = islands

(ROOT / "validation/v35_pla/layer_islands.json").write_text(json.dumps(results, indent=2)+"\n")
assert all(island["distance_to_underlying_5_layers"] < 1e-6
           for islands in results.values() for island in islands), "Unsupported new island remains"
