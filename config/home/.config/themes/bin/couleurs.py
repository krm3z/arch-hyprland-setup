"""Outils de couleur pour le générateur de thèmes (sRGB, Lab, LCh, contraste WCAG).

Toutes les couleurs sont des tuples (r, g, b) en flottants 0‑255.
"""
import math

from PIL import Image


def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(float(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c[:3])


def rgba(c, a):
    """Chaîne CSS rgba(r, g, b, a)."""
    r, g, b = (max(0, min(255, round(v))) for v in c[:3])
    return f"rgba({r}, {g}, {b}, {a:.2f})"


def hypr(c, a=1.0):
    """Couleur au format Hyprland : rgba(rrggbbaa)."""
    return "rgba(" + rgb2hex(c)[1:] + "%02x" % max(0, min(255, round(a * 255))) + ")"


def hexa(c, a=1.0):
    """#rrggbbaa (mako)."""
    return rgb2hex(c) + "%02x" % max(0, min(255, round(a * 255)))


# ---------------------------------------------------------------- conversions
def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _delin(v):
    v = 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055
    return v * 255.0


def rgb2lab(c):
    r, g, b = (_lin(v) for v in c[:3])
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _lab2lin(lab):
    L, a, b = lab
    fy = (L + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200

    def finv(t):
        return t ** 3 if t ** 3 > 0.008856 else (t - 16 / 116) / 7.787

    x, y, z = finv(fx) * 0.95047, finv(fy), finv(fz) * 1.08883
    return (3.2404542 * x - 1.5371385 * y - 0.4985314 * z,
            -0.9692660 * x + 1.8760108 * y + 0.0415560 * z,
            0.0556434 * x - 0.2040259 * y + 1.0572252 * z)


def lab2rgb(lab):
    return tuple(_delin(max(0.0, min(1.0, v))) for v in _lab2lin(lab))


def rgb2lch(c):
    L, a, b = rgb2lab(c)
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def lch2rgb(L, C, H):
    """LCh -> sRGB en réduisant la chroma si la couleur sort du gamut."""
    L = max(0.0, min(100.0, L))
    C = max(0.0, C)
    for _ in range(60):
        lin = _lab2lin((L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))))
        if all(-0.0005 <= v <= 1.0005 for v in lin):
            break
        C *= 0.93
    return tuple(_delin(max(0.0, min(1.0, v))) for v in lin)


# ---------------------------------------------------------------- mesures
def luminance(c):
    r, g, b = (_lin(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(c1, c2):
    a, b = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def melange(c1, c2, t):
    """Mélange linéaire en sRGB ; t = 0 -> c1, t = 1 -> c2."""
    return tuple(a + (b - a) * t for a, b in zip(c1[:3], c2[:3]))


def melange_lab(c1, c2, t):
    l1, l2 = rgb2lab(c1), rgb2lab(c2)
    return lab2rgb(tuple(a + (b - a) * t for a, b in zip(l1, l2)))


def compose(dessus, alpha, dessous):
    """Couleur obtenue en posant `dessus` (opacité alpha) sur `dessous`."""
    return melange(dessous, dessus, alpha)


def avec(c, L=None, C=None, Cmax=None, H=None):
    l, ch, h = rgb2lch(c)
    if L is not None:
        l = L
    if C is not None:
        ch = C
    if Cmax is not None:
        ch = min(ch, Cmax)
    if H is not None:
        h = H
    return lch2rgb(l, ch, h)


def assurer_contraste(c, fond, mini, sens=None):
    """Éclaircit (sens=+1) ou assombrit (sens=-1) c jusqu'à contraste >= mini."""
    if contraste(c, fond) >= mini:
        return c
    L, C, H = rgb2lch(c)
    if sens is None:
        sens = 1 if luminance(fond) < 0.2 else -1
    for _ in range(110):
        L += sens
        if L > 100 or L < 0:
            break
        c2 = lch2rgb(L, C, H)
        if contraste(c2, fond) >= mini:
            return c2
    return (255.0, 255.0, 255.0) if sens > 0 else (0.0, 0.0, 0.0)


def ecart_teinte(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


# ---------------------------------------------------------------- image
def extraire_palette(img, n=40):
    """Couleurs dominantes de l'image : liste [(rgb, proportion)] triée."""
    petit = img.convert("RGB").resize((240, 150), Image.LANCZOS)
    q = petit.quantize(colors=n, method=Image.Quantize.MEDIANCUT, kmeans=4)
    pal = q.getpalette()[: n * 3]
    total = 240 * 150
    res = []
    for compte, idx in sorted(q.getcolors(), reverse=True):
        res.append((tuple(float(v) for v in pal[idx * 3: idx * 3 + 3]), compte / total))
    return res


def plus_proche(indice, palette, poids_L=0.45):
    """Couleur de l'image la plus proche d'une indication (distance Lab pondérée)."""
    li = rgb2lab(indice)
    meilleur, dmin, dbrut = None, 1e9, 1e9
    for c, f in palette:
        if f < 0.002:
            continue
        lc = rgb2lab(c)
        d = math.sqrt((poids_L * (lc[0] - li[0])) ** 2 + (lc[1] - li[1]) ** 2 + (lc[2] - li[2]) ** 2)
        score = d - 2.0 * math.log10(f * 100 + 1)
        if score < dmin:
            dmin, meilleur, dbrut = score, c, d
    return meilleur, dbrut
