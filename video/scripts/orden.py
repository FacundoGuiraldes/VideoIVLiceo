"""Paso 2: arma el orden del video a partir de seleccion.tsv.
Cada alumno tiene 7 fotos (ordenadas por edad). Ronda k = k-ésima foto más chica de cada alumno,
así todos aparecen parejo a lo largo del video y las fotos de chicos van primero.
Uso: python3 -I orden.py seleccion.tsv prep orden.csv"""
import sys, csv, os
import numpy as np
from PIL import Image

sel, prep, out = sys.argv[1:4]
por_alumno = {}
for line in open(sel, encoding='utf-8'):
    if line.startswith('#') or line.startswith('BK') or not line.strip(): continue
    a, n, edad, nota = line.rstrip('\n').split('\t')[:4]
    por_alumno.setdefault(a, []).append((float(edad), n, nota))

rows = []
for a, fotos in por_alumno.items():
    fotos.sort(key=lambda x: (x[0], x[1]))          # de más chico a más grande
    for k, (edad, n, nota) in enumerate(fotos, 1):
        rows.append(dict(ronda=k, alumno=a, foto=n, edad_estimada=edad, archivo=f'{a}/{n}.jpg', nota=nota))
rows.sort(key=lambda r: (r['ronda'], r['edad_estimada'], r['alumno']))

def dhash(p):  # hash perceptual simple para detectar fotos repetidas entre alumnos
    g = np.asarray(Image.open(p).convert('L').resize((9, 8)), dtype=float)
    return (g[:, 1:] > g[:, :-1]).flatten()
hs = [dhash(os.path.join(prep, r['archivo'])) for r in rows]
dups = [(i, j) for i in range(len(rows)) for j in range(i+1, len(rows)) if (hs[i] != hs[j]).sum() <= 8]
for i, j in dups: print('REPETIDA:', rows[i]['archivo'], '~', rows[j]['archivo'])

with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), 'fotos en', out)
