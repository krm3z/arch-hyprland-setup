#!/bin/bash
# Déploie les configs de config/home/ dans $HOME (sans sudo) et recrée les liens vers le thème actif.
# Usage : scripts/install-config.sh [nom-du-thème-de-départ]   (défaut : foret)
# Pré-requis : paquets installés (packages/), fonds d'écran dans ~/Pictures/Fonds-ecran (voir docs/04-themes.md).
set -euo pipefail
DEPOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$DEPOT/config/home"
THEME="${1:-foret}"

# Le dépôt vient d'une machine où l'utilisateur s'appelait « kerem » : on adapte les chemins absolus.
if [ "$USER" != "kerem" ]; then
  echo "→ adaptation de /home/kerem vers $HOME dans les fichiers copiés"
fi

echo "→ copie des configs"
mkdir -p "$HOME/.config" "$HOME/.local/bin"
cp -rT "$SRC/.config" "$HOME/.config"
cp -rT "$SRC/.local" "$HOME/.local"
cp -n "$SRC/.bashrc" "$SRC/.bash_profile" "$HOME/" 2>/dev/null || echo "  (.bashrc/.bash_profile déjà présents : non écrasés, compare à la main)"
if [ "$USER" != "kerem" ]; then
  grep -rIl "/home/kerem" "$HOME/.config" "$HOME/.local/bin" 2>/dev/null | xargs -r sed -i "s#/home/kerem#$HOME#g"
fi
mkdir -p "$HOME/.local/share/dbus-1/services"
cp "$DEPOT/config/dbus-1/services/"* "$HOME/.local/share/dbus-1/services/"

echo "→ liens des commandes dans ~/.local/bin"
T="$HOME/.config/themes/bin"
for c in theme raccourcis raccourcis-afficher raccourcis-generer grille-applis notifications claude-usage; do
  ln -sfn "$T/$c" "$HOME/.local/bin/$c"
done
chmod +x "$T"/* "$HOME/.local/bin"/* 2>/dev/null || true

echo "→ dossiers attendus"
mkdir -p "$HOME/Pictures/Fonds-ecran" "$HOME/Pictures/Captures" "$HOME/Bureau" "$HOME/.config/ghostty/themes"

echo "→ génération des thèmes (nécessite les images de ~/Pictures/Fonds-ecran)"
python3 "$T/generer.py" || { echo "!! generer.py a échoué : il manque probablement des images de fond (voir docs/04-themes.md)"; exit 1; }

echo "→ activation du thème « $THEME »"
D=$(ls -d "$HOME/.config/themes/"[0-9][0-9]-"$THEME" | head -1)
ln -sfn "$(basename "$D")" "$HOME/.config/themes/actuel"
A="$HOME/.config/themes/actuel/gen"
ln -sfn "$A/hypr.lua"       "$HOME/.config/hypr/theme.lua"
ln -sfn "$A/hyprlock.conf"  "$HOME/.config/hypr/hyprlock.conf"
ln -sfn "$A/waybar.css"     "$HOME/.config/waybar/style.css"
ln -sfn "$A/wofi.css"       "$HOME/.config/wofi/style.css"
ln -sfn "$A/rofi.rasi"      "$HOME/.config/rofi/couleurs.rasi"
ln -sfn "$A/mako.conf"      "$HOME/.config/mako/config"
ln -sfn "$A/eww.yuck"       "$HOME/.config/eww/eww.yuck"
ln -sfn "$A/eww.scss"       "$HOME/.config/eww/eww.scss"
ln -sfn "$A/kitty.conf"     "$HOME/.config/kitty/theme.conf"
mkdir -p "$HOME/.config/nwg-drawer"; ln -sfn "$A/nwg-drawer.css" "$HOME/.config/nwg-drawer/drawer.css"
python3 "$T/installer-barre.py" || true   # écrit ~/.config/waybar/config.jsonc

echo "Terminé. Déconnecte-toi puis reconnecte-toi sur tty1 : Hyprland démarre via ~/.bash_profile."
