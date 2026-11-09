"""Broaden and stiffen the opposite-edge pair without extending reach/depth."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v35';O=R/'print/v35_pla'
b=trimesh.load_mesh(R/'source/v34/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);leading=upper-4
profile=Polygon([(8.35,-.45),(9.20,-.70),(9.80,-1.35),(9.80,-1.65),
                 (leading,-1.65),(leading,-2.565),(leading+.12,-2.685),
                 (11.20,-2.685),(11.40,-2.45),(11.40,-1.10),(10.0,-.45)])
gusset=Polygon([(9.20,-.45),(11.70,-.45),(11.40,-1.65),(9.80,-1.65)])
cutters=[];additions=[]
for lowx in [-13.8,7.8]:
 cut=trimesh.creation.box([6.02,5.0,3.55]);cut.apply_translation([lowx+3,9.5,-2.225]);cutters.append(cut) # top=-0.45
 root=Polygon([(yy,zz+.10 if zz>-.71 else zz) for yy,zz in profile.exterior.coords[:-1]])
 toe=extrude_polygon(root,6);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(toe)
 for xx in [lowx,lowx+5.2]:
  brace=extrude_polygon(gusset,.8);brace.apply_transform([[0,0,1,xx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(brace)
body=trimesh.boolean.difference([b]+cutters,engine='manifold');m=simplify(trimesh.boolean.union([body]+additions,engine='manifold'))
assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
assert abs(m.extents[0]-35)<.005 and abs(m.extents[1]-26)<.005
sec=m.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-21)<.01
p=b.vertices;outside=(p[:,2]>-.34)|(np.abs(p[:,0])<7.78)|(np.abs(p[:,0])>13.82)|(p[:,1]<6.99)|(p[:,1]>12.01)
_,d,_=trimesh.proximity.closest_point(m,p[outside]);assert d.max()<.01,d.max()
for sign in [-1,1]:
 for x in [sign*8.1,sign*10.8,sign*13.5]:
  for yy in [leading+.15,leading+.6,9.55]:
   h,_,_=m.ray.intersects_location([[x,yy,-4]],[[0,0,1]]);assert np.any(abs(h[:,2]+1.65)<.01),(x,yy,h)
for yy in [-9,-11,-13]:
 sec=m.section(plane_origin=[0,yy,0],plane_normal=[0,1,0]);p=np.vstack(sec.discrete);p=p[np.abs(p[:,0])<3];assert abs(np.ptp(p[:,0])-5)<.01
m.export(S/'Controller_Cover_A.stl');m.export(O/'V35_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V35_A_Vader_Mount.stl')
(R/'validation/v35_pla/wider_hook_checks.json').write_text(json.dumps({'baseline':'V34','target_pair':'opposite edge from middle clip','hook_width_mm':6,'previous_hook_width_mm':5,'neck_Y_thickness_mm':1.6,'previous_neck_Y_thickness_mm':1.2,'retaining_shoulder_projection_mm':9.8-leading,'gusset_width_mm':.8,'gussets_each_hook':2,'tip_reach_mm':4,'lowest_Z_mm':-2.685,'entry_chamfer_mm':.12,'outside_modified_region_max_sampled_surface_error_mm':float(d.max()),'shell_35x21_middle_5x5_overall_26_preserved':True,'controller_slot_clearance_measured':False,'physical_fit_or_strength_verified':False},indent=2)+'\n')
