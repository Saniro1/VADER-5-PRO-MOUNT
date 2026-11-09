"""V38 clip geometry retained; 2 mm shell corners and 0.25 mm side-edge lead-in."""
from pathlib import Path
import json
import numpy as np,trimesh,manifold3d
from shapely.geometry import Polygon,Point
from build_v28_supports import extrude_polygon
R=Path(__file__).resolve().parents[1];S=R/'source/v39';O=R/'print/v39_pla'
def simplify(mesh):
 solid=manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.asarray(mesh.vertices,dtype=np.float64),tri_verts=np.asarray(mesh.faces,dtype=np.uint64))).simplify(.001).to_mesh()
 m=trimesh.Trimesh(solid.vert_properties[:,:3],solid.tri_verts,process=True)
 assert m.is_watertight and m.is_winding_consistent
 pieces=[p for p in m.split(only_watertight=False) if abs(p.volume)>1e-7]
 assert len(pieces)==1
 return pieces[0]

b=trimesh.load_mesh(R/'source/v38/Controller_Cover_A.stl');upper=float(b.bounds[1,1]);lower=upper-24;radius=2.;lead=.25
# Identical arc centers on outer and inset rounded-rectangle loops.
centers=[(15.5,upper-2),(-15.5,upper-2),(-15.5,lower+2),(15.5,lower+2)]
def loop(rad):
 return np.array([[cx+rad*np.cos(t),cy+rad*np.sin(t)] for (cx,cy),start in zip(centers,[0,90,180,270]) for t in np.deg2rad(np.linspace(start,start+90,25))])
outer=loop(radius);inner=loop(radius-lead)
# Overlap the rounding mask by 0.01 mm: coincident cutter walls can leave
# zero-thickness sheets that disappear only when the mount is later united.
bevel_outer=loop(radius+.01);outline=Polygon(outer)
mask=extrude_polygon(outline,20);mask.apply_translation([0,0,-5])
# Preserve the central projecting tongue and its root independently of rim mask.
keep=trimesh.creation.box([7.2,lower+21,20]);keep.apply_translation([0,(-20+lower+1)/2,5])
mask=trimesh.boolean.union([mask,keep],engine='manifold');rounded=trimesh.boolean.intersection([b,mask],engine='manifold')
# Measure the existing lower shell surface away from all hooks, then form an
# edge-only wedge following that curvature. The side zones exclude all hooks.
ys=np.linspace(lower+.001,upper-.001,241);origins=np.c_[np.full(len(ys),5.),ys,np.full(len(ys),-5.)]
hits,ids,_=b.ray.intersects_location(origins,np.tile([0,0,1],(len(ys),1)));floors=np.full(len(ys),np.inf)
for hit,i in zip(hits,ids):floors[i]=min(floors[i],hit[2])
assert np.isfinite(floors).all()
n=len(outer);verts=[]
for pts,extra in [(bevel_outer,lead),(inner,0.)]:
 for x,y in pts:verts.append([x,y,float(np.interp(y,ys,floors))+extra])
for pts in [bevel_outer,inner]:
 for x,y in pts:verts.append([x,y,-5])
faces=[]
for i in range(n):
 j=(i+1)%n
 for a,c,d,e in [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]:faces.extend([[a,c,d],[a,d,e]])
wedge=trimesh.Trimesh(verts,faces,process=True);wedge.fix_normals();assert wedge.is_volume
zones=[]
for x in [-23.35,23.35]:
 z=trimesh.creation.box([18.3,50,20]);z.apply_translation([x,0,5]);zones.append(z) # |X| >=14.2
zone=trimesh.boolean.union(zones,engine='manifold');wedge=trimesh.boolean.intersection([wedge,zone],engine='manifold')
result=simplify(trimesh.boolean.difference([rounded,wedge],engine='manifold'))
assert result.volume<b.volume and abs(result.extents[0]-35)<.01 and abs(result.extents[1]-28.5)<.01
sec=result.section(plane_origin=[5,0,0],plane_normal=[1,0,0]);assert abs(np.ptp(np.vstack(sec.discrete)[:,1])-24)<.01
# Verify complete clip surfaces and roots, not merely total dimensions.
v=b.vertices;clips=((np.abs(v[:,0])<3.6)&(v[:,1]<-6))|((np.abs(v[:,0])>7.7)&(np.abs(v[:,0])<13.9)&(v[:,1]>4.6)&(v[:,2]<.1))|((np.abs(v[:,0])>14)&(np.abs(v[:,0])<16.5)&(v[:,1]<-3)&(v[:,1]>-8.4)&(v[:,2]<2))
_,d,_=trimesh.proximity.closest_point(result,v[clips]);assert d.max()<.01,d.max()
# Outer shell corners lie within the prescribed rounded plan outline.
outline_tolerance=outline.buffer(.005)
for point in result.vertices:
 if abs(point[0])>14.2:assert outline_tolerance.covers(Point(point[:2]))
result.export(S/'Controller_Cover_A.stl');result.export(O/'V39_A_Cover_Fit_Test.stl');core=trimesh.load_mesh(S/'Mount_Core.stl');mount=simplify(trimesh.boolean.union([result,core],engine='manifold'));assert mount.is_watertight and len(mount.split())==1;mount.export(O/'V39_A_Vader_Mount.stl')
(R/'validation/v39_pla/edge_clearance_checks.json').write_text(json.dumps({'baseline':'V38','owner_feedback':'Squared shell edges prevent sliding fully down','shell_plan_corner_radius_mm':2,'side_edge_lead_in_mm':.25,'lead_in_zones':'Shell perimeter at |X|>=14.2; follows existing controller-facing surface','clip_max_sampled_surface_error_mm':float(d.max()),'shell_mm':[35,24],'overall_mm':float(result.extents[1]),'removed_volume_mm3':float(b.volume-result.volume),'top_reach_mm':6.3,'middle_projection_mm':4.5,'clips_and_reinforced_roots_intentionally_changed':False,'physical_fit_verified':False,'OEM_corner_radius_measured':False},indent=2)+'\n')
