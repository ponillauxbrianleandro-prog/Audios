import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
box = tuple(int(x) for x in sys.argv[3:7]) if len(sys.argv) >= 7 else None
im = Image.open(src).convert("RGBA")
bg = Image.new("RGBA", im.size, (120, 130, 150, 255)); bg.alpha_composite(im)
im = bg.convert("RGB")
if box: im = im.crop(box)
im.save(out)
