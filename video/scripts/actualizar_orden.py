"""Actualiza orden.csv: quita fotos que no van y suma las fotos grupales (carpeta 'Grupales').
Uso: python3 -I actualizar_orden.py orden_entrada.csv grupales_indice.tsv orden_salida.csv
 - QUITAR: fotos eliminadas por pedido (se identifican por 'archivo').
 - Grupales 2023 (nº 01-02, ~14-15 años): ronda 6, ubicadas por edad estimada.
 - Grupales 2026 (nº 03-36): ronda 8 (nueva, al final), en orden cronológico por fecha de la foto."""
import csv, sys
QUITAR = {'Sferco Valentina/08.jpg', 'Ramon Abril/04.jpg', 'Buschittari Valentina/04.jpg', 'Fernandez Ares Juan Manuel/08.jpg',
          'Rodriguez Fregonese Micaela/08.jpg', 'Sferco Valentina/06.jpg', 'Di Pasquale Santino Rocco/01.jpg', 'Kramer Matias/18.jpg',
          'Fernandez Ares Juan Manuel/10.jpg', 'Sferco Valentina/07.jpg', 'Covato Benjamin/03.jpg', 'Sferco Valentina/04.jpg',
          'Buschittari Valentina/09.jpg', 'Covato Benjamin/04.jpg'}
ent, idx, sal = sys.argv[1:4]
rows = list(csv.DictReader(open(ent, encoding='utf-8'))); campos = list(rows[0].keys())
rows = [r for r in rows if r['archivo'] not in QUITAR]
grup = [l.rstrip('\n').split('\t') for l in open(idx, encoding='utf-8')]
def fila(g, ronda, edad):
    n, fecha, desc = g
    return {'ronda': ronda, 'alumno': 'Grupales', 'foto': n, 'edad_estimada': edad, 'archivo': f'Grupales/{n}.jpg', 'nota': f'{fecha} · {desc}'}
# 2023 -> ronda 6, por edad (14.5)
r6 = [i for i, r in enumerate(rows) if r['ronda'] == '6']
for g in grup[:2][::-1]:
    pos = next((i for i in r6 if float(rows[i]['edad_estimada']) > 14.5), r6[-1] + 1)
    rows.insert(pos, fila(g, '6', '14.5')); r6 = [i for i, r in enumerate(rows) if r['ronda'] == '6']
rows += [fila(g, '8', '') for g in grup[2:]]
w = csv.DictWriter(open(sal, 'w', newline='', encoding='utf-8'), fieldnames=campos); w.writeheader(); w.writerows(rows)
print(len(rows), 'filas')
