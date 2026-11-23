# 4 · Le système de thèmes

Le cœur du projet. Dossier : `~/.config/themes/` ([copie ici](../config/home/.config/themes/)).

## Les 11 thèmes

| # | Thème | Mode | Fond | Accent | 2ᵉ accent | Police de titre | Police du terminal | Animations | Transition | Phrase de verrouillage |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | Forêt | sombre | `#1c2614` | `#9fd23c` | `#e3d39b` | Quicksand | Mononoki NF | douce | fade | « Respire. » |
| 02 | Monolithe | sombre | `#1d120a` | `#e98b2a` | `#3d8fd6` | Montserrat | SpaceMono NF | glissement | wipe | « Un pas après l'autre. » |
| 03 | Rochers | sombre | `#24120c` | `#c8442a` | `#ecc58a` | Rye | BlexMono NF | moyenne | wave | « Trace ta route. » |
| 04 | Automne | sombre | `#1a100d` | `#d9472b` | `#f1eee8` | Shippori Mincho | VictorMono NF | feuilles | fade | « Le calme avant la tempête. » |
| 05 | Glace | sombre | `#0c1d27` | `#45d4e6` | `#7fb9d8` | Exo 2 | GeistMono NF | nette | grow | « Garde la tête froide. » |
| 06 | McQueen | sombre | `#140c1c` | `#e02d24` | `#f68b3c` | Racing Sans One | FiraCode NF | nerveuse | wipe | « Pied au plancher. » |
| 07 | F1 | sombre | `#18181a` | `#dc1f1a` | `#f7d117` | Saira Condensed | IosevkaTerm NF | éclair | left | « Chaque dixième compte. » |
| 08 | Porsche | sombre | `#0d0d0e` | `#d4202a` | `#3b3b3e` | Jost | MartianMono NF | sobre | fade | « Moins, mais mieux. » |
| 09 | Ronaldo nuit | sombre | `#0b0909` | `#d8261c` | `#ffffff` | Anton | JetBrainsMono NF | énergique | grow | « Le travail paie toujours. » |
| 10 | Ronaldo pelouse | sombre | `#0e170b` | `#d42a20` | `#5a8f33` | Bebas Neue | Hack NF | énergique | outer | « Relève-toi. » |
| 11 | Crème | **clair** | `#f3ead6` | `#f3a27f` | `#1d2b6e` | Caveat Brush | ComicShannsMono NF | douce | grow | « No risk, no story. » |

