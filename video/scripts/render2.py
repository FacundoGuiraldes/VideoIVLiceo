"""Versión 2 del render: título de apertura, movimientos variados por foto, mosaico final, texto de cierre y créditos.
Uso: python3 -I render2.py orden.csv prep crops.json salida.mp4 [ancho alto seg_por_foto fotos_por_alumno audio.mp3]"""
import sys, csv, json, random, subprocess, os
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

orden, prep, crops_f, out = sys.argv[1:5]
W = int(sys.argv[5]) if len(sys.argv) > 5 else 1280
H = int(sys.argv[6]) if len(sys.argv) > 6 else 720
S = float(sys.argv[7]) if len(sys.argv) > 7 else 1.6
KEEP = int(sys.argv[8]) if len(sys.argv) > 8 else 7
audio = sys.argv[9] if len(sys.argv) > 9 else None
FPS, FADE = 25, 0.4
sc = H / 720                                   # escala de textos según resolución
FD = '/usr/share/fonts/truetype/google-fonts/ofl/'
F_TIT, F_LIGHT, F_SEMI = FD + 'cardo/Cardo-Regular.ttf', FD + 'firasans/FiraSans-Light.ttf', FD + 'firasans/FiraSans-SemiBold.ttf'
crops = json.load(open(crops_f))

NOMBRES = ['Agustina Bianco', 'Jazmín Burnett', 'Valentina Buschittari', 'María Antonella Cayo', 'Benjamín Covato',
           'Thiago De Santis', 'Chiara De Somma', 'Santino Di Pasquale', 'Santiago Escudero', 'Tomás Estévez Trova',
           'Juan Manuel Fernández Ares', 'Renata Figari Saborido', 'Matías Kramer', 'Mateo Lachner', 'Benicio Lujan',
           'Josefina Moure', 'Dalina Prado Bortignon', 'Marcelo Preite', 'Abril Ramón', 'Micaela Rodriguez Fregonese',
           'Valentina Sferco', 'Santiago Surdo Godoy']
CARPETA = {'Bianco Agustina': 0, 'Burnett Jazmin': 1, 'Buschittari Valentina': 2, 'Cayo Maria Antonella': 3, 'Covato Benjamin': 4,
           'De Santis Thiago': 5, 'De Somma Chiara': 6, 'Di Pasquale Santino Rocco': 7, 'Escudero Santiago': 8,
           'Estevez Trova Tomas': 9, 'Fernandez Ares Juan Manuel': 10, 'Figari Saborido Renata': 11, 'Kramer Matias': 12,
           'Lachner Mateo': 13, 'Lujan Benicio': 14, 'Moure Josefina': 15, 'Prado Bortignon Dalina': 16, 'Preite Marcelo': 17,
           'Ramon Abril': 18, 'Rodriguez Fregonese Micaela': 19, 'Sferco Valentina': 20, 'Surdo Godoy Santiago': 21}

# Foto grupal de cada alumno para el mosaico final (la más reciente que tengan en grupo)
MOSAICO = {'Bianco Agustina': '05', 'Burnett Jazmin': '10', 'Buschittari Valentina': '03', 'Cayo Maria Antonella': '03',
           'Covato Benjamin': '06', 'De Santis Thiago': '05', 'De Somma Chiara': '08', 'Di Pasquale Santino Rocco': '07',
           'Escudero Santiago': '15', 'Estevez Trova Tomas': '05', 'Fernandez Ares Juan Manuel': '05', 'Figari Saborido Renata': '04',
           'Kramer Matias': '16', 'Lachner Mateo': '07', 'Lujan Benicio': '02', 'Moure Josefina': '09',
           'Prado Bortignon Dalina': '02', 'Preite Marcelo': '08', 'Ramon Abril': '08', 'Rodriguez Fregonese Micaela': '04',
           'Sferco Valentina': '06', 'Surdo Godoy Santiago': '07'}

# ---------- utilidades de texto ----------
def font(p, size): return ImageFont.truetype(p, max(8, int(size * sc)))

