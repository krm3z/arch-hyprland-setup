#!/usr/bin/env python3
"""generer.py — fabrique tous les fichiers d'un thème à partir de son theme.toml.

Pour chaque dossier ~/.config/themes/NN-nom/ :
  * recadre le fond d'écran au format de l'écran (gen/fond.jpg) + aperçu (gen/apercu.png)
  * extrait les vraies couleurs de l'image et les oriente vers l'ambiance décrite
    (couleurs.json), en vérifiant que le texte reste lisible (contraste WCAG)
  * écrit les configs : Hyprland (gen/hypr.lua), waybar, wofi, rofi, mako, hyprlock,
    eww (horloge + icônes), Ghostty (~/.config/ghostty/themes/<nom>.conf), kitty.

Usage : generer.py            -> tous les thèmes
        generer.py 03-rochers -> un seul thème
"""
import json
import math
import sys
import tomllib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from couleurs import (assurer_contraste, compose, contraste, ecart_teinte, extraire_palette,  # noqa: E402
                      hex2rgb, hexa, hypr, lch2rgb, luminance, melange, plus_proche,
                      rgb2hex, rgb2lch, rgba)

HOME = Path.home()
RACINE = HOME / ".config/themes"
FONDS = HOME / "Pictures/Fonds-ecran"
GHOSTTY_THEMES = HOME / ".config/ghostty/themes"
ECRAN = (1920, 1200)          # pixels physiques de l'écran
ECHELLE = 1.25                # mise à l'échelle Hyprland
LOGIQUE = (round(ECRAN[0] / ECHELLE), round(ECRAN[1] / ECHELLE))
HAUT_BARRE = 46               # hauteur réservée par waybar (6 + 34 + marge)

GLYPHES = {  # Nerd Fonts (écrits par code pour ne pas être perdus)
    "chrome": chr(0xF02AF), "terminal": chr(0xF018D), "dossier": chr(0xF024B),
    "claude": "✻", "reglages": chr(0xF0493), "clavier": chr(0xF030C),
    "vscode": chr(0xF0A1E), "applis": chr(0xF003B),
}

DEFAUTS = {
    "nom": "Thème", "image": "", "cadrage": [0.5, 0.5], "phrase": "",
    "couleurs": {"mode": "sombre", "fidelite": 0.6},
    "polices": {"titre": "Inter", "titre_graisse": 600, "titre_espacement": 0, "titre_italique": False,
                "ui": "Inter", "terminal": "JetBrainsMono Nerd Font", "terminal_taille": 12,
                "terminal_style": "", "barre_horloge_taille": 14},
    "barre": {"fond": "fond", "teinte": "", "teinte_force": 0.0, "opacite": 0.72, "flou": True, "accent": "accent",
              "texte": "", "bordure": "", "bordure_opacite": 0.10, "contraste_min": 4.5},
    "bordures": {"couleurs": ["accent"], "angle": 45, "taille": 2, "inactive": "", "inactive_opacite": 0.10,
                 "arrondi": 12},
    "fenetres": {"flou_taille": 6, "flou_passes": 3, "ombre": 0.40},
    "animations": {"style": "douce"},
    "fond_ecran": {"transition": "fade", "duree": 1.5, "angle": 30, "position": "center", "fps": 60,
                   "bezier": ".54,0,.34,.99"},
    "terminal": {"opacite": 0.90},
    "horloge": {"ancre": "top left", "x": "5%", "y": "5%", "taille": 110, "couleur": "texte",
                "date_couleur": "", "alignement": "start", "format": "%H:%M", "date": "%A %-d %B",
                "date_majuscules": False, "date_taille": 20, "date_police": "", "date_espacement": 1,
                "secondes": False, "surtitre": "", "sceau": "", "ombre": "auto", "style": ""},
    "icones": {"ancre": "top right", "x": "5%", "y": "30%", "disposition": "ligne", "taille": 54,
               "espacement": 14, "fond": "fond", "fond_opacite": 0.55, "glyphe": "accent",
               "nom_couleur": "texte", "style": ""},
    "verrouillage": {"luminosite": 0.55, "flou": 3, "couleur_texte": "", "phrase_couleur": "accent2"},
}


# ============================================================== chargement
def fusion(base, ajout):
    res = dict(base)
    for k, v in ajout.items():
        res[k] = fusion(res[k], v) if isinstance(v, dict) and isinstance(res.get(k), dict) else v
    return res


def charger(dossier):
    with open(dossier / "theme.toml", "rb") as f:
        t = fusion(DEFAUTS, tomllib.load(f))
    t["id"] = dossier.name
    t["court"] = dossier.name.split("-", 1)[1]
    t["dossier"] = dossier
    return t


def recadrer(img, cadrage):
    """Recadre en 16:10 (taille écran) autour du point de cadrage (x, y entre 0 et 1)."""
    w, h = img.size
    ech = max(ECRAN[0] / w, ECRAN[1] / h)
    nw, nh = math.ceil(w * ech), math.ceil(h * ech)
    img = img.resize((nw, nh), Image.LANCZOS)
    cx, cy = cadrage
    x0 = round((nw - ECRAN[0]) * cx)
    y0 = round((nh - ECRAN[1]) * cy)
    return img.crop((x0, y0, x0 + ECRAN[0], y0 + ECRAN[1]))


# ============================================================== palette
CANON = {1: "#e05561", 2: "#7fbf5a", 3: "#e3b856", 4: "#4a9ff0", 5: "#c162de", 6: "#3fb5c4"}


