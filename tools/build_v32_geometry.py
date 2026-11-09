"""Rebuild top-toe profiles: flat retaining ledge and beveled entry; preserve V31 reach."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v28_supports import extrude_polygon
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v32';O=R/'print/v32_pla'
b=trimesh.load_mesh(R/'source/v31/Controller_Cover_A.stl')
cutters=[];toes=[]
profile=Polygon([(7.56,-1.65),(9.40,-1.65),(10.65,-1.65),(10.65,-2.30),(10.43,-2.685),(7.86,-2.685),(7.56,-2.385)])
for lowx in [-13.3,8.3]:
 cut=trimesh.creation.box([5.02,4.5,2.3]);cut.apply_translation([lowx+2.5,9.25,-2.85]);cutters.append(cut)
 front=trimesh.creation.box([5.02,2.15,2.6]);front.apply_translation([lowx+2.5,8.075,-2.7]);cutters.append(front)
 toe=extrude_polygon(profile,5.0);toe.apply_transform([[0,0,1,lowx],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
 # Small plan-view corner chamfers at the two leading outside corners.
 fp=Polygon([(lowx+.15,7.56),(lowx+4.85,7.56),(lowx+5,7.71),(lowx+5,10.65),(lowx,10.65),(lowx,7.71)])
 mask=extrude_polygon(fp,3);mask.apply_translation([0,0,-3]);toe=trimesh.boolean.intersection([toe,mask],engine='manifold');toes.append(toe)
body=trimesh.boolean.difference([b]+cutters,engine='manifold');m=simplify(trimesh.boolean.union([body]+toes,engine='manifold'))
assert m.is_watertight and len(m.split())==1
m.export(S/'Controller_Cover_A.stl');m.export(O/'V32_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V32_A_Vader_Mount.stl')
p=b.vertices;outside=(p[:,2]>-1.39)|(np.abs(p[:,0])<8.28)|(np.abs(p[:,0])>13.32)|(p[:,1]<7)|(p[:,1]>11.5)
_,d,_=trimesh.proximity.closest_point(m,p[outside]);assert d.max()<.01,d.max()
assert abs(m.bounds[0,1]-b.bounds[0,1])<.005
for sign in [-1,1]:
 # The retaining face is horizontal, with the original reach maintained.
 for x in [sign*9,sign*10.8,sign*12.5]:
  for y in [7.9,8.4,8.9]:
   h,_,_=m.ray.intersects_location([[x,y,-4]],[[0,0,1]]);zs=h[:,2];assert np.any(abs(zs+1.65)<.01),(x,y,zs)
(R/'validation/v32_pla/hook_profile_change.json').write_text(json.dumps({'baseline':'V31','hook_width_mm':5,'leading_y_mm':7.56,'retaining_face_z_mm':-1.65,'lowest_z_mm':-2.685,'entry_bevel_mm':.30,'plan_corner_chamfer_mm':.15,'outside_hook_region_max_sampled_surface_error_mm':float(d.max()),'middle_clip_unchanged':True,'OEM_profile_exact':False,'physical_fit_verified':False},indent=2)+'\n')
