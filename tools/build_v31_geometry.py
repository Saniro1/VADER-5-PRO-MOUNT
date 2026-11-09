"""Top toes +0.40 mm from V29 (+0.20 mm nominal from V30); middle tongue retained."""
from pathlib import Path
import json
import numpy as np,trimesh
from build_v24_geometry import smooth
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v31';O=R/'print/v31_pla'
b=trimesh.load_mesh(R/'source/v29/Controller_Cover_A.stl')
v,f=trimesh.remesh.subdivide_to_size(b.vertices,b.faces,max_edge=.45,max_iter=7)
m=trimesh.Trimesh(v,f,process=True);x,y,z=m.vertices.T.copy();ax=np.abs(x)
w=smooth((-1.9-z)/.55)*smooth((ax-8)/.3)*smooth((13.5-ax)/.3)*smooth((y-7.1)/.4)*smooth((10.1-y)/.6)
new=m.vertices.copy();new[:,1]-=.40*w;m.vertices=new;m=simplify(m)
assert m.is_watertight and len(m.split())==1
m.export(S/'Controller_Cover_A.stl');m.export(O/'V31_A_Cover_Fit_Test.stl')
core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V31_A_Vader_Mount.stl')
# Confirm the middle tongue and everything outside the edited hook region agree.
p=b.vertices;outside=(p[:,2]>=-1.9)|(np.abs(p[:,0])<=8)|(np.abs(p[:,0])>=13.5)|(p[:,1]<=7.1)|(p[:,1]>=10.1)
_,dist,_=trimesh.proximity.closest_point(m,p[outside]);assert dist.max()<.01,dist.max()
reach={}
for sign in [-1,1]:
 def toe_min(mesh):
  q=mesh.vertices;mask=(q[:,2]<-2.5)&(q[:,0]*sign>8)&(q[:,0]*sign<13.5)&(q[:,1]>7)&(q[:,1]<10.1);return float(q[mask,1].min())
 reach[str(sign)]=toe_min(b)-toe_min(m);assert .37<reach[str(sign)]<.42
assert abs(m.bounds[0,1]-b.bounds[0,1])<.005
(R/'validation/v31_pla/top_clip_change.json').write_text(json.dumps({'baseline':'V29','previous_revision':'V30','nominal_increment_from_V30_mm':.20,'paired_top_toe_extra_reach_mm':.40,'direction':'negative CAD Y; same retaining-toe direction as V26','measured_deep_toe_reach_added_mm':reach,'whole_clip_insertion_depth_added_mm':0,'middle_clip_unchanged':True,'outside_hook_region_max_sampled_surface_error_mm':float(dist.max()),'physical_fit_verified':False},indent=2)+'\n')