def construire_palette(t, img):
    c = t["couleurs"]
    pal_img = extraire_palette(img)
    clair = c["mode"] == "clair"
    sens_texte = -1 if clair else 1
    fid = float(c["fidelite"])

    def role(indication):
        """Couleur de l'image la plus proche de l'indication, ajustée en LCh :
        la teinte vient de l'image (si elle reste dans l'ambiance décrite),
        la luminosité et la saturation restent proches de la description."""
        ind = hex2rgb(indication)
        trouve, d = plus_proche(ind, pal_img)
        f = fid if d < 30 else fid * max(0.0, 1 - (d - 30) / 45)
        Lh, Ch, Hh = rgb2lch(ind)
        Lt, Ct, Ht = rgb2lch(trouve)
        dh = ((Ht - Hh + 180) % 360) - 180
        w = 1.0 if abs(dh) < 12 else max(0.0, 1 - (abs(dh) - 12) / 25)
        if Ch < 6:
            w = 0.0
        L = Lh + f * 0.5 * (Lt - Lh)
        C = Ch + f * 0.5 * (Ct - Ch)
        H = (Hh + f * w * dh) % 360
        return lch2rgb(L, C, H), trouve, d

    p, origine = {}, {}
    fond, trouve, d = role(c["fond"])
    origine["fond"] = (rgb2hex(trouve), round(d, 1))
    L, C, H = rgb2lch(fond)
    fond = lch2rgb(min(max(L, 89), 95), min(C, 16), H) if clair else lch2rgb(min(max(L, 5), 13), min(C, 16), H)
    Lf, Cf, Hf = rgb2lch(fond)
    p["fond"] = fond
    p["fond2"] = lch2rgb(Lf - 6 if clair else Lf + 6, min(Cf, 14), Hf)
    p["fond3"] = lch2rgb(Lf - 13 if clair else Lf + 13, min(Cf, 12), Hf)
    if "texte" in c:
        texte, trouve, d = role(c["texte"])
        origine["texte"] = (rgb2hex(trouve), round(d, 1))
    else:
        texte = lch2rgb(18 if clair else 93, min(Cf, 6), Hf)
    p["texte"] = assurer_contraste(texte, fond, 10, sens_texte)
    p["texte2"] = assurer_contraste(melange(p["texte"], fond, 0.38), fond, 4.6, sens_texte)
    for k in ("accent", "accent2", "accent3"):
        col, trouve, d = role(c[k])
        origine[k] = (rgb2hex(trouve), round(d, 1))
        p[k] = col
        p[k + "_lisible"] = assurer_contraste(col, fond, 4.5, sens_texte)
    for k in ("accent", "accent2", "accent3"):
        cands = [fond, p["texte"], (255.0, 255.0, 255.0), (12.0, 12.0, 14.0)]
        p["sur_" + k] = max(cands, key=lambda x: contraste(x, p[k]))

    # ---- 16 couleurs du terminal : teintes classiques, nuancées par l'image
    vives = [(rgb2lch(col), f) for col, f in pal_img]
    term = {}
    for i, hx in CANON.items():
        Lc, Cc, Hc = rgb2lch(hex2rgb(hx))
        cands = [(ch, h, f) for (l, ch, h), f in vives if ch > 18 and ecart_teinte(h, Hc) < 24]
        if cands:
            tot = sum(f for *_, f in cands)
            x = sum(f * math.cos(math.radians(h)) for _, h, f in cands)
            y = sum(f * math.sin(math.radians(h)) for _, h, f in cands)
            hi = math.degrees(math.atan2(y, x)) % 360
            diff = ((hi - Hc + 180) % 360) - 180
            Hn = (Hc + 0.6 * diff) % 360
            Cn = max(38, min(72, 0.5 * sum(ch * f for ch, _, f in cands) / tot + 0.5 * Cc))
        else:
            Hn, Cn = Hc, min(Cc, 58)
        if clair:
            n, b = lch2rgb(46, Cn, Hn), lch2rgb(38, Cn * 0.95, Hn)
            term[i] = assurer_contraste(n, fond, 4.5, -1)
            term[i + 8] = assurer_contraste(b, fond, 5.5, -1)
        else:
            n, b = lch2rgb(68, Cn, Hn), lch2rgb(78, Cn * 0.9, Hn)
            term[i] = assurer_contraste(n, fond, 4.8, 1)
            term[i + 8] = assurer_contraste(b, fond, 6.0, 1)
    if clair:
        term[0] = melange(p["texte"], (0, 0, 0), 0.15)
        term[8] = assurer_contraste(lch2rgb(55, min(Cf, 8), Hf), fond, 3.6, -1)
        term[7] = assurer_contraste(lch2rgb(42, min(Cf, 8), Hf), fond, 5.0, -1)
        term[15] = assurer_contraste(lch2rgb(30, min(Cf, 8), Hf), fond, 7.0, -1)
    else:
        term[0] = lch2rgb(Lf + 10, min(Cf, 10), Hf)
        term[8] = assurer_contraste(lch2rgb(50, min(Cf, 8), Hf), fond, 3.6, 1)
        term[7] = melange(p["texte"], fond, 0.15)
        term[15] = p["texte"]
    p["term"] = term
    p["rouge"], p["vert"], p["jaune"] = term[1], term[2], term[3]
    return p, pal_img, origine


def resoudre(nom, p):
    if isinstance(nom, (list, tuple)):
        return tuple(float(v) for v in nom)
    if nom.startswith("#"):
        return hex2rgb(nom)
    return p[nom]


# ============================================================== lisibilité
def zone_pixels(img_flou, x0, y0, x1, y1, pas=6):
    """Échantillon de pixels (logiques -> physiques) d'une zone de l'écran."""
    W, H = img_flou.size
    px = []
    X0, Y0 = max(0, int(x0 * ECHELLE)), max(0, int(y0 * ECHELLE))
    X1, Y1 = min(W - 1, int(x1 * ECHELLE)), min(H - 1, int(y1 * ECHELLE))
    for y in range(Y0, Y1 + 1, pas):
        for x in range(X0, X1 + 1, pas):
            px.append(tuple(float(v) for v in img_flou.getpixel((x, y))[:3]))
    return px or [(0.0, 0.0, 0.0)]


def pire_contraste(texte, pixels, fond=None, alpha=0.0):
    pire = 99
    for px in pixels:
        dessous = compose(fond, alpha, px) if fond is not None else px
        pire = min(pire, contraste(texte, dessous))
    return pire


def regler_barre(t, p, img, rapport):
    b = t["barre"]
    bf = resoudre(b["fond"], p)
    if b["teinte"]:
        bf = melange(bf, resoudre(b["teinte"], p), float(b["teinte_force"]))
    alpha = float(b["opacite"])
    img_flou = img.filter(ImageFilter.GaussianBlur(22 if b["flou"] else 3))
    W = LOGIQUE[0]
    zones = [(10, 6, 0.24 * W, 40), (0.41 * W, 6, 0.59 * W, 40), (0.58 * W, 6, W - 10, 40)]
    pixels = sum((zone_pixels(img_flou, *z) for z in zones), [])
    if b["texte"]:
        candidats = [resoudre(b["texte"], p)]
    else:
        candidats = [p["texte"], p["fond"], (250.0, 250.0, 250.0), (18.0, 18.0, 20.0)]
    mini = float(b["contraste_min"])
    while True:
        meilleur = max(candidats, key=lambda c: pire_contraste(c, pixels, bf, alpha))
        score = pire_contraste(meilleur, pixels, bf, alpha)
        if score >= mini or alpha >= 0.96:
            break
        alpha = round(alpha + 0.04, 2)
    moyen = tuple(sum(c[i] for c in pixels) / len(pixels) for i in range(3))
    eff = compose(bf, alpha, moyen)
    sombre = luminance(eff) < 0.25
    texte = meilleur
    texte2 = assurer_contraste(melange(texte, eff, 0.32), eff, 4.0, 1 if luminance(eff) < 0.25 else -1)
    brut = resoudre(b["accent"], p)
    acc = assurer_contraste(brut, eff, 3.2, 1 if sombre else -1)
    sur = max([p["fond"], p["texte"], (255.0, 255.0, 255.0), (12.0, 12.0, 14.0)], key=lambda x: contraste(x, brut))
    rapport.append(f"  barre : fond {rgb2hex(bf)} opacité {alpha:.2f} (demandée {b['opacite']}), "
                   f"texte {rgb2hex(texte)}, pire contraste {score:.1f}")
    bord = resoudre(b["bordure"], p) if b["bordure"] else texte
    return {"fond": bf, "alpha": alpha, "texte": texte, "texte2": texte2, "accent": acc, "brut": brut, "sur": sur,
            "bordure": rgba(bord, float(b["bordure_opacite"])), "effectif": eff, "sombre": sombre}


