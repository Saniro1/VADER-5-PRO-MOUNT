# Caliper R2 — looser replacement slider

[Print just the replacement slider](Caliper_R2_Replacement_Slider_U1_PLA.3mf) · [Replacement STL](Caliper_Slider.stl) · [Complete R2 caliper on one plate](Caliper_R2_Complete_U1_PLA.3mf)

The owner reports the original slider is too tight to move on the printed beam. R2 opens the guide from **12.4 × 3.6 mm to 12.8 × 4.1 mm**: nominal clearance is now **0.40 mm on each side and 0.45 mm above/below** a 12 × 3.2 mm beam, instead of 0.20 mm. Both channel entrances are flared by another 0.20 mm at the mouth to help insertion. These are design clearances, not measured printed gaps.

**Reuse the original beam and check gauge.** They are byte-identical to the first release. The outside contact faces, inside tips, reading reference and 2 mm inside correction remain unchanged. Only the channel/reading-window clearance is relieved. More clearance introduces more play; keep the slider square and use very light jaw pressure. Physical sliding fit and accuracy remain unverified.

## Print and fit

Open the slider-only 3MF **as a project** in Snapmaker Orca. It contains one replacement slider, centered on one U1 plate, with the saved standard **0.4 mm nozzle / regular Snapmaker black PLA / textured PEI** settings. Estimated **17m 46s**. The full R2 project prints beam, slider and gauge together, estimated **1h 36m**.

Settings: 220°C nozzle, 65°C bed, 0.12 mm layers / 0.20 mm first layer, four walls, 35% gyroid, 3 mm brims, automatic supports off. The bridge flow is reduced from 0.95 to 0.90 to limit excess material on the short channel roof; this is a starting setting, not physical calibration. The enlarged channel spans a 12.8 mm roof bridge.

After cooling, remove the brim and any loose strings inside the guide. Feed the free end of your existing beam through the slider with the jaws facing each other. Do not force it. If it catches immediately at an edge, inspect for leftover brim or a first-layer lip before trying again. Avoid filing the measuring faces or forcing a tight part over the scale.

Check that the outside jaws close at zero and compare several readings against a real ruler. Hold the slider square to avoid skew from the added clearance. Inside measurements still require **adding 2 mm**. The caliper remains a rough 1 mm-graduation measuring aid, not a precision instrument for OEM hook tolerances. The printed check gauge checks technique/repeatability; it cannot independently calibrate printer scale.

[Assembly and reading guide](../printable_caliper/README.md) · [Editable SCAD](../../source/printable_caliper_v2/Caliper_80mm.scad) · [Geometry and clearance checks](../../validation/printable_caliper_v2/geometry_checks.json) · [Slider native project checks](../../validation/printable_caliper_v2/slider_project_checks.json) · [Slider slicing checks](../../validation/printable_caliper_v2/slider_slice_result.json)
