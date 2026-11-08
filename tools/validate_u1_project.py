"""Reopen native 3MF, verify settings, exact placed geometry, and plate clearance."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "print/u1_black_pla/Vader5Pro_V23_U1_Black_PLA_Complete.3mf"
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PRODUCTION = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def transform(text):
    t = np.eye(4)
    if text:
        a = np.array([float(s) for s in text.split()])
        t[:3, :3], t[:3, 3] = a[:9].reshape(3, 3).T, a[9:]
    return t


with zipfile.ZipFile(PROJECT) as z:
    settings = json.loads(z.read("Metadata/project_settings.config"))
    config = ET.fromstring(z.read("Metadata/model_settings.config"))
    model = ET.fromstring(z.read("3D/3dmodel.model"))
    docs = {name: ET.fromstring(z.read(name)) for name in z.namelist() if name.endswith(".model")}

    def meshes(filename, objid):
        obj = next(o for o in docs[filename].find(NS+"resources") if o.get("id") == str(objid))
        node = obj.find(NS+"mesh")
        if node is not None:
            vertices = [[float(v.get(c)) for c in "xyz"] for v in node.find(NS+"vertices")]
            faces = [[int(f.get("v"+str(j))) for j in (1, 2, 3)] for f in node.find(NS+"triangles")]
            return [trimesh.Trimesh(vertices=vertices, faces=faces, process=True)]
        result = []
        for c in obj.find(NS+"components"):
            name = c.get(PRODUCTION+"path", filename).lstrip("/")
            for m in meshes(name, c.get("objectid")):
                m.apply_transform(transform(c.get("transform")))
                result.append(m)
        return result

    cfg = {o.get("id"): o for o in config.findall("object")}
    support_report = json.loads((ROOT / "validation/u1_black_pla/support_geometry.json").read_text())
    objects = []
    results = {}
    for item in model.find(NS+"build"):
        objid = item.get("objectid")
        obj_config = cfg[objid]
        for node in [obj_config]+obj_config.findall("part"):
            tools = [m.get("value") for m in node.findall("metadata") if m.get("key") == "extruder"]
            # An omitted part assignment inherits the object's filament.
            assert tools == ["1"] or (node is not obj_config and tools == []), (objid, tools)
        name = next(n.get("value") for n in obj_config.findall("metadata") if n.get("key") == "name")
        actual = meshes("3D/3dmodel.model", objid)
        for m in actual:
            m.apply_transform(transform(item.get("transform")))
            assert m.is_watertight and m.is_winding_consistent and m.volume > 0
        assert len(actual) == (1 if name == "Receiver_Fit_Test" else 2)
        expected = trimesh.load_mesh(ROOT / "print/u1_black_pla" / (name+"_Oriented.stl"))
        xy = support_report[name]["plate_center_xy_mm"]
        expected.apply_translation([*xy, 0])
        distance = max(cKDTree(actual[0].vertices).query(expected.vertices)[0].max(),
                       cKDTree(expected.vertices).query(actual[0].vertices)[0].max())
        assert distance < 0.0001, (name, distance)
        combined = trimesh.util.concatenate(actual)
        assert np.all(combined.bounds[0, :2] >= [0.5, 1])
        assert np.all(combined.bounds[1, :2] <= [270.5, 271])
        assert abs(combined.bounds[0, 2]) < 1e-5
        if len(actual) == 2:
            overlap = float(trimesh.boolean.intersection(actual, engine="manifold").volume)
            assert overlap < 1e-6
        else:
            overlap = 0.0
        results[name] = {"volumes": len(actual), "max_part_vertex_error_mm": float(distance),
                         "part_support_overlap_mm3": overlap, "bounds_mm": combined.bounds.tolist()}
        objects.append(combined)
    assert len(objects) == 5
    for i, a in enumerate(objects):
        for b in objects[:i]:
            assert trimesh.boolean.intersection([a, b], engine="manifold").volume < 1e-6

checks = {"printer_settings_id": "Snapmaker U1 (0.4 nozzle)", "layer_height": "0.16",
          "wall_loops": "4", "enable_support": "0", "enable_prime_tower": "0",
          "curr_bed_type": "Textured PEI Plate", "brim_type": "no_brim"}
for key, expected in checks.items():
    assert settings[key] == expected, (key, settings[key])
assert settings["filament_colour"] == ["#101010"]
assert settings["nozzle_temperature"] == ["220"]
assert settings["textured_plate_temp"] == ["65"]
assert settings["filament_max_volumetric_speed"] == ["10"]
assert settings["outer_wall_speed"] == ["40"]
results = {"native_project_reopened": True, "objects": results, "positive_volumes": 9,
           "same_filament_for_all_parts_and_supports": True,
           "physical_support_removal_tested": False, "verified_settings": checks}
(ROOT / "validation/u1_black_pla/project_checks.json").write_text(json.dumps(results, indent=2)+"\n")
print("PASS: five objects, nine volumes, retained orientations and exact part geometry, embedded U1/PLA settings.")
