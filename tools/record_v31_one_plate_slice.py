"""Verify exported per-plate G-code and record estimates; no printer is contacted."""
from pathlib import Path
import sys
import re
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
directory = Path(sys.argv[1])
result = json.loads((directory / "result.json").read_text())
assert result["return_code"] == 0 and len(result["sliced_plates"]) == 1
plates = []
for index in range(1, 2):
    text = (directory / f"plate_{index}.gcode").read_text()
    names = sorted(set(re.findall(r"; printing object (.+?) id:", text)))
    assert len(names) == 3, names
    assert not re.search(r"^\s*TIMELAPSE_(START|STOP|TAKE_FRAME)", text, re.M)
    assert ";WIPE_START" in text
    assert ";TYPE:Brim" in text and "M190 S65" in text and "M140 S65" in text
    assert re.search(r"G1 E-(?:0?\.56)(?:\s|$)", text)
    position = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    relative, relative_e, last_e, in_layers = False, True, 0.0, False
    count = 0
    bounds = [[float("inf")]*3, [float("-inf")]*3]
    for line in text.splitlines():
        if line.startswith(";LAYER_CHANGE"):
            in_layers = True
        line = line.split(";", 1)[0].strip()
        if line == "G90":
            relative = False
        elif line == "G91":
            relative = True
        elif line == "M83":
            relative_e = True
        elif line == "M82":
            relative_e = False
        values = {k: float(v) for k, v in re.findall(r"([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))", line)}
        if line.startswith("G92"):
            last_e = values.get("E", last_e)
        if not re.match(r"G[01](?:\s|$)", line):
            continue
        for axis in "XYZ":
            if axis in values:
                position[axis] = position[axis]+values[axis] if relative else values[axis]
        delta_e = values.get("E", 0) if relative_e else values.get("E", last_e)-last_e
        if "E" in values:
            last_e = values["E"]
        if in_layers and delta_e > 0 and ("X" in values or "Y" in values):
            assert 0.5 <= position["X"] <= 270.5, (index, position)
            assert 1 <= position["Y"] <= 271, (index, position)
            assert 0 <= position["Z"] <= 270.05
            for axis_index, axis in enumerate("XYZ"):
                bounds[0][axis_index] = min(bounds[0][axis_index], position[axis])
                bounds[1][axis_index] = max(bounds[1][axis_index], position[axis])
            count += 1
    assert count > 0
    plates.append({"plate": index, "objects": names,
                   "estimated_time": re.search(r"estimated printing time \(normal mode\) = (.+)", text).group(1),
                   "estimated_filament_g": float(re.search(r"total filament used \[g\] = (.+)", text).group(1)),
                   "extruding_moves_checked": count, "extrusion_bounds_mm": bounds,
                   "three_objects_on_one_plate": True, "timelapse_commands_present": False,
                   "wipe_and_70pct_retraction_seen": True})
result.update(slicer_release="Snapmaker Orca 2.4.1", plate_details=plates,
              physical_print_tested=False, exact_OEM_fit_verified=False,
              published_file_contains_gcode=False,
              project_sha256=hashlib.sha256((ROOT / "print/v31_pla/Vader5Pro_V31_All_Parts_One_Plate_PLA.3mf").read_bytes()).hexdigest())
(ROOT / "validation/v31_pla/one_plate_slice_result.json").write_text(json.dumps(result, indent=2)+"\n")
print("PASS: one plate sliced; three objects on the same plate; extrusion within bed; wipe/retraction present; no timelapse capture.")
