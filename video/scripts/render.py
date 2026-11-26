"""Paso 3: arma el video (fotos con fondo difuminado, zoom suave y fundido cruzado) y lo manda a ffmpeg.
Uso: python3 -I render.py orden.csv prep crops.json salida.mp4 [ancho alto seg_por_foto fotos_por_alumno audio.mp3]"""
import sys, csv, json, subprocess
import cv2, numpy as np

orden, prep, crops_f, out = sys.argv[1:5]
W = int(sys.argv[5]) if len(sys.argv) > 5 else 1280
H = int(sys.argv[6]) if len(sys.argv) > 6 else 720
S = float(sys.argv[7]) if len(sys.argv) > 7 else 1.6       # segundos por foto
KEEP = int(sys.argv[8]) if len(sys.argv) > 8 else 7        # fotos por alumno a usar (7 = todas)
audio = sys.argv[9] if len(sys.argv) > 9 else None
FPS, FADE = 25, 0.4
crops = json.load(open(crops_f))

rows = [r for r in csv.DictReader(open(orden, encoding='utf-8'))]
if KEEP < 7:  # si hay que acortar, se saca la ronda que menos aporta de cada alumno (la 2ª, no las puntas)
    drop = {7: [], 6: [4], 5: [2, 4], 4: [2, 4, 6]}[KEEP]
    rows = [r for r in rows if int(r['ronda']) not in drop]

def prepare(r):
    im = cv2.imread(f"{prep}/{r['archivo']}")
    if r['archivo'] in crops:
        l, t, rr, b = crops[r['archivo']]; im = im[t:b, l:rr]
    h, w = im.shape[:2]
    s = min(W / w, H / h)                                    # foto completa, sin deformar ni cortar
    fg = cv2.resize(im, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
    sb = max(W / w, H / h)                                   # fondo = misma foto rellenando y desenfocada
    bg = cv2.resize(im, (int(w * sb) + 1, int(h * sb) + 1))
    y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
    bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 25)
    bg = (bg * 0.55).astype(np.uint8)
    return fg, bg

def frame(p, t):
    fg, bg = p
    z = 1 + 0.05 * min(1, t / (S + FADE))                    # zoom lento
    fh, fw = fg.shape[:2]
    nw, nh = int(fw * z), int(fh * z)
    f = cv2.resize(fg, (nw, nh), interpolation=cv2.INTER_LINEAR)
    c = bg.copy()
    x, y = (W - nw) // 2, (H - nh) // 2
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    ww, hh = min(nw - sx0, W - dx0), min(nh - sy0, H - dy0)
    c[dy0:dy0 + hh, dx0:dx0 + ww] = f[sy0:sy0 + hh, sx0:sx0 + ww]
    return c

n = len(rows); total = n * S + FADE
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if audio: cmd += ['-i', audio, '-shortest', '-c:a', 'aac', '-b:a', '192k', '-af', f'afade=t=out:st={total-3}:d=3']
cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

cache = {}
def get(i):
    if i not in cache:
        cache[i] = prepare(rows[i]); cache.pop(i - 3, None)
    return cache[i]

for k in range(int(total * FPS)):
    T = k / FPS
    i = min(int(T // S), n - 1)
    t = T - i * S
    cur = frame(get(i), t)
    if i > 0 and t < FADE:                                   # fundido cruzado con la foto anterior
        a = t / FADE
        prev = frame(get(i - 1), T - (i - 1) * S)
        cur = cv2.addWeighted(prev, 1 - a, cur, a, 0)
    g = min(1, T / 1.0, (total - T) / 1.5)                   # entrada y salida en negro
    if g < 1: cur = (cur * max(g, 0)).astype(np.uint8)
    ff.stdin.write(cur.tobytes())
ff.stdin.close(); ff.wait()
print(f'{n} fotos, {total:.1f}s ->', out)
