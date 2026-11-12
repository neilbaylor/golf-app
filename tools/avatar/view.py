"""quick look: render svgs (+ optional trace overlays) side by side -> tmp/view.png
usage: python3 view.py out.png size file1.svg file2.svg ..."""
import sys, os
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from avlib import render, T
out, size = sys.argv[1], int(sys.argv[2]); files = sys.argv[3:]
ims = []
for i, f in enumerate(files):
    p = T + f'_v{i}.png'; render(f, p, size, size); ims.append(Image.open(p).convert('RGB'))
W = Image.new('RGB', (size * len(ims) + 8 * (len(ims) - 1), size), 'white')
for i, im in enumerate(ims): W.paste(im, (i * (size + 8), 0))
W.save(out)