(Les couleurs ci-dessus sont les *indications* du `theme.toml` ; les couleurs finales sont tirées de l'image.)

## Images attendues (non fournies)

Dossier `~/Pictures/Fonds-ecran/` (le chemin est la constante `FONDS` dans `generer.py`) :

```
foret-brume.jpg   desert-monolithe.jpg   desert-rochers.jpg   automne-ghost-of-yotei.jpg   glace-canyon.jpg
racing-mcqueen.png   racing-f1.png   noir-porsche.png   noir-ronaldo-fond-noir.png   noir-ronaldo-herbe.png
creme-no-risk.png
```
Prends des images de **1920×1200 ou plus** (le générateur recadre sur le ratio de l'écran selon `cadrage = [x, y]`). Avec
d'autres images, garde le même `theme.toml` : les couleurs seront recalculées d'après ta nouvelle image (c'est le but).
Constantes à adapter dans `generer.py` : `ECRAN = (1920, 1200)` et `ECHELLE = 1.25`.

## Anatomie d'un `theme.toml`

Chaque section est optionnelle (valeurs par défaut dans `DEFAUTS` en tête de `generer.py`). Exemple : [`01-foret/theme.toml`](../config/home/.config/themes/01-foret/theme.toml).

| Section | Rôle |
|---|---|
| racine | `nom`, `image`, `cadrage = [x, y]` (centre du recadrage de 0 à 1), `phrase` (écran de verrouillage + notification) |
| `[couleurs]` | `mode` (sombre/clair), `fond`, `accent`, `accent2`, `accent3` = **indications** ; `fidelite` : 1 = couleur exacte de l'image, 0 = indication exacte |
| `[polices]` | `titre` (+ `titre_graisse`), `ui`, `terminal`, `terminal_taille` |
| `[barre]` | `teinte`, `teinte_force`, `opacite`, `flou`, `contraste_min` (4,5 = WCAG AA) |
| `[bordures]` | liste de `couleurs` (dégradé), `angle`, `taille`, `arrondi` |
| `[fenetres]` | `flou_taille`, `flou_passes`, `ombre` |
| `[animations]` | `style` : douce, glissement, moyenne, feuilles, nette, nerveuse, éclair, sobre, énergique |
| `[fond_ecran]` | transition `awww` : `fade/wipe/wave/grow/outer/left…`, `duree`, `angle`, `position`, `fps`, `bezier` |
| `[terminal]` | `opacite` de Ghostty/kitty |
| `[horloge]` | `ancre` (`top left`…), `x`/`y` en %, `taille`, couleurs, format `%H:%M`, date, secondes, surtitre, sceau |
| `[icones]` | `ancre`, `x`/`y`, `disposition` (`ligne`/`colonne`), `taille`, fond, opacité, couleur du glyphe |
| `[verrouillage]` | luminosité/flou de l'image sur hyprlock |

Principe de placement : **l'horloge et les icônes sont posées dans la zone calme de chaque image** (brume, ciel…) ; c'est
pourquoi chaque thème a ses propres `ancre/x/y`.

## Le générateur (`bin/generer.py`, ~900 lignes)

Étapes pour chaque thème :

1. **Chargement** : fusionne `DEFAUTS` + `theme.toml` (`fusion`), ouvre l'image, la **recadre** au format de l'écran.
2. **Palette** (`construire_palette`, `couleurs.py`) : extrait la palette de l'image (`extraire_palette`), pour chaque rôle
   (`fond`, `accent`…) prend la couleur réelle **la plus proche** de l'indication et la mélange en espace **LCh**
   selon `fidelite` (teinte venant de l'image, luminosité/saturation proches de la description). Dérive
   `fond2/fond3`, `texte`, `texte_doux`, et les 6 couleurs ANSI du terminal (palette canonique `CANON` recalée sur la teinte).
3. **Lisibilité** (`regler_barre`, `verifier_horloge`) : mesure le pire contraste du texte de la barre et de l'horloge
   sur les pixels réellement situés dessous (`zone_pixels`, `pire_contraste`, WCAG) et ajuste opacité/luminosité jusqu'à
   `contraste_min`. Rapport : `verification.txt`.
4. **Écriture de `gen/`** : `hypr.lua` (bordures, flou, courbes et animations du style choisi + règles de couches),
   `waybar.css`, `wofi.css`, `nwg-drawer.css` (grille), `rofi.rasi`, `mako.conf`, `hyprlock.conf`, `kitty.conf`,
   `eww.yuck` + `eww.scss`, `fond.jpg`, `apercu.png` (miniature pour `theme choisir`), `env.sh` (variables lues par `theme`),
   puis `couleurs.json` et `~/.config/ghostty/themes/<nom-court>.conf`.

```bash
python3 ~/.config/themes/bin/generer.py          # tous les thèmes
python3 ~/.config/themes/bin/generer.py foret    # un seul
```

## Le script `theme`

| Commande | Effet |
|---|---|
| `theme suivant` / `precedent` | thème suivant/précédent (`Super+F1` / `Super+Maj+F1`) |
| `theme choisir` | liste rofi avec aperçus (`Super+W`) |
| `theme hasard` | au hasard (`Super+Maj+W`) |
| `theme appliquer glace` | par nom (`glace` ou `05-glace`) |
| `theme actuel` / `liste` | information |
| `theme regenerer [nom]` | relance `generer.py` puis réapplique (après avoir édité un `theme.toml`) |
| `theme barre` | redémarre waybar + eww (`Super+Maj+R`) |
| `theme demarrage` | appelé au démarrage de Hyprland : réapplique le dernier thème **sans animation** |

`appliquer()` fait, dans l'ordre : source `gen/env.sh` → lien `actuel` → lien `ghostty/themes/actuel.conf` →
`~/.cache/fond-actuel` → **fond** (`awww img … --transition-type …`) → `hyprctl reload config-only` (bordures/animations) →
**barre** (`SIGUSR2` à waybar) → **mako** (`makoctl reload`) → **grille** (lien CSS nwg-drawer + fermeture) →
**couleur d'accent GNOME** → `SIGUSR2` Ghostty / `SIGUSR1` kitty → **widgets eww** → notification « Thème : … ».

Un `flock` sérialise les changements (utile quand on martèle `Super+F1`).

### Couleur d'accent GNOME qui suit le thème

`accent_gnome()` convertit l'accent du thème en **OKLab**, calcule sa teinte et choisit la plus proche des 9 accents GNOME
(`blue teal green yellow orange red pink purple slate`) → `gsettings set org.gnome.desktop.interface accent-color`.
Les applis libadwaita (Logiciels…) suivent donc le thème.

## Ajouter un thème

1. `mkdir ~/.config/themes/12-mon-theme` et y copier un `theme.toml` existant ; changer `nom`, `image`, `phrase`, les couleurs.
2. Déposer l'image dans `~/Pictures/Fonds-ecran/`.
3. `theme regenerer 12-mon-theme && theme appliquer mon-theme`.
4. Ajuster `[horloge]`/`[icones]` (ancre, x, y) pour tomber dans une zone calme, `theme regenerer`, recommencer.

## Pièges rencontrés

- **eww** : les labels sont tronqués par défaut → `:show-truncated false`. Des caractères non ASCII dans un commentaire
  *loud* (`/* … */`) du SCSS font émettre `@charset` à grass → GTK rejette **toute** la feuille de style.
- **Glyphes Nerd Font** : les caractères de la zone privée sont supprimés quand on les tape dans l'outil d'écriture ;
  les générer par code (`chr(0xF018D)`) et vérifier avec `od` (voir `GLYPHES` dans `generer.py`).
- **hyprlock** : se déverrouille avec `SIGUSR1` mais il faut ~2 s ; ne pas tester trop vite.
- **`pkill -f motif`** lancé dans la même ligne bash que le motif **tue le shell lui-même**.
- Remplacements : **awww** (ex-swww) remplace `hyprpaper` ; **mako** remplace `swaync` (le fichier D-Bus de swaync est
  surchargé par `~/.local/share/dbus-1/services/org.erikreider.swaync.service` qui lance mako).
