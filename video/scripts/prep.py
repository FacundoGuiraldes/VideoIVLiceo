"""Paso 1: normaliza fotos (HEIC->JPG, rotación EXIF, tamaño máx) y arma contact sheets por alumno.
Uso: python3 -I prep.py <carpeta_fotos> <salida_prep> <salida_sheets>"""
import os, sys, re
from PIL import Image, ImageOps, ImageDraw, ImageFont
import pillow_heif
pillow_heif.register_heif_opener()  # permite abrir .HEIC con Pillow

src, out, sheets = sys.argv[1:4]
MAXSIDE = 2000
font = ImageFont.load_default(size=28)
index = []  # (alumno, nº, archivo original, tamaño)

for alumno in sorted(os.listdir(src)):
    d = os.path.join(src, alumno)
    if not os.path.isdir(d): continue
    os.makedirs(os.path.join(out, alumno), exist_ok=True)
    thumbs = []
    for i, f in enumerate(sorted(os.listdir(d)), 1):
        im = ImageOps.exif_transpose(Image.open(os.path.join(d, f))).convert('RGB')
        orig = im.size
        im.thumbnail((MAXSIDE, MAXSIDE))
        im.save(os.path.join(out, alumno, f'{i:02d}.jpg'), quality=92)
        index.append((alumno, i, f, orig))
        t = im.copy(); t.thumbnail((360, 360))
        ImageDraw.Draw(t).rectangle((0, 0, 44, 36), fill='black')
        ImageDraw.Draw(t).text((6, 2), str(i), fill='yellow', font=font)  # nº de foto
        thumbs.append(t)
    cols = 5; rows = -(-len(thumbs) // cols)
    sh = Image.new('RGB', (cols * 364, rows * 364), 'white')
    for k, t in enumerate(thumbs):
        sh.paste(t, ((k % cols) * 364, (k // cols) * 364))
    sh.save(os.path.join(sheets, alumno + '.jpg'), quality=82)

with open(os.path.join(out, 'indice.tsv'), 'w') as fh:
    for a, i, f, s in index: fh.write(f'{a}\t{i:02d}\t{f}\t{s[0]}x{s[1]}\n')
print(len(index), 'fotos procesadas')
