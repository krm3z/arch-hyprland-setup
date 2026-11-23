# 🏔️ Arch + Hyprland — un bureau à thèmes, façon Windows, en français

> Un portable HP OmniBook X en double démarrage Windows 11 / Arch Linux, transformé en bureau **minimaliste, animé et
> entièrement thémable** : un seul raccourci (`Windows + F1`) change d'un coup le fond d'écran, les couleurs, les polices,
> la barre, les bordures, les animations, le terminal, les notifications et l'écran de verrouillage.
> Tout a été monté avec **Claude Code**, en autonomie, en trois sessions (21, 22 et 23 novembre 2026).

Ce dépôt sert à trois choses :

1. **Documenter de A à Z** ce qui a été fait, avec tous les détails → [`docs/`](docs/)
2. **Présenter le projet** → cette page
3. **Tout refaire depuis un Arch nu** avec un seul prompt pour Claude → [`prompts/REBUILD-PROMPT.md`](prompts/REBUILD-PROMPT.md)

Les vrais fichiers de configuration sont dans [`config/`](config/), les listes de paquets dans [`packages/`](packages/),
les scripts de déploiement dans [`scripts/`](scripts/).

---

## ✨ Ce que ça donne

| | |
|---|---|
| **Session** | Hyprland 0.57 (config en **Lua**), lancé depuis `tty1` par `~/.bash_profile` |
| **11 thèmes** | Forêt · Monolithe · Rochers · Automne · Glace · McQueen · F1 · Porsche · Ronaldo nuit · Ronaldo pelouse · Crème |
| **Changement de thème** | `Windows+F1` (suivant), `Windows+Maj+F1` (précédent), `Windows+W` (liste avec aperçus), `Windows+Maj+W` (hasard) |
| **Barre** | waybar flottante, floutée, teintée par le thème ; apparaît au survol en plein écran |
| **Bureau** | horloge géante et 6 icônes (eww) posées dans la partie « calme » de chaque fond d'écran |
| **Lanceurs** | wofi (`Windows`), grille façon menu Démarrer (`Windows+A`, nwg-drawer), rofi (menus) |
| **Raccourcis Windows** | `Windows+←/→/↑/↓`, `Alt+Tab`, `Alt+F4`, `Windows+D`, `Windows+L`, `Windows+Maj+S`… |
| **Fiche d'aide** | `Windows+F2` : `~/Bureau/Raccourcis.md` **générée automatiquement** depuis la config Hyprland |
| **Démarrage** | GRUB minimal (Arch / Windows 11 / Paramètres UEFI), menu « Redémarrer sous Windows » |
| **Applis** | Chrome, Firefox, VS Code, Claude Desktop, Discord, Teams, LibreOffice, DBeaver, PostgreSQL, JupyterLab, GitHub Desktop… + 11 applis web |
| **Sécurité** | Timeshift (instantanés), ufw, mises à jour automatiques quotidiennes, Wi-Fi 802.1X sans mot de passe en clair |

## 🧠 L'idée centrale : un générateur de thèmes

Chaque thème est **un fichier de 40 lignes** (`theme.toml`) + une image. Un générateur Python
([`generer.py`](config/home/.config/themes/bin/generer.py)) lit l'image, en extrait les vraies couleurs, vérifie le
contraste (WCAG) et fabrique **tous** les fichiers de configuration des programmes :

```
theme.toml + image ──► generer.py ──► gen/hypr.lua      (bordures, flou, animations)
                                      gen/waybar.css    (barre)
                                      gen/wofi.css, rofi.rasi, mako.conf, hyprlock.conf
                                      gen/eww.yuck/.scss (horloge + icônes du bureau)
                                      gen/nwg-drawer.css (grille des applis)
                                      gen/kitty.conf + ~/.config/ghostty/themes/<nom>.conf
                                      gen/fond.jpg      (image recadrée à l'écran)
```

Les configs des programmes sont de simples **liens symboliques** vers `~/.config/themes/actuel/gen/…` ; le script
[`theme`](config/home/.config/themes/bin/theme) change le lien `actuel`, recharge chaque programme (signaux, `eww reload`,
`makoctl reload`, `hyprctl reload`…) et lance la transition animée du fond (`awww`). Résultat : zéro redémarrage.

