# V23 validation

Geometry checks use OpenSCAD 2021.01, trimesh and the Manifold solid Boolean engine. See `tools/build_validate.py` and `results.json` for the executable checks and measured results.

## Passed checks

- Complete mount, receiver fit test, shared Box 2 and key each form one connected, watertight solid with consistent winding and positive volume.
- Shared Box 2 and key match the supplied G7 files byte-for-byte; SHA-256 hashes are recorded in `results.json`.
- Controller-facing cover geometry below Z=5 mm matches the original within a 0.01 mm³ symmetric-difference tolerance for mesh serialization. The added receiver and bridge are outside this region.
- Box/mount, box/key and key/mount have no positive solid intersection in either reference orientation.
- With the key removed, both box orientations clear the mount throughout a +Y removal sweep from 0 to 40 mm, checked every 0.25 mm. Insertion follows the same path in reverse. The straight prismatic rail/channel profiles have clearance along that direction.
- Moving the box 0.01 mm downward intersects the bearing bed, confirming support at the intended seating height. Moving it 1 mm toward the exit intersects the installed key; moving it 0.5 mm toward the closed end intersects the stop.
- Saved 3MF independently reopened and checked: three separate watertight objects, each at bed level, with no part overlaps.

## Nominal interface dimensions

| Feature | V23 |
| --- | ---: |
| Receiver outer width × length × height | 20.50 × 25.80 × 4.85 mm |
| Mount overall width × length × height | approximately 35.20 × 26.28 × 14.535 mm |
| Box floor above receiver lip | 0.25 mm |
| Male rail bottom above bearing bed | 0 mm, bearing contact |
| Tightest horizontal flank clearance per side | approximately 0.265 mm |
| Tightest normal flank clearance | approximately 0.215 mm |
| Key detent below box floor | 0.16 mm |
| Rail end clearance to key / closed stop | 0.25 / 0.25 mm |
| Total nominal fore/aft play | 0.50 mm |

The exact reference assembly transforms are: receiver/key translation `[0,0,7]`; USB-down box translation `[1,3.75,13.10]`; USB-up box rotation 180° around Z followed by translation `[-1,-1.85,13.10]`. Box STLs retain the original off-center rail and enclosure coordinates; do not center the box on X=0 by eye in the assembly.

## Limits

The controller-facing cover is inherited from the user-supplied model. The user reports that its maker says it fits; no independent physical fit has been established here. No controller shell model, mounting-slot measurements, electronics model or cable model was provided. Button/paddle clearance, electronics fit, cable access, clip retention, print tolerances, fatigue and load capacity require a physical test.

The G7 receiver itself was not supplied as a complete controller assembly; interoperability here means preserving the exact supplied G7 V22 male rail and key. It does not establish compatibility with other G7 revisions.

The key's original retention detent flexes during lateral insertion and removal. Its transient interference with the receiver wall is intentional; this is not a rigid collision-free key insertion claim. Material flexibility and print quality must be checked with the fit-test receiver.

Nominal clearances and zero solid intersections do not guarantee a particular printer's fit. Start with the coupon and original cover before printing the full assembly.
