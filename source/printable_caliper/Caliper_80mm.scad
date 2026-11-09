// Millimeters. Sliding PLA measuring aid; not a precision metrology instrument.
$fn=32;
part="beam";
module engraving(x,y,label,size=2.7){translate([x,y,2.75])linear_extrude(0.6)text(label,size=size,font="DejaVu Sans:style=Bold",halign="center");}
module beam(){difference(){
 union(){
  cube([124,12,3.2]);
  // Outside jaw: fixed measuring face at X=11.
  translate([8,-24,0])cube([3,25,5]);
  // Inside tips: 1 mm each; add 2 mm to the scale reading.
  translate([8,11,0])cube([3,9,5]);translate([10,20,0])cube([1,5,5]);
 }
 for(i=[0:80]){
  translate([11+i,0.65,2.75])cube([0.42,i%10==0?5.0:(i%5==0?3.8:2.5),0.6]);
  if(i%10==0)engraving(11+i,7.0,str(i));
 }
 engraving(106,7,"mm",2.5);engraving(107,2,"IN +2",2.3);
}}
module slider(){difference(){
 union(){
  // Enclosed guide: 0.20 mm clearance around the beam.
  translate([11,-1.5,-1.4])cube([20,15,6.4]);
  translate([11,-24,-1.4])cube([3,23,6.4]);
  translate([11,13,-1.4])cube([3,7,6.4]);translate([11,20,-1.4])cube([1,5,6.4]);
 }
 translate([10.8,-0.20,-0.20])cube([20.5,12.4,3.6]);
 // Open front reading window; side rails and floor remain.
 translate([10.8,-0.20,3.40])cube([7.2,12.4,2]);
 // Index line is the left measuring face X=11, beside the scale.
 translate([10.99,-1.51,4.5])cube([0.45,1.6,0.6]);
}}
module gauge(){difference(){
 cube([40,20,3.2]);translate([10,10,-.1])cube([20,10.1,3.4]);
 engraving(20,3,"40 / 20",2.8);
}}
if(part=="beam")beam();
if(part=="slider")slider();
if(part=="gauge")gauge();
if(part=="assembly"){beam();translate([25,0,0])slider();}
