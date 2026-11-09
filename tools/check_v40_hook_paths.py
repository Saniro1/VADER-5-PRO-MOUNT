"""Confirm straight retaining-shoulder segments survive Orca's extrusion paths."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];s=Path('/workspace/slicer/v40-fit-validation/plate_1.gcode').read_text();pos={'X':0.,'Y':0.,'Z':0.};role='';segments=[]
for line in s.splitlines():
 if line.startswith(';TYPE:'):role=line[6:]
 code=line.split(';')[0].strip()
 if not re.match(r'G[01](?:\s|$)',code):continue
 vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)};old=pos.copy()
 for a in 'XYZ':pos[a]=vals.get(a,pos[a])
 if vals.get('E',0)<=0 or role!='Outer wall':continue
 if not (6.25<pos['Z']<7.2 or 27.8<pos['Z']<28.8):continue
 if abs(pos['X']-old['X'])<.015 and 131.5<pos['X']<132.5 and min(pos['Y'],old['Y'])>142.2 and max(pos['Y'],old['Y'])<147.4:
  length=abs(pos['Y']-old['Y'])
  if length>.4:segments.append({'Z':pos['Z'],'length_mm':length,'start':[old['X'],old['Y']],'end':[pos['X'],pos['Y']]})
assert segments,'No straight shoulder contours found in expected hook region'
assert any(v['Z']<10 for v in segments) and any(v['Z']>20 for v in segments)
(R/'validation/v40_pla/hook_toolpath_checks.json').write_text(json.dumps({'check':'straight outer-wall shoulder segments in both hook layer bands','minimum_segment_mm':.4,'segments':segments,'physical_edge_sharpness_verified':False},indent=2)+'\n');print('PASS: straight shoulders retained in toolpaths for both hooks:',len(segments))
