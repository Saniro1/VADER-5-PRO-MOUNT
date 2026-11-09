"""Build a single-plate U1 PLA seed and check caliper assembly clearances."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import trimesh,numpy as np
import build_v28_supports as writer
R=Path(__file__).resolve().parents[1];S=R/'source/printable_caliper_v2';P=R/'print/printable_caliper_v2';V=R/'validation/printable_caliper_v2'
for n in ['U1_0p4_machine.json','Snapmaker_PLA_Black.json','Orca_Base_Project_Settings.json']:(S/n).write_bytes((R/'source/v31'/n).read_bytes())
f=json.loads((R/'source/v31/U1_PLA_Quality_Process.json').read_text());f.update(name='Printable Caliper R2 - PLA 0.12 @U1',print_settings_id='Printable Caliper R2 - PLA 0.12 @U1',description='80 mm sliding measuring aid: embossed/engraved 1 mm scale; not a precision caliper. No supports; enlarged channel and flared entrances; 0.40 mm sides / 0.45 mm vertical clearance. Short slider roof bridge.',sparse_infill_density='35%',brim_width='3',brim_object_gap='0.10',bridge_flow='0.90');(S/'Caliper_PLA_Process.json').write_text(json.dumps(f,indent=2)+'\n')
beam=trimesh.load_mesh(P/'Caliper_Beam.stl');slider=trimesh.load_mesh(P/'Caliper_Slider.stl');gauge=trimesh.load_mesh(P/'Check_Gauge_40_20.stl')
for m in [beam,slider,gauge]:assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
worst=0
for distance in np.linspace(0,80,81):
 s=slider.copy();s.apply_translation([distance,0,0]);vol=trimesh.boolean.intersection([beam,s],engine='manifold').volume;worst=max(worst,vol);assert vol<.001,(distance,vol)
groups=[];report={'physical_print_tested':False,'range_mm':[0,80],'graduation_mm':1,'inside_reading_correction_mm':2,'assembly_overlap_max_mm3':float(worst),'layout':{}}
for name,m,xy in [('Caliper_Beam',beam,[110,105]),('Caliper_Slider',slider,[100,180]),('Check_Gauge_40_20',gauge,[170,180])]:
 p=m.copy();p.apply_translation([-p.bounds[:,0].mean(),-p.bounds[:,1].mean(),-p.bounds[0,2]]);p.export(P/(name+'_Oriented.stl'));groups.append((name,p,None,xy));report['layout'][name]={'xy':xy,'bounds':p.bounds.tolist()}
writer.SOURCE=S;writer.write_seed(groups)
f=S/'U1_Oriented_Seed.3mf'
with zipfile.ZipFile(f) as z:files={n:z.read(n) for n in z.namelist()}
cfg=ET.fromstring(files['Metadata/model_settings.config'])
for obj in cfg.findall('object'):
 for k,v in [('brim_type','outer_only'),('brim_width','3'),('brim_object_gap','0.10')]:ET.SubElement(obj,'metadata',key=k,value=v)
for n in cfg.find('plate').findall('metadata'):
 if n.get('key')=='plater_name':n.set('value','80 mm caliper - beam, slider, check gauge')
files['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED) as z:
 for n,d in files.items():z.writestr(n,d)
old=trimesh.load_mesh(R/'print/printable_caliper/Caliper_Slider.stl')
assert trimesh.boolean.difference([slider,old],engine='manifold').volume<0.001
for y,z in [(6,1)]:
 h,_,_=slider.ray.intersects_location([[21,-3,z]],[[0,1,0]]);assert all(np.any(abs(h[:,1]-value)<.002) for value in [-.4,12.4])
 h,_,_=slider.ray.intersects_location([[21,y,-3]],[[0,0,1]]);assert all(np.any(abs(h[:,2]-value)<.002) for value in [-.45,3.65])
for n in ['Caliper_Beam.stl','Check_Gauge_40_20.stl']:assert (P/n).read_bytes()==(R/'print/printable_caliper'/n).read_bytes()
# Check measurement contact areas remain unchanged, away from the guide bore.
for bounds in [[[10.9,-24,-1.4],[14.1,-5,5.1]],[[10.9,20,-1.4],[12.1,25.1,5.1]]]:
 bounds=np.array(bounds);roi=trimesh.creation.box(bounds[1]-bounds[0]);roi.apply_translation(bounds.mean(0));a=trimesh.boolean.intersection([old,roi],engine='manifold');b=trimesh.boolean.intersection([slider,roi],engine='manifold');assert abs(a.volume-b.volume)<.001
report.update(revision='R2',side_clearance_each_mm=.4,vertical_clearance_each_mm=.45,channel_width_mm=12.8,channel_height_mm=4.1,flared_entrances=True,original_beam_and_gauge_byte_identical=True,measurement_contact_regions_unchanged=True)
(V/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: three closed meshes and no caliper interference from 0 to 80 mm.')
