# Vader 5 Pro detachable Box 2 mount — V25 seating trial

**Latest:** [V25 seating-trial and PETG quality 3MF](print/v25_quality/Vader5Pro_V25_PETG_Seating_Trial_Quality.3mf). It restores original-source clip reach after V24 failed to seat, relieves the cover rim/exterior, and uses five individual plates with 0.12 mm PETG settings, revised retraction/wiping and no timelapse capture commands. **Print plate 1 to check seating before the full mount.** [Details and limits](print/v25_quality/README.md).

No exact OEM cover drawing was found. The owner's 0.91/0.90-inch comparison is approximate, so V25 is a fit trial rather than an OEM-dimension claim.

## V24 — previous revision

**Current PETG project:** [Download V24 for Snapmaker U1 / IEMAI matte black PETG](print/v24_iemai_petg/Vader5Pro_V24_U1_IEMAI_Matte_PETG_Complete.3mf). It includes the corrected box, a matching sliding cap, thinner/longer controller clips, custom supports and a controller-cover fit piece. The separate locking key is removed. [Settings, fitting and support-removal instructions](print/v24_iemai_petg/README.md).

V24 keeps the current box opening size and extends its 20 × 24.5 mm cavity down to the floor. The original male rail stays compatible with the supplied G7 interface. Clip changes and PETG settings still need a physical fit/print trial.

## Previous V23 release — archived

A replacement V2 mounting cover with a slide receiver for the **same detachable G7 Pro V22 Box 2**. Move the box between controllers without changing its enclosure or male rail. Both Box 2 and the removable key are byte-for-byte copies of the supplied G7 parts.

**Snapmaker U1 print project:** [Download the complete black PLA / 0.4 mm 3MF](print/u1_black_pla/Vader5Pro_V23_U1_Black_PLA_Complete.3mf), with saved printer/material settings, oriented parts, custom peelable supports, a spare key and fit-test receiver. [Print and removal instructions](print/u1_black_pla/README.md).

**Status: mesh-checked prototype; physical Vader fit still needs testing.** The V2 cover came from another maker and is reported to fit by the user. No measured controller interface or controller CAD was supplied. The original cover's controller-facing geometry is preserved within STL export precision; this does not independently prove controller fit.

![V23 assembly and receiver](preview/V23_Overview.png)

## Files to print

| File | Purpose |
| --- | --- |
| [Vader5Pro_V23_Mount.stl](print/Vader5Pro_V23_Mount.stl) | V2 cover plus corrected receiver, printed as one part |
| [Box 2.stl](print/Box%202.stl) | Shared detachable G7 V22 box; reuse your existing box |
| [G7_V22_Lock_Key.stl](print/G7_V22_Lock_Key.stl) | Shared G7 V22 removable key |
| [Vader5Pro_V23_Three_Parts.3mf](print/Vader5Pro_V23_Three_Parts.3mf) | Three separate objects arranged on the bed; geometry only, no printer settings |
| [Vader5Pro_V23_Receiver_Fit_Test.stl](print/Vader5Pro_V23_Receiver_Fit_Test.stl) | Small standalone receiver to test with your existing G7 box and key first |

All dimensions are millimeters. Import at **100% scale**. STLs retain their design coordinates; use your slicer's “drop to bed.” The 3MF places all three parts at Z=0 and keeps them separate.

## Corrections from V22

Only the Vader receiver changes. The original G7 box, key, cover clips, external bridge, and receiver key tunnel are retained.

- Raised the rail's bearing bed by **0.41 mm**. The bed now supports the rail at a seating height that gives **0.25 mm** between the receiver lip and box floor, versus V22's nominal 0.07 mm. This also leaves **0.16 mm** above the key tab and avoids using that tab to support the box.
- Relieved each internal dovetail flank by **0.20 mm horizontally** to accommodate the higher rail position. The tightest nominal side gap is approximately **0.265 mm horizontally / 0.215 mm normal to the flank**.
- Extended the closed end stop by **2.30 mm**, reducing nominal fore/aft play from **2.80 mm to 0.50 mm** with the key installed. There is 0.25 mm clearance at each rail end in the reference pose.
- Rebuilt both assembly previews and the three-object 3MF from the corrected geometry.

## First print and assembly

1. Print the small receiver fit test. With the key removed, try your existing G7 Box 2. It should slide by hand and remain captured vertically by the dovetail. Test both 180° orientations.
2. Insert the key laterally through the paired slots at the open end. The original key includes a small flexible retention detent. It must flex while passing the side wall; do not force a rigid or brittle print. Confirm that the installed key blocks the box from sliding out.
3. Print and test the **original V2 cover alone** if its controller fit has not already been established. This isolates controller-clip fit from receiver fit. The archived original is [here](originals/Vader5Pro_Original_V2_Cover.stl).
4. Print the complete V23 mount. Fit it in place of the controller's removable mounting cover, then attach Box 2 and the key. Check the controller buttons, paddles, switches and cable path on your actual controller.
5. To detach, release and withdraw the key sideways, then slide the box out through the open end. Rotate the box 180° in the mounting plane to reverse its USB opening and slide it back in. The enclosure opening remains outward.

In the CAD coordinate system the **open end is +Y**; the closed stop is −Y. Enter from +Y and slide toward −Y. Withdraw toward +Y. The key pulls toward +X from its larger handle. The USB up/down preview names follow the supplied V22 convention.

PETG is a reasonable starting material for the cover and key. Use a calibrated printer, around 0.16–0.20 mm layers and at least four walls. Verify supports in the slicer: the complete mount has downward clips, and the box has a projecting underside rail. The supplied bed layout is not a support preset. Keep support scars off clips, dovetail flanks and key slots. Do not rescale the shared box to tune the fit; adjust `side_relief` in the Vader receiver source instead. Print the fit test again after adjustments.

## Validation and source

[Validation report](validation/VALIDATION.md) · [Machine-readable results](validation/results.json) · [Editable OpenSCAD](source/Vader5Pro_V23.scad) · [USB down inspection GLB](preview/V23_USB_Down.glb) · [USB up inspection GLB](preview/V23_USB_Up.glb)

To reproduce the exports and checks, install OpenSCAD and Python dependencies, then run:

```sh
python -m pip install -r tools/requirements.txt
python tools/build_validate.py
```

The PNG preview can also be regenerated with Blender 4.x and Pillow installed: `python tools/render_preview.py`. The GLB inspection files are generated by the main build script.

All supplied ZIP contents are preserved under [`originals/`](originals/), including the older V22 previews, claims and print layout. **Use `print/` for V23; `originals/` is an archive.** Original maker attribution and redistribution terms were not supplied; this repository does not claim authorship or grant a new license for the imported cover or G7 parts.
