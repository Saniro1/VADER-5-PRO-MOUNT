from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import trimesh
R=Path(__file__).resolve().parents[1];fig,axs=plt.subplots(1,2,figsize=(13,5))
for ver,c in [('v36','gray'),('v37','#1261a0')]:
 m=trimesh.load_mesh(R/f'source/{ver}/Controller_Cover_A.stl')
 for ax,x in zip(axs,[10.8,0]):
  sec=m.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
  for i,line in enumerate(sec.discrete):ax.plot(line[:,1],line[:,2],c=c,lw=2,label=ver.upper() if i==0 else None)
axs[0].set(xlim=(4.7,12),ylim=(-3.3,.2),title='Top: catch-lip overhang +3 mm; leg depth unchanged')
axs[0].annotate('',xy=(5.24036,-3),xytext=(8.24036,-3),arrowprops=dict(arrowstyle='<->'));axs[0].text(6.74,-2.94,'3 mm',ha='center',fontsize=9)
axs[1].set(xlim=(-17.5,-5.5),ylim=(.3,5.4),title='Bottom: shell rim +3 mm; middle hook moves with it')
for y in [-8.45964,-11.45964]:axs[1].axvline(y,c='#777',ls='--',lw=1)
axs[1].annotate('',xy=(-11.45964,5.1),xytext=(-8.45964,5.1),arrowprops=dict(arrowstyle='<->'));axs[1].text(-9.96,4.96,'3 mm shell extension',ha='center',va='top',fontsize=8)
for ax in axs:ax.set_xlabel('Along cover: CAD Y (mm)');ax.set_ylabel('CAD Z (mm)');ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(loc='lower right')
fig.text(.5,.025,'CAD comparison only. Controller clearance, actual fit and strength remain unverified.',ha='center',fontsize=10);fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(R/'preview/V37_Direction_Changes.png',dpi=150)
