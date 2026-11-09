// Millimeters. V36 uses the supplied male rail and unchanged top-opening width.
// Clip revisions are localized in build_v36_geometry.py, not global scaling.
$fn=48;
part="mount";
variant="A"; // A: measured shell preserved; top reach 4.3 mm; middle reach 5.5 mm with solid tapered web
module cover(){import(str("Controller_Cover_",variant,".stl"),convexity=12);}
module box2(){
    difference(){
        import("../../originals/G7_V22_Reversible_Box2.stl",convexity=12);
        // Extend the EXISTING 20 x 24.5 mm top opening down to the 2 mm floor.
        // Removes the lower 18 x 20 mm step, preserving outer walls and rails.
        translate([-11,-14.5,1])cube([20,24.5,30]);
    }
}
module keyless_receiver(){
    union(){
        difference(){
            union(){
                import("../../originals/G7_V22_Universal_Receiver.stl",convexity=12);
                // Fill both old key tunnels. No key or locking slot remains.
                translate([-10.25,10.75,2.40])cube([4.50,2.45,2.45]);
                translate([5.75,10.75,2.40])cube([4.50,2.45,2.45]);
            }
            translate([0,13.3,0])rotate([90,0,0])linear_extrude(height=24.7)
                polygon([[-7.78,2.40],[7.78,2.40],[6.00182,4.85],[6.00182,7],[-6.00182,7],[-6.00182,4.85]]);
        }
        translate([-7.35,-11.4,2.20])cube([14.7,24.6,0.45]);
        translate([-7.35,-11.4,2.20])cube([14.7,2.30,2.65]);
    }
}
module bridge(){translate([0,0,4.5])linear_extrude(height=2.85)offset(r=1.15)square([15.5,9.7],center=true);}
module mount(){union(){cover();bridge();translate([0,0,7])keyless_receiver();}}

// Replacement sliding cap: 1 mm outer guide walls, 0.9 mm retaining lips,
// 0.30 mm lateral rail/hook clearance; 0.30 mm clearance below the side rails.
// No tiny snap detents. Positive-Y end is open; negative-Y has a rail end stop.
module cap(){
    difference(){
        union(){
            translate([-16.15,-17.8,23.75])cube([30.30,30.10,1.60]);
            translate([-16.15,-17.8,20.60])cube([1.00,30.10,3.20]);
            translate([13.15,-17.8,20.60])cube([1.00,30.10,3.20]);
            translate([-16.15,-17.8,20.60])cube([2.90,30.10,0.90]);
            translate([11.25,-17.8,20.60])cube([2.90,30.10,0.90]);
            translate([-16.15,-17.8,20.60])cube([2.90,1.70,4.75]);
            translate([11.25,-17.8,20.60])cube([2.90,1.70,4.75]);
            // Shallow raised grip at the closed edge; no unsupported pull tab.
            translate([-4.75,-17.8,25.30])cube([7.50,2.20,0.65]);
        }
        // USB/cable notch is slightly wider than the existing box notch.
        translate([-8.90,8.65,23.70])cube([15.80,5,4]);
    }
}
if(part=="cover")cover();
if(part=="box")box2();
if(part=="cap")cap();
if(part=="mount")mount();
if(part=="receiver")keyless_receiver();
if(part=="assembly"){
    color("#3c434b")mount();
    translate([1,3.75,13.10]){
        color("#60656c")box2();
        color("#9da5af")cap();
    }
}

if(part=="mount_core")union(){bridge();translate([0,0,7])keyless_receiver();}
