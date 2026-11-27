# VideoIVLiceo

Video de fin de año de IV Liceo (22 alumnos). Las fotos están en `IV LICEO/<Apellido Nombre>/`.

## Cómo se arma el video (carpeta `video/`)
1. `scripts/prep.py`: normaliza las fotos (HEIC a JPG, rotación, tamaño) y arma una planilla de contacto por alumno.
2. `seleccion.tsv`: las 7 fotos elegidas por alumno con la edad estimada (más "BK" = reservas).
3. `scripts/orden.py`: genera `orden.csv`. Ronda 1 = la foto más chica de cada alumno, ronda 7 = la más grande, así todos aparecen parejo y el video va de chicos a grandes.
4. `crops.json`: recortes para capturas de pantalla.
5. `scripts/render2.py` (versión actual) y `render.py` (primer borrador): generan el video (fondo difuminado, zoom suave, fundido cruzado) y le agrega la música si se le pasa un MP3.

Para corregir el orden: editar la edad estimada en `seleccion.tsv` (o cambiar la foto elegida) y volver a correr `orden.py` y `render.py`.

## Versión final
```
python3 -I video/scripts/render2.py video/orden.csv <prep> video/crops.json VideoIVLiceo_final.mp4 1920 1080 1.668 7 "baile.mp3,ojitos.mp3"
```
La primera canción suena completa durante las rondas 1 a 5 y la segunda entra (con cruce de 3 s) en la ronda 6 y sigue hasta el final.
Los MP3 y el video final no se suben al repo (música con derechos de autor).

## Actualización (fotos grupales y ajustes)
- `IV LICEO/Grupales/`: 36 fotos grupales/de eventos (01-02 de 2023; 03-36 de 2026, en orden cronológico). El detalle está en `video/grupales_indice.tsv`.
- `video/scripts/actualizar_orden.py` quita las fotos descartadas y suma las grupales: las de 2023 van en la ronda 6 (por edad) y las de 2026 forman la ronda 8, al final.
- Se quitó "In bocca al lupo!" del cierre y el video termina con el escudo de Scuole CCI (`video/escudo.jpg`).
