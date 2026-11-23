#
# ~/.bash_profile
#

[[ -f ~/.bashrc ]] && . ~/.bashrc

# Lancer Hyprland automatiquement après la connexion sur le premier terminal (tty1)
if [ -z "$WAYLAND_DISPLAY" ] && [ -z "$DISPLAY" ] && [ "${XDG_VTNR:-0}" -eq 1 ] && command -v start-hyprland >/dev/null; then
    exec start-hyprland
fi
