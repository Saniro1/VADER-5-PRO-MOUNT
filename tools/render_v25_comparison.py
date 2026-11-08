"""Plot CAD cover sections; deliberately does not infer OEM dimensions from photos."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import trimesh

ROOT = Path(__file__).resolve().parents[1]
fig, ax = plt.subplots(figsize=(11, 4.5), layout="constrained")
handles = []
for filename, label, color, style in [
    ("originals/Vader5Pro_Original_V2_Cover.stl", "Original supplied mesh (not measured OEM)", "#4b83b3", "dashed"),
    ("source/v24/Revised_Controller_Cover.stl", "V24: extended clips", "#d68036", "solid"),
    ("source/v25/Revised_Controller_Cover.stl", "V25 seating trial", "#142e3c", "solid"),
]:
    mesh = trimesh.load_mesh(ROOT / filename)
    lines = trimesh.intersections.mesh_plane(mesh, [1, 0, 0], [0, 0, 0])
    ax.add_collection(LineCollection(lines[:, :, [1, 2]], colors=color, linewidths=1.5, linestyles=style))
    handles.append(Line2D([], [], color=color, linestyle=style, label=label))
ax.autoscale()
ax.set_aspect("equal")
ax.set_xlabel("CAD Y (mm)")
ax.set_ylabel("CAD Z (mm)")
ax.grid(alpha=0.18)
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=1, frameon=False)
ax.set_title("Center section: thinner outside shell and original-source clip reach\nNo exact OEM cover drawing was found; physical fit remains unverified.", loc="left", fontsize=12)
fig.savefig(ROOT / "preview/V25_Cover_Comparison.png", dpi=160, bbox_inches="tight", pad_inches=0.15)
