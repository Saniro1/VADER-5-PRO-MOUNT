"""Make a true-size A4 reference sheet; photographs remain approximate measurements."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/fit_reference/OEM_Profile_Reference.pdf'
def sheet(title):
 fig=plt.figure(figsize=(210/25.4,297/25.4));ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,210),ylim=(0,297));ax.axis('off');ax.text(15,280,title,fontsize=15,weight='bold');return fig,ax
def grid(ax,x,y,w,h):
 for i in range(w+1):ax.plot([x+i,x+i],[y,y+h],color='#aaa' if i%5==0 else '#ddd',lw=.6 if i%5==0 else .25)
 for i in range(h+1):ax.plot([x,x+w],[y+i,y+i],color='#aaa' if i%5==0 else '#ddd',lw=.6 if i%5==0 else .25)
 ax.plot([x,x+w],[y,y],color='black',lw=1.2)
def scale(ax):
 ax.plot([20,70],[30,30],color='black',lw=2);ax.plot([20,20],[28,32],color='black');ax.plot([70,70],[28,32],color='black');ax.text(20,21,'This bar must measure 50 mm after printing.',fontsize=10)
with PdfPages(OUT) as pdf:
 fig,ax=sheet('Vader 5 Pro: underside comparison')
 ax.text(15,265,'Print A4 at Actual size / 100%. Disable Fit to page.',fontsize=11)
 ax.text(15,254,'1 mm grid; darker lines every 5 mm. Check the 50 mm bar.',fontsize=10)
 ax.text(15,243,'Place OEM and bare V28 B with hooks facing the camera.',fontsize=10)
 ax.text(15,234,'Photograph straight down, centered, close enough to see hooks.',fontsize=10)
 grid(ax,15,130,85,85);grid(ax,110,130,85,85)
 ax.text(40,220,'OEM',fontsize=13);ax.text(135,220,'V28 B',fontsize=13)
 ax.text(15,105,'Keep all brim/supports off. Do not force, bend or modify the OEM.',fontsize=10)
 ax.text(15,92,'Photo reference only: curvature and camera perspective limit precision.',fontsize=9)
 scale(ax);pdf.savefig(fig);plt.close(fig)
 fig,ax=sheet('Vader 5 Pro: side-profile comparison')
 ax.text(15,265,'Stand this page upright behind the covers; keep it close to them.',fontsize=10)
 ax.text(15,254,'Rest both covers on the same flat table. Photograph horizontally.',fontsize=10)
 ax.text(15,243,'Camera square to the profile: avoid looking down at the parts.',fontsize=10)
 grid(ax,15,155,180,60)
 ax.text(38,221,'OEM',fontsize=13);ax.text(132,221,'V28 B',fontsize=13)
 ax.text(15,137,'Align the grid baseline with the table. Show shell and hook tips.',fontsize=10)
 ax.text(15,124,'Take a second side-profile photo after rotating both covers 90 degrees.',fontsize=10)
 ax.text(15,101,'No printer? Use a millimeter ruler immediately beside the parts instead.',fontsize=10)
 ax.text(15,88,'Calipers are better for wall thickness and hook-clearance measurements.',fontsize=10)
 scale(ax);pdf.savefig(fig);plt.close(fig)
print(OUT)
