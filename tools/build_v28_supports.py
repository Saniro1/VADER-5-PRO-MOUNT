"""Make an oriented U1 plate with custom removable PLA support combs.

Run with build dependencies plus shapely>=2.1. Export/slice the seed project
with Snapmaker Orca as documented in print/u1_black_pla/README.md.
"""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d
import shapely
from shapely.geometry import box, LineString, Point, Polygon, MultiPolygon
from shapely.ops import unary_union, nearest_points

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "print/u1_black_pla"
SOURCE = ROOT / "source/u1_black_pla"
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)
tag = lambda n: "{" + NS + "}" + n
GAP = 0.24
PITCH = 0.80


def solid_box(bounds):
    bounds = np.asarray(bounds)
    m = trimesh.creation.box(extents=bounds[1]-bounds[0])
    m.apply_translation(bounds.mean(axis=0))
    return m


def extrude_polygon(poly, height):
    from shapely import set_precision
    poly = set_precision(poly.buffer(0.01).buffer(-0.01), 0.001).simplify(0.001, preserve_topology=True)
    polys = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
    rings = []
    for p in polys:
        rings.append(np.array(p.exterior.coords)[:-1])
        rings.extend(np.array(r.coords)[:-1] for r in p.interiors)
    result = manifold3d.CrossSection(rings, manifold3d.FillRule.EvenOdd).extrude(height).to_mesh()
    return trimesh.Trimesh(vertices=result.vert_properties[:, :3], faces=result.tri_verts, process=True)


def bottom_heights(mesh, points):
    """First downward-facing surface along each vertical ray from the bed."""
    z = np.full(len(points), np.inf)
    for tri, normal in zip(mesh.triangles, mesh.face_normals):
        if normal[2] > -0.025:
            continue
        a, b, c = tri
        v0, v1 = b[:2]-a[:2], c[:2]-a[:2]
        det = v0[0]*v1[1]-v0[1]*v1[0]
        if abs(det) < 1e-10:
            continue
        ix = np.flatnonzero(np.all(points >= tri[:, :2].min(axis=0)-1e-6, axis=1) &
                            np.all(points <= tri[:, :2].max(axis=0)+1e-6, axis=1))
        p = points[ix]-a[:2]
        u = (p[:, 0]*v1[1]-p[:, 1]*v1[0])/det
        v = (v0[0]*p[:, 1]-v0[1]*p[:, 0])/det
        inside = (u >= -1e-6) & (v >= -1e-6) & (u+v <= 1+1e-6)
        hit = a[2]+u*(b[2]-a[2])+v*(c[2]-a[2])
        indices = ix[inside]
        z[indices] = np.minimum(z[indices], hit[inside])
    return z


