"""Catch lips +3 mm in reach, lower shell edge +3 mm with anchored middle hook."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v24_geometry import smooth
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v37';O=R/'print/v37_pla'
b=trimesh.load_mesh(R/'source/v36/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);old_lower=upper-21;new_lower=old_lower-3;leading=upper-7.3
v,f=trimesh.remesh.subdivide_to_size(b.vertices,b.faces,max_edge=.35,max_iter=8);m=trimesh.Trimesh(v,f,process=True);x,y,z=m.vertices.T.copy()
# Extend the last 2 mm of the lower shell progressively, reaching +3 mm at
# its rim. The projecting middle hook moves with the rim, not relative to it.
t=smooth((old_lower+2-y)/2)
# Keep low controller-contact faces of the supplementary side latches fixed;
# their root transition blends into the extended shell above Z=3.0..3.4.
side_latch=smooth((np.abs(x)-13.6)/.4)*smooth((3.4-z)/.4)
v=m.vertices.copy();v[:,1]-=3*t*(1-side_latch);m.vertices=v
# Rebuild only the toe overhang: legs retain their Z-depth and neck positions.
profile=Polygon([(8.35,-.45),(9.20,-.70),(9.80,-1.35),(9.80,-1.65),(leading,-1.65),(leading,-2.565),(leading+.12,-2.685),(11.20,-2.685),(11.40,-2.45),(11.40,-1.10),(10.,-.45)])
gusset=Polygon([(9.20,-.45),(11.70,-.45),(11.40,-1.65),(9.80,-1.65)])
cutters=[];adds=[]
for lowx in [-13.8,7.8]:
 cut=trimesh.creation.box([6.02,7.3,3.55]);cut.apply_translation([lowx+3,8.35,-2.225]);cutters.append(cut)
 root=Polygon([(yy,zz+.1 if zz>-.71 else zz) for yy,zz in profile.exterior.coords[:-1]])
 toe=extrude_polygon(root,6);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);adds.append(toe)
 for xx in [lowx,lowx+5.2]:
  brace=extrude_polygon(gusset,.8);brace.apply_transform([[0,0,1,xx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);adds.append(brace)
body=trimesh.boolean.difference([m]+cutters,engine='manifold');result=simplify(trimesh.boolean.union([body]+adds,engine='manifold'))
assert result.is_watertight and result.is_winding_consistent and len(result.split())==1
assert abs(result.extents[0]-35)<.005 and abs(result.extents[1]-29.5)<.005
sec=result.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);shell_h=float(np.ptp(np.vstack(sec.discrete)[:,1]));assert abs(shell_h-24)<.01
assert abs(result.bounds[0,2]-b.bounds[0,2])<.005
# Check the middle tongue is still five wide and projects 5.5 beyond NEW rim.
assert abs(new_lower-result.bounds[0,1]-5.5)<.01
for yy in [new_lower-.5,new_lower-2.5,new_lower-4.5]:
 sec=result.section(plane_origin=[0,yy,0],plane_normal=[0,1,0]);p=np.vstack(sec.discrete);p=p[np.abs(p[:,0])<3];assert abs(np.ptp(p[:,0])-5)<.01
roots=[]
for source_y in [-7.4,-7.8,-7.9,-8.2]:
 yy=source_y-3*float(smooth((old_lower+2-source_y)/2));h,_,_=result.ray.intersects_location([[0,yy,-5]],[[0,0,1]]);zs=np.sort(h[:,2]);assert len(zs)==2 and np.ptp(zs)>1.15,(yy,zs);roots.append({'Y':yy,'Z_thickness':float(np.ptp(zs))})
v=b.vertices;contacts=(np.abs(v[:,0])>14)&(np.abs(v[:,0])<16.5)&(v[:,1]<-3)&(v[:,1]>-8.4)&(v[:,2]<2)
_,contact_error,_=trimesh.proximity.closest_point(result,v[contacts]);assert contact_error.max()<.01
result.export(S/'Controller_Cover_A.stl');result.export(O/'V37_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([result,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V37_A_Vader_Mount.stl')
(R/'validation/v37_pla/direction_correction.json').write_text(json.dumps({'baseline':'V36','owner_confirmed_top_change':'Catch lips only, +3 mm overhang; not 3 mm deeper legs','catch_lip_extra_reach_mm':3,'new_inward_reach_mm':7.3,'top_hook_width_mm':6,'top_neck_mm':1.6,'lowest_Z_old_new':[float(b.bounds[0,2]),float(result.bounds[0,2])],'owner_confirmed_bottom_change':'Main curved cover edge +3 mm','shell_old_mm':[35,21],'shell_new_mm':[35,shell_h],'middle_hook_moved_with_rim_mm':3,'middle_projection_beyond_new_rim_mm':5.5,'overall_including_middle_mm':float(result.extents[1]),'lower_shell_transition':'Continuous localized Y stretch over last 2 mm of prior shell; X/Z retained. Low supplementary side-latch contacts excluded from stretch.','middle_root_sections':roots,'physical_clearance_fit_strength_verified':False,'exact_OEM_replica':False,'supplementary_side_latch_contact_max_sampled_error_mm':float(contact_error.max())},indent=2)+'\n')
