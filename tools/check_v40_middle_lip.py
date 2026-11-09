"""Confirm new end-catch material and an open undercut in actual Orca paths."""
from pathlib import Path
import re,json
from shapely.geometry import LineString,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];text=Path('/workspace/slicer/v40-fit-validation/plate_1.gcode').read_text();pos={'X':0.,'Y':0.,'Z':0.};width=.42;strokes={}
for line in text.splitlines():
 if line.startswith(';WIDTH:'):width=float(line.split(':')[1])
 code=line.split(';')[0].strip()
 if not re.match(r'G[01](?:\s|$)',code):continue
 vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)};old=pos.copy()
 for a in 'XYZ':pos[a]=vals.get(a,pos[a])
 if vals.get('E',0)<=0 or not 17.2<pos['Z']<17.8:continue
 a=[old['X'],old['Y']];b=[pos['X'],pos['Y']]
 if a==b:continue
 segment=LineString([a,b])
 if segment.bounds[2]<134.5 or segment.bounds[0]>137 or segment.bounds[3]<121 or segment.bounds[1]>123:continue
 strokes.setdefault(pos['Z'],[]).append(segment.buffer(width/2,cap_style=1))
# Side-pose locations of interior material and air beneath the retaining lip.
material=box(135.90,121.95,136.15,122.15)
clearance=box(135.32,121.97,135.52,122.13)
checks=[]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon
first_z=min(strokes);first=unary_union(strokes[first_z]);fig,ax=plt.subplots(figsize=(7,5))
for poly in ([first] if first.geom_type=='Polygon' else first.geoms):
 ax.add_patch(PlotPolygon(poly.exterior.coords,facecolor='#8ab1d1',edgecolor='#1261a0',alpha=.7))
for poly,color in [(material,'green'),(clearance,'orange')]:ax.plot(*poly.exterior.xy,c=color)
ax.set(xlim=(134.8,136.7),ylim=(121,122.8),title='V40 middle-lip planned extrusion, layer '+str(first_z));ax.set_aspect('equal');ax.grid(alpha=.2);fig.savefig(R/'preview/V40_Lip_Toolpath.png',dpi=150)

for z,polys in sorted(strokes.items()):
 filled=unary_union(polys);mat_fraction=filled.intersection(material).area/material.area;air_filled=filled.intersection(clearance).area/clearance.area
 checks.append({'layer_Z':z,'lip_material_fraction':mat_fraction,'undercut_air_filled_fraction':air_filled})
 assert mat_fraction>.80 and air_filled<.10,(z,mat_fraction,air_filled)
assert len(checks)>=3
(R/'validation/v40_pla/middle_lip_toolpaths.json').write_text(json.dumps({'checks':checks,'physical_capture_verified':False,'footprint_model':'Swept line-width disks with round end caps; estimates planned deposited material, not a physical measurement.','meaning':'Material exists in the end lip and an air pocket remains beneath it in sampled central layers.'},indent=2)+'\n');print('PASS: end lip material and clear undercut on',len(checks),'sampled layers.')
