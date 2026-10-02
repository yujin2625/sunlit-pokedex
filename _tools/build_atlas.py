# Packs rendered sprites into WebP atlas sheets + sprites.json
import json, os
from PIL import Image

T = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(T)
OUTDIR = os.path.join(S, 'pokedex')
SRC = os.path.join(T, 'out')
CELL, COLS, ROWS = 192, 10, 10
PER = COLS * ROWS

jobs = [j['id'] for j in json.load(open(os.path.join(T, 'jobs.json')))]
have = set(f[:-4] for f in os.listdir(SRC) if f.endswith('.png'))
base = [j for j in jobs if '__' not in j and j in have]
rest = [j for j in jobs if '__' in j and j in have]
order = base + rest
missing = [j for j in jobs if j not in have]
print('sprites', len(order), 'missing', len(missing), missing[:20])

os.makedirs(os.path.join(OUTDIR, 'sprites'), exist_ok=True)
for f in os.listdir(os.path.join(OUTDIR, 'sprites')):
    os.remove(os.path.join(OUTDIR, 'sprites', f))
sheets, mp = [], {}


def pack(ids):
    for k in range(0, len(ids), PER):
        chunk = ids[k:k + PER]
        rows = (len(chunk) + COLS - 1) // COLS
        cols = COLS if rows > 1 else len(chunk)
        im = Image.new('RGBA', (cols * CELL, rows * CELL), (0, 0, 0, 0))
        si = len(sheets)
        for i, sid in enumerate(chunk):
            t = Image.open(os.path.join(SRC, sid + '.png')).convert('RGBA')
            if t.size != (CELL, CELL):
                t = t.resize((CELL, CELL), Image.LANCZOS)
            im.paste(t, ((i % cols) * CELL, (i // cols) * CELL))
            mp[sid] = [si, i]
        name = 'sprites/s%02d.webp' % si
        im.save(os.path.join(OUTDIR, name), 'WEBP', quality=86, method=6)
        sheets.append({'f': name, 'cols': cols, 'rows': rows})

pack(base)
pack(rest)
json.dump({'sheets': sheets, 'map': mp}, open(os.path.join(OUTDIR, 'data', 'sprites.json'), 'w'), separators=(',', ':'))
tot = sum(os.path.getsize(os.path.join(OUTDIR, s['f'])) for s in sheets)
print('sheets', len(sheets), 'MB', round(tot / 1e6, 1), 'max', round(max(os.path.getsize(os.path.join(OUTDIR, s['f'])) for s in sheets) / 1e6, 2))
# ---- small thumbnails for the grid (base forms only), embedded in the page as data URIs
import base64, io
TC, TCOLS = 96, 16
TPER = TCOLS * TCOLS
tsheets, tmap = [], {}
for k in range(0, len(base), TPER):
    chunk = base[k:k + TPER]
    rows = (len(chunk) + TCOLS - 1) // TCOLS
    im = Image.new('RGBA', (TCOLS * TC, rows * TC), (0, 0, 0, 0))
    for i, sid in enumerate(chunk):
        t = Image.open(os.path.join(SRC, sid + '.png')).convert('RGBA').resize((TC, TC), Image.LANCZOS)
        im.paste(t, ((i % TCOLS) * TC, (i // TCOLS) * TC))
        tmap[sid] = [len(tsheets), i]
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=82, method=6)
    tsheets.append({'d': 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode(), 'cols': TCOLS, 'rows': rows})
json.dump({'sheets': tsheets, 'map': tmap}, open(os.path.join(OUTDIR, 'data', 'thumbs.json'), 'w'), separators=(',', ':'))
print('thumb sheets', len(tsheets), 'KB', os.path.getsize(os.path.join(OUTDIR, 'data', 'thumbs.json')) // 1024)
