# V27 printing recovery — unchanged V26 controller parts

[Small cover-test project](Vader5Pro_V27_Cover_Tests_Print_Recovery.3mf) · [Complete project](Vader5Pro_V27_Print_Recovery_Complete.3mf)

The owner reported a tangled failed print with a loose strip visible beside the part. Bed/support detachment or failure to bridge a support gap is plausible, but the photo does not establish the initiating cause. V26's lack of brims and generous support separation were weak points. Successful CAD/slicing checks did not establish reliable physical printing.

V27 changes printing aids and settings only. Every part STL is byte-identical to its V26 equivalent; the A/B hook trial dimensions remain unchanged.

| Printing change | V27 |
| --- | --- |
| Brim on every object, including custom support footprints | 5 mm, 0 mm object gap |
| Minimum designed custom support top gap | 0.20 mm, reduced from 0.32 mm |
| Support height quantization | 0.12 mm, matching layer height |
| Three central support arms | 0.80 mm wide, increased from 0.60 mm |
| Textured PEI bed | 75°C first layer, then 70°C |
| First-layer wall/infill speed | 15 mm/s |
| First-layer acceleration | 300 mm/s² |

Nozzle temperatures remain 245°C first / 240°C later; 0.12 mm layers after a 0.20 mm first layer. Retraction/wipe and ordinary fan settings remain unchanged. The smaller gap favors support reliability and may make removal less effortless; removal force is not physically tested. Brims contact the parts and require trimming. They are disposable, not part of the controller interface.

## Try one small part first

1. Remove all failed material, including any on the nozzle. Wash the cool removable plate with dish soap and water, rinse and dry fully, and avoid touching the print area. Use dry PETG, dried according to the spool maker's instructions if needed. Check that the plate is seated correctly.
2. Open the new 3MF **as a project**, retain its orientations, custom support parts and saved settings, and select the correct U1 0.4 mm nozzle and black PETG tool. Run normal bed leveling. Print only **plate 1 / cover A** first (about 27 minutes).
3. Watch the first few layers. The brim and support feet should lie flat with continuous, joined lines. Stop if they lift, drag, or form loose strands; continuing cannot recover them. If this happens on the first layer despite a clean plate, inspect nozzle cleanliness and run the U1's bed/first-layer calibration before another attempt.
4. Let the plate cool, trim the brim, then gently peel the supports with their pull tabs. Remove remnants beneath the hooks before testing retention. Do not force a cover into the controller.

The small project has A on plate 1 and B on plate 2. Try B only if A fully seats but releases too easily. The complete project retains the seven-plate order: cover A, cover B, matching mount A, matching mount B, shared Box 2, sliding lid, optional stringing test. There is no need to print both full mounts or replace an already good box/lid.

## Evidence and limits

[Native project/geometry checks](../../validation/v27_print_recovery/geometry_and_project_checks.json) · [Layer-overlap checks](../../validation/v27_print_recovery/layer_islands.json) · [Full-project slicing checks](../../validation/v27_print_recovery/slice_result.json) · [Support geometry](../../validation/v27_print_recovery/support_geometry.json)

Native Snapmaker Orca 2.4.1 exports are sliced independently. Custom support air gaps still trigger floating-region/cantilever warnings; inspect the sliced preview. These files have not been physically printed here, and OEM fit, retention force, adhesion and support removal remain unverified. See [V26](../v26_retention/README.md) for unchanged hook geometry and earlier fit feedback.
