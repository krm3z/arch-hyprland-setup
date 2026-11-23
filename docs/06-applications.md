# 6 · Applications

Session du 22 novembre 2026. Listes complètes : [`packages/`](../packages/).

## Ce qui a été installé

| Source | Applications |
|---|---|
| **AUR** (construits avec `makepkg` dans `~/.cache/aur-build/`, `yay-bin` installé aussi) | `claude-desktop` (le .deb officiel de downloads.claude.ai repaqueté), `visual-studio-code-bin`, `github-desktop-bin`, `teams-for-linux`, `google-chrome`, `eww`, `ccusage`, `bibata-cursor-theme-bin`, polices `otf-bebas-neue-git`, `ttf-quicksand-variable`, `ttf-shippori-mincho` |
| **Dépôts officiels** | Firefox (+FR), Discord, LibreOffice Fresh (+FR, hunspell-fr-comprehensive, hyphen-fr, mythes-fr), DBeaver, PostgreSQL, JupyterLab, jupyter-notebook, python-pandas, python-ipykernel, Timeshift, cronie, nwg-drawer, Papers (PDF), Seahorse (trousseau), Mission Center, Loupe, mpv, Thunar (+plugins), Dolphin, Ark, gnome-calculator, gnome-text-editor, gnome-software (Flatpak), btop, fastfetch, Ghostty, kitty… |
| **Flatpak** | dépôt Flathub activé, aucune appli résidente |
| **Applis web** | 11 : Claude Web, Deezer, Flathub, Gmail, Mail iCloud, LinkedIn, Microsoft 365, Netflix, Outlook, Power BI, Extranet Ynov |

Polices (affichage + terminal) : Inter, Montserrat, Noto (+CJK, emoji), Font Awesome, DejaVu, Liberation, et des Nerd Fonts :
FiraCode, Hack, IBM Plex Mono, IosevkaTerm, JetBrains Mono, Mononoki, Martian Mono, Space Mono, Victor Mono, Geist Mono,
ComicShanns. Chaque thème choisit une police de titre et une police de terminal différentes.

## PostgreSQL

```bash
sudo -iu postgres initdb --locale=fr_FR.UTF-8 -D /var/lib/postgres/data
sudo systemctl enable --now postgresql
sudo -iu postgres createuser --superuser kerem        # poste de dev personnel : rôle du même nom que l'utilisateur
sudo -iu postgres createdb -O kerem kerem
```
Rôle et base `kerem` : `psql` fonctionne sans arguments ; DBeaver s'y connecte en socket local.

## Trousseau (Chrome, Electron, VS Code)

Hyprland n'est pas détecté comme environnement de bureau par Chromium/Electron, qui retombent alors sur un stockage en clair.
On force `gnome-libsecret` (`gnome-keyring` est déverrouillé par PAM à la connexion) :

| Fichier | Contenu |
|---|---|
| `~/.config/chrome-flags.conf` | `--password-store=gnome-libsecret` |
| `~/.config/claude-desktop-flags.conf` | idem (lu par `/usr/bin/claude-desktop`) |
| `~/.vscode/argv.json` | `"password-store": "gnome-libsecret"` |
| chaque `.desktop` d'appli web | `--password-store=gnome-libsecret` dans `Exec=` |

## Applis web

Script [`scripts/creer-appli-web.sh`](../scripts/creer-appli-web.sh) : une fenêtre `google-chrome-stable --app=URL` avec un **profil séparé**
(`--user-data-dir=~/.local/share/applis-web/<id>`), donc sessions/cookies isolés, et une entrée `.desktop`
`appli-web-<id>` avec icône `~/.local/share/icons/hicolor/256x256/apps/appli-web-<id>.png`.

Détails : sous Wayland Chrome **ignore `--class`** ; l'`app_id` réel est `chrome-<hôte>__<chemin>-Default`, utilisé comme
`StartupWMClass` pour que la fenêtre se rattache à la bonne icône. Widevine (Netflix, Deezer) a été vérifié via CDP
(`requestMediaKeySystemAccess`). `Super+Y` ouvre l'Extranet Ynov (`gtk-launch appli-web-ynov`).

Chrome est le **navigateur par défaut** (`mimeapps.list`, `xfce4/helpers.rc` pour Thunar ; sauvegardes `*.avant-chrome-2026-11-23`).

## Grille « Toutes les applications » (`Windows+A`)

`nwg-drawer`, lancée par [`grille-applis`](../config/home/.config/themes/bin/grille-applis) (non résidente : le script la tue si elle est ouverte → bascule) :
`-c 7 -is 64 -spacing 18 -ovl -nofs -closebtn right`, boutons verrouiller/veille/redémarrer/éteindre. Son CSS est généré par thème
(`css_grille()`), lié depuis `~/.config/nwg-drawer/drawer.css`.

**Nettoyage** (demande : « garde que ce que j'ai besoin ») : 32 entrées techniques cachées sans les désinstaller, en posant dans
`~/.local/share/applications/` une **copie** du `.desktop` avec `NoDisplay=true` et le marqueur `X-Grille-Masquee=true`
(exemples d'entrées masquées : `btop`, `jconsole`, `jshell`, `lstopo`, `qv4l2`, `rofi`, `nvtop`, `xgps`, `kitty`, `cups`…).
Pour restaurer une entrée : supprimer la copie. Il reste **35 applications**.

## Icônes du bureau

6 icônes eww (Claude Desktop, VS Code, Chrome, Terminal, Raccourcis, Applications) — voir [chap. 5](05-barre-widgets-outils.md).
Pour en changer : `eww_yuck()` dans `generer.py`, puis `theme regenerer`.
