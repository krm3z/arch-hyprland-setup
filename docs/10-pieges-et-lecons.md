# 10 · Pièges et leçons apprises

Tout ce qui a cassé (ou failli) pendant le montage, et la règle qui en est restée. À lire **avant** de modifier quoi que ce soit.

## Hyprland 0.57 (config Lua)
- `hyprctl dispatch` prend des **expressions Lua** : `hyprctl dispatch 'hl.dsp.exec_cmd("waybar")'`. Les anciennes syntaxes (`exec waybar`) échouent.
  Conséquence : `nwg-drawer -wm hyprland` ne fonctionne pas → on utilise `grille-applis` sans `-wm`.
- Toujours `hyprctl configerrors` après une modif. Garder une sauvegarde datée (`hyprland.lua.bak-AAAA-MM-JJ`) avant les gros changements.
- Les classes de fenêtres Chrome en mode appli ne suivent pas `--class` sous Wayland : voir [chap. 6](06-applications.md).

## Session et variables d'environnement
- Lancer Hyprland depuis `tty1` laisse `XDG_DATA_DIRS` vide → pas d'applis Flatpak dans les menus. Corrigé dans `hyprland.lua`.
- Chrome/Electron/VS Code ne reconnaissent pas Hyprland → trousseau forcé (`--password-store=gnome-libsecret`).
- Wi-Fi d'entreprise : sans `nm-applet` (agent de secrets) l'autoconnexion n'a pas le mot de passe.

## Thèmes et affichage
- **Glyphes Nerd Font** : les caractères privés (U+F0000…) sont supprimés quand on les écrit via un éditeur/heredoc ; les produire par code
  (`chr(0xF018D)`) et contrôler avec `od -c`.
- **grim** capture en **résolution physique** (1,25× de plus que les coordonnées logiques) → recadrer en conséquence.
- **eww** : `:show-truncated false` sur les labels ; pas de caractères non ASCII dans un commentaire `/* */` du SCSS (sinon `@charset` → GTK rejette tout).
- **hyprlock** : `SIGUSR1` déverrouille mais prend ~2 s.
- L'utilisateur appuie souvent sur `Super+F1` pendant les tests : toujours vérifier `theme actuel` avant de se fier à une capture d'écran.
- Pour tester les icônes eww cachées : passer `:stacking` à `"overlay"` le temps de la capture.

## Shell
- `pkill -f motif` dans la même ligne bash que le motif **tue ce shell**. Utiliser `pkill -x nom` ou un motif qui ne figure pas dans la ligne de commande.
- Ne pas automatiser l'écran de l'utilisateur sans demander : l'ouverture de la grille ou de fenêtres pendant des tests l'a agacé ; préférer des vérifications
  par fichiers/IPC (`hyprctl`, `eww`, `makoctl`).

## pacman / AUR
- Toujours `sudo pacman -Syu --needed <paquets>` : un index périmé donne des 404 (ex. `hwloc`) et pacman abandonne.
- `yay` demande le mot de passe sudo dans un terminal : pour les installations d'AUR, construire avec `makepkg` (hors sudo), puis `sudo pacman -U`.
- `packagekit` ne doit **pas** être installé (voir [chap. 7](07-reseau-wifi-flatpak.md)).
- `NoExtract` pour les scripts GRUB : sinon une mise à jour de `grub` rétablit les scripts d'origine et crée des doublons dans le menu.

## Sudo
- Claude ne peut pas taper le mot de passe : fournir les commandes exactes à lancer (`! sudo …`). Ne laisser aucun `NOPASSWD` général en place.

## Sauvegarde avant modification
Convention : copier en `fichier.avant-<sujet>-AAAA-MM-JJ` avant chaque évolution importante (`generer.py`, `theme`, `raccourcis-generer`, `hyprland.lua`,
`waybar/config.jsonc`). Ces sauvegardes ne sont pas dans ce dépôt (voir `.gitignore`).
