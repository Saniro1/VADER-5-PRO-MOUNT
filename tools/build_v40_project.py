"""V40 side-oriented cover/mount with recalculated removable comb supports."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d
import build_v28_supports as support_tools
from shapely.geometry import Polygon, box, Point

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/v40"
OUT = ROOT / "print/v40_pla"
support_tools.OUT = OUT
support_tools.SOURCE = SOURCE
support_tools.GAP = 0.20


def main():
    groups, report = [], {}
    definitions = [
        ("V40_A_Cover_Fit_Test.stl", "Cover_A", np.pi),
        ("V40_A_Vader_Mount.stl", "Mount_A", np.pi),
        ("Box_2_V40.stl", "Shared_Box_2", 0),
        ("Box_2_V40_Sliding_Cap.stl", "Sliding_Cap", np.pi/2),
        ("Optional_Stringing_Test.stl", "Optional_Stringing_Test", 0),
    ]
    columns = int(np.ceil(np.sqrt(len(definitions))))
    for plate_index, (filename, name, rotation) in enumerate(definitions):
        # Orca: ceil(sqrt(plate_count)) columns, 20% bed-to-bed gap.
        origin = [324*(plate_index % columns), -324*(plate_index // columns)]
        xy = [135+origin[0], 135+origin[1]]
        part = trimesh.load_mesh(OUT / filename)
        if rotation:
            part.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2 if name.startswith(("Cover_", "Mount_")) else rotation, [0, 1, 0] if name.startswith(("Cover_", "Mount_")) else [1, 0, 0]))
        part.apply_translation([-part.bounds[:, 0].mean(), -part.bounds[:, 1].mean(), -part.bounds[0, 2]])
        if name in ("Sliding_Cap", "Optional_Stringing_Test"):
            support, result = None, {"support_needed": False, "brim_width_mm": 3.0 if name == "Sliding_Cap" else 0}
        else:
            support_tools.GAP = 0.16 if name.startswith(("Cover_", "Mount_")) else 0.20
            support, result = support_tools.supports(part, name, custom_targets=False if name.startswith("Mount_") else True)
            # Keep side clearance and each object's designed top gap.
            # These cutters never change the actual part.
            side_gap = .25
            cutters = []
            for dx, dy, dz in [(0, 0, -support_tools.GAP), (side_gap, 0, 0), (-side_gap, 0, 0),
                               (0, side_gap, 0), (0, -side_gap, 0)]:
                cutter = part.copy()
                cutter.apply_translation([dx, dy, dz])
                cutters.append(cutter)
            support = trimesh.boolean.difference([support]+cutters, engine="manifold")
            support = trimesh.util.concatenate([p for p in support.split()
                                                 if p.volume > 0.03 and p.bounds[0, 2] < 1e-5])
            # Remove sub-micron Boolean slivers before STL float32 serialization.
            solid = manifold3d.Manifold(manifold3d.Mesh64(
                vert_properties=np.asarray(support.vertices, dtype=np.float64),
                tri_verts=np.asarray(support.faces, dtype=np.uint64))).set_tolerance(0.0001).simplify(0.003).to_mesh64()
            raw_support = trimesh.Trimesh(vertices=solid.vert_properties[:, :3], faces=solid.tri_verts, process=False)
            support = raw_support.copy(); support.process()
            base_joins = 0
            if not support.is_watertight:
                # Two disposable base pads touch along a vertical edge. Add a
                # small real bridge so STL vertex welding cannot create a
                # four-face edge. Never apply this repair to the printed part.
                bad = support.edges_unique[np.bincount(support.edges_unique_inverse)!=2]
                pins = []
                for edge in bad:
                    vertices = support.vertices[edge]
                    assert vertices[:,2].min() >= -1e-5 and vertices[:,2].max() <= .361
                    assert np.linalg.norm(vertices[0,:2]-vertices[1,:2]) < 1e-5
                    pin = trimesh.creation.cylinder(radius=.15, height=.36, sections=20)
                    pin.apply_translation([*vertices[:,:2].mean(0),.18]);pins.append(pin)
                assert raw_support.is_watertight and raw_support.is_winding_consistent
                support = trimesh.boolean.union([raw_support]+pins,engine="manifold")
                base_joins = len(pins)
            assert support.is_watertight and support.is_winding_consistent
            assert abs(trimesh.boolean.intersection([support,part],engine="manifold").volume) < 1e-6
            result["disposable_base_corner_bridges"] = base_joins
            support.export(OUT / (name+"_Custom_Supports.stl"))
            serialized = trimesh.load_mesh(OUT / (name+"_Custom_Supports.stl"))
            assert serialized.is_watertight and serialized.is_winding_consistent
            result.update(support_volume_mm3=float(support.volume), removable_components=len(support.split()),
                          additional_xy_clearance_mm=side_gap)
        part.export(OUT / (name+"_Oriented.stl"))
        result.update(part_bounds_mm=part.bounds.tolist(), part_volume_mm3=float(part.volume),
                      plate_center_xy_mm=xy, rotation_axis="Y" if name.startswith(("Cover_", "Mount_")) else "X", rotation_radians=np.pi/2 if name.startswith(("Cover_", "Mount_")) else rotation,
                      plate_index=plate_index+1, plate_origin_xy_mm=origin)
        report[name] = result
        groups.append((name, part, support, xy))
    support_tools.write_seed(groups)
    seed = SOURCE / "U1_Oriented_Seed.3mf"
    with zipfile.ZipFile(seed) as z:
        files = {n: z.read(n) for n in z.namelist()}
    cfg = ET.fromstring(files["Metadata/model_settings.config"])
    for obj in cfg.findall("object"):
        name = next(n.get("value") for n in obj.findall("metadata") if n.get("key") == "name")
        if True:
            for key, value in [("brim_type", "outer_only"), ("brim_width", "5"), ("brim_object_gap", "0")]:
                ET.SubElement(obj, "metadata", key=key, value=value)
    old_plate = cfg.find("plate")
    cfg.remove(old_plate)
    model_xml = ET.fromstring(files["3D/3dmodel.model"])
    items = list(model_xml.find(support_tools.tag("build")))
    titles = ["1 - Curved middle latch test", "2 - Matching mount", "3 - Shared Box 2", "4 - Sliding lid", "5 - Optional stringing test"]
    for i, (item, title) in enumerate(zip(items, titles)):
        plate = ET.SubElement(cfg, "plate")
        for key, value in [("plater_id", i+1), ("plater_name", title), ("locked", "false"), ("filament_maps", "1")]:
            ET.SubElement(plate, "metadata", key=key, value=str(value))
        instance = ET.SubElement(plate, "model_instance")
        for key, value in [("object_id", item.get("objectid")), ("instance_id", 0), ("identify_id", item.get("objectid"))]:
            ET.SubElement(instance, "metadata", key=key, value=str(value))
    files["Metadata/model_settings.config"] = ET.tostring(cfg, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(seed, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    # A small second project contains only the two fit covers. Their first
    # two positions are identical in the 7-plate and 2-plate layouts.
    fit_files = files.copy()
    fit_model = ET.fromstring(files["3D/3dmodel.model"])
    fit_build = fit_model.find(support_tools.tag("build"))
    for item in list(fit_build)[1:]:
        fit_build.remove(item)
    fit_ids = {i.get("objectid") for i in fit_build}
    resources = fit_model.find(support_tools.tag("resources"))
    resource_objects = {o.get("id"): o for o in resources}
    required = set(fit_ids)
    pending = list(fit_ids)
    while pending:
        obj = resource_objects[pending.pop()]
        components = obj.find(support_tools.tag("components"))
        if components is not None:
            for component in components:
                objid = component.get("objectid")
                if objid not in required:
                    required.add(objid)
                    pending.append(objid)
    for obj in list(resources):
        if obj.get("id") not in required:
            resources.remove(obj)
    fit_cfg = ET.fromstring(files["Metadata/model_settings.config"])
    for obj in list(fit_cfg.findall("object")):
        if obj.get("id") not in fit_ids:
            fit_cfg.remove(obj)
    for plate in fit_cfg.findall("plate")[1:]:
        fit_cfg.remove(plate)
    fit_files["3D/3dmodel.model"] = ET.tostring(fit_model, encoding="utf-8", xml_declaration=True)
    fit_files["Metadata/model_settings.config"] = ET.tostring(fit_cfg, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(SOURCE / "U1_Fit_Only_Seed.3mf", "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in fit_files.items():
            z.writestr(name, data)
    (ROOT / "validation/v40_pla/support_geometry.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
