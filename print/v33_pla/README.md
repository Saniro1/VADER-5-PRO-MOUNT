# V33 — owner-measured cover dimensions / Snapmaker black PLA

[Small cover test](Vader5Pro_V33_PLA_Measured_Cover_Test.3mf) · [All functional parts on ONE plate](Vader5Pro_V33_All_Parts_One_Plate_PLA.3mf) · [Separate-plate project](Vader5Pro_V33_PLA_Measured_Cover_Complete.3mf)

The owner supplied 35 mm width, 21 mm shell height excluding the middle clip, a 5 × 5 mm middle clip and confirmed 26 mm overall including that clip. V33 targets those nominal CAD dimensions. The owner also supplied 4 mm for top clips “measured from the edge.” **This revision assumes that means inward from the shell edge to the hook tip; that direction has not been explicitly confirmed.** If it means height above the shell, do not treat these top clips as measured equivalents.

| Feature | V33 CAD target |
| --- | --- |
| Shell width | 35 mm |
| Shell up/down extent away from clips | 21 mm |
| Middle clip width / projection beyond shell rim | 5 / 5 mm |
| Overall including middle clip | 26 mm |
| Paired top-clip reach from retained shell edge | 4 mm, assumed inward datum |

V32's shell measured approximately 22.8 mm away from its clips. V33 trims about 1.8 mm from the lower shell rim while preserving the upper rim and shell curvature. This exposes the middle tongue to the full measured 5 mm projection; the tongue is narrowed to 5 mm and its tip trimmed to the 26 mm overall extent. No global scaling is used. Paired top-hook ends are rebuilt to 4 mm reach with V32's flat retaining ledge, 0.30 mm entry bevel and 0.15 mm plan-corner chamfers. Other unmeasured hook-profile dimensions, shell curvature and thickness remain trial geometry. Measurements were supplied without an uncertainty or instrument specification.

These dimensions are checked on the exported CAD mesh. They do not establish an exact OEM copy or actual printed fit. The KIRI scan has no unit metadata and does not resolve all hook undercuts reliably; it is a qualitative layout reference and is not copied into the printable geometry. The damaged top scan area is excluded as requested. No scan texture or hand imagery is published here.

## Printing and checking

Print the **small cover test first** and remove every brim/support remnant after cooling. Check seating and retention with gentle pressure; stop if it needs force. The one-plate project prints the full mount, Box 2 and sliding lid together. The separate-plate project has cover, mount, box, lid and optional stringing test on plates 1–5. Reuse already good boxes/lids.

Open as a project in Snapmaker Orca, retain U1 standard 0.4 mm nozzle / Textured PEI Plate / regular Snapmaker black PLA, and map it to the tool holding that PLA. Keep 100% scale, orientations, custom supports and brims. Settings remain 220°C nozzle, 65°C bed, 0.12 mm layers / 0.20 mm first, four walls, 25% gyroid, 8 mm³/s flow cap, 0.8 mm retraction at 30 mm/s, 2 mm wipe, 0.20 mm Z hop, PLA cooling and 5 mm contacting brims. [Full inherited settings](../v28_pla/README.md).

[Measured-dimension checks and datums](../../validation/v33_pla/measured_dimensions.json) · [Native mesh/settings checks](../../validation/v33_pla/geometry_and_project_checks.json) · [Layer checks](../../validation/v33_pla/layer_islands.json) · [One-plate layout](../../validation/v33_pla/one_plate_checks.json) · [Separate-plate slice](../../validation/v33_pla/slice_result.json) · [One-plate slice](../../validation/v33_pla/one_plate_slice_result.json) · [Geometry builder](../../tools/build_v33_geometry.py)

Native Snapmaker Orca 2.4.1 projects are independently sliced. Support gaps may trigger floating-region/cantilever warnings; inspect the preview. Physical fit, force, hook strength and printing reliability remain unverified. Use the Python builder for reproducible Manifold union with the mount core; legacy CGAL unions of imported meshes can fail on mesh tolerances.
