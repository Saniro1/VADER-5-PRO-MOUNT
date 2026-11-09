"""Longer top/middle hooks, with full-width web and spread root at middle tongue."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v24_geometry import smooth
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v36';O=R/'print/v36_pla'
b=trimesh.load_mesh(R/'source/v35/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);lower=upper-21;leading=upper-4.3
v,f=trimesh.remesh.subdivide_to_size(b.vertices,b.faces,max_edge=.5,max_iter=7);m=trimesh.Trimesh(v,f,process=True);x,y,z=m.vertices.T.copy()
w=smooth((-9.4-y)/2)*smooth((2.6-np.abs(x))/.1);v=m.vertices.copy();v[:,1]-=.5*w;m.vertices=v
# Top pair retains the V35 width/neck/braces; rebuild only the longer profile.
profile=Polygon([(8.35,-.45),(9.20,-.70),(9.80,-1.35),(9.80,-1.65),(leading,-1.65),(leading,-2.565),(leading+.12,-2.685),(11.20,-2.685),(11.40,-2.45),(11.40,-1.10),(10.,-.45)])
gusset=Polygon([(9.20,-.45),(11.70,-.45),(11.40,-1.65),(9.80,-1.65)])
cutters=[];additions=[]
for lowx in [-13.8,7.8]:
 cut=trimesh.creation.box([6.02,5.,3.55]);cut.apply_translation([lowx+3,9.5,-2.225]);cutters.append(cut)
 root=Polygon([(yy,zz+.1 if zz>-.71 else zz) for yy,zz in profile.exterior.coords[:-1]])
 toe=extrude_polygon(root,6);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(toe)
 for xx in [lowx,lowx+5.2]:
  g=extrude_polygon(gusset,.8);g.apply_transform([[0,0,1,xx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(g)
body=trimesh.boolean.difference([m]+cutters,engine='manifold')
# Solid web fills the middle root's thin step, joining shell and tongue across 5 mm.
web_profile=Polygon([(-6.5,3.7),(-7.9,3.1),(-9.8,1.9),(-10.6,2.4),(-10.6,3.6),(-8.6,3.95),(-7.8,4.45),(-6.5,4.7)])
web=extrude_polygon(web_profile,5);web.apply_transform([[0,0,1,-2.5],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(web)
# Root spreads to 7 mm only INSIDE the shell boundary; projecting tongue stays 5 mm.
brace_profile=Polygon([(-6.4,3.8),(-7.9,3.15),(lower,3.0),(lower,3.98),(-7.8,4.45),(-6.4,4.75)])
brace_footprint=Polygon([(-3.5,-6.4),(3.5,-6.4),(2.5,lower),(-2.5,lower)])
brace=extrude_polygon(brace_profile,7);brace.apply_transform([[0,0,1,-3.5],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
mask=extrude_polygon(brace_footprint,6);additions.append(trimesh.boolean.intersection([brace,mask],engine='manifold'))
result=simplify(trimesh.boolean.union([body]+additions,engine='manifold'));assert result.is_watertight and result.is_winding_consistent and len(result.split())==1
assert abs(result.extents[0]-35)<.005 and abs(result.extents[1]-26.5)<.005
sec=result.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-21)<.01
root_samples=[]
for yy in [-7.4,-7.8,-7.9,-8.2]:
 h,_,_=result.ray.intersects_location([[0,yy,-5]],[[0,0,1]]);zs=np.sort(h[:,2]);assert len(zs)==2 and zs[1]-zs[0]>1.15,(yy,zs);root_samples.append({'Y':yy,'Z_thickness':float(zs[1]-zs[0])})
for yy in [-9,-11,-13.5]:
 sec=result.section(plane_origin=[0,yy,0],plane_normal=[0,1,0]);p=np.vstack(sec.discrete);p=p[np.abs(p[:,0])<3];assert abs(np.ptp(p[:,0])-5)<.01
# Web must overlap BOTH original shell and tongue with positive volume.
web_shell_overlap=trimesh.boolean.intersection([b,web],engine='manifold').volume;assert web_shell_overlap>1
overlap_by_attachment={}
for name,lo,hi in [('shell',lower,0),('tongue',-15,lower)]:
 roi=trimesh.creation.box([10,hi-lo,10]);roi.apply_translation([0,(lo+hi)/2,3]);vol=trimesh.boolean.intersection([web,b,roi],engine='manifold').volume;assert vol>1;overlap_by_attachment[name]=float(vol)
result.export(S/'Controller_Cover_A.stl');result.export(O/'V36_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([result,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V36_A_Vader_Mount.stl')
(R/'validation/v36_pla/anchored_hook_checks.json').write_text(json.dumps({'baseline':'V35','top_reach_mm':4.3,'top_extra_reach_mm':.3,'top_width_mm':6,'top_neck_mm':1.6,'middle_projection_mm':5.5,'middle_extra_reach_mm':.5,'middle_width_mm':5,'shell_mm':[35,21],'overall_mm':26.5,'middle_web_width_mm':5,'middle_root_spread_within_shell_mm':7,'web_overlap_with_old_part_mm3':float(web_shell_overlap),'web_overlap_by_attachment_mm3':overlap_by_attachment,'sampled_root_sections':root_samples,'cover_components':1,'mount_components':1,'physical_fit_strength_verified':False,'local_clearance_of_added_web_measured':False},indent=2)+'\n')