def verifier_horloge(t, p, img, rapport):
    """Mesure le contraste de l'horloge avec l'image derrière elle et choisit l'ombre."""
    h = t["horloge"]
    W, H = LOGIQUE
    larg = len(h["format"].replace("%", "")) * 0.62 * h["taille"] * (1.4 if h["secondes"] else 1)
    haut = h["taille"] * 1.25 + h["date_taille"] * 1.6

    def pos(v, total):
        return float(v.rstrip("%")) / 100 * total if v.endswith("%") else float(v.replace("px", ""))

    x, y = pos(h["x"], W), pos(h["y"], H)
    anc = h["ancre"]
    if "right" in anc:
        x0 = W - x - larg
    elif "center" in anc and "left" not in anc:
        x0 = (W - larg) / 2 + x
    else:
        x0 = x
    if "bottom" in anc:
        y0 = H - y - haut
    else:
        y0 = y + HAUT_BARRE
    img_flou = img.filter(ImageFilter.GaussianBlur(4))
    px = zone_pixels(img_flou, x0, y0, x0 + larg, y0 + haut, pas=8)
    coul = resoudre(h["couleur"], p)
    pire = pire_contraste(coul, px)
    moy = sorted(contraste(coul, c) for c in px)[len(px) // 2]
    rapport.append(f"  horloge : zone ~({x0:.0f},{y0:.0f})-({x0 + larg:.0f},{y0 + haut:.0f}) "
                   f"contraste médian {moy:.1f}, pire {pire:.1f}")
    return moy, pire


# ============================================================== Hyprland
COURBES = {
    "douce": [("doux", (0.25, 0.1, 0.25, 1.0)), ("douxSortie", (0.42, 0.0, 0.58, 1.0))],
    "glissement": [("sable", (0.3, 0.0, 0.1, 1.0)), ("sableSortie", (0.5, 0.0, 0.75, 0.6))],
    "moyenne": [("poussiere", (0.2, 0.8, 0.3, 1.0)), ("poussiereSortie", (0.45, 0.0, 0.7, 0.4))],
    "feuilles": [("feuille", (0.45, 0.05, 0.25, 1.0)), ("chute", (0.55, 0.0, 0.85, 0.35))],
    "nette": [("givre", (0.16, 1.0, 0.3, 1.0)), ("givreSortie", (0.7, 0.0, 0.84, 0.0))],
    "nerveuse": [("nitro", (0.05, 0.9, 0.1, 1.08)), ("freinage", (0.6, 0.0, 0.9, 0.4))],
    "eclair": [("dragster", (0.0, 0.75, 0.1, 1.0)), ("dragsterSortie", (0.7, 0.0, 1.0, 0.5))],
    "sobre": [("precision", (0.65, 0.0, 0.35, 1.0)), ("precisionSortie", (0.65, 0.0, 0.35, 1.0))],
    "energique": [("rebond", (0.34, 1.4, 0.64, 1.0)), ("elan", (0.36, 0.0, 0.66, -0.4))],
}
RESSORTS = {"energique": ("ressort", 1, 320, 17)}
# feuille -> (vitesse, courbe, style)   vitesse en dixièmes de seconde
PRESETS = {
    "douce": {"global": (8, "doux"), "border": (10, "doux"), "windows": (5, "doux"),
              "windowsIn": (5, "doux", "popin 90%"), "windowsOut": (4, "douxSortie", "popin 90%"),
              "windowsMove": (5, "doux"), "fade": (4.5, "doux"), "layers": (4, "doux", "fade"),
              "layersOut": (3, "douxSortie", "fade"), "workspaces": (6, "doux", "slidefade 15%"),
              "specialWorkspace": (5, "doux", "slidefadevert 20%")},
    "glissement": {"global": (9, "sable"), "border": (12, "sable"), "windows": (8, "sable"),
                   "windowsIn": (8, "sable", "slide"), "windowsOut": (6, "sableSortie", "slide"),
                   "windowsMove": (7, "sable"), "fade": (6, "sable"), "layers": (5, "sable", "fade"),
                   "layersOut": (4, "sableSortie", "fade"), "workspaces": (9, "sable", "slide"),
                   "specialWorkspace": (8, "sable", "slidevert")},
    "moyenne": {"global": (6, "poussiere"), "border": (6, "poussiere"), "windows": (4.5, "poussiere"),
                "windowsIn": (4.5, "poussiere", "popin 85%"), "windowsOut": (3.5, "poussiereSortie", "popin 85%"),
                "windowsMove": (4.5, "poussiere"), "fade": (4, "poussiere"), "layers": (3.5, "poussiere", "fade"),
                "layersOut": (3, "poussiereSortie", "fade"), "workspaces": (5, "poussiere", "slidefade 25%"),
                "specialWorkspace": (4.5, "poussiere", "slidefadevert 20%")},
    "feuilles": {"global": (10, "feuille"), "border": (14, "feuille"), "windows": (9, "feuille"),
                 "windowsIn": (9, "feuille", "slide top"), "windowsOut": (7, "chute", "slide bottom"),
                 "windowsMove": (8, "feuille"), "fade": (8, "feuille"), "layers": (6, "feuille", "fade"),
                 "layersOut": (5, "chute", "fade"), "workspaces": (10, "feuille", "slidefadevert 25%"),
                 "specialWorkspace": (9, "feuille", "slidefadevert 30%")},
    "nette": {"global": (5, "givre"), "border": (5, "givre"), "windows": (4, "givre"),
              "windowsIn": (4, "givre", "popin 94%"), "windowsOut": (2.5, "givreSortie", "popin 94%"),
              "windowsMove": (4, "givre"), "fade": (3, "givre"), "layers": (3, "givre", "fade"),
              "layersOut": (2.2, "givreSortie", "fade"), "workspaces": (4.5, "givre", "slidefade 8%"),
              "specialWorkspace": (4, "givre", "slidefadevert 12%")},
    "nerveuse": {"global": (3, "nitro"), "border": (3, "nitro"), "windows": (2.6, "nitro"),
                 "windowsIn": (2.6, "nitro", "slide left"), "windowsOut": (1.8, "freinage", "slide right"),
                 "windowsMove": (2.4, "nitro"), "fade": (2, "nitro"), "layers": (2, "nitro", "fade"),
                 "layersOut": (1.5, "freinage", "fade"), "workspaces": (2.6, "nitro", "slide"),
                 "specialWorkspace": (2.4, "nitro", "slidevert")},
    "eclair": {"global": (2, "dragster"), "border": (2, "dragster"), "windows": (1.6, "dragster"),
               "windowsIn": (1.5, "dragster", "popin 95%"), "windowsOut": (1.1, "dragsterSortie", "popin 95%"),
               "windowsMove": (1.5, "dragster"), "fade": (1.2, "dragster"), "layers": (1.2, "dragster", "fade"),
               "layersOut": (1.0, "dragsterSortie", "fade"), "workspaces": (1.8, "dragster", "slide"),
               "specialWorkspace": (1.6, "dragster", "slidevert")},
    "sobre": {"global": (5, "precision"), "border": (6, "precision"), "windows": (4, "precision"),
              "windowsIn": (4, "precision", "popin 97%"), "windowsOut": (3, "precisionSortie", "popin 97%"),
              "windowsMove": (4, "precision"), "fade": (3.5, "precision"), "layers": (3, "precision", "fade"),
              "layersOut": (2.5, "precision", "fade"), "workspaces": (5, "precision", "fade"),
              "specialWorkspace": (4, "precision", "fade")},
    "energique": {"global": (4, "rebond"), "border": (4, "rebond"), "windows": (3.5, "@ressort"),
                  "windowsIn": (3.5, "@ressort", "popin 70%"), "windowsOut": (2, "elan", "popin 75%"),
                  "windowsMove": (3, "@ressort"), "fade": (2.5, "rebond"), "layers": (2.5, "rebond", "fade"),
                  "layersOut": (1.8, "elan", "fade"), "workspaces": (3, "rebond", "slide"),
                  "specialWorkspace": (3, "rebond", "slidevert")},
}
ENFANTS = {  # pour que chaque thème écrase aussi les sous-animations
    "windows": [], "fade": ["fadeIn", "fadeOut", "fadeSwitch", "fadeShadow", "fadeDim"],
    "layers": ["layersIn"], "layersOut": ["fadeLayersOut"], "workspaces": ["workspacesIn", "workspacesOut"],
}


def lua_hypr(t, p, barre):
    b = t["bordures"]
    cols = [resoudre(c, p) for c in b["couleurs"]]
    if len(cols) == 1:
        actif = f'"{hypr(cols[0])}"'
    else:
        liste = ", ".join(f'"{hypr(c)}"' for c in cols)
        actif = f'{{ colors = {{ {liste} }}, angle = {b["angle"]} }}'
    inact = resoudre(b["inactive"], p) if b["inactive"] else p["texte"]
    inactif = hypr(inact, float(b["inactive_opacite"]))
    f = t["fenetres"]
    style = t["animations"]["style"]
    variante = t["animations"].get("variante", {})
    L = [f'-- Thème « {t["nom"]} » — généré par ~/.config/themes/bin/generer.py',
         f'-- (modifier ~/.config/themes/{t["id"]}/theme.toml puis lancer : theme regenerer)',
         "hl.config({",
         "    general = {",
         f'        border_size = {b["taille"]},',
         f"        col = {{ active_border = {actif}, inactive_border = \"{inactif}\" }},",
         "    },",
         "    decoration = {",
         f'        rounding = {b["arrondi"]},',
         f'        shadow = {{ enabled = true, range = 20, render_power = 3, color = "{hypr((0, 0, 0), f["ombre"])}" }},',
         f'        blur = {{ enabled = true, size = {f["flou_taille"]}, passes = {f["flou_passes"]}, vibrancy = 0.17, popups = true }},',
         "    },",
         "})", ""]
    for nom, (x1, y1, x2, y2) in COURBES[style]:
        L.append(f'hl.curve("{nom}", {{ type = "bezier", points = {{ {{{x1}, {y1}}}, {{{x2}, {y2}}} }} }})')
    if style in RESSORTS:
        n, m, s, d = RESSORTS[style]
        L.append(f'hl.curve("{n}", {{ type = "spring", mass = {m}, stiffness = {s}, damping = {d} }})')
    L.append("")
    anims = dict(PRESETS[style])
    anims.update({k: tuple(v) for k, v in variante.items()})
    for feuille, val in anims.items():
        for f2 in [feuille] + ENFANTS.get(feuille, []):
            vit, courbe = val[0], val[1]
            sty = val[2] if len(val) > 2 else None
            if f2 in ("fadeIn", "fadeOut", "fadeSwitch", "fadeShadow", "fadeDim", "fadeLayersOut"):
                sty = None
            c = f'spring = "{courbe[1:]}"' if courbe.startswith("@") else f'bezier = "{courbe}"'
            s = f', style = "{sty}"' if sty else ""
            L.append(f'hl.animation({{ leaf = "{f2}", enabled = true, speed = {vit}, {c}{s} }})')
    L.append("")
    if t["barre"]["flou"]:
        L.append('hl.layer_rule({ name = "theme-barre", match = { namespace = "^waybar$" }, blur = true, ignore_alpha = 0.05 })')
    L.append('hl.layer_rule({ name = "theme-icones", match = { namespace = "^eww-icones$" }, blur = true, ignore_alpha = 0.2 })')
    return "\n".join(L) + "\n"


# ============================================================== waybar
def css_waybar(t, p, b):
    po = t["polices"]
    bg = rgba(b["fond"], b["alpha"])
    italique = "italic" if po["titre_italique"] else "normal"
    return f"""/* Waybar — thème « {t['nom']} » (généré : la forme reste identique pour tous les thèmes) */
* {{ font-family: "{po['ui']}", "JetBrainsMono Nerd Font", sans-serif; font-size: 13px; font-weight: 600;
     border: none; border-radius: 0; min-height: 0; }}
window#waybar {{ background: transparent; color: {rgb2hex(b['texte'])}; }}
tooltip {{ background: {rgba(p['fond'], 0.96)}; border: 1px solid {rgba(p['accent'], 0.45)}; border-radius: 10px; }}
tooltip label {{ color: {rgb2hex(p['texte'])}; padding: 2px 4px; font-weight: 500; }}

.modules-left, .modules-center, .modules-right {{ background: transparent; }}

/* Pastilles arrondies */
#custom-claude, #workspaces, #clock, #systeme, #controles, #session {{
  background: {bg};
  border: 1px solid {b['bordure']};
  border-radius: 14px;
  padding: 0 6px;
  margin: 0 3px;
}}

#custom-claude {{ padding: 0 12px; color: {rgb2hex(b['texte'])}; }}
#custom-claude.actif {{ color: {rgb2hex(b['texte'])}; }}
#custom-claude.inactif {{ color: {rgb2hex(b['texte2'])}; }}
#custom-claude:hover {{ background: {rgba(b['brut'], 0.9)}; color: {rgb2hex(b['sur'])}; }}

#workspaces {{ padding: 0 4px; }}
#workspaces button {{ padding: 0 7px; margin: 4px 1px; min-width: 14px; border-radius: 10px;
  color: {rgb2hex(b['texte'])}; background: transparent; box-shadow: none; transition: all 0.2s ease; }}
#workspaces button.empty {{ color: {rgba(b['texte'], 0.72)}; }}
#workspaces button.active {{ background: {rgb2hex(b['brut'])}; color: {rgb2hex(b['sur'])}; }}
#workspaces button:hover {{ background: {rgba(b['texte'], 0.14)}; color: {rgb2hex(b['texte'])}; }}
#workspaces button.active:hover {{ background: {rgb2hex(b['brut'])}; color: {rgb2hex(b['sur'])}; }}
#workspaces button.urgent {{ background: {rgb2hex(p['rouge'])}; color: #ffffff; }}

#clock {{ padding: 0 16px; font-family: "{po['titre']}", "{po['ui']}"; font-size: {po['barre_horloge_taille']}px;
  font-weight: {max(500, po['titre_graisse'])}; font-style: {italique}; letter-spacing: {max(0, po['titre_espacement']) / 4:.1f}px; }}

#cpu, #memory, #temperature, #pulseaudio, #network, #bluetooth, #backlight, #battery,
#custom-notif, #custom-alim {{ padding: 0 8px; font-family: "JetBrainsMono Nerd Font", "{po['ui']}"; }}
#cpu, #memory, #temperature {{ color: {rgb2hex(b['texte'])}; }}
#temperature.critical {{ color: {rgb2hex(p['rouge'])}; }}
#bluetooth.off, #bluetooth.disabled, #network.disconnected, #network.disabled, #pulseaudio.muted {{ color: {rgb2hex(b['texte2'])}; }}
#battery.charging, #battery.plugged {{ color: {rgb2hex(assurer_contraste(p['vert'], b['effectif'], 3, 1 if b['sombre'] else -1))}; }}
#battery.warning:not(.charging) {{ color: {rgb2hex(assurer_contraste(p['jaune'], b['effectif'], 3, 1 if b['sombre'] else -1))}; }}
#battery.critical:not(.charging) {{ color: {rgb2hex(p['rouge'])}; animation: clignote 1s steps(2) infinite; }}
@keyframes clignote {{ to {{ color: {rgb2hex(b['texte'])}; }} }}
#custom-notif.notification {{ color: {rgb2hex(b['accent'])}; }}
#custom-notif.dnd {{ color: {rgb2hex(b['texte2'])}; }}
#custom-alim {{ color: {rgb2hex(b['accent'])}; padding-right: 12px; }}
#custom-alim:hover, #custom-notif:hover {{ color: {rgb2hex(b['texte'])}; }}
"""


# ============================================================== wofi / rofi
def css_wofi(t, p):
    po = t["polices"]
    clair = t["couleurs"]["mode"] == "clair"
    return f"""/* wofi — thème « {t['nom']} » (généré) */
* {{ font-family: "{po['ui']}", "JetBrainsMono Nerd Font", sans-serif; font-size: 14px; }}
window {{ background-color: {rgba(p['fond'], 0.93)}; border: 2px solid {rgb2hex(p['accent'])}; border-radius: 18px; }}
#outer-box {{ padding: 14px; }}
#input {{ background-color: {rgb2hex(p['fond2'])}; color: {rgb2hex(p['texte'])}; border: 1px solid {rgba(p['texte'], 0.08)};
  border-radius: 12px; padding: 10px 14px; margin-bottom: 10px; font-family: "{po['titre']}", "{po['ui']}"; font-size: 16px; }}
#input:focus {{ border-color: {rgb2hex(p['accent'])}; box-shadow: none; }}
#input image {{ color: {rgb2hex(p['accent_lisible'])}; }}
#scroll {{ margin: 0; }}
#inner-box {{ background: transparent; }}
#entry {{ padding: 8px 12px; border-radius: 12px; background: transparent; }}
#entry:selected {{ background-color: {rgba(p['accent'], 0.85 if not clair else 0.9)}; outline: none; }}
#entry:selected #text {{ color: {rgb2hex(p['sur_accent'])}; font-weight: 600; }}
#text {{ color: {rgb2hex(p['texte'])}; margin-left: 6px; }}
#img {{ margin-right: 6px; }}
"""


def css_grille(t, p):
    """nwg-drawer : grille « Toutes les applications » (Windows + A, icône du bureau)."""
    po = t["polices"]
    clair = t["couleurs"]["mode"] == "clair"
    tx, tx2, ac = rgb2hex(p['texte']), rgb2hex(p['texte2']), rgb2hex(p['accent'])
    return f"""/* nwg-drawer — thème « {t['nom']} » (généré par ~/.config/themes/bin/generer.py) */
* {{ font-family: "{po['ui']}", "JetBrainsMono Nerd Font", sans-serif; }}
window {{ background-color: {rgba(p['fond'], 0.90 if not clair else 0.93)}; color: {tx}; }}
entry {{ background-color: {rgb2hex(p['fond2'])}; color: {tx}; caret-color: {ac};
  border: 1px solid {rgba(p['texte'], 0.10)}; border-radius: 14px; box-shadow: none;
  padding: 8px 16px; margin-top: 34px; margin-bottom: 8px; min-width: 460px;
  font-family: "{po['titre']}", "{po['ui']}"; font-size: 17px; }}
entry:focus {{ border-color: {ac}; }}
entry image {{ color: {rgb2hex(p['accent_lisible'])}; }}
entry selection {{ background-color: {rgba(p['accent'], 0.5)}; }}
button, image {{ background: none; border: none; box-shadow: none; }}
button {{ color: {tx}; border-radius: 16px; padding: 8px; transition: all 150ms ease; }}
button label {{ color: {tx}; font-size: 13px; }}
button:hover, button:focus {{ background-color: {rgba(p['accent'], 0.22 if not clair else 0.28)}; outline: none; }}
button:hover label, button:focus label {{ color: {rgb2hex(p['accent_lisible'] if not clair else p['texte'])}; }}
button:active {{ background-color: {rgba(p['accent'], 0.45)}; }}
#category-button {{ margin: 0 5px; padding: 5px 16px; border-radius: 999px; background-color: {rgba(p['fond3'], 0.55)};
  color: {tx2}; font-weight: 600; }}
#category-button label {{ color: {tx2}; }}
#category-button:hover, #category-button:focus {{ background-color: {ac}; }}
#category-button:hover label, #category-button:focus label {{ color: {rgb2hex(p['sur_accent'])}; }}
#pinned-box {{ padding-bottom: 8px; border-bottom: 1px solid {rgba(p['accent'], 0.35)}; }}
#files-box {{ padding: 6px; border: 1px solid {rgba(p['accent'], 0.35)}; border-radius: 15px; }}
#math-label {{ font-weight: bold; font-size: 16px; color: {rgb2hex(p['accent_lisible'])}; }}
scrollbar, scrollbar trough {{ background: none; border: none; }}
scrollbar slider {{ background-color: {rgba(p['accent'], 0.45)}; border-radius: 8px; min-width: 6px; border: none; }}
tooltip {{ background-color: {rgba(p['fond'], 0.95)}; color: {tx}; border-radius: 8px; border: 1px solid {rgba(p['accent'], 0.5)}; }}
tooltip label {{ color: {tx}; }}
"""


def rasi_rofi(t, p):
    po = t["polices"]
    return f"""/* rofi — couleurs du thème « {t['nom']} » (généré) */
* {{
  bg:      {rgba(p['fond'], 0.93)};
  bg-alt:  {rgba(p['fond3'], 0.55)};
  sel:     {rgba(p['accent'], 0.85)};
  sel-fg:  {rgb2hex(p['sur_accent'])};
  fg:      {rgb2hex(p['texte'])};
  muted:   {rgb2hex(p['texte2'])};
  accent:  {rgb2hex(p['accent_lisible'])};
  bordure: {rgb2hex(p['accent'])};
  font:    "{po['ui']} 11";
}}
"""


# ============================================================== mako
def conf_mako(t, p):
    po = t["polices"]
    italique = ' style="italic"' if po["titre_italique"] else ""
    return f"""# mako — thème « {t['nom']} » (généré)
font={po['ui']} 11
background-color={hexa(p['fond'], 0.94)}
text-color={rgb2hex(p['texte'])}
border-color={rgb2hex(p['accent'])}
progress-color=over {hexa(p['accent'], 0.35)}
border-size=2
border-radius=14
padding=14,16
margin=10
outer-margin=4,6,0,0
width=380
height=180
icon-location=left
max-icon-size=56
anchor=top-right
layer=overlay
default-timeout=6000
max-history=50
markup=1
format=<span font_family="{po['titre']}" weight="{po['titre_graisse']}"{italique} size="large" foreground="{rgb2hex(p['accent_lisible'])}">%s</span>\\n%b

[urgency=low]
border-color={rgb2hex(p['fond3'])}

[urgency=critical]
border-color={rgb2hex(p['rouge'])}
default-timeout=0

[app-name=Thèmes]
border-size=3
default-timeout=3500
max-icon-size=80

[mode=do-not-disturb]
invisible=1
"""


# ============================================================== hyprlock
def conf_hyprlock(t, p):
    po = t["polices"]
    v = t["verrouillage"]
    clair = t["couleurs"]["mode"] == "clair"
    txt = resoudre(v["couleur_texte"], p) if v["couleur_texte"] else ((25, 25, 40) if clair else (250, 250, 250))
    phr = resoudre(v["phrase_couleur"], p)
    # la phrase doit rester lisible sur le fond flouté
    phr = assurer_contraste(phr, p["fond"] if not clair else p["fond"], 4.5, -1 if clair else 1)
    sec = melange(txt, p["fond"], 0.12 if clair else 0.25)
    cols = [resoudre(c, p) for c in t["bordures"]["couleurs"]]
    contour = " ".join(hypr(c) for c in cols) + (" 45deg" if len(cols) > 1 else "")
    graisse = "Bold" if po["titre_graisse"] >= 650 else ("Light" if po["titre_graisse"] <= 300 else "")
    police = f'{po["titre"]} {graisse}'.strip()
    phrase = t["phrase"].replace("&", "&amp;")
    ital = "<i>" if po["titre_italique"] else ""
    itf = "</i>" if po["titre_italique"] else ""
    return f"""# Écran de verrouillage — thème « {t['nom']} » (généré)
general {{
    hide_cursor = true
    ignore_empty_input = true
}}
auth {{
    fingerprint:enabled = false
}}
background {{
    monitor =
    path = {t['dossier']}/gen/fond.jpg
    blur_passes = {v['flou']}
    blur_size = 8
    brightness = {v['luminosite']}
    contrast = 0.95
    vibrancy = 0.18
}}
label {{
    monitor =
    text = <span letter_spacing="{int(po['titre_espacement']) * 1024}">{ital}$TIME{itf}</span>
    font_size = 104
    font_family = {police}
    color = {hypr(txt)}
    shadow_passes = 2
    shadow_size = 6
    shadow_color = {hypr((0, 0, 0) if not clair else (255, 255, 255), 0.35)}
    position = 0, 210
    halign = center
    valign = center
}}
label {{
    monitor =
    text = cmd[update:60000] LC_ALL=fr_FR.UTF-8 date +"%A %-d %B"
    font_size = 20
    font_family = {po['ui']}
    color = {hypr(sec)}
    position = 0, 112
    halign = center
    valign = center
}}
label {{
    monitor =
    text = {ital}{phrase}{itf}
    font_size = 26
    font_family = {police}
    color = {hypr(phr)}
    shadow_passes = 2
    shadow_size = 5
    shadow_color = {hypr((0, 0, 0) if not clair else (255, 255, 255), 0.4)}
    position = 0, 50
    halign = center
    valign = center
}}
input-field {{
    monitor =
    size = 320, 54
    outline_thickness = 2
    rounding = 27
    dots_size = 0.22
    dots_spacing = 0.3
    inner_color = {hypr(p['fond'], 0.62)}
    outer_color = {contour}
    check_color = {hypr(p['accent2'])}
    fail_color = {hypr(p['rouge'])}
    font_color = {hypr(p['texte'])}
    font_family = {po['ui']}
    placeholder_text = <span foreground="##{rgb2hex(p['texte2'])[1:]}">Mot de passe…</span>
    fail_text = Mot de passe incorrect
    capslock_color = {hypr(p['jaune'])}
    fade_on_empty = false
    position = 0, -40
    halign = center
    valign = center
}}
label {{
    monitor =
    text = $USER
    font_size = 13
    font_family = {po['ui']}
    color = {hypr(sec)}
    position = 0, -100
    halign = center
    valign = center
}}
"""


# ============================================================== terminaux
def conf_ghostty(t, p):
    po = t["polices"]
    term = p["term"]
    L = [f"# Ghostty — thème « {t['nom']} » (généré par ~/.config/themes/bin/generer.py)",
         f"# Couleurs tirées de {t['image']}, police et transparence propres au thème.",
         f'font-family = "{po["terminal"]}"',
         f"font-size = {po['terminal_taille']}"]
    if po["terminal_style"]:
        L.append(f'font-style = "{po["terminal_style"]}"')
    L += [f"background-opacity = {t['terminal']['opacite']}",
          f"background = {rgb2hex(p['fond'])}",
          f"foreground = {rgb2hex(p['texte'])}",
          f"cursor-color = {rgb2hex(p['accent_lisible'])}",
          f"cursor-text = {rgb2hex(p['fond'])}",
          f"selection-background = {rgb2hex(p['accent'])}",
          f"selection-foreground = {rgb2hex(p['sur_accent'])}"]
    L += [f"palette = {i}={rgb2hex(term[i])}" for i in range(16)]
    return "\n".join(L) + "\n"


def conf_kitty(t, p):
    po = t["polices"]
    term = p["term"]
    L = [f"# kitty (secours) — thème « {t['nom']} » (généré)",
         f"font_family {po['terminal']}", f"font_size {po['terminal_taille'] - 1}",
         f"background_opacity {t['terminal']['opacite']}",
         f"foreground {rgb2hex(p['texte'])}", f"background {rgb2hex(p['fond'])}",
         f"selection_foreground {rgb2hex(p['sur_accent'])}", f"selection_background {rgb2hex(p['accent'])}",
         f"cursor {rgb2hex(p['accent_lisible'])}", f"url_color {rgb2hex(p['accent2_lisible'])}",
         f"active_tab_background {rgb2hex(p['accent'])}", f"active_tab_foreground {rgb2hex(p['sur_accent'])}",
         f"inactive_tab_background {rgb2hex(p['fond2'])}", f"inactive_tab_foreground {rgb2hex(p['texte2'])}"]
    L += [f"color{i} {rgb2hex(term[i])}" for i in range(16)]
    return "\n".join(L) + "\n"


# ============================================================== eww
def eww_yuck(t, p):
    h, ic = t["horloge"], t["icones"]
    al = h["alignement"]
    date_cmd = f"LC_ALL=fr_FR.UTF-8 date '+{h['date']}'"
    if h["date_majuscules"]:
        date_cmd += " | LC_ALL=fr_FR.UTF-8 awk '{print toupper($0)}'"
    sec_poll = '(defpoll secondes :interval "1s" :initial "00" `date +%S`)\n' if h["secondes"] else ""
    sec_lbl = '(label :class "secondes" :show-truncated false :valign "end" :text ":${secondes}")' if h["secondes"] else ""
    surtitre = f'(label :class "surtitre" :show-truncated false :halign "{al}" :text "{h["surtitre"]}")' if h["surtitre"] else ""
    sceau = f'(label :class "sceau" :show-truncated false :valign "center" :text "{h["sceau"]}")' if h["sceau"] else ""
    col = ic["disposition"] == "colonne"
    o = "v" if col else "h"
    o_item = "h" if col else "v"
    G = GLYPHES
    # Exactement 6 éléments, dans cet ordre (le reste est dans la grille « Applications »)
    items = [(G["claude"], "Claude", "Claude Desktop", "setsid -f claude-desktop >/dev/null 2>&1"),
             (G["vscode"], "VS Code", "Visual Studio Code", "setsid -f code >/dev/null 2>&1"),
             (G["chrome"], "Chrome", "Google Chrome", "setsid -f google-chrome-stable >/dev/null 2>&1"),
             (G["terminal"], "Terminal", "Terminal (Ghostty)", "setsid -f ghostty >/dev/null 2>&1"),
             (G["clavier"], "Raccourcis", "Fiche des raccourcis (Windows + F2)", "setsid -f raccourcis >/dev/null 2>&1"),
             (G["applis"], "Applications", "Toutes les applications (Windows + A)",
              "setsid -f grille-applis >/dev/null 2>&1")]
    icones = "\n    ".join(f'(icone :glyphe "{g}" :nom "{n}" :bulle "{b}" :cmd "{c}")' for g, n, b, c in items)
    return f""";; eww — thème « {t['nom']} » (généré par ~/.config/themes/bin/generer.py)
;; Positions : voir [horloge] et [icones] dans ~/.config/themes/{t['id']}/theme.toml

(defpoll heure :interval "1s" :initial "--:--" `date +{h['format']}`)
{sec_poll}(defpoll ladate :interval "30s" :initial "" `{date_cmd}`)

(defwidget horloge []
  (box :class "horloge" :orientation "v" :space-evenly false :halign "{al}"
    {surtitre}
    (box :orientation "h" :space-evenly false :halign "{al}" :spacing 14
      {sceau}
      (label :class "heure" :show-truncated false :text heure)
      {sec_lbl})
    (label :class "date" :show-truncated false :halign "{al}" :text ladate)))

(defwidget icone [glyphe nom bulle cmd]
  (eventbox :cursor "pointer"
    (button :class "icone" :tooltip bulle :onclick cmd
      (box :class "contenu" :orientation "{o_item}" :space-evenly false :spacing {8 if col else 6}
        (label :class "tuile" :show-truncated false :text glyphe)
        (label :class "nom" :show-truncated false :halign "{'start' if col else 'center'}" :text nom)))))

(defwidget icones []
  (box :class "icones" :orientation "{o}" :space-evenly false :spacing {ic['espacement']}
    {icones}))

(defwindow horloge
  :monitor 0
  :geometry (geometry :x "{h['x']}" :y "{h['y']}" :anchor "{h['ancre']}")
  :stacking "bottom"
  :exclusive false
  :focusable false
  :namespace "eww-horloge"
  (horloge))

(defwindow icones
  :monitor 0
  :geometry (geometry :x "{ic['x']}" :y "{ic['y']}" :anchor "{ic['ancre']}")
  :stacking "bottom"
  :exclusive false
  :focusable false
  :namespace "eww-icones"
  (icones))
"""


def eww_scss(t, p, ombre_forte):
    po, h, ic = t["polices"], t["horloge"], t["icones"]
    clair = t["couleurs"]["mode"] == "clair"
    coul = resoudre(h["couleur"], p)
    dcoul = resoudre(h["date_couleur"], p) if h["date_couleur"] else coul
    sombre_txt = luminance(coul) < 0.3
    base = (255, 255, 255) if sombre_txt else (0, 0, 0)
    if h["ombre"] == "aucune":
        ombre = "none"
    elif h["ombre"] == "forte" or (ombre_forte and h["ombre"] == "auto"):
        ombre = (f"0 0 2px {rgba(base, 0.75)}, 0 1px 1px {rgba(base, 0.6)}, "
                 f"0 2px 10px {rgba(base, 0.55)}, 0 3px 18px {rgba(base, 0.45)}")
    else:
        ombre = f"0 2px 14px {rgba(base, 0.35)}"
    t_ = ic["taille"]
    tuile_fond = rgba(resoudre(ic["fond"], p), ic["fond_opacite"])
    glyphe = resoudre(ic["glyphe"], p)
    nomc = resoudre(ic["nom_couleur"], p)
    nom_ombre_base = (255, 255, 255) if luminance(nomc) < 0.3 else (0, 0, 0)
    italique = "italic" if po["titre_italique"] else "normal"
    date_police = h["date_police"] or po["titre"]
    return f"""// eww — thème « {t['nom']} » (généré)
* {{ all: unset; }}
tooltip {{ background-color: {rgba(p['fond'], 0.95)}; color: {rgb2hex(p['texte'])}; border-radius: 8px;
  border: 1px solid {rgba(p['accent'], 0.5)}; padding: 6px 10px; font-family: "{po['ui']}"; font-size: 12px; }}

.horloge {{ padding: 26px 30px; }}  // marge : l'ombre du texte n'est pas rognee
.icones {{ padding: 14px; }}
.heure {{ font-family: "{po['titre']}"; font-size: {h['taille']}px; font-weight: {po['titre_graisse']};
  font-style: {italique}; letter-spacing: {po['titre_espacement']}px; color: {rgb2hex(coul)}; text-shadow: {ombre}; }}
.secondes {{ font-family: "{po['titre']}"; font-size: {int(h['taille'] * 0.42)}px; font-weight: {po['titre_graisse']};
  font-style: {italique}; color: {rgb2hex(p['accent2_lisible'])}; text-shadow: {ombre}; margin-bottom: {int(h['taille'] * 0.16)}px; }}
.date {{ font-family: "{date_police}"; font-size: {h['date_taille']}px; font-weight: {min(po['titre_graisse'], 600)};
  font-style: {italique}; letter-spacing: {h['date_espacement']}px; color: {rgb2hex(dcoul)}; text-shadow: {ombre}; margin-top: -4px; }}
.surtitre {{ font-family: "{po['titre']}"; font-size: {max(12, int(h['date_taille'] * 0.8))}px; letter-spacing: 3px;
  color: {rgb2hex(p['accent_lisible'] if not clair else p['accent2'])}; text-shadow: {ombre}; }}
.sceau {{ font-family: "{po['titre']}"; font-size: {int(h['taille'] * 0.34)}px; color: {rgb2hex(p['sur_accent'])};
  background-color: {rgb2hex(p['accent'])}; border-radius: 6px; padding: 6px 10px; }}

.icone {{ padding: 4px; border-radius: 16px; }}
.icone .tuile {{ font-family: "JetBrainsMono Nerd Font", "DejaVu Sans"; font-size: {int(t_ * 0.46)}px;
  min-width: {t_}px; min-height: {t_}px; border-radius: {int(t_ * 0.3)}px;
  background-color: {tuile_fond}; color: {rgb2hex(glyphe)}; border: 1px solid {rgba(glyphe, 0.35)};
  box-shadow: 0 4px 14px {rgba((0, 0, 0), 0.25)}; transition: all 180ms ease; }}
.icone .nom {{ font-family: "{po['ui']}"; font-size: 12px; font-weight: 600; color: {rgb2hex(nomc)};
  text-shadow: 0 1px 6px {rgba(nom_ombre_base, 0.7)}; transition: all 180ms ease; }}
.icone:hover .tuile {{ background-color: {rgb2hex(p['accent'])}; color: {rgb2hex(p['sur_accent'])};
  border-color: {rgb2hex(p['accent'])}; box-shadow: 0 6px 22px {rgba(p['accent'], 0.6)}; margin-top: -3px; margin-bottom: 3px; }}
.icone:hover .nom {{ color: {rgb2hex(p['accent_lisible'] if not clair else p['texte'])}; }}
.icone:active .tuile {{ margin-top: 0; margin-bottom: 0; }}
{h['style']}
{ic['style']}
"""


# ============================================================== divers
def apercu(fond):
    a = fond.resize((320, 200), Image.LANCZOS)
    masque = Image.new("L", a.size, 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, 319, 199), 22, fill=255)
    res = Image.new("RGBA", a.size)
    res.paste(a, (0, 0), masque)
    return res


