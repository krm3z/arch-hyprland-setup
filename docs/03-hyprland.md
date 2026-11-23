# 3 · Hyprland

Version **0.57** : la configuration est en **Lua** (`~/.config/hypr/hyprland.lua`), plus en `hyprland.conf`. L'API Lua est
documentée par des stubs : `/usr/share/hypr/stubs/hl.meta.lua`. Fichier complet : [`hyprland.lua`](../config/home/.config/hypr/hyprland.lua).

Utile : `hyprctl configerrors` (erreurs de config), `hyprctl binds -j` (toutes les touches),
`hyprctl dispatch 'hl.dsp.exec_cmd("waybar")'` (les `dispatch` prennent maintenant des **expressions Lua**).
N'utilise **pas** `nwg-drawer -wm hyprland` (il parle l'ancien dispatch).

## Structure du fichier

1. **Écrans** : `eDP-1` en `preferred`, échelle **1,25** ; tout écran externe à droite (`auto-right`, échelle auto).
2. **Variables d'environnement** : curseur Bibata, `QT_QPA_PLATFORMTHEME=qt6ct`, `LIBVA_DRIVER_NAME=iHD`,
   `ELECTRON_OZONE_PLATFORM_HINT=auto`, `XDG_MENU_PREFIX=arch-`, et la reconstruction de `XDG_DATA_DIRS` (flatpak).
3. **Démarrage** (`hl.on("hyprland.start", …)`) : `dbus-update-activation-environment`, `hyprpolkitagent`, `nm-applet`
   (agent de secrets Wi-Fi), `theme demarrage` (fond, barre, widgets…), `swayosd-server`, `hypridle`, curseur,
   historique du presse-papiers (`wl-paste … cliphist store`, `wl-clip-persist`), `udiskie`, `alerte-batterie`,
   `barre-plein-ecran`, `raccourcis-generer --silencieux`.
4. **Rechargement** (`config.reloaded`) : régénère la fiche des raccourcis.
5. **Apparence de base** : marges 4/10, bordure 2 px, `rounding = 12`, ombre, flou (3 passes), `dwindle`.
   Le **thème actif** (`theme.lua`, chargé par `pcall(dofile, …)`) remplace couleurs de bordure, flou, ombres, animations ;
   un jeu d'animations de secours existe si le thème est absent.
6. **Entrées** : AZERTY, `numlock_by_default`, répétition 35/300, pavé tactile « façon Windows » (défilement naturel, toucher
   = clic, clic 2 doigts = clic droit, désactivé en tapant), geste **3 doigts horizontal = changer de bureau**.
7. **Raccourcis** (voir [chap. 9](09-raccourcis.md)) : chacun avec `description = "Catégorie | Action"`.
8. **Règles de fenêtres/couches.**

## Les raccourcis façon Windows : trucs d'implémentation

- **Touche Windows seule = menu** : `hl.bind("SUPER + SUPER_L", …, { release = true })` ouvre wofi au *relâchement* de la
  touche, sans gêner les combinaisons.
- **`Super+↑`** agrandit (mode `maximized`, pas plein écran) ou restaure une fenêtre réduite ; **`Super+↓`** restaure puis
  *réduit* (déplace la fenêtre dans le bureau spécial `special:reduites`, ré-affichable par `Super+Maj+M`).
- **`Super+←/→`** ancre à gauche/droite (désactive le flottant, sort du plein écran).
- **`Super+D`** « afficher le bureau » : va sur un bureau vide, une 2ᵉ pression revient au précédent (mémorisé dans une
  variable Lua).
- **`Alt+Tab`** : `cycle_next` + `bring_to_top` (la fenêtre passe devant même si flottante).
- **`Super+1…0`** par keycode `code:10…19` : indépendant de la disposition (AZERTY ou non).
- **Molette + Super** envoie `Ctrl+-`/`Ctrl+=` (zoom d'appli), clic molette `Ctrl+0`.
- Volume/luminosité/média : touches `XF86*` avec `locked = true` (marchent écran verrouillé) et `repeating`, via
  `swayosd-client` (affichage à l'écran). `Caps_Lock` affiche l'état du verrou majuscule.

## Règles de fenêtres

- `ignorer-maximiser` : `suppress_event = "maximize"` pour toutes les classes (les applis ne se maximisent pas toutes seules).
- `outils-flottants` : pavucontrol, blueman, nm-connection-editor, system-config-printer, Calculatrice, nwg-look, qt6ct,
  Mission Center, Ark, `fr.kerem.flottant`… → flottantes et centrées ; tailles 960×640 (outils) / 380×560 (calculatrice).
- `fiche-raccourcis` (`fr.kerem.raccourcis`) : 1000×800 flottante centrée.
- `firefox-pip` : image dans l'image flottante, épinglée, en bas à droite.
- `satty` (annotation des captures), dialogues Thunar flottants, `fix-xwayland-drags`.
- **Couches** : flou derrière wofi, rofi, notifications, swayosd, nwg-drawer ; pas d'animation pour la sélection de capture.

## Veille et verrouillage (`hypridle.conf`)

| Inactivité | Action |
|---|---|
| 2 min 30 | luminosité à 10 % (rétablie à la reprise) |
| 5 min | verrouillage (`hyprlock`) |
| 5 min 30 | écran éteint (DPMS) |
| 15 min | mise en veille (`systemctl suspend`) |

`before_sleep_cmd = loginctl lock-session`. L'écran de verrouillage (`hyprlock.conf`) est **généré par thème**
(image du fond floutée/assombrie, phrase du thème, horloge).

## Divers

- Session lancée par `exec start-hyprland` depuis `tty1` ([chap. 1](01-systeme-base.md)).
- Terminal par défaut **Ghostty** (`xdg-terminals.list` → `com.mitchellh.ghostty.desktop`, `TERMINAL=ghostty`) ; kitty reste en secours.
- Presse-papiers : `Super+V` → `cliphist` + rofi, puis `wtype`/`wl-copy` pour coller.
- Captures : `capture zone|ecran|fenetre|annoter` (grim + slurp + satty), enregistrées dans `~/Pictures/Captures` ET copiées.
