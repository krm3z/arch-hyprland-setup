#!/bin/bash
# creer-appli-web.sh <id> "<Nom>" <URL> [icône.png]
# Crée une « appli web » : fenêtre Chrome dédiée (profil séparé), entrée dans le lanceur et la grille Windows+A.
# Exemple : creer-appli-web.sh deezer "Deezer" https://www.deezer.com
set -euo pipefail
id="$1"; nom="$2"; url="$3"; icone="${4:-}"
host=$(echo "$url" | sed -E 's#https?://([^/]+)(/.*)?#\1#'); chemin=$(echo "$url" | sed -E 's#https?://[^/]+(/.*)?#\1#'); chemin=${chemin%/}
# Sous Wayland, Chrome ignore --class : l'app_id est « chrome-<hôte>__<chemin>-Default » (« / » devient « _ »)
wmclass="chrome-${host}_$(echo "$chemin" | tr '/' '_')-Default"
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/applis-web/$id" "$HOME/.local/share/icons/hicolor/256x256/apps"
[ -n "$icone" ] && cp "$icone" "$HOME/.local/share/icons/hicolor/256x256/apps/appli-web-$id.png"
cat > "$HOME/.local/share/applications/appli-web-$id.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$nom
Exec=google-chrome-stable --user-data-dir=$HOME/.local/share/applis-web/$id --app=$url --no-first-run --no-default-browser-check --password-store=gnome-libsecret
Icon=appli-web-$id
Terminal=false
Categories=Network;WebBrowser;
StartupWMClass=$wmclass
StartupNotify=true
X-Appli-Web=true
EOF
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
echo "Créé : appli-web-$id (lancer : gtk-launch appli-web-$id)"
