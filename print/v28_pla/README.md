# V28 — regular Snapmaker black PLA / U1 0.4 mm

[Small cover-test 3MF](Vader5Pro_V28_Snapmaker_PLA_Black_Cover_Tests.3mf) · [Complete seven-plate 3MF](Vader5Pro_V28_Snapmaker_PLA_Black_Complete.3mf)

These projects retain the V28 underside-clearance geometry, orientations, custom supports and brims, with embedded PLA printer/material/process settings. This is **regular Snapmaker PLA Basic, black, 1.75 mm**, not SnapSpeed PLA. The filament profile starts from Snapmaker Orca's bundled U1 PLA Basic profile. Retraction, cooling timing and flow limits below are conservative starting choices, not measurements of your spool.

| Saved setting | Value |
| --- | --- |
| Printer / nozzle | Snapmaker U1 / standard 0.4 mm |
| Bed selected | Textured PEI Plate |
| Filament | Snapmaker PLA Basic black, 1.75 mm |
| Nozzle temperature | 220°C first and subsequent layers |
| Bed temperature | 65°C first and subsequent layers |
| Layer height | 0.12 mm; 0.20 mm first layer |
| Walls / infill | 4 / 25% gyroid |
| Outer wall / top surface | 25 / 20 mm/s |
| First layer wall/infill | 15 mm/s |
| Maximum volumetric speed | 8 mm³/s |
| Flow ratio | 0.98 starting value |
| Retraction | 0.8 mm at 30 mm/s; recovery 30 mm/s |
| Wipe / Z hop | 2 mm, 70% retract before wipe / 0.20 mm |
| Part fan | Off first layer; full cooling by layer 3 |
| Auxiliary cooling | 30% |
| Brim | 5 mm, contacting the object; trim after cooling |
| Supports | Included custom same-PLA supports; automatic supports off |
| Designed support top gap | At least 0.20 mm |

Normal U1 homing, bed leveling and nozzle cleaning routines are retained. Timelapse capture commands remain removed from this project. Single material, one object per plate avoids travel between separate printed items. No printer connection, host address or credentials are embedded.

## Open and print

1. Load regular black Snapmaker PLA into the chosen U1 tool. Wash, rinse and dry the cool build plate and remove failed material from the nozzle.
2. Open the 3MF **as a project**, keeping its saved printer, filament and process settings. Confirm **Snapmaker U1 / 0.4 nozzle**, **Textured PEI Plate** and the black PLA filament. If Orca asks for filament mapping, map it to the tool containing that PLA. Keep 100% scale and the included support objects.
3. Slice **plate 1 / cover A** and inspect the preview. Use normal bed leveling. Watch the first few layers and stop if a brim/support foot lifts or strands drag.
4. After cooling, trim the brim and gently remove the support combs and arms. Clear support remnants under the clips before trying the cover. Test B on plate 2 only if A still sits high; do not force either cover.

Both covers use V26 A retaining features. A has 0.15 mm additional underside clearance; B has 0.30 mm. The complete project's plates 3/4 contain their matching full mounts, 5 contains shared Box 2, 6 contains its sliding lid, and 7 is an optional stringing test. Print the matching mount only after a bare cover seats and retains properly. Existing good boxes/lids can be reused.

PLA changes shrinkage and flexibility, so earlier PETG fit results do not establish PLA fit. Physical print quality, snap durability and seating remain unverified. Custom support gaps may still trigger floating-region warnings in Orca; inspect the preview. The support layout is geometrically unchanged from V28 PETG and retains its prior layer-overlap checks.

[Saved profiles](../../source/v28_pla) · [Native geometry/settings checks](../../validation/v28_pla/geometry_and_project_checks.json) · [Complete slice checks](../../validation/v28_pla/slice_result.json) · [Fit-only slice checks](../../validation/v28_pla/fit_only_slice_result.json) · [V28 geometry and limitations](../v28_seating/README.md)

For reproducible CLI export with Snapmaker Orca, load `source/v28_pla/U1_0p4_machine.json` and `source/v28_pla/U1_PLA_Quality_Process.json` using `--load-settings`, and `source/v28_pla/Snapmaker_PLA_Black.json` using `--load-filaments`. Use `source/v28/U1_Oriented_Seed.3mf` (complete) or `source/v28/U1_Fit_Only_Seed.3mf` (covers), with `--arrange 0 --orient 0 --export-3mf <output.3mf>`.
