# V29 — longer middle clip / Snapmaker black PLA

[Single-cover test 3MF](Vader5Pro_V29_PLA_Longer_Middle_Clip_Test.3mf) · [Complete five-plate project](Vader5Pro_V29_PLA_Longer_Middle_Clip_Complete.3mf)

Requested change: extend the middle clip. V29 starts from **V28 B** and extends the central tongue **0.40 mm along negative CAD Y**, its existing reach direction. The attachment blends into the unchanged root; the tongue's height, width and retaining ridge shape are not intentionally changed. Other hooks, underside relief, box, lid and receiver stay as before, using 0.004 mm mesh simplification tolerance. Sampled non-clip surface error is below 0.01 mm. This is a physical fit trial, not a verified fix.

Print the **single-cover test first**. The complete project has cover on plate 1, matching full mount on plate 2, shared Box 2 on plate 3, sliding lid on plate 4 and optional stringing test on plate 5. There is one clip variant; internal A labels are identifiers only. Reuse an already good box/lid. Print the full mount after the bare cover seats and retains correctly.

Open the 3MF **as a project** in Snapmaker Orca and retain the saved U1 standard 0.4 mm nozzle, Textured PEI Plate and regular Snapmaker black PLA settings. Map the filament to the tool holding black PLA. No scaling or automatic arrangement is needed.

Settings remain those of V28 PLA: 220°C nozzle, 65°C bed, 0.12 mm layers / 0.20 mm first, four walls, 25% gyroid, 8 mm³/s flow cap, 0.8 mm retraction at 30 mm/s, 2 mm wipe, 0.20 mm Z hop, PLA cooling, 5 mm contacting brim and custom supports with at least 0.20 mm designed top gap. [Full inherited settings](../v28_pla/README.md). These are starting values, not physical calibration.

Wash/rinse/dry the cool plate before printing. Stop if the brim or a support foot lifts. After cooling, remove the brim and all custom support material before fitting. Insert gently; stop if the longer tongue prevents seating or requires excessive force. Do not force the PLA hook. Physical seating, latch force, durability and print reliability remain unverified.

[Geometry change](../../validation/v29_pla/middle_clip_change.json) · [Native project/mesh checks](../../validation/v29_pla/geometry_and_project_checks.json) · [Layer checks](../../validation/v29_pla/layer_islands.json) · [Slice checks](../../validation/v29_pla/slice_result.json) · [Geometry builder](../../tools/build_v29_geometry.py)

The geometry builder uses Manifold to unite the revised cover with the OpenSCAD-exported bridge/receiver core. Use the Python builder for reproducible full mount geometry; direct legacy CGAL union of the imported cover may fail on mesh tolerances. Native Snapmaker Orca exports are independently sliced. Custom support gaps can produce floating-region/cantilever warnings; inspect the sliced preview. There are no exact verified OEM dimensions.