def supports(mesh, name, custom_targets=True):
    lo, hi = mesh.bounds[:, :2]
    xs = np.arange(lo[0]+PITCH/2, hi[0], PITCH)
    ys = np.arange(lo[1]+PITCH/2, hi[1], PITCH)
    points = np.array([[x, y] for y in ys for x in xs])
    heights = bottom_heights(mesh, points)
    # Box rim lips are short cantilevers; do not grow tall supports up to them.
    # The box needs support under its floor only. The key only needs a carrier.
    max_height = 3.0 if name == "Shared_Box_2" else (2.0 if name == "Lock_Key" else np.inf)
    valid = np.isfinite(heights) & (heights > 0.60) & (heights <= max_height)
    occupied = np.isfinite(heights) & (heights <= 0.60)
    cells = lambda mask: [box(x-PITCH/2, y-PITCH/2, x+PITCH/2, y+PITCH/2) for x, y in points[mask]]
    if not valid.any():
        return None, {}
    blocked = unary_union(cells(occupied)).buffer(0.45, join_style=2)
    footprint = unary_union(cells(valid)).buffer(1.25, join_style=2).difference(blocked)
    components = list(footprint.geoms) if isinstance(footprint, MultiPolygon) else [footprint]
    bodies = []
    pull_tabs = []
    for poly in components:
        if poly.area < 1:
            continue
        # Route a 3-mm-wide pull tab to the closest unobstructed outer edge.
        center = poly.representative_point()
        targets = [Point(lo[0]-4, center.y), Point(hi[0]+4, center.y),
                   Point(center.x, lo[1]-4), Point(center.x, hi[1]+4)]
        choices = []
        for target in targets:
            start = nearest_points(poly, target)[0]
            tab = LineString([start, target]).buffer(1.5, cap_style=2).union(target.buffer(2.0))
            if tab.intersection(blocked).area < 1e-6:
                choices.append((start.distance(target), tab))
        if choices:
            tab = min(choices, key=lambda x: x[0])[1]
            poly = poly.union(tab)
            pull_tabs.append(list(tab.bounds))
        bodies.append(extrude_polygon(poly, 0.36))

    ribs = []
    # Thin parallel comb teeth; ~2.4 mm between rows. These are modeled solids,
    # not automatic slicer supports, and print in the same black PLA.
    centers = np.array([[x, y] for iy, y in enumerate(ys) if iy % 3 == 0 for x in xs])
    offsets = np.array([[dx, dy] for dx in [-0.4, 0, 0.4] for dy in [-0.22, 0, 0.22]])
    h = bottom_heights(mesh, (centers[:, None, :]+offsets[None, :, :]).reshape(-1, 2)).reshape(-1, 9)
    for (x, y), height in zip(centers, h.min(axis=1)):
        if not np.isfinite(height) or height <= 0.60 or height > max_height:
            continue
        top = 0.20+0.12*np.floor((height-GAP-0.20)/0.12+1e-7)
        if top <= 0.36:
            continue
        ribs.append(solid_box([[x-0.405, y-0.22, 0.32], [x+0.405, y+0.22, top]]))
    for i, m in enumerate(bodies+ribs):
        if not m.is_volume:
            print("Invalid support primitive", name, i, m.is_watertight, m.volume, m.bounds, flush=True)
    support = trimesh.boolean.union(bodies+ribs, engine="manifold")
    targeted = []
    if custom_targets and name == "Vader_Mount":
        # This original cover tab starts above the closed receiver end. A support
        # from the bed directly below it would hit the receiver; three thin,
        # self-supporting arms reach in from outside instead.
        profile = Polygon([(13.3, 0), (13.9, 0), (13.9, 8.84),
                           (11.7, 8.84), (11.7, 8.52), (13.3, 6.92)])
        for x in [-2.0, 0.0, 2.0]:
            arm = extrude_polygon(profile, 0.60)
            arm.apply_transform([[0, 0, 1, x-0.30], [1, 0, 0, 0],
                                 [0, 1, 0, 0], [0, 0, 0, 1]])
            targeted.append(arm)
        tab = box(-3.5, 13.1, 3.5, 16.0).union(Point(0, 17).buffer(2))
        targeted.append(extrude_polygon(tab, 0.36))
    if name == "Shared_Box_2":
        # Two tiny original lid-retention hooks start in mid-air. Support only
        # those hooks with narrow blades, rather than fencing the whole rim.
        for sign in [-1, 1]:
            x = sign*13.85
            targeted.append(solid_box([[x-0.22, 10.35, 0.32], [x+0.22, 12.75, 25.08]]))
            foot = box(min(sign*11.5, sign*17), 9.8, max(sign*11.5, sign*17), 13.3)
            foot = foot.union(Point(sign*18, 11.55).buffer(2))
            targeted.append(extrude_polygon(foot, 0.36))
    if targeted:
        support = trimesh.boolean.union([support]+targeted, engine="manifold")
    # Clip sampling-edge discrepancies; the ray-defined contact gap is kept.
    shifted = mesh.copy()
    shifted.apply_translation([0, 0, -GAP])
    support = trimesh.boolean.difference([support, mesh, shifted], engine="manifold")
    pieces = [m for m in support.split() if m.volume > 0.03 and m.bounds[0, 2] < 1e-5]
    support = trimesh.util.concatenate(pieces)
    assert support.is_watertight and support.is_winding_consistent
    assert abs(trimesh.boolean.intersection([support, mesh]).volume) < 1e-5
    support.export(OUT / (name+"_Custom_Supports.stl"))
    return support, {"support_volume_mm3": float(support.volume), "removable_components": len(pieces),
                     "targeted_clip_supports": len(targeted),
                     "minimum_designed_top_gap_mm": GAP, "rib_width_mm": 0.44,
                     "rib_row_pitch_mm": 2.4, "base_height_mm": 0.36, "pull_tabs_bounds": pull_tabs}


