"""Rebuild V23, check assembly geometry, and write portable print/inspection files.

Requires OpenSCAD and: pip install -r tools/requirements.txt
Run from any directory: python tools/build_validate.py
"""
from pathlib import Path
import hashlib
import json
import subprocess
import warnings
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "print"
ORIGINAL = ROOT / "originals"
warnings.filterwarnings("ignore", category=RuntimeWarning, module="trimesh")


def load(path):
    return trimesh.load_mesh(path, process=True)


def intersection_volume(a, b):
    return float(trimesh.boolean.intersection([a, b], engine="manifold").volume)


def check_mesh(mesh):
    result = dict(watertight=bool(mesh.is_watertight),
                  consistent_winding=bool(mesh.is_winding_consistent),
                  components=len(mesh.split()), faces=len(mesh.faces),
                  volume_mm3=float(mesh.volume), bounds_mm=mesh.bounds.tolist())
    assert result["watertight"] and result["consistent_winding"]
    assert result["components"] == 1 and result["volume_mm3"] > 0
    return result


def make_3mf(parts, path):
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    tag = lambda n: "{" + ns + "}" + n
    model = ET.Element(tag("model"), unit="millimeter", attrib={"xml:lang": "en-US"})
    resources = ET.SubElement(model, tag("resources"))
    build = ET.SubElement(model, tag("build"))
    for i, (name, mesh, xy) in enumerate(parts, 1):
        obj = ET.SubElement(resources, tag("object"), id=str(i), type="model", name=name)
        node = ET.SubElement(obj, tag("mesh"))
        vertices = ET.SubElement(node, tag("vertices"))
        m = mesh.copy()
        m.apply_translation([xy[0], xy[1], -m.bounds[0, 2]])
        for v in m.vertices:
            ET.SubElement(vertices, tag("vertex"), **dict(zip("xyz", (f"{x:.7f}" for x in v))))
        triangles = ET.SubElement(node, tag("triangles"))
        for face in m.faces:
            ET.SubElement(triangles, tag("triangle"), **{f"v{j+1}": str(v) for j, v in enumerate(face)})
        ET.SubElement(build, tag("item"), objectid=str(i))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    # Independently parse the saved package, check every mesh and layout bounds.
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    objects = root.findall(".//" + tag("object"))
    assert len(objects) == 3 and len(root.find(tag("build"))) == 3
    meshes = []
    for obj in objects:
        vertices = [[float(v.get(c)) for c in "xyz"] for v in obj.findall(".//" + tag("vertex"))]
        faces = [[int(f.get(f"v{j}")) for j in (1, 2, 3)] for f in obj.findall(".//" + tag("triangle"))]
        m = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        check_mesh(m)
        assert abs(m.bounds[0, 2]) < 1e-6
        meshes.append(m)
    for i in range(3):
        for j in range(i):
            assert intersection_volume(meshes[i], meshes[j]) < 1e-6
    return {"objects": 3, "all_watertight": True, "on_bed": True, "overlap": False}


