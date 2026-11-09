# V28 underside-clearance trials

[Small two-cover project](Vader5Pro_V28_Underside_Clearance_Tests.3mf) · [Complete seven-plate project](Vader5Pro_V28_Underside_Clearance_Complete.3mf)

The owner reports the cover still sits high. Earlier exterior thinning largely preserved the controller-facing shell; V28 tests whether relief on that surface allows deeper seating. The exact interfering surface remains unmeasured. This is a controlled clearance trial, not a verified fit correction.

Both variants start from **V26 A**, including its modest retaining ridge and longer top-hook toes. B now means greater underside clearance, not V26 B's larger retaining lips.

| Variant | Additional controller-facing shell relief | Retaining features |
| --- | --- | --- |
| A | 0.15 mm in CAD Z direction | V26 A |
| B | 0.30 mm in CAD Z direction | V26 A |

The shell's lower skin is removed using intersection with a translated copy. Five hook/root regions are restored, with 0.004 mm mesh simplification tolerance; this avoids shortening the hooks to gain clearance. Curved shell rims can also retreat slightly as a result. No global scaling or additional exterior thinning is applied. Sampled shell thickness is checked above 0.8 mm, but this is not a strength test or a minimum-thickness guarantee over every point. [Exact operation and sample results](../../validation/v28_seating/underside_clearance.json).

## Printing and fitting

Open as a project in Snapmaker Orca for the U1 0.4 mm nozzle and IEMAI matte black PETG. Retain 100% scale, saved orientation, custom supports and brims. V27 recovery settings remain: 5 mm contacting brim, 0.20 mm minimum designed support gap, strengthened support arms, 75°C first bed layer / 70°C later, 245°C first nozzle layer / 240°C later, and 0.12 mm layers after a 0.20 mm first layer.

Print **plate 1 / A** first. Clean and dry the plate beforehand; watch the first layers and stop if a foot or brim lifts. Let it cool, trim the brim, and remove support remnants from beneath the cover and hooks. Check whether the bare cover sits flush and latches with gentle pressure. If A is still high, test **plate 2 / B**. Do not force either variant. A fully seated cover that still releases needs retention diagnosis, not more underside relief.

The complete project has covers A/B on plates 1/2 and their matching mounts on plates 3/4. Print the matching mount only after a cover passes the seating/retention test. Plates 5/6 hold the unchanged shared Box 2 and sliding lid; plate 7 is the optional stringing test. No need to reprint a good existing box or lid.

## Validation and limits

[Mesh/native project checks](../../validation/v28_seating/geometry_and_project_checks.json) · [Layer checks](../../validation/v28_seating/layer_islands.json) · [Slice/toolpath checks](../../validation/v28_seating/slice_result.json) · [Editable assembly](../../source/v28/Vader5Pro_V28.scad) · [Geometry builder](../../tools/build_v28_geometry.py)

Projects are exported and sliced in Snapmaker Orca 2.4.1. Custom support gaps can trigger floating-region/cantilever warnings; inspect the preview. CAD and slicing checks cannot establish controller fit, latch force, support removal or reliable printing. Physical fit remains unverified and no exact OEM drawing is available.
