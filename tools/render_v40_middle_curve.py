from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import trimesh
R=Path(__file__).resolve().parents[1];fig,ax=plt.subplots(figsize=(9,5.5));rim=12.53999996-24;tip=rim-4.5
for ver,c in [('v39','gray'),('v40','#1261a0')]:
 m=trimesh.load_mesh(R/f'source/{ver}/Controller_Cover_A.stl');sec=m.section(plane_origin=[0,0,0],plane_normal=[1,0,0])
 for i,p in enumerate(sec.discrete):ax.plot(p[:,1],p[:,2],c=c,lw=2,label=ver.upper() if i==0 else None)
ax.axvline(rim,c='#888',ls='--',lw=1);ax.text(rim+.08,.35,'Shell edge',rotation=90,va='bottom',fontsize=9)
ax.annotate('Free-end retaining lip',xy=(tip+1.4,2.15),xytext=(-15.8,4.45),arrowprops=dict(arrowstyle='->'),fontsize=11)
ax.set(xlim=(-16.6,-10.2),ylim=(.3,4.7),xlabel='CAD Y (mm)',ylabel='CAD Z (mm)',title='V40 middle latch: edge-start curve and a defined end catch');ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(loc='lower right');fig.text(.5,.025,'Shape trial, not a measured OEM profile. Top hooks and shell remain as V39.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(R/'preview/V40_Middle_Curve.png',dpi=150)
