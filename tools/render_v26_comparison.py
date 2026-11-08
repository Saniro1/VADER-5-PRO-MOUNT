"""Plot the retaining features, without asserting an OEM dimension or fit."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import trimesh

ROOT = Path(__file__).resolve().parents[1]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
handles = []
for path, label, color in [
    ("source/v25/Revised_Controller_Cover.stl", "V25", "#7e8790"),
    ("source/v26/Controller_Cover_A.stl", "A: modest engagement", "#216a9b"),
    ("source/v26/Controller_Cover_B.stl", "B: more engagement", "#ce7b27"),
]:
    mesh = trimesh.load_mesh(ROOT / path)
    for ax, x in zip(axes, [0, 10.8]):
        lines = trimesh.intersections.mesh_plane(mesh, [1, 0, 0], [x, 0, 0])
        ax.add_collection(LineCollection(lines[:, :, [1, 2]], colors=color, linewidths=1.7))
    handles.append(Line2D([], [], color=color, label=label, linewidth=1.7))
axes[0].set(xlim=(-12.9, -11.0), ylim=(0.3, 3.15), title="Center retaining ridge")
axes[1].set(xlim=(7.5, 9.5), ylim=(-2.85, -1.6), title="One of the paired top-hook toes")
for ax in axes:
    ax.set_aspect("equal")
    ax.set_xlabel("CAD Y (mm)")
    ax.set_ylabel("CAD Z (mm)")
    ax.grid(alpha=0.2)
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False)
fig.suptitle("V26: change the retaining lips; keep whole-clip insertion depth\nCAD comparison only — controller engagement and removal force remain untested.", fontsize=12)
fig.subplots_adjust(top=0.78, bottom=0.22, wspace=0.4)
fig.savefig(ROOT / "preview/V26_Retaining_Features.png", dpi=160, bbox_inches="tight", pad_inches=0.15)
