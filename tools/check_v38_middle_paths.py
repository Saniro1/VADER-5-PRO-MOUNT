"""Check material is planned through the reinforced middle-root section."""
from pathlib import Path
import re,json
from shapely.geometry import LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];text=Path('/workspace/slicer/v38-fit-validation/plate_1.gcode').read_text();pos={'X':0.,'Y':0.,'Z':0.};width=.42;strokes={}
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
 if segment.bounds[2]<136 or segment.bounds[0]>139 or segment.bounds[3]<125.8 or segment.bounds[1]>128.1:continue
 strokes.setdefault(pos['Z'],[]).append(segment.buffer(width/2,cap_style=2))
# V38 side pose: X=design Z -1.43003 +135; Y=trimmed-design Y +1.70964 +135.
# Interior root line stays 0.10+ mm away from nominal section boundaries.
probe=LineString([(136.80,126.38287),(137.85,126.38287)])
checks=[]
for z,polys in sorted(strokes.items()):
 covered=unary_union(polys).intersection(probe).length;checks.append({'layer_Z':z,'root_line_covered_mm':covered,'probe_length_mm':probe.length});assert covered>.95,(z,covered)
assert len(checks)>=3
(R/'validation/v38_pla/middle_root_toolpaths.json').write_text(json.dumps({'checks':checks,'physical_bond_strength_verified':False,'meaning':'Extrusion planned through an interior line across the extended thicker root, on several central hook layers.'},indent=2)+'\n');print('PASS: reinforced middle-root material present on',len(checks),'sampled layers.')
