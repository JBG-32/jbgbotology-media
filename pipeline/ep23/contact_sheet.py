"""Build one combined keyframe contact sheet for Ep 2 + Ep 3.
Usage: python3 contact_sheet.py <keys_dir> <out.jpg>
keys_dir holds files named <SHOTID>_A.png / <SHOTID>_B.png."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
keys, out = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
shots = json.load(open(os.path.join(HERE, 'shots.json')))
FD = os.path.join(HERE, '..', 'fonts')
F = lambda n, s: ImageFont.truetype(os.path.join(FD, n), s)
fb, fm = F('space-grotesk-latin-700-normal.woff', 30), F('ibm-plex-mono-latin-500-normal.woff', 20)
TW, TH = 216, 384
TYPE = {'hero': 'HERO · Seedance', 'veo': 'Veo Lite', 'still': 'STILL'}
cells = []
for ep in ('ep2', 'ep3'):
    for s in shots[ep]:
        if s['type'] in TYPE:
            cells.append((ep, s))
cols = 4
rows = (len(cells) + cols - 1) // cols
CW, CH = TW * 2 + 30, TH + 70
W, H = cols * CW + 40, rows * CH + 120
img = Image.new('RGB', (W, H), (5, 6, 10))
d = ImageDraw.Draw(img)
d.text((20, 30), 'STARGATE EP 2 + EP 3 · KEYFRAME PICKS (A or B per shot)', font=fb, fill=(245, 185, 66))
for i, (ep, s) in enumerate(cells):
    x, y = 20 + (i % cols) * CW, 100 + (i // cols) * CH
    col = (63, 224, 255) if ep == 'ep2' else (123, 92, 255)
    d.text((x, y), f"{s['id']}  {TYPE[s['type']]}  {s['t'][0]:.0f}-{s['t'][1]:.0f}s", font=fm, fill=col)
    for j, opt in enumerate('AB'):
        p = os.path.join(keys, f"{s['id']}_{opt}.png")
        if os.path.exists(p):
            im = Image.open(p).convert('RGB').resize((TW, TH))
            img.paste(im, (x + j * (TW + 10), y + 30))
            d.text((x + j * (TW + 10) + 8, y + 36), opt, font=fb, fill=(245, 185, 66), stroke_width=3, stroke_fill=(5, 6, 10))
img.save(out, quality=85)
print(out, img.size)
