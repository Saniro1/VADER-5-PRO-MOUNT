from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import trimesh
R=Path(__file__).resolve().parents[1]
fig,ax=plt.subplots(figsize=(8,4.5))
for v,c in [('v34','gray'),('v35','#1261a0')]:
 m=trimesh.load_mesh(R/f'source/{v}/Controller_Cover_A.stl');s=m.section(plane_origin=[10.8,0,0],plane_normal=[1,0,0])
 for i,line in enumerate(s.discrete):ax.plot(line[:,1],line[:,2],color=c,lw=2,label=v.upper() if i==0 else None)
ax.set(xlim=(8.2,11.9),ylim=(-2.9,-.3),xlabel='CAD Y (mm)',ylabel='CAD Z (mm)',title='V35: thicker neck and deeper retaining shoulder')
ax.set_aspect('equal');ax.grid(alpha=.25);ax.legend();fig.text(.5,.015,'CAD comparison only; OEM shape and physical retention are unverified.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(R/'preview/V35_Hook_Profile.png',dpi=160)
