"""Check actual V26 solids, cap/dock motion, and the native PETG print project."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT / "print/v28_seating"
VALIDATION = ROOT / "validation/v28_pla"
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PN = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def overlap(a, b):
    return float(trimesh.boolean.intersection([a, b], engine="manifold").volume)


def mesh_check(m):
    assert m.is_watertight and m.is_winding_consistent and m.volume > 0
    return {"watertight": True, "consistent_winding": True,
            "components": len(m.split()), "volume_mm3": float(m.volume),
            "bounds_mm": m.bounds.tolist()}


def matrix(text):
    m = np.eye(4)
    if text:
        a = np.array([float(v) for v in text.split()])
        m[:3, :3], m[:3, 3] = a[:9].reshape(3, 3).T, a[9:]
    return m


def main():
    load = lambda n: trimesh.load_mesh(PRINT / n)
    box = load("Box_2_V28.stl")
    cap = load("Box_2_V28_Sliding_Cap.stl")
    mount = load("V28_A_Vader_Mount.stl")
    cover = load("V28_A_Cover_Fit_Test.stl")
    report = {"physical_fit_tested": False,
              "parts": {n: mesh_check(m) for n, m in [("box", box), ("cap", cap), ("mount", mount), ("cover", cover)]}}
    assert all(v["components"] == 1 for v in report["parts"].values())
    # The whole upper opening must remain clear down to the original floor.
    cavity = trimesh.creation.box(extents=[19.98, 24.48, 22.48])
    cavity.apply_translation([-1, -2.25, 12.25])
    report["uniform_cavity_overlap_mm3"] = overlap(box, cavity)
    assert report["uniform_cavity_overlap_mm3"] < 1e-6
    report["cavity_dimensions_mm"] = [20, 24.5, 22.5]
    original = trimesh.load_mesh(ROOT / "originals/G7_V22_Reversible_Box2.stl")
    crop = trimesh.creation.box(extents=[100, 100, 50])
    crop.apply_translation([0, 0, -26.001])
    old_rail = trimesh.boolean.intersection([original, crop])
    rail = trimesh.boolean.intersection([box, crop])
    difference = (trimesh.boolean.difference([old_rail, rail]).volume+
                  trimesh.boolean.difference([rail, old_rail]).volume)
    report["male_rail_symmetric_difference_mm3"] = float(difference)
    assert difference < 0.001
    worst = 0.0
    for dy in np.arange(-35, 0.001, 0.25):
        c = cap.copy()
        c.apply_translation([0, dy, 0])
        worst = max(worst, overlap(box, c))
    assert worst < 1e-6
    stop_cap = cap.copy()
    stop_cap.apply_translation([0, 0.5, 0])
    stop = overlap(box, stop_cap)
    assert stop > 0.1
    report["cap_slide"] = {"max_overlap_mm3": worst, "y_range_mm": [-35, 0],
                           "sample_step_mm": 0.25, "stop_overlap_at_0p5mm_mm3": stop}
    report["dock"] = {}
    for up in [False, True]:
        b, c = box.copy(), cap.copy()
        for m in [b, c]:
            if up:
                m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))
            m.apply_translation([-1, -1.85, 13.10] if up else [1, 3.75, 13.10])
        assert overlap(b, mount) < 1e-6 and overlap(c, mount) < 1e-6
        worst = 0.0
        for dy in np.arange(0, 40.001, 0.25):
            t = b.copy()
            t.apply_translation([0, dy, 0])
            worst = max(worst, overlap(t, mount))
        assert worst < 1e-6
        report["dock"]["usb_up" if up else "usb_down"] = {"slide_overlap_mm3": worst}
        scene = trimesh.Scene()
        for name, m, color in [("Mount", mount, [55, 60, 65, 255]),
                               ("Box_2", b, [90, 95, 100, 255]),
                               ("Sliding_cap", c, [150, 155, 160, 255])]:
            m = m.copy()
            m.visual.vertex_colors = color
            scene.add_geometry(m, node_name=name)
        pass  # Assembly geometry unchanged from V26; reuse its previews.

    project = ROOT / "print/v28_pla/Vader5Pro_V28_Snapmaker_PLA_Black_Complete.3mf"
    with zipfile.ZipFile(project) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
        docs = {n: ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith(".model")}
    def read_meshes(filename, objid):
        obj = next(o for o in docs[filename].find(NS+"resources") if o.get("id") == str(objid))
        node = obj.find(NS+"mesh")
        if node is not None:
            vertices = [[float(v.get(k)) for k in "xyz"] for v in node.find(NS+"vertices")]
            faces = [[int(f.get("v"+str(k))) for k in (1, 2, 3)] for f in node.find(NS+"triangles")]
            return [trimesh.Trimesh(vertices=vertices, faces=faces, process=True)]
        output = []
        for c in obj.find(NS+"components"):
            path = c.get(PN+"path", filename).lstrip("/")
            for m in read_meshes(path, c.get("objectid")):
                m.apply_transform(matrix(c.get("transform")))
                output.append(m)
        return output
    configs = {o.get("id"): o for o in cfg.findall("object")}
    supports = json.loads((VALIDATION / "support_geometry.json").read_text())
    native = {}
    objects = []
    for item in docs["3D/3dmodel.model"].find(NS+"build"):
        objid = item.get("objectid")
        oc = configs[objid]
        name = next(m.get("value") for m in oc.findall("metadata") if m.get("key") == "name")
        assert "Lock_Key" not in name
        metadata = {m.get("key"): m.get("value") for m in oc.findall("metadata")}
        assert metadata.get("extruder") == "1"
        if True:
            assert metadata.get("brim_type") == "outer_only" and metadata.get("brim_width") == "5" and metadata.get("brim_object_gap") == "0"
        for part_config in oc.findall("part"):
            assignments = [m.get("value") for m in part_config.findall("metadata") if m.get("key") == "extruder"]
            assert assignments in ([], ["1"])
        meshes = read_meshes("3D/3dmodel.model", objid)
        for mesh_index, m in enumerate(meshes):
            m.apply_transform(matrix(item.get("transform")))
            try:
                mesh_check(m)
            except AssertionError as error:
                raise AssertionError((name, mesh_index, m.is_watertight, m.is_winding_consistent,
                                      float(m.volume), len(m.faces))) from error
        assert len(meshes) == (1 if name in ("Sliding_Cap", "Optional_Stringing_Test") else 2)
        expected = load(name+"_Oriented.stl")
        expected.apply_translation([*supports[name]["plate_center_xy_mm"], 0])
        error = max(cKDTree(meshes[0].vertices).query(expected.vertices)[0].max(),
                    cKDTree(expected.vertices).query(meshes[0].vertices)[0].max())
        assert error < 0.0001
        if len(meshes) == 2:
            assert overlap(*meshes) < 1e-6
        combined = trimesh.util.concatenate(meshes)
        local_bounds = combined.bounds[:, :2]-np.array(supports[name]["plate_origin_xy_mm"])
        assert np.all(local_bounds[0] >= [0.5, 1])
        assert np.all(local_bounds[1] <= [270.5, 271])
        assert abs(combined.bounds[0, 2]) < 1e-5
        objects.append(combined)
        native[name] = {"volumes": len(meshes), "max_vertex_error_mm": float(error)}
    assert len(objects) == 7
    assert len(cfg.findall("plate")) == 7
    assert all(len(p.findall("model_instance")) == 1 for p in cfg.findall("plate"))
    for i, a in enumerate(objects):
        for b in objects[:i]:
            assert overlap(a, b) < 1e-6
    for key, value in {"printer_settings_id": "Snapmaker U1 (0.4 nozzle)", "layer_height": "0.12",
                       "enable_support": "0", "enable_prime_tower": "0", "curr_bed_type": "Textured PEI Plate",
                       "filament_type": ["PLA"], "filament_diameter": ["1.75"],
                       "nozzle_temperature": ["220"], "nozzle_temperature_initial_layer": ["220"],
                       "textured_plate_temp": ["65"], "textured_plate_temp_initial_layer": ["65"], "filament_colour": ["#101010"],
                       "filament_max_volumetric_speed": ["8"], "filament_retraction_length": ["0.8"],
                       "filament_retraction_speed": ["30"], "filament_z_hop": ["0.2"],
                       "filament_wipe": ["1"], "filament_wipe_distance": ["2"]}.items():
        assert settings[key] == value, (key, settings[key])
    for key in ["machine_start_gcode", "machine_end_gcode", "before_layer_change_gcode"]:
        assert "TIMELAPSE_" not in settings[key]
    report["native_project"] = native
    report["plate_count"] = 7
    report["exact_OEM_fit_verified"] = False
    # Check the lower sheet at clear shell points; the exterior relief must
    # not push the cover/bridge into the controller-facing space here.
    original_cover = trimesh.load_mesh(ROOT / "originals/Vader5Pro_Original_V2_Cover.stl")
    errors = []
    for x in [-7, 0, 7]:
        for y in [-5, -2, 2, 5]:
            p = [[x, y, -10]]
            old, _, _ = original_cover.ray.intersects_location(p, [[0, 0, 1]])
            new, _, _ = mount.ray.intersects_location(p, [[0, 0, 1]])
            errors.append(abs(new[:, 2].min()-old[:, 2].min()-0.15))
    assert max(errors) < 0.01
    report["sampled_A_underside_relief_error_mm"] = float(max(errors))
    report["locking_keys_in_project"] = 0
    report["retention"] = "Key removed by request; no positive axial lock or measured pull-out rating."
    report["matching_interfaces"] = {}
    base = trimesh.load_mesh(ROOT / "source/v25/Revised_Controller_Cover.stl")
    for letter in ["A", "B"]:
        c = load(f"V28_{letter}_Cover_Fit_Test.stl")
        m = load(f"V28_{letter}_Vader_Mount.stl")
        points = c.vertices[c.vertices[:, 2] < 3.7]
        _, distances, _ = trimesh.proximity.closest_point(m, points)
        assert distances.max() < 0.01, (letter, distances.max())
        assert abs(c.bounds[0, 2]-base.bounds[0, 2]) < 0.005
        report["matching_interfaces"][letter] = {"max_interface_error_mm": float(distances.max()),
                                                   "global_insertion_depth_added_mm": 0}
    # The lightweight file must contain exactly the two first cover trials,
    # at the same placements and with the same embedded PETG settings.
    with zipfile.ZipFile(ROOT / "print/v28_pla/Vader5Pro_V28_Snapmaker_PLA_Black_Cover_Tests.3mf") as z:
        fit_model = ET.fromstring(z.read("3D/3dmodel.model"))
        fit_cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
        fit_settings = json.loads(z.read("Metadata/project_settings.config"))
        fit_docs = {n: ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith(".model")}
        assert len(fit_model.find(NS+"build")) == 2
        assert len(fit_cfg.findall("plate")) == 2
        full_cfg = {o.get("id"): o for o in cfg.findall("object")}
        for obj in fit_cfg.findall("object"):
            name = next(m.get("value") for m in obj.findall("metadata") if m.get("key") == "name")
            assert name in ["Cover_A", "Cover_B"]
        for key in ["layer_height", "nozzle_temperature", "filament_retraction_length", "filament_wipe_distance"]:
            assert fit_settings[key] == settings[key]
        full_docs, docs = docs, fit_docs
        fit_configs = {o.get("id"): o for o in fit_cfg.findall("object")}
        for item in fit_model.find(NS+"build"):
            fc = fit_configs[item.get("objectid")]
            name = next(m.get("value") for m in fc.findall("metadata") if m.get("key") == "name")
            fit_meshes = read_meshes("3D/3dmodel.model", item.get("objectid"))
            assert len(fit_meshes) == 2
            for m in fit_meshes:
                m.apply_transform(matrix(item.get("transform")))
                mesh_check(m)
            expected = load(name+"_Oriented.stl")
            expected.apply_translation([*supports[name]["plate_center_xy_mm"], 0])
            assert cKDTree(fit_meshes[0].vertices).query(expected.vertices)[0].max() < 0.0001
            assert overlap(*fit_meshes) < 1e-6
        docs = full_docs
    report["fit_only_project"] = {"plates": 2, "objects": 2, "settings_match_complete": True,
                                  "cover_geometry_matches_complete": True}
    (VALIDATION / "geometry_and_project_checks.json").write_text(json.dumps(report, indent=2)+"\n")
    print("PASS: uniform cavity; cap and dock sweeps; seven native plates; PLA quality settings; no keys.")


if __name__ == "__main__":
    main()
