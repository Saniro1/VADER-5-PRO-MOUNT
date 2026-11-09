"""Opposite-edge hook pair: defined L shoulder, stronger neck, root-side gussets."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v34';O=R/'print/v34_pla'
b=trimesh.load_mesh(R/'source/v33/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);leading=upper-4
# Preserve reach and lowest insertion depth. The neck is set back to leave a
# true 1.01 mm shoulder, and the insertion chamfer is only 0.12 mm.
profile=Polygon([(8.35,-.55),(9.20,-.80),(9.55,-1.35),(9.55,-1.65),
                 (leading,-1.65),(leading,-2.565),(leading+.12,-2.685),
                 (10.55,-2.685),(10.75,-2.45),(10.75,-1.10),(9.50,-.55)])
gusset=Polygon([(9.20,-.55),(11.10,-.55),(10.75,-1.65),(9.55,-1.65)])
cutters=[];additions=[]
for lowx in [-13.3,8.3]:
 cut=trimesh.creation.box([5.02,4.6,3.45]);cut.apply_translation([lowx+2.5,9.25,-2.275]);cutters.append(cut) # top Z=-0.55
 # Raise the new root 0.10 mm beyond the cut for a robust Boolean overlap.
 root_profile=Polygon([(yy,zz+.10 if zz>-.81 else zz) for yy,zz in profile.exterior.coords[:-1]])
 toe=extrude_polygon(root_profile,5);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(toe)
 for xx in [lowx,lowx+4.4]:
  brace=extrude_polygon(gusset,.60);brace.apply_transform([[0,0,1,xx],[1,0,0,0],[0,1,0,0],[0,0,0,1]]);additions.append(brace)
body=trimesh.boolean.difference([b]+cutters,engine='manifold');m=simplify(trimesh.boolean.union([body]+additions,engine='manifold'))
assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
assert abs(m.extents[0]-35)<.005 and abs(m.extents[1]-26)<.005
sec=m.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-21)<.01
p=b.vertices;outside=(p[:,2]>-.44)|(np.abs(p[:,0])<8.28)|(np.abs(p[:,0])>13.32)|(p[:,1]<6.95)|(p[:,1]>11.55)
_,dist,_=trimesh.proximity.closest_point(m,p[outside]);assert dist.max()<.01,dist.max()
for sign in [-1,1]:
 for x in [sign*9,sign*10.8,sign*12.5]:
  for yy in [leading+.15,leading+.5,9.3]:
   h,_,_=m.ray.intersects_location([[x,yy,-4]],[[0,0,1]]);assert np.any(abs(h[:,2]+1.65)<.01),(x,yy,h)
m.export(S/'Controller_Cover_A.stl');m.export(O/'V34_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V34_A_Vader_Mount.stl')
(R/'validation/v34_pla/hook_reinforcement.json').write_text(json.dumps({'baseline':'V33','owner_confirmed_hook_pair':'opposite edge from middle clip','owner_feedback':'cover fits better; hooks slip and one broke','nominal_reach_mm':4,'reach_direction_still_assumed':'inward from edge','flat_retaining_shoulder_projection_mm':9.55-leading,'neck_setback_Y':9.55,'rear_neck_Y':10.75,'neck_nominal_Y_thickness_mm':1.20,'entry_chamfer_mm':.12,'gussets_each_hook':2,'gusset_width_mm':.60,'lowest_Z_mm':-2.685,'outside_modified_region_max_sampled_surface_error_mm':float(dist.max()),'printing_change':'Cover and mount rotated 90 degrees about Y: hook profile lies in each XY layer. Designed supports 0.16 mm minimum gap.','measured_shell_and_middle_preserved':True,'physical_strength_or_fit_verified':False,'OEM_shape_exact':False},indent=2)+'\n')
