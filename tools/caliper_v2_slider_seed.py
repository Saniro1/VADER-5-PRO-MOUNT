"""Extract just the R2 replacement slider, centered on one plate."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];S=R/'source/printable_caliper_v2';NS='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
ET.register_namespace('',NS[1:-1])
with zipfile.ZipFile(S/'U1_Oriented_Seed.3mf') as z:files={n:z.read(n) for n in z.namelist()}
m=ET.fromstring(files['3D/3dmodel.model']);cfg=ET.fromstring(files['Metadata/model_settings.config']);objects={o.get('id'):o for o in cfg.findall('object')}
keep={id for id,o in objects.items() if any(n.get('key')=='name' and n.get('value')=='Caliper_Slider' for n in o.findall('metadata'))};assert len(keep)==1
for i in list(m.find(NS+'build')):
 if i.get('objectid') not in keep:m.find(NS+'build').remove(i)
 else:i.set('transform','1 0 0 0 1 0 0 0 1 135 135 0')
res=m.find(NS+'resources');byid={o.get('id'):o for o in res};needed=set(keep);pending=list(keep)
while pending:
 obj=byid[pending.pop()];cs=obj.find(NS+'components')
 if cs is not None:
  for c in cs:
   k=c.get('objectid')
   if k not in needed:needed.add(k);pending.append(k)
for o in list(res):
 if o.get('id') not in needed:res.remove(o)
for o in cfg.findall('object'):
 if o.get('id') not in keep:cfg.remove(o)
plate=cfg.find('plate')
for i in plate.findall('model_instance'):
 if not any(n.get('key')=='object_id' and n.get('value') in keep for n in i.findall('metadata')):plate.remove(i)
for n in plate.findall('metadata'):
 if n.get('key')=='plater_name':n.set('value','R2 replacement slider only')
files['3D/3dmodel.model']=ET.tostring(m,encoding='utf-8',xml_declaration=True);files['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(S/'Replacement_Slider_Seed.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,d in files.items():z.writestr(n,d)
