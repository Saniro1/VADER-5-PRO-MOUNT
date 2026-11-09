from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import trimesh
R=Path(__file__).resolve().parents[1];fig,ax=plt.subplots(figsize=(9,4.8))
for ver,color in [('v35','gray'),('v36','#1261a0')]:
 m=trimesh.load_mesh(R/f'source/{ver}/Controller_Cover_A.stl');s=m.section(plane_origin=[0,0,0],plane_normal=[1,0,0])
 for i,line in enumerate(s.discrete):ax.plot(line[:,1],line[:,2],c=color,lw=2,label=ver.upper() if i==0 else None)
ax.axvline(-8.459638,ls='--',c='#777',lw=1);ax.text(-8.3,.4,'Shell rim',rotation=90,fontsize=9)
ax.set(xlim=(-14.2,-6),ylim=(.3,5.1),xlabel='CAD Y (mm)',ylabel='CAD Z (mm)',title='V36 middle hook: extended tip and solid tapered anchor web');ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend();fig.text(.5,.02,'Blue is the revised cover profile. Physical fit and strength remain untested.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(R/'preview/V36_Middle_Anchor.png',dpi=150)
