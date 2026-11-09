"""Extend only V28 B's middle tab 0.40 mm along its existing reach direction."""
from pathlib import Path
import subprocess,json
import trimesh,numpy as np
from build_v24_geometry import smooth
from build_v26_geometry import simplify
R=Path(__file__).resolve().parents[1];S=R/'source/v29';O=R/'print/v29_pla'
b=trimesh.load_mesh(R/'source/v28/Controller_Cover_B.stl')
v,f=trimesh.remesh.subdivide_to_size(b.vertices,b.faces,max_edge=.5,max_iter=7)
m=trimesh.Trimesh(v,f,process=True);x,y,z=m.vertices.T.copy()
w=smooth((-9.6-y)/1.6)*smooth((3.4-np.abs(x))/.3)
new=m.vertices.copy();new[:,1]-=.4*w;m.vertices=new;m=simplify(m)
assert m.is_watertight and len(m.split())==1
assert abs(m.bounds[0,1]-b.bounds[0,1]+.4)<.01
assert abs(m.bounds[0,2]-b.bounds[0,2])<.005
m.export(S/'Controller_Cover_A.stl')
m.export(O/'V29_A_Cover_Fit_Test.stl')
core_path=S/'Mount_Core.stl'
subprocess.run(['openscad','--export-format','binstl','-D','part="mount_core"','-o',str(core_path),str(S/'Vader5Pro_V29.scad')],check=True)
core=trimesh.load_mesh(core_path)
mount=simplify(trimesh.boolean.union([m,core],engine='manifold'))
assert mount.is_watertight and len(mount.split())==1
mount.export(O/'V29_A_Vader_Mount.stl')
(R/'validation/v29_pla/middle_clip_change.json').write_text(json.dumps({'baseline':'V28 B','middle_clip_extra_reach_mm':.4,'direction':'negative Y, along existing tongue','middle_clip_height_or_width_intentionally_changed':False,'other_hooks_intentionally_changed':False,'mesh_simplification_tolerance_mm':.004,'physical_fit_verified':False,'OEM_dimensions_verified':False},indent=2)+'\n')
