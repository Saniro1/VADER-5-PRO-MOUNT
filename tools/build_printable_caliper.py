"""Build a single-plate U1 PLA seed and check caliper assembly clearances."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import trimesh,numpy as np
import build_v28_supports as writer
R=Path(__file__).resolve().parents[1];S=R/'source/printable_caliper';P=R/'print/printable_caliper';V=R/'validation/printable_caliper'
for n in ['U1_0p4_machine.json','Snapmaker_PLA_Black.json','Orca_Base_Project_Settings.json']:(S/n).write_bytes((R/'source/v31'/n).read_bytes())
f=json.loads((R/'source/v31/U1_PLA_Quality_Process.json').read_text());f.update(name='Printable Caliper - PLA 0.12 @U1',print_settings_id='Printable Caliper - PLA 0.12 @U1',description='80 mm sliding measuring aid: embossed/engraved 1 mm scale; not a precision caliper. No supports; short slider roof bridge.',sparse_infill_density='35%',brim_width='3',brim_object_gap='0.10',bridge_flow='0.95');(S/'Caliper_PLA_Process.json').write_text(json.dumps(f,indent=2)+'\n')
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
(V/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: three closed meshes and no caliper interference from 0 to 80 mm.')
