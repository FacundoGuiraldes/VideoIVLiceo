import csv,sys,shutil,os
SEL=[ # carpeta, alumno, [(nº, edad)]
('Bianco','Bianco Agustina',[(7,12),(5,12.5),(3,14)]),
('Burnett','Burnett Jazmin',[(4,12),(5,13),(9,13.5)]),
('Buschittari','Buschittari Valentina',[(4,10.5),(5,11),(3,11.5)]),
('Cayo','Cayo Maria Antonella',[(9,10.5),(8,11),(2,13)]),
('Covato','Covato Benjamin',[(8,12),(3,13),(4,13.5)]),
('De Santis','De Santis Thiago',[(5,10.5),(4,11),(1,11.5)]),
('De Somma','De Somma Chiara',[(2,13),(5,13.5),(8,14.5)]),
('Di Pasquale','Di Pasquale Santino Rocco',[(10,11),(7,11.5),(8,12)]),
('Escudero','Escudero Santiago',[(10,11),(7,12),(13,13)]),
('Estevez Trova','Estevez Trova Tomas',[(11,12),(12,12.5),(13,13)]),
('Fernandez Ares','Fernandez Ares Juan Manuel',[(10,10.5),(9,11),(11,13)]),
('Figari Saborido','Figari Saborido Renata',[(1,10.5),(11,12),(10,13)]),
('Kramer','Kramer Matias',[(3,12),(13,12.5),(4,13)]),
('LUJAN','Lujan Benicio',[(23,10),(20,10.5),(21,11)]),
('Lachner','Lachner Mateo',[(3,13.5),(6,14),(5,14.5)]),
('Moure','Moure Josefina',[(5,13),(9,13.5),(10,14)]),
('Prado Bortignon','Prado Bortignon Dalina',[(4,12.5),(2,13),(5,13.5)]),
('Ramon','Ramon Abril',[(7,13),(1,13.2),(2,13.5)]),
('Rodriguez Fregonese','Rodriguez Fregonese Micaela',[(9,11.5),(10,12),(13,14)]),
('Sferco','Sferco Valentina',[(7,12.5),(15,13),(16,13.5)]),
('Surdo Godoy','Surdo Godoy Santiago',[(9,12),(4,13),(1,14)]),
]
rows=list(csv.DictReader(open('orden.csv')))
# quitar III Media previas si se re-ejecuta
rows=[r for r in rows if not r['nota'].startswith('III Media')]
# mover Grupales 36 al inicio de la ronda 8
g36=[r for r in rows if r['archivo']=='Grupales/36.jpg']
if g36:
    rows.remove(g36[0]); i8=next(i for i,r in enumerate(rows) if r['ronda']=='8'); rows.insert(i8,g36[0])
new=[]
for k in range(3):
    sub=[]
    for fol,al,l in SEL:
        n,ed=l[k]
        dst=f'prep/{al}/M{n:02d}.jpg'
        shutil.copy(f'prep_iii/{fol}/{n:02d}.jpg',dst)
        sub.append({'ronda':'5','alumno':al,'foto':f'M{n:02d}','edad_estimada':str(ed),'archivo':f'{al}/M{n:02d}.jpg','nota':f'III Media ({fol} {n:02d})'})
    sub.sort(key=lambda r:float(r['edad_estimada'])); new+=sub
j=max(i for i,r in enumerate(rows) if r['ronda']=='5')+1
rows[j:j]=new
w=csv.DictWriter(open('orden.csv','w',newline=''),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows),len(new))
