"""Check new layer islands against the previous three layers. Requires rtree."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "print/u1_black_pla"
results = {}
for name in ["Vader_Mount", "Shared_Box_2", "Lock_Key"]:
    part = trimesh.load_mesh(PRINT / (name+"_Oriented.stl"))
    support = trimesh.load_mesh(PRINT / (name+"_Custom_Supports.stl"))
    mesh = trimesh.util.concatenate([part, support])
    # Midplanes for a 0.20 mm first layer, followed by 0.16 mm layers.
    heights = np.r_[0.10, 0.28+np.arange(int(mesh.bounds[1, 2]/0.16))*0.16]
    paths = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
    polygons, islands = [], []
    for i, (path, height) in enumerate(zip(paths, heights)):
        pieces = [] if path is None else list(path.polygons_full)
        polygons.append(unary_union(pieces))
        if i == 0:
            continue
        previous = polygons[i-1].buffer(0.15)
        previous_three = unary_union(polygons[max(0, i-3):i]).buffer(0.15)
        for polygon in pieces:
            if polygon.area > 0.03 and not polygon.intersects(previous):
                islands.append({"z": float(height), "area": polygon.area,
                                "distance_to_underlying_3_layers": polygon.distance(previous_three),
                                "bounds": list(polygon.bounds)})
    print(name, "new islands checked:", len(islands), flush=True)
    results[name] = islands

(ROOT / "validation/u1_black_pla/layer_islands.json").write_text(json.dumps(results, indent=2)+"\n")
assert all(island["distance_to_underlying_3_layers"] < 1e-6
           for islands in results.values() for island in islands), "Unsupported new island remains"
