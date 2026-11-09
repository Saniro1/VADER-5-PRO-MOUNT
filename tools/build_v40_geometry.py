"""Retain working V39 top pair/shell; edge-start curved middle tongue with end lip."""
from pathlib import Path
import json
import numpy as np,trimesh,manifold3d
from shapely.geometry import Polygon,LineString
from build_v28_supports import extrude_polygon
R=Path(__file__).resolve().parents[1];S=R/'source/v40';O=R/'print/v40_pla'
def simplify(mesh):
 s=manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.asarray(mesh.vertices,dtype=np.float64),tri_verts=np.asarray(mesh.faces,dtype=np.uint64))).simplify(.001).to_mesh()
 m=trimesh.Trimesh(s.vert_properties[:,:3],s.tri_verts,process=True);assert m.is_watertight and m.is_winding_consistent
 ps=[p for p in m.split(only_watertight=False) if abs(p.volume)>1e-7];assert len(ps)==1;return ps[0]
b=trimesh.load_mesh(R/'source/v39/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);rim=upper-24;tip=rim-4.5
# Clip width and projection stay unchanged. Only the root-to-tip YZ profile changes.
def bezier(a,b,c,d,n=35):
 t=np.linspace(0,1,n)[:,None];return (1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)
root_center=[rim+.6,3.75]
a=bezier(root_center,[rim-.3,3.70],[rim-.75,1.0],[rim-2.8,1.0])
z=bezier([rim-2.8,1.0],[rim-3.7,1.0],[tip+.5,1.15],[tip+.5,1.8])
centerline=np.vstack([a,z[1:],[[tip+.5,2.45]]])
wall=LineString(centerline).buffer(.50,cap_style=2,join_style=1)
# Free-end catch cap: 0.65 mm back-facing overhang; keep a flat lower shoulder.
cap=Polygon([(tip,2.1),(tip+1.,2.1),(tip+1.,2.15),(tip+1.65,2.15),(tip+1.65,2.75),(tip+.15,2.75),(tip,2.60)])
profile=wall.union(cap);assert profile.geom_type=='Polygon' and profile.is_valid
latch=extrude_polygon(profile,5);latch.apply_transform([[0,0,1,-2.5],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
cut=trimesh.creation.box([5.02,rim+.20+22,20]);cut.apply_translation([0,(-22+rim+.20)/2,3])
body=trimesh.boolean.difference([b,cut],engine='manifold')
# Blend away the old underside root ledge so it cannot leave a sharp step at
# the slot mouth beside the new curve. Keep the reinforced anchor farther in.
root_boundary=[]
for yy in np.linspace(rim+.15,rim+.60,24):
 section=wall.intersection(LineString([(yy,-5),(yy,6)]));assert not section.is_empty
 root_boundary.append((yy,section.bounds[1]))
anchor_y=rim+.95
hh,_,_=b.ray.intersects_location([[0,anchor_y,-5]],[[0,0,1]]);anchor_floor=float(hh[:,2].min())
root_boundary.extend([(rim+.75,root_boundary[-1][1]*.5+anchor_floor*.5),(anchor_y,anchor_floor)])
relief_profile=Polygon([(rim+.15,-5),(anchor_y,-5)]+list(reversed(root_boundary)))
relief=extrude_polygon(relief_profile,5.02);relief.apply_transform([[0,0,1,-2.51],[1,0,0,0],[0,1,0,0],[0,0,0,1]])
body=trimesh.boolean.difference([body,relief],engine='manifold')
joint=trimesh.boolean.intersection([body,latch],engine='manifold').volume;assert joint>1,joint
m=simplify(trimesh.boolean.union([body,latch],engine='manifold'))
assert abs(m.extents[0]-35)<.01 and abs(m.extents[1]-28.5)<.01
sec=m.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-24)<.01
# All successful top hooks, rounded outer corners and roots in the main shell
# are checked against V39; the edited central profile is explicitly excluded.
p=b.vertices;edit=(np.abs(p[:,0])<2.52)&(p[:,1]<rim+1.0)
_,err,_=trimesh.proximity.closest_point(m,p[~edit]);assert err.max()<.01,err.max()
# Assert a real underside retaining shelf at the free end, not just a ramp.
for xx in [-2,0,2]:
 h,_,_=m.ray.intersects_location([[xx,tip+1.4,-4]],[[0,0,1]]);assert np.any(abs(h[:,2]-2.15)<.01),(xx,h)
m.export(S/'Controller_Cover_A.stl');m.export(O/'V40_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([m,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V40_A_Vader_Mount.stl')
(R/'validation/v40_pla/middle_profile_checks.json').write_text(json.dumps({'baseline':'V39','owner_feedback':'Top now clips fine; middle curve starts too late, is tight, and lacks an end catch','profile_method':'Cubic centerline begins curving at shell edge; 0.5 mm offset each side makes 1 mm nominal normal wall.','middle_width_mm':5,'projection_mm':4.5,'terminal_lip_overhang_mm':.65,'terminal_cap_Z_mm':[2.15,2.75],'entry_tip_chamfer_mm':.15,'positive_overlap_with_retained_shell_mm3':float(joint),'unchanged_top_shell_root_max_sampled_error_mm':float(err.max()),'profile_control_points':{'root':root_center,'first_curve_end':[rim-2.8,1.0],'tip_center':[tip+.5,2.45]},'shell_mm':[35,24],'overall_mm':float(m.extents[1]),'physical_fit_force_strength_verified':False,'exact_OEM_profile':False},indent=2)+'\n')
