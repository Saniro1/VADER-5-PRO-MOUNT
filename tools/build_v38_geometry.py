"""Trim one millimeter from V37 top-lip reach and middle projection; shell unchanged."""
from pathlib import Path
import json
import numpy as np,trimesh
from shapely.geometry import Polygon
from build_v24_geometry import smooth
from build_v28_supports import extrude_polygon
import manifold3d
def simplify(mesh):
 solid=manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.asarray(mesh.vertices,dtype=np.float64),tri_verts=np.asarray(mesh.faces,dtype=np.uint64))).simplify(.001).to_mesh()
 result=trimesh.Trimesh(solid.vert_properties[:,:3],solid.tri_verts,process=True)
 assert result.is_watertight and result.is_winding_consistent and len(result.split())==1
 return result
R=Path(__file__).resolve().parents[1];S=R/'source/v38';O=R/'print/v38_pla'
b=trimesh.load_mesh(R/'source/v37/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);lower=upper-24;leading=upper-6.3
v,f=trimesh.remesh.subdivide_to_size(b.vertices,b.faces,max_edge=.35,max_iter=8);m=trimesh.Trimesh(v,f,process=True);x,y,z=m.vertices.T.copy()
# Compress a short transition below the root, moving the entire distal catch
# inward by 1 mm so its end/ridge profile survives instead of being cut off.
w=smooth((lower-1-y)/2)*smooth((2.6-np.abs(x))/.1);v=m.vertices.copy();v[:,1]+=w;m.vertices=v
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
assert abs(result.extents[0]-35)<.005 and abs(result.extents[1]-28.5)<.005
sec=result.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-24)<.01
assert abs(result.bounds[0,2]-b.bounds[0,2])<.005 and abs(lower-result.bounds[0,1]-4.5)<.01
p=b.vertices;middle=(np.abs(p[:,0])<2.61)&(p[:,1]<lower-1);tops=(np.abs(p[:,0])>7.78)&(np.abs(p[:,0])<13.82)&(p[:,1]>4.69)&(p[:,1]<12.01)&(p[:,2]<-.34)
_,errors,_=trimesh.proximity.closest_point(result,p[~(middle|tops)]);assert errors.max()<.01,(errors.max(),p[~(middle|tops)][errors.argmax()])
root_samples=[]
for yy in [-8.765974,-10.036243,-10.326769,-11.061451]:
 h,_,_=result.ray.intersects_location([[0,yy,-5]],[[0,0,1]]);zs=np.sort(h[:,2]);assert len(zs)==2 and np.ptp(zs)>1.15;root_samples.append({'Y':yy,'thickness_Z':float(np.ptp(zs))})
result.export(S/'Controller_Cover_A.stl');result.export(O/'V38_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([result,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V38_A_Vader_Mount.stl')
(R/'validation/v38_pla/trim_checks.json').write_text(json.dumps({'baseline':'V37','owner_feedback':'V37 finally holds but slightly too big; shorten top and middle clips 1 mm','top_old_reach_mm':7.3,'top_new_reach_mm':6.3,'middle_old_projection_mm':5.5,'middle_new_projection_mm':4.5,'shell_mm':[35,24],'overall_mm':float(result.extents[1]),'lowest_hook_Z_unchanged':True,'top_width_and_neck_mm':[6,1.6],'middle_width_mm':5,'root_samples':root_samples,'unchanged_region_max_sampled_surface_error_mm':float(errors.max()),'middle_catch_method':'Move distal catch inward with blended transition; preserve ridge and terminal profile.','V38_physical_fit_verified':False},indent=2)+'\n')
