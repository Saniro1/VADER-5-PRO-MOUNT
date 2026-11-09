"""Check one native plate, unchanged three parts, supports and brim separation."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import trimesh,numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint
from validate_v35 import matrix,mesh_check,overlap,NS,PN
R=Path(__file__).resolve().parents[1];P=R/'print/v35_pla';F=P/'Vader5Pro_V35_All_Parts_One_Plate_PLA.3mf'
with zipfile.ZipFile(F) as z:
 settings=json.loads(z.read('Metadata/project_settings.config'));cfg=ET.fromstring(z.read('Metadata/model_settings.config'));docs={n:ET.fromstring(z.read(n)) for n in z.namelist() if n.endswith('.model')}
def meshes(filename,objid):
 obj=next(o for o in docs[filename].find(NS+'resources') if o.get('id')==str(objid));node=obj.find(NS+'mesh')
 if node is not None:return [trimesh.Trimesh([[float(v.get(k)) for k in 'xyz'] for v in node.find(NS+'vertices')],[[int(f.get('v'+str(k))) for k in [1,2,3]] for f in node.find(NS+'triangles')],process=True)]
 out=[]
 for c in obj.find(NS+'components'):
  for m in meshes(c.get(PN+'path',filename).lstrip('/'),c.get('objectid')):m.apply_transform(matrix(c.get('transform')));out.append(m)
 return out
assert len(cfg.findall('plate'))==1 and len(cfg.find('plate').findall('model_instance'))==3
build=docs['3D/3dmodel.model'].find(NS+'build');assert len(build)==3
layout=json.loads((R/'validation/v35_pla/one_plate_layout.json').read_text());configs={o.get('id'):o for o in cfg.findall('object')};report={};footprints=[]
for item in build:
 obj=configs[item.get('objectid')];meta={n.get('key'):n.get('value') for n in obj.findall('metadata')};name=meta['name'];assert name in layout
 assert meta['brim_width']=='5' and meta['brim_object_gap']=='0'
 parts=meshes('3D/3dmodel.model',item.get('objectid'));assert len(parts)==(1 if name=='Sliding_Cap' else 2)
 for m in parts:m.apply_transform(matrix(item.get('transform')));mesh_check(m)
 for i,m in enumerate(parts):
  expected=trimesh.load_mesh(P/(name+('_Oriented.stl' if i==0 else '_Custom_Supports.stl')));expected.apply_translation([*layout[name]['xy'],0]);assert cKDTree(m.vertices).query(expected.vertices)[0].max()<.0001
 if len(parts)==2:assert overlap(*parts)<1e-6
 combined=trimesh.util.concatenate(parts);hull=MultiPoint(combined.vertices[:,:2]).convex_hull.buffer(5)
 assert hull.bounds[0]>1 and hull.bounds[1]>1 and hull.bounds[2]<269 and hull.bounds[3]<269
 for prior in footprints:assert not hull.intersects(prior)
 footprints.append(hull);report[name]={'bounds_mm':combined.bounds.tolist(),'brim_and_support_footprint_clear':True,'geometry_matches_V35':True}
for k,v in {'filament_type':['PLA'],'nozzle_temperature':['220'],'textured_plate_temp':['65'],'layer_height':'0.12','print_sequence':'by layer','enable_support':'0'}.items():assert settings[k]==v,(k,settings[k])
report.update(plate_count=1,functional_part_count=3,print_sequence='by layer',physical_print_tested=False)
(R/'validation/v35_pla/one_plate_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: one plate; three unchanged parts with supports; separated brims; saved PLA settings.')
