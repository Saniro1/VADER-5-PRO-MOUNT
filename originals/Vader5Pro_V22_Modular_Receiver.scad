// VADER 5 PRO / FLYDIGI V2 rear cover: universal G7 V22 modular gyro docking receiver.
// Matches G7 Pro V22 box and locking key exactly (source STLs imported unchanged).
// Original 85盖.3mf cover mounting clips preserved. Only the outside center is joined.
// All dimensions in millimeters.
// To view only: change show to "exploded". Export for printing with show="mount".
show = "mount"; // [mount,assembled_usb_down,assembled_usb_up,exploded]
receiver_height = 7.0;
box_height = receiver_height+5.92; // 0.07 gap to rail top (female lip z=4.85, male box bottom z=-1)
$fn=48;
module original_cover(){import("Vader5Pro_Original_V2_Cover.stl", convexity=10);}
module original_g7_v22_receiver(){translate([0,0,receiver_height])import("G7_V22_Universal_Receiver.stl", convexity=10);}
module bridge_to_outer_cover(){
    // Centered outer pad; sits at Z>=5.0 (cover's controller-facing clips are underneath).
    translate([0,0,5.0])linear_extrude(height=2.35)
        offset(r=1.15)square([15.5,9.7],center=true);
}
module vader_cover_with_receiver(){union(){original_cover();bridge_to_outer_cover();original_g7_v22_receiver();}}
module box_usb_down(){
    // G7 v22 male rail is centered at X=-1. 1mm shift matches universal receiver.
    // Male rail occupies receiver Y[-8.85,+10.75], leaving room for lock key at +Y.
    translate([1.0,3.75,box_height])import("G7_V22_Reversible_Box2.stl",convexity=10);
}
module box_usb_up(){
    // 180-degree reversal preserves the same male rail location in the receiver.
    translate([-1.0,-1.85,box_height])rotate([0,0,180])import("G7_V22_Reversible_Box2.stl",convexity=10);
}
module lock_key(){translate([0,0,receiver_height])import("G7_V22_Lock_Key.stl",convexity=10);}
if(show=="mount")vader_cover_with_receiver();
if(show=="assembled_usb_down"){vader_cover_with_receiver();box_usb_down();lock_key();}
if(show=="assembled_usb_up"){vader_cover_with_receiver();box_usb_up();lock_key();}
if(show=="exploded"){vader_cover_with_receiver();translate([0,0,12])box_usb_down();translate([0,0,6])lock_key();}