def write_seed(groups):
    model = ET.Element(tag("model"), unit="millimeter")
    ET.SubElement(model, tag("metadata"), name="Application").text = "Snapmaker_Orca-2.4.1"
    ET.SubElement(model, tag("metadata"), name="Snapmaker_Orca:3mfVersion").text = "1"
    resources = ET.SubElement(model, tag("resources"))
    build = ET.SubElement(model, tag("build"))
    config = ET.Element("config")
    plate = ET.SubElement(config, "plate")
    ET.SubElement(plate, "metadata", key="plater_id", value="1")
    ET.SubElement(plate, "metadata", key="plater_name", value="U1 black PLA - complete V23 kit")
    ET.SubElement(plate, "metadata", key="locked", value="false")
    ET.SubElement(plate, "metadata", key="filament_maps", value="1")
    next_id = 1
    for name, part, support, xy in groups:
        ids = []
        for label, mesh in [(name, part), (name+" - PEEL OFF custom supports", support)]:
            if mesh is None:
                continue
            objid = next_id
            next_id += 1
            ids.append((objid, label))
            obj = ET.SubElement(resources, tag("object"), id=str(objid), type="model", name=label)
            node = ET.SubElement(obj, tag("mesh"))
            vs = ET.SubElement(node, tag("vertices"))
            for v in mesh.vertices:
                ET.SubElement(vs, tag("vertex"), **dict(zip("xyz", (f"{n:.6f}" for n in v))))
            fs = ET.SubElement(node, tag("triangles"))
            for f in mesh.faces:
                ET.SubElement(fs, tag("triangle"), **{f"v{j+1}": str(v) for j, v in enumerate(f)})
        rootid = next_id
        next_id += 1
        obj = ET.SubElement(resources, tag("object"), id=str(rootid), type="model", name=name)
        components = ET.SubElement(obj, tag("components"))
        config_obj = ET.SubElement(config, "object", id=str(rootid))
        ET.SubElement(config_obj, "metadata", key="name", value=name)
        ET.SubElement(config_obj, "metadata", key="extruder", value="1")
        if "Lock_Key" in name:
            for key, value in [("brim_type", "outer_only"), ("brim_width", "2"), ("brim_object_gap", "0.12")]:
                ET.SubElement(config_obj, "metadata", key=key, value=value)
        for objid, label in ids:
            ET.SubElement(components, tag("component"), objectid=str(objid))
            config_part = ET.SubElement(config_obj, "part", id=str(objid), subtype="normal_part")
            ET.SubElement(config_part, "metadata", key="name", value=label)
            ET.SubElement(config_part, "metadata", key="extruder", value="1")
        ET.SubElement(build, tag("item"), objectid=str(rootid), printable="1",
                      transform=f"1 0 0 0 1 0 0 0 1 {xy[0]} {xy[1]} 0")
        instance = ET.SubElement(plate, "model_instance")
        for key, value in [("object_id", rootid), ("instance_id", 0), ("identify_id", rootid)]:
            ET.SubElement(instance, "metadata", key=key, value=str(value))
    with zipfile.ZipFile(SOURCE / "U1_Oriented_Seed.3mf", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
        z.writestr("Metadata/model_settings.config", ET.tostring(config, encoding="utf-8", xml_declaration=True))
        z.writestr("Metadata/project_settings.config", (SOURCE / "Orca_Base_Project_Settings.json").read_bytes())
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')


def main():
    groups = []
    report = {}
    for filename, name, inverted, xy in [
        ("Vader5Pro_V23_Mount.stl", "Vader_Mount", True, [105, 115]),
        ("Box 2.stl", "Shared_Box_2", False, [155, 115]),
        ("G7_V22_Lock_Key.stl", "Lock_Key", False, [103, 160]),
        ("G7_V22_Lock_Key.stl", "Spare_Lock_Key", False, [147, 160]),
        ("Vader5Pro_V23_Receiver_Fit_Test.stl", "Receiver_Fit_Test", False, [105, 70]),
    ]:
        part = trimesh.load_mesh(ROOT / "print" / filename)
        if inverted:
            part.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
        part.apply_translation([-part.bounds[:, 0].mean(), -part.bounds[:, 1].mean(), -part.bounds[0, 2]])
        if name == "Spare_Lock_Key":
            support = groups[-1][2].copy()
            result = report["Lock_Key"].copy()
            support.export(OUT / (name+"_Custom_Supports.stl"))
        elif name == "Receiver_Fit_Test":
            support, result = None, {"support_needed": False}
        else:
            support, result = supports(part, name)
        part.export(OUT / (name+"_Oriented.stl"))
        result["orientation"] = "180 degrees about X; clips point up" if inverted else "native Z up; dropped to bed"
        result["part_volume_mm3"] = float(part.volume)
        result["part_bounds_mm"] = part.bounds.tolist()
        result["plate_center_xy_mm"] = xy
        report[name] = result
        groups.append((name, part, support, xy))
    write_seed(groups)
    (ROOT / "validation/u1_black_pla/support_geometry.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