## 🗺️ Sommaire de la documentation

| # | Chapitre | Contenu |
|---|---|---|
| 0 | [Vue d'ensemble](docs/00-vue-ensemble.md) | architecture, chronologie des 3 sessions, choix de conception |
| 1 | [Système de base](docs/01-systeme-base.md) | disque, partitions, fstab, locale, clavier, pacman, services |
| 2 | [GRUB et double démarrage](docs/02-grub-dualboot.md) | scripts `06_arch/07_windows/08_uefi`, thème, « Redémarrer sous Windows » |
| 3 | [Hyprland](docs/03-hyprland.md) | config Lua, démarrage, entrées, règles de fenêtres, veille/verrouillage |
| 4 | [Le système de thèmes](docs/04-themes.md) | `theme.toml`, générateur, les 11 thèmes, ajouter un thème |
| 5 | [Barre, widgets et outils](docs/05-barre-widgets-outils.md) | waybar, eww, mako, wofi, rofi, scripts `~/.local/bin` |
| 6 | [Applications](docs/06-applications.md) | AUR, applis web, grille Windows+A, icônes du bureau, trousseau |
| 7 | [Réseau, Wi-Fi Ynov, Flatpak](docs/07-reseau-wifi-flatpak.md) | profil 802.1X, nm-applet, boutique Logiciels |
| 8 | [Maintenance et sécurité](docs/08-maintenance-securite.md) | Timeshift, ufw, `maj-auto`, reflector, PostgreSQL |
| 9 | [Raccourcis clavier](docs/09-raccourcis.md) | table complète |
| 10 | [Pièges et leçons apprises](docs/10-pieges-et-lecons.md) | tout ce qui a cassé et comment c'est réglé |

## 🚀 Refaire la même chose

**Option A — avec Claude Code (recommandé)** : installe Arch minimal, lance `claude` dans ce dépôt cloné, puis colle le
prompt de [`prompts/REBUILD-PROMPT.md`](prompts/REBUILD-PROMPT.md). Claude lit la doc, adapte au matériel (écran, GPU,
disque, nom d'utilisateur) et déroule les étapes.

**Option B — à la main** :

```bash
git clone <ce-dépôt> ~/arch-hyprland-setup && cd ~/arch-hyprland-setup
sudo pacman -S --needed - < packages/pacman.txt          # paquets officiels
# installer yay (voir packages/README.md) puis :
yay -S --needed - < packages/aur.txt
# mettre tes images dans ~/Pictures/Fonds-ecran (voir docs/04-themes.md)
scripts/install-config.sh foret                          # configs + thèmes (sans sudo)
sudo scripts/install-systeme.sh                          # GRUB, maj-auto, ufw… (lis-le avant !)
```

## ⚠️ À savoir avant de copier

- **Les fonds d'écran ne sont pas dans le dépôt** (images protégées : Ghost of Yōtei, Cars/McQueen, Porsche,
  Cristiano Ronaldo, F1…). Chaque `theme.toml` nomme l'image attendue dans `~/Pictures/Fonds-ecran/` ; mets-y les
  tiens (mêmes noms de fichier, ou change `image =` dans le `theme.toml`). Le générateur recalcule les couleurs.
- Le matériel est spécifique : **HP OmniBook X, Intel Core Ultra 7 258V (Lunar Lake), écran `eDP-1` à l'échelle 1,25,
  clavier AZERTY**. Adapte `hl.monitor`, `LIBVA_DRIVER_NAME`, les UUID de disque et les partitions.
- Les UUID de disque, l'identifiant Wi-Fi de l'école et tous les mots de passe sont **volontairement absents** :
  le Wi-Fi d'entreprise garde son mot de passe dans le trousseau GNOME, jamais dans un fichier.
- Les noms de fichiers, commentaires et menus sont **en français** (choix de l'utilisateur).

## 📜 Licence

Configs et scripts sous licence MIT (voir [`LICENSE`](LICENSE)). Les marques et visuels cités appartiennent à leurs
propriétaires ; aucun fond d'écran n'est redistribué ici.
