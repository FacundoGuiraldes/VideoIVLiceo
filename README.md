# VideoIVLiceo

Video de fin de año de IV Liceo (22 alumnos). Las fotos están en `IV LICEO/<Apellido Nombre>/`.

## Cómo se arma el video (carpeta `video/`)
1. `scripts/prep.py`: normaliza las fotos (HEIC a JPG, rotación, tamaño) y arma una planilla de contacto por alumno.
2. `seleccion.tsv`: las 7 fotos elegidas por alumno con la edad estimada (más "BK" = reservas).
3. `scripts/orden.py`: genera `orden.csv`. Ronda 1 = la foto más chica de cada alumno, ronda 7 = la más grande, así todos aparecen parejo y el video va de chicos a grandes.
4. `crops.json`: recortes para capturas de pantalla.
5. `scripts/render2.py` (versión actual) y `render.py` (primer borrador): generan el video (fondo difuminado, zoom suave, fundido cruzado) y le agrega la música si se le pasa un MP3.

Para corregir el orden: editar la edad estimada en `seleccion.tsv` (o cambiar la foto elegida) y volver a correr `orden.py` y `render.py`.
