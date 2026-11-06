// Units: mm. Source imports are the unmodified V22 meshes in ../originals.
// Box 2 and key stay identical to the supplied G7 V22 parts.
show = "mount"; // [mount,receiver,usb_down,usb_up,exploded]
receiver_height = 7;
box_height = 13.10; // V22 12.92 + 0.18: 0.25 mm box-floor/lip clearance
side_relief = 0.20; // additional clearance on each female dovetail flank
$fn = 48;

module cover() { import("../originals/Vader5Pro_Original_V2_Cover.stl", convexity=10); }
module box2() { import("../originals/G7_V22_Reversible_Box2.stl", convexity=10); }
module key() { import("../originals/G7_V22_Lock_Key.stl", convexity=10); }

module receiver() {
  union() {
    difference() {
        import("../originals/G7_V22_Universal_Receiver.stl", convexity=10);
        // Enlarge internal dovetail; preserve stop, roof and key slot.
        // Rotate extrusion +90 about X: local Z extrusion points toward -Y.
        translate([0,13.3,0]) rotate([90,0,0]) linear_extrude(height=24.7)
            polygon([[-7.58-side_relief,2.40], [7.58+side_relief,2.40],
                     [5.80182+side_relief,4.85], [5.80182+side_relief,7],
                     [-5.80182-side_relief,7], [-5.80182-side_relief,4.85]]);
    }
    // A bearing bed supports the unchanged male rail at the new seating height.
    // Without this bed, the box could drop onto the original key detent.
    translate([-7.35,-11.4,2.20]) cube([14.7,24.6,0.45]);
    // Bring the closed stop within 0.25 mm of the seated rail end.
    // V22 left 2.55 mm here, allowing unnecessary fore/aft movement.
    translate([-7.35,-11.4,2.20]) cube([14.7,2.30,2.65]);
  }
}
module bridge() {
    translate([0,0,5]) linear_extrude(height=2.35)
        offset(r=1.15) square([15.5,9.7],center=true);
}
module mount() { union() { cover(); bridge(); translate([0,0,receiver_height]) receiver(); } }
module placed_box(up=false) {
    if (up) translate([-1,-1.85,box_height]) rotate([0,0,180]) box2();
    else translate([1,3.75,box_height]) box2();
}
module placed_key() { translate([0,0,receiver_height]) key(); }

if (show == "mount") mount();
if (show == "receiver") receiver();
if (show == "usb_down") { mount(); placed_box(); placed_key(); }
if (show == "usb_up") { mount(); placed_box(true); placed_key(); }
if (show == "exploded") {
    mount(); translate([0,0,14]) placed_box(); translate([12,0,0]) placed_key();
}
