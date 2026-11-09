"""Top-view assembly/reading guide from the generated caliper meshes."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
import trimesh,numpy as np
R=Path(__file__).resolve().parents[1];P=R/'print/printable_caliper'
fig,ax=plt.subplots(figsize=(12,6))
for name,z,dx,color in [('Caliper_Beam',1,0,'#c5d9eb'),('Caliper_Slider',4.2,30,'#e4a559')]:
 m=trimesh.load_mesh(P/(name+'.stl'));s=m.section([0,0,1],[0,0,z])
 for line in s.discrete:ax.add_patch(Patch(line[:,:2]+[dx,0],facecolor=color,edgecolor='#333',lw=.7))
for i in range(81):
 x=11+i;h=5 if i%10==0 else (3.8 if i%5==0 else 2.5)
 # Reading window and exposed beam only.
 if not 48<=x<=61:
  ax.plot([x,x],[.65,.65+h],color='#333',lw=.65)
  if i%10==0:ax.text(x,7,str(i),ha='center',fontsize=9)
ax.annotate('',xy=(11,-28),xytext=(41,-28),arrowprops=dict(arrowstyle='<->',lw=1.4));ax.text(26,-33,'Outside: 30 mm example',ha='center',fontsize=11)
ax.annotate('',xy=(10,28),xytext=(42,28),arrowprops=dict(arrowstyle='<->',lw=1.4));ax.text(26,32,'Inside: scale + 2 mm = 32 mm',ha='center',fontsize=11)
ax.annotate('Read the slider’s LEFT edge\nagainst the scale',xy=(41,.5),xytext=(71,-18),arrowprops=dict(arrowstyle='->'),fontsize=11)
ax.text(99,19,'Beam',color='#315a7e',fontsize=12);ax.text(52,19,'Slider',color='#9a5f13',fontsize=12)
ax.set(xlim=(-3,129),ylim=(-38,40),title='80 mm printable caliper — assembled at 30 mm opening');ax.set_aspect('equal');ax.axis('off');fig.text(.5,.025,'1 mm graduations. Rough measuring aid; verify against a real ruler. Diagram is not a print-to-scale template.',ha='center',fontsize=10);fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(R/'preview/Printable_Caliper_Guide.png',dpi=150)
