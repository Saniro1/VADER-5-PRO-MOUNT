# V38 — 1 mm shorter top and middle hooks

[Small cover test](Vader5Pro_V38_PLA_Trimmed_Hooks_Test.3mf) · [All functional parts on ONE plate](Vader5Pro_V38_All_Parts_One_Plate_PLA.3mf) · [Separate-plate project](Vader5Pro_V38_PLA_Trimmed_Hooks_Complete.3mf)

The owner reports **V37 finally holds in place but is slightly too big**, and requests 1 mm off the bottom center clip and top clips. V38 reduces their projections relative to V37, keeping the successful larger shell and reinforced roots.

| Feature | V37 | V38 |
| --- | --- | --- |
| Top catch-lip inward reach | 7.3 mm | **6.3 mm** (−1) |
| Middle tongue projection beyond lower rim | 5.5 mm | **4.5 mm** (−1) |
| Main shell | 35 × 24 mm | Retained |
| Overall including middle tongue | 29.5 mm | **28.5 mm** |
| Top width / neck | 6 / 1.6 mm | Retained |
| Hook leg depth, root braces, middle anchor | Reinforced V37 design | Retained within mesh tolerance |

The middle hook's distal catch is moved inward with a compressed transition below the root so its terminal/ridge profile survives. Its solid root anchor and the main cover edge remain in place. The top lips are rebuilt to the shorter reach at the existing neck/leg positions. Outside the edited regions, sampled surface error is below 0.01 mm; exported shell width/height, middle projection, overall height and root thickness are checked. V38 is untested physically; V37 retention is owner-reported, not independently measured.

**Keep the saved side-print orientation**, 100% scale, custom supports and brims. Open as a project in Snapmaker Orca with **U1 standard 0.4 mm nozzle / Textured PEI Plate / regular Snapmaker black PLA**, and map the filament to the tool containing it. Parameters remain 220°C nozzle, 65°C bed, 0.12 mm layers / 0.20 mm first, four walls, 25% gyroid, 8 mm³/s flow cap, 0.8 mm retraction at 30 mm/s, 2 mm wipe, 0.20 mm Z hop and PLA cooling. [Full inherited settings](../v28_pla/README.md).

The regenerated disposable supports include a tiny bridge where two base pads otherwise touch only along an edge; this prevents invalid STL topology and does not alter the printed cover. Cover/mount support gap remains at least 0.16 mm by design, subject to layer quantization. Leave the solid middle-root web attached when removing the separate supports and brim after cooling. Test gently without forcing the hooks.

Start with the small cover test (estimated **44m 35s**). The one-plate project prints the matching full mount, shared Box 2 and sliding lid in one job (estimated **2h 55m 18s**). Existing good boxes/lids can be reused. The separate-plate project has cover, mount, box, lid and optional stringing test on plates 1–5.

[Trim geometry](../../validation/v38_pla/trim_checks.json) · [Native meshes/settings](../../validation/v38_pla/geometry_and_project_checks.json) · [Layer/support checks](../../validation/v38_pla/layer_islands.json) · [Middle-root paths](../../validation/v38_pla/middle_root_toolpaths.json) · [Top-shoulder paths](../../validation/v38_pla/hook_toolpath_checks.json) · [One-plate layout](../../validation/v38_pla/one_plate_checks.json) · [Separate-plate slicing](../../validation/v38_pla/slice_result.json) · [One-plate slicing](../../validation/v38_pla/one_plate_slice_result.json)

Native Orca 2.4.1 exports are independently sliced. Extrusion coverage and shoulder contours are planned-path checks, not physical strength tests. Support gaps may trigger floating-region/cantilever warnings; inspect the preview. Physical V38 fit, holding force, durability and print quality remain unverified. Use the Python geometry builder's Manifold union for reproducibility; legacy CGAL import unions can fail on mesh tolerances. No private user imagery is published.