def build_layer(items, Wl, Hl=None):
    """items: ('t', texto, fuente, tamaño, (r,g,b), tracking, espacio_abajo) | ('b', espacio_abajo) barra tricolor | ('s', espacio)"""
    hs = []
    for it in items:
        if it[0] == 't': hs.append(int(it[3] * sc * 1.3) + int(it[6] * sc))
        elif it[0] == 'b': hs.append(int(5 * sc) + int(it[1] * sc))
        else: hs.append(int(it[1] * sc))
    total = sum(hs); Hl = Hl or total
    img = Image.new('RGBA', (Wl, Hl), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = (Hl - total) // 2
    for it, h in zip(items, hs):
        if it[0] == 't':
            f = font(it[2], it[3]); tr = it[5] * sc
            wtot = sum(f.getlength(c) + tr for c in it[1]) - tr
            x = (Wl - wtot) / 2
            for c in it[1]:
                d.text((x, y), c, font=f, fill=it[4] + (255,)); x += f.getlength(c) + tr
        elif it[0] == 'b':
            bw, bh = int(220 * sc), int(5 * sc); x0 = (Wl - bw) // 2
            for k, col in enumerate([(0, 146, 70), (255, 255, 255), (206, 43, 55)]):   # verde-blanco-rojo
                d.rectangle((x0 + k * bw // 3, y, x0 + (k + 1) * bw // 3, y + bh), fill=col + (255,))
        y += h
    return np.array(img)[:, :, [2, 1, 0, 3]]                  # BGRA

def over(canvas, layer, alpha=1.0, y=0):
    h = layer.shape[0]; y0, y1 = max(0, y), min(H, y + h)
    if y1 <= y0 or alpha <= 0: return
    sub = layer[y0 - y:y1 - y]
    a = sub[..., 3:4].astype(np.float32) / 255 * alpha
    canvas[y0:y1] = (canvas[y0:y1].astype(np.float32) * (1 - a) + sub[..., :3] * a).astype(np.uint8)

def smooth(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

# ---------- datos ----------
rows = list(csv.DictReader(open(orden, encoding='utf-8')))
if KEEP < 7:
    rows = [r for r in rows if int(r['ronda']) not in {7: [], 6: [4], 5: [2, 4], 4: [2, 4, 6]}[KEEP]]

def load(r):
    im = cv2.imread(f"{prep}/{r['archivo']}")
    if r['archivo'] in crops:
        l, t, rr, b = crops[r['archivo']]; im = im[t:b, l:rr]
    return im

# ---------- escenas ----------
class Title:
    dur, fade_in = 5.0, 0.0
    def __init__(s):
        top, bot = np.array([56, 30, 14], float), np.array([26, 12, 6], float)      # azul marino (BGR)
        g = np.linspace(0, 1, H)[:, None, None]
        s.bg = (top * (1 - g) + bot * g).repeat(W, 1).astype(np.uint8)
        s.layer = build_layer([('t', 'IV LICEO', F_TIT, 92, (255, 255, 255), 16, 8), ('b', 18),
                               ('t', '2026', F_LIGHT, 46, (230, 220, 200), 10, 34),
                               ('t', 'Scuole CCI · Scuola Alessandro Manzoni', F_LIGHT, 25, (200, 210, 230), 2, 0)], W, H)
    def frame(s, t):
        c = s.bg.copy(); over(c, s.layer, smooth(t / 1.0)); return c

EFECTOS_H = ['in', 'out', 'left', 'right', 'in', 'out']          # fotos apaisadas
EFECTOS_V = ['in', 'up', 'out', 'down', 'up', 'down']            # fotos verticales

class Photo:
    fade_in = FADE
    dur = S
    def __init__(s, r, eff): s.r, s.eff, s.p = r, eff, None
    def prepare(s):
        im = load(s.r); h, w = im.shape[:2]
        k = min(W / w, H / h)
        fg = cv2.resize(im, (max(1, int(w * k)), max(1, int(h * k))), interpolation=cv2.INTER_AREA)
        kb = max(W / w, H / h); bg = cv2.resize(im, (int(w * kb) + 1, int(h * kb) + 1))
        y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
        bg = (cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 25) * 0.55).astype(np.uint8)
        s.p = (fg, bg)
    def frame(s, t):
        if s.p is None: s.prepare()
        fg, bg = s.p; u = smooth(t / (S + FADE)); e = s.eff
        z0, z1, dx0, dx1, dy0, dy1 = 1.0, 1.0, 0, 0, 0, 0
        if e == 'in': z0, z1 = 1.0, 1.08
        elif e == 'out': z0, z1 = 1.08, 1.0
        elif e == 'left': z0 = z1 = 1.06; dx0, dx1 = .03, -.03
        elif e == 'right': z0 = z1 = 1.06; dx0, dx1 = -.03, .03
        elif e == 'up': z0 = z1 = 1.06; dy0, dy1 = .03, -.03
        elif e == 'down': z0 = z1 = 1.06; dy0, dy1 = -.03, .03
        z = z0 + (z1 - z0) * u; dx = (dx0 + (dx1 - dx0) * u) * W; dy = (dy0 + (dy1 - dy0) * u) * H
        fh, fw = fg.shape[:2]; nw, nh = int(fw * z), int(fh * z)
        f = cv2.resize(fg, (nw, nh), interpolation=cv2.INTER_LINEAR); c = bg.copy()
        x, y = int((W - nw) // 2 + dx), int((H - nh) // 2 + dy)
        sx0, sy0, dx0_, dy0_ = max(0, -x), max(0, -y), max(0, x), max(0, y)
        ww, hh = min(nw - sx0, W - dx0_), min(nh - sy0, H - dy0_)
        if ww > 0 and hh > 0: c[dy0_:dy0_ + hh, dx0_:dx0_ + ww] = f[sy0:sy0 + hh, sx0:sx0 + ww]
        return c

class Ending:
    fade_in, T_TEXT, T_CRED, CRED = 1.2, 6.2, 21.0, 18.0
    def __init__(s):
        s.dur = s.T_CRED + s.CRED + 1.5
        ultimas = {a: {'archivo': f'{a}/{n}.jpg'} for a, n in MOSAICO.items()}   # fotos grupales elegidas a mano
        cols, rws = 6, 4; tw, th = W // cols, H // rws
        orden_t = sorted(ultimas, key=lambda a: CARPETA[a]); random.Random(5).shuffle(orden_t)
        s.tiles = []
        for k, a in enumerate(orden_t):
            im = load(ultimas[a]); h, w = im.shape[:2]; asp = tw / th
            cw, ch = (w, int(w / asp)) if w / h < asp else (int(h * asp), h)
            x0 = (w - cw) // 2; y0 = int((h - ch) * 0.3)         # recorte con sesgo hacia arriba (donde suelen estar las caras)
            tile = cv2.resize(im[y0:y0 + ch, x0:x0 + cw], (tw - 2, th - 2), interpolation=cv2.INTER_AREA)
            row, col = divmod(k, cols); n_row = cols if row < 3 else len(orden_t) - 18
            x = col * tw + (W - n_row * tw) // 2 + 1 if row == 3 else col * tw + 1
            s.tiles.append((x, row * th + 1, tile, 0.2 + k * 0.18))
        blanco, crema = (255, 255, 255), (235, 225, 205)
        s.msgs = [  # (capa, entra, sale)
            (build_layer([('t', 'Grazie per tutti questi anni!', F_TIT, 64, blanco, 2, 10), ('b', 26),
                          ('t', 'Che non vi manchi il coraggio di sbagliare', F_LIGHT, 34, crema, 1, 6),
                          ('t', 'né la gioia di ricominciare.', F_LIGHT, 34, crema, 1, 0)], W, H), 6.2, 11.4),
            (build_layer([('t', 'Qui avete scritto pagine indimenticabili.', F_TIT, 52, blanco, 1, 22),
                          ('t', 'Ora andate a scrivere', F_LIGHT, 38, crema, 1, 6),
                          ('t', 'il resto della vostra storia.', F_LIGHT, 38, crema, 1, 0)], W, H), 11.4, 16.4),
            (build_layer([('t', 'Grazie di tutto', F_TIT, 88, blanco, 4, 6), ('b', 18),
                          ('t', 'IV Liceo · 2026', F_LIGHT, 40, crema, 6, 26),
                          ('t', 'In bocca al lupo!', F_TIT, 48, blanco, 2, 0)], W, H), 16.4, 20.6)]
        items = [('t', 'IV LICEO 2026', F_SEMI, 34, (255, 255, 255), 10, 14), ('b', 40)]
        items += [('t', n, F_LIGHT, 42, (245, 245, 245), 1, 12) for n in NOMBRES]
        items += [('s', 36), ('t', 'Scuole CCI · Scuola Alessandro Manzoni', F_TIT, 28, (200, 210, 230), 1, 0)]
        s.cred = build_layer(items, W); s.speed = (H + s.cred.shape[0]) / s.CRED
    def frame(s, t):
        c = np.zeros((H, W, 3), np.uint8); c[:] = (28, 18, 10)
        for x, y, tile, t0 in s.tiles:
            a = smooth((t - t0) / 0.6)
            if a > 0: c[y:y + tile.shape[0], x:x + tile.shape[1]] = (c[y:y + tile.shape[0], x:x + tile.shape[1]] * (1 - a) + tile * a).astype(np.uint8)
        c = (c * (1 - 0.84 * smooth((t - s.T_TEXT + .2) / 0.8))).astype(np.uint8)
        for capa, ti, to in s.msgs: over(c, capa, smooth((t - ti) / 0.7) * (1 - smooth((t - (to - 0.7)) / 0.7)))
        if t >= s.T_CRED: over(c, s.cred, 1.0, int(H - (t - s.T_CRED) * s.speed))
        return c

rng = random.Random(11); prev = None; escenas = [Title()]
for i, r in enumerate(rows):
    h, w = load(r).shape[:2]
    opts = [e for e in (EFECTOS_V if h > w else EFECTOS_H) if e != prev]
    prev = rng.choice(opts); escenas.append(Photo(r, prev))
escenas.append(Ending())
escenas[1].fade_in = 1.0
starts = [0.0]
for e in escenas[:-1]: starts.append(starts[-1] + e.dur)
total = starts[-1] + escenas[-1].dur

cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if audio:
    a = audio.split(',')
    if len(a) == 2:   # canción 1 hasta que empieza la ronda 5; canción 2 entra con cruce de 3 s y sigue hasta el final
        t7 = next(starts[i] for i, e in enumerate(escenas) if isinstance(e, Photo) and e.r['ronda'] == '5'); X = 3.0
        fc = (f"[1:a]volume=-3.5dB,atrim=0:{t7:.2f},asetpts=PTS-STARTPTS,afade=t=out:st={t7-X:.2f}:d={X}[a0];"
              f"[2:a]atrim=start=14,asetpts=PTS-STARTPTS,dynaudnorm=f=300:g=9:m=6,volume=-5dB,adelay={int((t7-X)*1000)}:all=1,afade=t=in:st={t7-X:.2f}:d={X}[a1];"
              f"[a0][a1]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95,afade=t=out:st={total-4:.2f}:d=4[aout]")
        cmd += ['-i', a[0], '-i', a[1], '-filter_complex', fc, '-map', '0:v', '-map', '[aout]', '-c:a', 'aac', '-b:a', '192k']
    else:
        cmd += ['-i', a[0], '-c:a', 'aac', '-b:a', '192k', '-af', f'afade=t=out:st={total-4}:d=4']
cmd += ['-t', f'{total:.2f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

def scene_at(T):
    i = max(k for k, s0 in enumerate(starts) if s0 <= T); return i, T - starts[i]
for k in range(int(total * FPS)):
    T = k / FPS; i, t = scene_at(T); e = escenas[i]
    cur = e.frame(t)
    if i > 0 and t < e.fade_in:
        a = smooth(t / e.fade_in); cur = cv2.addWeighted(escenas[i - 1].frame(T - starts[i - 1]), 1 - a, cur, a, 0)
    if i >= 2: escenas[i - 2].p = None if isinstance(escenas[i - 2], Photo) else None   # libera memoria
    g = min(1, T / 0.8, (total - T) / 2.0)
    if g < 1: cur = (cur * max(g, 0)).astype(np.uint8)
    ff.stdin.write(cur.tobytes())
ff.stdin.close(); ff.wait()
print(f'{len(rows)} fotos, {total:.1f}s ->', out)
