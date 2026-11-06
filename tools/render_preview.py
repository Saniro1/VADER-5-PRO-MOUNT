"""Render actual STL geometry with Blender 4.x and compose an overview using Pillow."""
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
with tempfile.TemporaryDirectory(prefix="vader-preview-") as directory:
    subprocess.run(["blender", "-b", "--python", str(ROOT / "tools/render_blender.py"), "--", directory], check=True)
    out = Image.new("RGB", (1900, 1700), "#f4f7fa")
    draw = ImageDraw.Draw(out)
    draw.text((50, 35), "VADER 5 PRO · V23 DETACHABLE BOX 2", font=ImageFont.truetype(FONT, 43), fill="#1d3347")
    draw.text((50, 100), "Shared G7 V22 box and key · Corrected Vader receiver · Physical fit test required", font=ImageFont.truetype(FONT, 24), fill="#4e6376")
    titles = ["Shared G7 Box 2 on Vader V23", "Withdraw key, then slide box toward +Y",
              "V23 bearing bed and closer end stop", "Small receiver fit test and shared key"]
    for i, title in enumerate(titles):
        x, y = 25 + (i % 2) * 950, 175 + (i // 2) * 750
        draw.text((x + 20, y), title, font=ImageFont.truetype(FONT, 26), fill="#1d3347")
        panel = Image.open(Path(directory) / f"panel{i}.png").convert("RGBA")
        out.paste(panel, (x, y + 30), panel)
    out.save(ROOT / "preview/V23_Overview.png")
