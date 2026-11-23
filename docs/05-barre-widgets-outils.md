# 5 · Barre, widgets et petits outils

## waybar (barre du haut)

`~/.config/waybar/config.jsonc` est **écrit une fois** par [`installer-barre.py`](../config/home/.config/themes/bin/installer-barre.py)
(forme fixe : 34 px, marges 6/10, flottante). Seule la feuille `style.css` change (lien vers le thème actif).

| Zone | Modules |
|---|---|
| gauche | `custom/claude` (consommation Claude Code via `ccusage`, voir plus bas) · `hyprland/workspaces` (5 bureaux persistants, clic = activer) |
| centre | `clock` (calendrier au survol) |
| droite | groupe **système** (CPU, mémoire, température) · groupe **contrôles** (son, réseau, Bluetooth, luminosité, batterie) · groupe **session** (notifications, bouton d'alimentation) |

Actions : réseau → `wifi-menu` / `nm-connection-editor`, son → `pavucontrol`, Bluetooth → `blueman-manager`,
alimentation → `menu-alimentation`, molette = volume/luminosité. Pas de zone *tray* (donc pas d'icône pour `nm-applet`).

- **Pastille Claude** (`claude-usage`, `signal 9`) : Python + `ccusage blocks --active --json` : tokens du bloc de 5 h en
  cours et heure du prochain reset ; clic = page d'usage de claude.ai ; clic droit = rafraîchir. `ccusage` est dans l'AUR.
- **Notifications** (`notifications`, signal 10) : cloche + compteur, `etat | historique | nepasderanger | effacer`, appuie sur mako (`makoctl`).
- **Mises à jour** (`mises-a-jour`, signal 8) : script prévu pour la barre (`compter` : checkupdates + `yay -Qua` ; `lancer` : Ghostty flottant qui lance `yay -Syu` ; `demarrage` : une fois par jour). Le module n'est plus dans la barre actuelle : l'installation automatique est faite par `maj-auto` ([chap. 8](08-maintenance-securite.md)) ; le script reste accessible via `Super+I` → Mises à jour.
- **Barre en plein écran** (`barre-plein-ecran`) : une 2ᵉ instance de waybar en couche `overlay` est lancée quand la souris touche le
  haut de l'écran et tuée quand elle redescend.

## eww (horloge et icônes du bureau)

`eww.yuck/.scss` sont générés par thème. Deux fenêtres : `horloge` (heure + date, polices/positions du thème) et `icones` (6 icônes,
couche `bottom`, namespace `eww-icones`). Les 6 icônes, dans l'ordre : **Claude Desktop, VS Code, Chrome, Terminal, Raccourcis, Applications**
(liste codée dans `eww_yuck()` de `generer.py`).
Pour vérifier une icône cachée derrière une fenêtre : passer temporairement `:stacking "bottom"` à `"overlay"`, `eww reload`, capturer, remettre.

## Lanceurs et menus

- **wofi** (`Windows`, `Windows+S`, `Windows+Espace`, `Windows+R` pour « exécuter ») : menu rapide, CSS généré.
- **nwg-drawer** (`Windows+A`) : grille 7 colonnes, icônes 64 px, recherche, catégories, boutons d'alimentation ;
  [`grille-applis`](../config/home/.config/themes/bin/grille-applis) ouvre/ferme (non résident).
- **rofi** : menus déroulants (paramètres, alimentation, presse-papiers, thèmes, Wi-Fi, émojis `Windows+;`, liste des fenêtres `Windows+Tab`, calculatrice).
- **mako** : notifications ; **swayosd** : affichage de volume/luminosité/majuscules ; **hyprpicker** : pipette (`Windows+Maj+C`).

## Scripts de `~/.local/bin` (tous en français)

| Commande | Raccourci | Fonction |
|---|---|---|
| `theme` | `Super+F1`… | changer de thème ([chap. 4](04-themes.md)) |
| `raccourcis` / `raccourcis-afficher` / `raccourcis-generer` | `Super+F2`, `Super+H` | fiche des raccourcis : affiche une fenêtre Markdown flottante, régénérée depuis `hyprctl binds -j` (+ `ghostty +list-keybinds`) |
| `grille-applis` | `Super+A` | grille des applications |
| `capture zone\|ecran\|fenetre\|annoter` | `Super+Maj+S`, `Impr`, `Alt+Impr`, `Ctrl+Impr` | hyprshot/grim/slurp ; annotation dans satty ; copie au presse-papiers |
| `presse-papiers` | `Super+V` | historique cliphist → rofi → colle avec `wtype` |
| `menu-alimentation` | `Super+X`, `Ctrl+Alt+Suppr` | verrouiller, veille, déconnexion, redémarrer, **redémarrer sous Windows**, éteindre |
| `parametres` | `Super+I` | menu : Wi-Fi, Bluetooth, son, apparence GTK, thèmes, éclairage nocturne (`hyprsunset -t 4000`), mode d'énergie, imprimantes, mises à jour… |
| `wifi-menu` | clic réseau | liste `nmcli` dans rofi, mot de passe demandé si inconnu |
| `alerte-batterie` | auto | notifications à 15 % et 5 % |
| `mises-a-jour` | barre | voir plus haut |
| `fond-ecran` | | délègue à `theme` (compatibilité) |

Aucun de ces scripts ne contient de secret.
