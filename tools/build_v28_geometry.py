"""Controlled underside-clearance trials; both retain V26 A hook geometry."""
from pathlib import Path
import subprocess,json
import numpy as np
import trimesh
from build_v26_geometry import simplify
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source/v28'; OUT=ROOT/'print/v28_seating'
base=trimesh.load_mesh(ROOT/'source/v26/Controller_Cover_A.stl')
# Preserve all five clip/root regions. Only relieve the remaining shell's low skin.
regions=[([ -3.5,-14,-2],[3.5,-8.5,3.7]),([-16.5,-8.5,-2],[-13.5,-3,4.3]),([13.5,-8.5,-2],[16.5,-3,4.3]),([-13.6,7,-5],[-8,10,-.8]),([8,7,-5],[13.6,10,-.8])]
protected=[]
for low,high in regions:
 low,high=np.array(low),np.array(high);b=trimesh.creation.box(high-low);b.apply_translation((low+high)/2)
 protected.append(trimesh.boolean.intersection([base,b],engine='manifold'))
report={'physical_fit_verified':False,'OEM_dimensions_available':False,'baseline':'V26 A for BOTH variants','hypothesis':'Controller-facing shell interference may prevent seating; exact contact is unmeasured.','variants':{}}
for letter,depth in [('A',.15),('B',.30)]:
 shifted=base.copy();shifted.apply_translation([0,0,depth])
 relieved=trimesh.boolean.intersection([base,shifted],engine='manifold')
 result=simplify(trimesh.boolean.union([relieved]+protected,engine='manifold'))
 assert result.is_watertight and len(result.split())==1
 assert result.volume<base.volume
 for p in protected:
  assert trimesh.boolean.difference([p,result],engine='manifold').volume<.05
 samples=[]
 for x in [-10,-5,0,5,10]:
  for y in [-5,-2,0,2,5]:
   old,_,_=base.ray.intersects_location([[x,y,-10]],[[0,0,1]])
   new,_,_=result.ray.intersects_location([[x,y,-10]],[[0,0,1]])
   assert len(old)==len(new)==2
   oldz,newz=np.sort(old[:,2]),np.sort(new[:,2])
   assert abs(newz[0]-oldz[0]-depth)<.015
   assert abs(newz[1]-oldz[1])<.015
   assert newz[1]-newz[0]>.8
   samples.append({'xy':[x,y],'vertical_thickness_mm':float(newz[1]-newz[0])})
 result.export(SRC/f'Controller_Cover_{letter}.stl')
 for selector,filename in [('cover',f'V28_{letter}_Cover_Fit_Test.stl'),('mount',f'V28_{letter}_Vader_Mount.stl')]:
  path=OUT/filename
  subprocess.run(['openscad','--export-format','binstl','-D',f'part="{selector}"','-D',f'variant="{letter}"','-o',str(path),str(SRC/'Vader5Pro_V28.scad')],check=True)
  simplify(trimesh.load_mesh(path)).export(path)
 report['variants'][letter]={'underside_relief_mm':depth,'protected_hook_regions_preserved_with_0p004mm_simplification':True,'sampled_min_vertical_shell_thickness_mm':min(s['vertical_thickness_mm'] for s in samples),'samples':samples}
(ROOT/'validation/v28_seating/underside_clearance.json').write_text(json.dumps(report,indent=2)+'\n')
