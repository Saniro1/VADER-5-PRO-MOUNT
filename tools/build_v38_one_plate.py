"""Arrange V38's three functional parts and existing supports on one U1 plate."""
from pathlib import Path
import tempfile,zipfile,xml.etree.ElementTree as ET,json
import trimesh
import build_v28_supports as writer
R=Path(__file__).resolve().parents[1];P=R/'print/v38_pla';S=R/'source/v38'
groups=[];report={}
for name,xy in [('Mount_A',[100,105]),('Shared_Box_2',[170,105]),('Sliding_Cap',[135,165])]:
 part=trimesh.load_mesh(P/(name+'_Oriented.stl'));f=P/(name+'_Custom_Supports.stl');support=trimesh.load_mesh(f) if f.exists() else None
 groups.append((name,part,support,xy));report[name]={'xy':xy,'support_included':support is not None}
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);(t/'Orca_Base_Project_Settings.json').write_bytes((S/'Orca_Base_Project_Settings.json').read_bytes());writer.SOURCE=t;writer.write_seed(groups)
 with zipfile.ZipFile(t/'U1_Oriented_Seed.3mf') as z:files={n:z.read(n) for n in z.namelist()}
cfg=ET.fromstring(files['Metadata/model_settings.config'])
for obj in cfg.findall('object'):
 for k,v in [('brim_type','outer_only'),('brim_width','5'),('brim_object_gap','0')]:ET.SubElement(obj,'metadata',key=k,value=v)
plate=cfg.find('plate')
for node in plate.findall('metadata'):
 if node.get('key')=='plater_name':node.set('value','V38 - mount, box and lid - one print')
files['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(S/'U1_All_Parts_One_Plate_Seed.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,d in files.items():z.writestr(n,d)
(R/'validation/v38_pla/one_plate_layout.json').write_text(json.dumps(report,indent=2)+'\n')
