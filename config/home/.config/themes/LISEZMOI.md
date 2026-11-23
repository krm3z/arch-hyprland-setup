# Thèmes du bureau

11 thèmes, un par fond d'écran de `~/Pictures/Fonds-ecran`. Un thème change d'un coup, sans redémarrer :
fond d'écran (transition animée awww), couleurs tirées de l'image, bordures Hyprland, animations,
barre waybar (couleurs, transparence, flou — la forme ne change pas), terminal Ghostty (couleurs,
police, transparence), lanceur wofi, menus rofi, notifications mako, écran de verrouillage hyprlock,
horloge et icônes du bureau (eww), grille « Toutes les applications » (nwg-drawer, Windows + A).
Le dernier thème choisi est conservé au redémarrage.

## Raccourcis

| Touches | Action |
|---|---|
| Windows + F1 | Thème suivant |
| Windows + Maj + F1 | Thème précédent |
| Windows + W | Choisir un thème dans une liste avec aperçus |
| Windows + Maj + W | Thème au hasard |
| Windows + F2 | Fiche de tous les raccourcis (`~/Bureau/Raccourcis.md`) |

## Organisation

```
~/.config/themes/
├── 01-foret/ … 11-creme/   un dossier par thème
│   ├── theme.toml          ← À MODIFIER : couleurs, polices, barre, bordures, animations,
│   │                         position de l'horloge et des icônes, phrase de verrouillage
│   ├── couleurs.json       couleurs finales (tirées de l'image) — généré
│   └── gen/                fichiers générés (ne pas modifier à la main)
├── actuel -> 06-mcqueen    thème actif (lien)
├── bin/
│   ├── theme               script de changement de thème
│   ├── generer.py          fabrique gen/ et couleurs.json à partir de theme.toml + l'image
│   ├── couleurs.py         calculs de couleurs et de contraste (lisibilité)
│   ├── installer-barre.py  écrit la forme fixe de la barre (~/.config/waybar/config.jsonc)
│   ├── raccourcis*         fiche des raccourcis (génération + affichage)
│   ├── claude-usage        pastille Claude de la barre (ccusage)
│   └── notifications       module notifications de la barre (mako)
├── verification.txt        rapport de lisibilité (contraste barre / horloge) de la dernière génération
└── sauvegarde-…/           copie des configs d'origine
```

Les configs des programmes pointent vers le thème actif par des liens :
`~/.config/hypr/theme.lua`, `~/.config/hypr/hyprlock.conf`, `~/.config/waybar/style.css`,
`~/.config/wofi/style.css`, `~/.config/rofi/couleurs.rasi`, `~/.config/mako/config`,
`~/.config/eww/eww.yuck` + `eww.scss`, `~/.config/kitty/theme.conf`,
`~/.config/nwg-drawer/drawer.css` (grille des applications, ouverte par `grille-applis`).

Icônes du bureau (6, dans cet ordre) : Claude Desktop, VS Code, Chrome, Terminal, Raccourcis,
Applications. Liste définie dans `eww_yuck()` de `bin/generer.py` ; positions par thème dans `[icones]`.
Ghostty : un fichier par thème dans `~/.config/ghostty/themes/<nom>.conf`, inclus par
`~/.config/ghostty/config` via `themes/actuel.conf`.

## Modifier un thème

1. Éditer `~/.config/themes/NN-nom/theme.toml` (tout est commenté en français).
2. Lancer `theme regenerer` (ou `theme regenerer foret` pour un seul thème).

Les couleurs indiquées dans `[couleurs]` sont des **indications** : le générateur prend la couleur
la plus proche réellement présente dans l'image (`fidelite` règle le mélange), puis vérifie le
contraste (WCAG) et ajuste la luminosité ou l'opacité de la barre pour que le texte reste lisible.

Positions de l'horloge et des icônes : `ancre` (`top left`, `top right`, `bottom left`…), `x` et `y`
en % de l'écran ; `disposition = "ligne"` ou `"colonne"` pour les icônes.

## Commandes utiles

```
theme liste | actuel | suivant | precedent | choisir | hasard | appliquer glace
theme regenerer [nom]     après modification d'un theme.toml
theme barre               relancer la barre et les widgets (aussi Windows + Maj + R)
raccourcis-generer        régénérer ~/Bureau/Raccourcis.md (automatique quand la config Hyprland change)
```

## Revenir en arrière

Les configs d'origine sont dans `sauvegarde-…/`. kitty (terminal de secours) et swaync sont
toujours installés ; swaync est simplement neutralisé côté D-Bus par
`~/.local/share/dbus-1/services/org.erikreider.swaync.service`.