def main():
    for show, name in [("mount", "Vader5Pro_V23_Mount.stl"),
                       ("receiver", "Vader5Pro_V23_Receiver_Fit_Test.stl")]:
        subprocess.run(["openscad", "-D", f'show="{show}"', "-o", str(PRINT / name),
                        str(ROOT / "source/Vader5Pro_V23.scad")], check=True)
        # Store compact binary STLs, retaining native assembly coordinates.
        load(PRINT / name).export(PRINT / name, file_type="stl")
    for source, target in [("G7_V22_Reversible_Box2.stl", "Box 2.stl"),
                           ("G7_V22_Lock_Key.stl", "G7_V22_Lock_Key.stl")]:
        (PRINT / target).write_bytes((ORIGINAL / source).read_bytes())

    mount = load(PRINT / "Vader5Pro_V23_Mount.stl")
    receiver = load(PRINT / "Vader5Pro_V23_Receiver_Fit_Test.stl")
    box = load(PRINT / "Box 2.stl")
    key = load(PRINT / "G7_V22_Lock_Key.stl")
    cover = load(ORIGINAL / "Vader5Pro_Original_V2_Cover.stl")
    report = {"units": "mm", "physical_test_fit": False,
              "controller_mesh_available": False,
              "meshes": {n: check_mesh(m) for n, m in
                         [("mount", mount), ("receiver_coupon", receiver), ("box2", box), ("key", key)]}}
    report["unchanged_shared_parts"] = {}
    for orig, target in [("G7_V22_Reversible_Box2.stl", "Box 2.stl"),
                         ("G7_V22_Lock_Key.stl", "G7_V22_Lock_Key.stl")]:
        assert (ORIGINAL / orig).read_bytes() == (PRINT / target).read_bytes()
        report["unchanged_shared_parts"][target] = hashlib.sha256((PRINT / target).read_bytes()).hexdigest()

    # OpenSCAD/STL serialization introduces micron-scale numerical differences.
    # Compare the whole controller-facing region with a stated volume tolerance.
    below5 = trimesh.creation.box(extents=[100, 100, 100])
    below5.apply_translation([0, 0, -45])
    a = trimesh.boolean.intersection([mount, below5])
    b = trimesh.boolean.intersection([cover, below5])
    symmetric = (trimesh.boolean.difference([a, b]).volume +
                 trimesh.boolean.difference([b, a]).volume)
    assert symmetric < 0.01
    report["cover_below_z5_symmetric_difference_mm3"] = float(symmetric)
    report["cover_comparison_tolerance_mm3"] = 0.01

    placed_key = key.copy()
    placed_key.apply_translation([0, 0, 7])
    report["key_mount_overlap_mm3"] = intersection_volume(placed_key, mount)
    assert report["key_mount_overlap_mm3"] < 1e-6
    report["assembly"] = {}
    for up in [False, True]:
        m = box.copy()
        if up:
            m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
        m.apply_translation([-1, -1.85, 13.10] if up else [1, 3.75, 13.10])
        overlaps = {"box_mount_mm3": intersection_volume(m, mount),
                    "box_key_mm3": intersection_volume(m, placed_key)}
        assert max(overlaps.values()) < 1e-6
        # Entry/exit is +Y, beyond the key. -Y has a permanent stop.
        worst = 0.0
        for dy in np.arange(0, 40.01, 0.25):
            t = m.copy()
            t.apply_translation([0, dy, 0])
            worst = max(worst, intersection_volume(t, mount))
        assert worst < 1e-6
        overlaps["slide_sweep_max_overlap_mm3"] = worst
        # The rail must bear on the bed: downward travel must be blocked.
        lower = m.copy()
        lower.apply_translation([0, 0, -0.01])
        overlaps["bed_blocks_0p01mm_down_mm3"] = intersection_volume(lower, mount)
        assert overlaps["bed_blocks_0p01mm_down_mm3"] > 1.0
        overlaps["slide_sweep"] = {"axis": "+Y", "range_mm": [0, 40], "step_mm": 0.25, "key_removed": True}
        # Verify the key blocks escape, and the closed stop blocks reverse travel.
        blocked = m.copy()
        blocked.apply_translation([0, 1, 0])
        overlaps["key_blocks_1mm_escape_mm3"] = intersection_volume(blocked, placed_key)
        blocked.apply_translation([0, -5, 0])
        overlaps["stop_blocks_minus4mm_mm3"] = intersection_volume(blocked, mount)
        stop_near = m.copy()
        stop_near.apply_translation([0, -0.5, 0])
        overlaps["stop_blocks_minus0p5mm_mm3"] = intersection_volume(stop_near, mount)
        assert overlaps["key_blocks_1mm_escape_mm3"] > 0.1
        assert overlaps["stop_blocks_minus4mm_mm3"] > 0.1
        assert overlaps["stop_blocks_minus0p5mm_mm3"] > 0.1
        report["assembly"]["usb_up" if up else "usb_down"] = overlaps
        scene = trimesh.Scene()
        for name, mesh, color in [("Vader_mount", mount, [37, 125, 160, 255]),
                                  ("Box_2", m, [236, 160, 53, 255]),
                                  ("Lock_key", placed_key, [155, 85, 190, 255])]:
            t = mesh.copy()
            t.visual.vertex_colors = color
            scene.add_geometry(t, node_name=name)
        scene.export(ROOT / "preview" / ("V23_USB_Up.glb" if up else "V23_USB_Down.glb"))

    # Analytical planar clearance at the tightest dovetail section (lip height).
    male_slope = (7.1 - 5.55781) / 2.15
    male_x_at_lip = 7.1 - (4.85 - 2.95) * male_slope
    female_x_at_lip = 5.80182 + 0.20
    horizontal_gap = female_x_at_lip - male_x_at_lip
    report["nominal_clearances_mm"] = {
        "box_floor_to_receiver_lip": 0.25,
        "rail_bottom_to_bearing_bed": 0.0,
        "bearing_bed_raise_from_original_floor": 0.41,
        "tightest_horizontal_flank_gap_per_side": horizontal_gap,
        "tightest_normal_flank_gap_approx": horizontal_gap / np.sqrt(1 + male_slope**2),
        "rail_end_to_key": 0.25,
        "rail_end_to_closed_stop": 0.25,
        "total_fore_aft_play": 0.50,
        "key_tab_to_box_floor": 0.16,
    }
    assert horizontal_gap > 0.25
    report["print_3mf"] = make_3mf([
        ("Vader V23 mount", mount, [25, 25]),
        ("Shared G7 Box 2", box, [70, 25]),
        ("Shared G7 key", key, [110, 15]),
    ], PRINT / "Vader5Pro_V23_Three_Parts.3mf")
    report["limits"] = [
        "Controller clip dimensions are inherited from the supplied cover, not independently measured.",
        "No controller mesh, electronics model, physical print or load test is available.",
        "Collision-free samples and nominal clearances do not guarantee printer or material fit.",
        "The original key detent requires elastic flex during lateral insertion; not a rigid clearance fit.",
    ]
    (ROOT / "validation/results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
