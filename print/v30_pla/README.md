# V30 — slightly larger top clips / Snapmaker black PLA

[Single-cover test 3MF](Vader5Pro_V30_PLA_Larger_Top_Clips_Test.3mf) · [Complete five-plate project](Vader5Pro_V30_PLA_Larger_Top_Clips_Complete.3mf)

The owner reports V29's longer middle clip is better and requests slightly larger top clips. V30 extends the **two fixed top-hook toes another 0.20 mm along their existing negative-Y retaining direction** relative to V29. It does not increase the entire clip's insertion depth. The middle tongue remains V29's version, including its 0.40 mm extension; the shell, underside clearance, side hooks, box, lid and receiver are not intentionally changed. Sampled surface error outside the modified top-hook region is checked below 0.01 mm after mesh simplification.

This is one controlled physical fit trial. Greater engagement is the goal, not an established result. Stop if the longer toes prevent seating or need excessive force; do not force PLA hooks into the controller.

## Print

Open the 3MF **as a project** in Snapmaker Orca, preserving the U1 standard 0.4 mm nozzle, Textured PEI Plate, regular black Snapmaker PLA filament, saved orientations, custom supports and 100% scale. Map the filament to the tool containing that PLA. Start with the single-cover project. After cooling, remove all support material and brim before fitting.

PLA settings remain unchanged: 220°C nozzle, 65°C bed, 0.12 mm layers / 0.20 mm first layer, four walls, 25% gyroid, 8 mm³/s volumetric cap, 0.8 mm retraction at 30 mm/s, 2 mm wipe and 0.20 mm Z hop. PLA cooling, 5 mm contacting brims and at least 0.20 mm designed custom support gap remain included. [Full inherited settings](../v28_pla/README.md).

The complete project has cover on plate 1, matching mount on plate 2, shared Box 2 on plate 3, sliding lid on plate 4 and optional stringing test on plate 5. Print the matching mount only after the bare cover seats and retains properly. Existing good box/lid prints can be reused. Internal A object labels identify the single supplied version.

## Checks and source

[Clip-change checks](../../validation/v30_pla/top_clip_change.json) · [Native geometry/settings checks](../../validation/v30_pla/geometry_and_project_checks.json) · [Layer checks](../../validation/v30_pla/layer_islands.json) · [Slice/toolpath checks](../../validation/v30_pla/slice_result.json) · [Geometry builder](../../tools/build_v30_geometry.py)

Native Snapmaker Orca 2.4.1 exports are independently sliced. Deliberate support gaps may produce floating-region/cantilever warnings; inspect the preview. Physical fit, engagement, hook durability and print reliability remain unverified. No exact OEM dimensions are claimed. Source profiles retain their inherited V28 setting names because the print settings are unchanged. Use the Python builder's Manifold union for the complete mount; legacy CGAL union of the imported cover can fail on mesh tolerance.
