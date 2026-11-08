"""Make the complete V24 PETG plate, using the established support/3MF writer."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d
import build_u1_project as support_tools
from shapely.geometry import Polygon, box, Point

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/v24"
OUT = ROOT / "print/v24_iemai_petg"
support_tools.OUT = OUT
support_tools.SOURCE = SOURCE
support_tools.GAP = 0.32


def main():
    groups, report = [], {}
    for filename, name, rotation, xy in [
        ("Vader5Pro_V24_Mount.stl", "Vader_Mount", np.pi, [105, 115]),
        ("Box_2_V24.stl", "Shared_Box_2", 0, [155, 115]),
        ("Box_2_V24_Sliding_Cap.stl", "Sliding_Cap", np.pi/2, [155, 68]),
        ("Vader5Pro_V24_Clip_Fit_Cover.stl", "Clip_Fit_Cover", np.pi, [105, 68]),
    ]:
        part = trimesh.load_mesh(OUT / filename)
        if rotation:
            part.apply_transform(trimesh.transformations.rotation_matrix(rotation, [1, 0, 0]))
        part.apply_translation([-part.bounds[:, 0].mean(), -part.bounds[:, 1].mean(), -part.bounds[0, 2]])
        if name == "Sliding_Cap":
            support, result = None, {"support_needed": False, "brim_width_mm": 3.0}
        else:
            support, result = support_tools.supports(part, name, custom_targets=(name != "Vader_Mount"))
            if name in ("Vader_Mount", "Clip_Fit_Cover"):
                # The revised tab starts higher than V23. Reach around the
                # rear edge instead of printing a support through the model.
                top = 9.32 if name == "Vader_Mount" else 3.88
                profile = Polygon([(13.65, 0), (14.25, 0), (14.25, top),
                                   (11.6, top), (11.6, top-0.32), (13.65, top-2.37)])
                arms = []
                for x in [-2.0, 0.0, 2.0]:
                    arm = support_tools.extrude_polygon(profile, 0.60)
                    arm.apply_transform([[0, 0, 1, x-0.30], [1, 0, 0, 0],
                                         [0, 1, 0, 0], [0, 0, 0, 1]])
                    arms.append(arm)
                base = box(-3.5, 13.45, 3.5, 16.5).union(Point(0, 17).buffer(2))
                arms.append(support_tools.extrude_polygon(base, 0.36))
                support = trimesh.boolean.union([support]+arms, engine="manifold")
                result["revised_tab_support_arms"] = 3
            # PETG welds readily: keep extra side clearance as well as the
            # 0.32 mm vertical gap. These cutters never change the actual part.
            cutters = []
            for dx, dy, dz in [(0, 0, -0.32), (0.25, 0, 0), (-0.25, 0, 0),
                               (0, 0.25, 0), (0, -0.25, 0)]:
                cutter = part.copy()
                cutter.apply_translation([dx, dy, dz])
                cutters.append(cutter)
            support = trimesh.boolean.difference([support]+cutters, engine="manifold")
            support = trimesh.util.concatenate([p for p in support.split()
                                                 if p.volume > 0.03 and p.bounds[0, 2] < 1e-5])
            # Remove sub-micron Boolean slivers before STL float32 serialization.
            solid = manifold3d.Manifold(manifold3d.Mesh64(
                vert_properties=np.asarray(support.vertices, dtype=np.float64),
                tri_verts=np.asarray(support.faces, dtype=np.uint64))).simplify(0.003).to_mesh()
            support = trimesh.Trimesh(vertices=solid.vert_properties[:, :3], faces=solid.tri_verts, process=True)
            assert support.is_watertight and support.is_winding_consistent
            support.export(OUT / (name+"_Custom_Supports.stl"))
            serialized = trimesh.load_mesh(OUT / (name+"_Custom_Supports.stl"))
            assert serialized.is_watertight and serialized.is_winding_consistent
            result.update(support_volume_mm3=float(support.volume), removable_components=len(support.split()),
                          additional_xy_clearance_mm=0.25)
        part.export(OUT / (name+"_Oriented.stl"))
        result.update(part_bounds_mm=part.bounds.tolist(), part_volume_mm3=float(part.volume),
                      plate_center_xy_mm=xy, x_rotation_radians=rotation)
        report[name] = result
        groups.append((name, part, support, xy))
    support_tools.write_seed(groups)
    seed = SOURCE / "U1_Oriented_Seed.3mf"
    with zipfile.ZipFile(seed) as z:
        files = {n: z.read(n) for n in z.namelist()}
    cfg = ET.fromstring(files["Metadata/model_settings.config"])
    for obj in cfg.findall("object"):
        name = next(n.get("value") for n in obj.findall("metadata") if n.get("key") == "name")
        if name == "Sliding_Cap":
            for key, value in [("brim_type", "outer_only"), ("brim_width", "3"), ("brim_object_gap", "0.20")]:
                ET.SubElement(obj, "metadata", key=key, value=value)
    for meta in cfg.find("plate").findall("metadata"):
        if meta.get("key") == "plater_name":
            meta.set("value", "V24 - IEMAI matte PETG - complete keyless kit")
    files["Metadata/model_settings.config"] = ET.tostring(cfg, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(seed, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    (ROOT / "validation/v24_iemai_petg/support_geometry.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