def env_sh(t):
    f = t["fond_ecran"]

    def q(s):
        return "'" + str(s).replace("'", "'\\''") + "'"
    return "\n".join([
        f"NOM={q(t['nom'])}", f"PHRASE={q(t['phrase'])}", f"COURT={q(t['court'])}",
        f"TR_TYPE={q(f['transition'])}", f"TR_DUREE={q(f['duree'])}", f"TR_ANGLE={q(f['angle'])}",
        f"TR_POS={q(f['position'])}", f"TR_FPS={q(f['fps'])}", f"TR_BEZIER={q(f['bezier'])}"]) + "\n"


def generer(dossier):
    t = charger(dossier)
    gen = dossier / "gen"
    gen.mkdir(exist_ok=True)
    rapport = [f"[{t['id']}] {t['nom']}"]
    src = FONDS / t["image"]
    img = Image.open(src).convert("RGB")
    fond = recadrer(img, t["cadrage"])
    fond.save(gen / "fond.jpg", quality=93, optimize=True)
    apercu(fond).save(gen / "apercu.png")
    p, pal_img, origine = construire_palette(t, fond)
    barre = regler_barre(t, p, fond, rapport)
    moy, pire = verifier_horloge(t, p, fond, rapport)
    ombre_forte = moy < 4.5 or pire < 2.0

    (gen / "hypr.lua").write_text(lua_hypr(t, p, barre))
    (gen / "waybar.css").write_text(css_waybar(t, p, barre))
    (gen / "wofi.css").write_text(css_wofi(t, p))
    (gen / "nwg-drawer.css").write_text(css_grille(t, p))
    (gen / "rofi.rasi").write_text(rasi_rofi(t, p))
    (gen / "mako.conf").write_text(conf_mako(t, p))
    (gen / "hyprlock.conf").write_text(conf_hyprlock(t, p))
    (gen / "eww.yuck").write_text(eww_yuck(t, p))
    (gen / "eww.scss").write_text(eww_scss(t, p, ombre_forte))
    (gen / "kitty.conf").write_text(conf_kitty(t, p))
    (gen / "env.sh").write_text(env_sh(t))
    GHOSTTY_THEMES.mkdir(parents=True, exist_ok=True)
    (GHOSTTY_THEMES / f"{t['court']}.conf").write_text(conf_ghostty(t, p))

    sortie = {k: rgb2hex(v) for k, v in p.items() if k != "term"}
    sortie["terminal"] = {str(i): rgb2hex(p["term"][i]) for i in range(16)}
    sortie["barre"] = {"fond": rgb2hex(barre["fond"]), "opacite": barre["alpha"], "texte": rgb2hex(barre["texte"])}
    sortie["couleurs_de_l_image"] = [{"couleur": rgb2hex(c), "part": round(f, 3)} for c, f in pal_img[:16]]
    sortie["correspondances"] = {k: {"couleur_image": v[0], "distance": v[1]} for k, v in origine.items()}
    (dossier / "couleurs.json").write_text(json.dumps(sortie, indent=2, ensure_ascii=False) + "\n")
    rapport.append(f"  fond {sortie['fond']} texte {sortie['texte']} accent {sortie['accent']} "
                   f"accent2 {sortie['accent2']} accent3 {sortie['accent3']}")
    return rapport


def main():
    cibles = sys.argv[1:]
    dossiers = sorted(d for d in RACINE.iterdir()
                      if d.is_dir() and not d.is_symlink() and d.name[:2].isdigit() and (d / "theme.toml").exists())
    if cibles:
        dossiers = [d for d in dossiers if d.name in cibles or d.name.split("-", 1)[1] in cibles]
    lignes = []
    for d in dossiers:
        try:
            lignes += generer(d)
        except Exception as e:  # on continue avec les autres thèmes
            lignes.append(f"[{d.name}] ERREUR : {e!r}")
            import traceback
            traceback.print_exc()
    texte = "\n".join(lignes)
    print(texte)
    (RACINE / "verification.txt").write_text(texte + "\n")


if __name__ == "__main__":
    main()
