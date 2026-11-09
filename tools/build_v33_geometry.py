"""Measured shell 35x21 mm, 5x5 middle tongue, 26 overall; top reach assumed 4 mm inward."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v33';O=R/'print/v33_pla'
b=trimesh.load_mesh(R/'source/v32/Controller_Cover_A.stl')
upper=float(b.bounds[1,1]);lower=upper-21;tip=upper-26;leading=upper-4
# Remove the overlong shell rim outside the measured 5 mm-wide central tongue.
cutters=[]
for xlo,xhi in [(-30,-2.5),(2.5,30)]:
 box=trimesh.creation.box([xhi-xlo,lower+30,30]);box.apply_translation([(xlo+xhi)/2,(-30+lower)/2,0]);cutters.append(box)
end=trimesh.creation.box([60,tip+30,30]);end.apply_translation([0,(-30+tip)/2,0]);cutters.append(end)
# Rebuild the top toes to 4 mm from the retained upper shell edge.
profile=Polygon([(leading,-1.65),(9.40,-1.65),(10.65,-1.65),(10.65,-2.30),(10.43,-2.685),(leading+.30,-2.685),(leading,-2.385)])
toes=[]
for lowx in [-13.3,8.3]:
 cut=trimesh.creation.box([5.02,4.5,2.3]);cut.apply_translation([lowx+2.5,9.25,-2.85]);cutters.append(cut)
 front=trimesh.creation.box([5.02,2.15,2.6]);front.apply_translation([lowx+2.5,8.075,-2.7]);cutters.append(front)
 toe=extrude_polygon(profile,5);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
 fp=Polygon([(lowx+.15,leading),(lowx+4.85,leading),(lowx+5,leading+.15),(lowx+5,10.65),(lowx,10.65),(lowx,leading+.15)])
 mask=extrude_polygon(fp,3);mask.apply_translation([0,0,-3]);toes.append(trimesh.boolean.intersection([toe,mask],engine='manifold'))
body=trimesh.boolean.difference([b]+cutters,engine='manifold');m=simplify(trimesh.boolean.union([body]+toes,engine='manifold'))
assert m.is_watertight and len(m.split())==1
assert abs(m.extents[0]-35)<.005 and abs(m.extents[1]-26)<.005
# Shell measured away from clips, tongue measured below the shell edge.
s=m.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);pts=np.vstack(s.discrete);shell_length=np.ptp(pts[:,1]);assert abs(shell_length-21)<.01
widths=[]
for yy in [lower-.5,lower-2.5,lower-4.5]:
 sec=m.section(plane_origin=[0,yy,0],plane_normal=[0,1,0]);p=np.vstack(sec.discrete);p=p[np.abs(p[:,0])<3];widths.append(float(np.ptp(p[:,0])));assert abs(widths[-1]-5)<.01
for sign in [-1,1]:
 p=m.vertices;sel=(p[:,0]*sign>8)&(p[:,0]*sign<13.5)&(p[:,1]>7)&(p[:,2]<-1.7);assert abs(p[sel,1].min()-leading)<.01
m.export(S/'Controller_Cover_A.stl');m.export(O/'V33_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V33_A_Vader_Mount.stl')
(R/'validation/v33_pla/measured_dimensions.json').write_text(json.dumps({'owner_measured_mm':{'shell_width':35,'shell_height':21,'middle_width':5,'middle_length':5,'overall_height':26,'top_clip_from_edge':4},'CAD_mm':{'width':float(m.extents[0]),'shell_height_section_X_5':float(shell_length),'overall_height':float(m.extents[1]),'middle_width_samples':widths,'middle_projection':lower-float(m.bounds[0,1]),'top_clip_inward_reach':upper-leading},'datums':{'shell_upper_Y':upper,'shell_lower_Y':lower,'middle_tip_Y':tip,'top_toe_Y':leading},'top_clip_reference_assumption':'4 mm inward from shell edge to tip; owner has not explicitly confirmed this direction.','method':'Trim lower shell rim and narrow middle tongue; rebuild top toes to reach. No global scaling.','physical_fit_verified':False,'shell_curvature_and_thickness_measured':False,'OEM_hook_profile_exact':False},indent=2)+'\n')
