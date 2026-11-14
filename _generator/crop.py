"""Cut a picture out of a book page: python -X utf8 -I _generator/crop.py PAGE x0 y0 x1 y1 NAME [vol-slug]
x0..y1 are fractions (0-1) of the page. Writes assets/img/<vol-slug>/<NAME>.png (default vol-1)."""
import sys, os
from PIL import Image

page, x0, y0, x1, y1, name = int(sys.argv[1]), *map(float, sys.argv[2:6]), sys.argv[6]
slug = sys.argv[7] if len(sys.argv) > 7 else 'vol-1'
im = Image.open('D:/HarperSites/_scratch/vol1/png/p%03d.png' % page).convert('RGB')
w, h = im.size
crop = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'img', slug)
os.makedirs(out, exist_ok=True)
crop.save(os.path.join(out, name + '.png'), optimize=True)
print(os.path.join(out, name + '.png'), crop.size)
