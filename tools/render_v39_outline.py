from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,trimesh
R=Path(__file__).resolve().parents[1];m=trimesh.load_mesh(R/'source/v38/Controller_Cover_A.stl');upper=m.bounds[1,1];lower=upper-24
fig,axs=plt.subplots(1,2,figsize=(11,5))
centers=[(15.5,upper-2),(-15.5,upper-2),(-15.5,lower+2),(15.5,lower+2)]
xy=np.array([[x+2*np.cos(t),y+2*np.sin(t)] for (x,y),start in zip(centers,[0,90,180,270]) for t in np.deg2rad(np.linspace(start,start+90,50))]);xy=np.vstack([xy,xy[0]])
rect=np.array([[-17.5,lower],[17.5,lower],[17.5,upper],[-17.5,upper],[-17.5,lower]])
for ax in axs:
 ax.plot(rect[:,0],rect[:,1],'--',c='gray',label='V38 square shell envelope');ax.plot(xy[:,0],xy[:,1],c='#1261a0',lw=2,label='V39 nominal rounded outline');ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('CAD X (mm)');ax.set_ylabel('CAD Y (mm)')
axs[0].set(xlim=(-19,19),ylim=(lower-1,upper+1),title='Shell outline: same 35 × 24 mm envelope');axs[0].legend(fontsize=8)
axs[1].set(xlim=(14.5,18),ylim=(lower-0.5,lower+3),title='Lower-right corner: 2 mm radius')
fig.text(.5,.02,'Outline diagram only; clips omitted. Side-edge lead-in is 0.25 mm nominal. Physical clearance remains untested.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(R/'preview/V39_Rounded_Outline.png',dpi=150)
