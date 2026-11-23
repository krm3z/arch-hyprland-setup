# Paquets

| Fichier | Contenu | Installation |
|---|---|---|
| `pacman.txt` | paquets explicitement installés depuis les dépôts officiels (`pacman -Qqen`) | `sudo pacman -S --needed - < packages/pacman.txt` |
| `aur.txt` | paquets AUR / étrangers (`pacman -Qqem`, sans les `-debug`) | `yay -S --needed - < packages/aur.txt` (après avoir installé `yay`) |

Notes :
- `yay-bin` s'installe à la main (`git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si`).
- Le dépôt AUR utilisé par la session a construit `claude-desktop`, `visual-studio-code-bin`, `github-desktop-bin`,
  `teams-for-linux` et `google-chrome` avec `makepkg` dans `~/.cache/aur-build/`.
- `eww` est en AUR (la version affiche 0.5 alors que le paquet est 0.6).
- Flatpak : seul le dépôt **flathub** (système) est configuré, aucun flatpak n'est resté installé.
- **Ne PAS installer `packagekit`** : `gnome-software` d'Arch n'en dépend pas, et l'utilisateur veut la boutique
  uniquement pour Flatpak (les mises à jour Arch passent par `yay`).
- Certains paquets de la liste sont des restes de l'installation d'origine (`hyprpaper`, `swaync`, `kitty`) :
  conservés comme secours, voir `docs/04-themes.md`.
